#!/usr/bin/env python3
"""Produce the requested dated weekly edition and two separately framed Shorts."""
import argparse,concurrent.futures,datetime as dt,hashlib,json,math,os,re,shutil,subprocess,sys
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw
import market,editorial,visuals

def engine(cache):
    sys.path.insert(0,str(Path(__file__).parent.parent/'stock_video'))
    import run as stock_run
    # Import by path avoids the __main__/run naming ambiguity.
    import importlib.util
    spec=importlib.util.spec_from_file_location('stock_helpers',Path(__file__).parent.parent/'stock_video'/'run.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    import onnxruntime as ort
    from kokoro_onnx import Kokoro
    cache.mkdir(parents=True,exist_ok=True)
    model,_=helper.model_file(cache,'kokoro-v1.0.onnx','https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx')
    voices,_=helper.model_file(cache,'voices-v1.0.bin','https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin')
    original=ort.InferenceSession
    def session(*args,**kwargs):
        opt=ort.SessionOptions();opt.intra_op_num_threads=2;opt.inter_op_num_threads=1;kwargs['sess_options']=opt
        return original(*args,**kwargs)
    ort.InferenceSession=session
    return Kokoro(str(model),str(voices))

def stamp(t):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'

def narration(rows,out,voice,speed,intro=0):
    all_audio=[np.zeros(round(intro*24000))] if intro else [];cursor=intro;subtitles=[]
    for i,row in enumerate(rows):
        pieces=[];captions=[];local=0
        for words in editorial.caption_chunks(row['voice']):
            audio,sr=voice.create(words,voice='am_michael',speed=speed,lang='en-us');assert sr==24000
            audio=np.concatenate([np.zeros(720),audio,np.zeros(960)])
            duration=len(audio)/sr;captions.append({'text':words,'start':local,'end':local+duration})
            subtitles.append((cursor+local,cursor+local+duration,words));pieces.append(audio);local+=duration
        duration=math.ceil((local+.22)*24)/24
        samples=np.pad(np.concatenate(pieces),(0,round(duration*24000)-sum(len(p) for p in pieces)))
        row.update(duration=duration,start=cursor,end=cursor+duration,captions=captions);all_audio.append(samples);cursor+=duration
        print(f'Narration {out.name} {i+1}/{len(rows)} {duration:.2f}s',flush=True)
    speech=np.concatenate(all_audio);peak=float(np.max(np.abs(speech)));speech*=min(1.8,.85/max(peak,1e-8))
    sr=24000;t=np.arange(len(speech))/sr;bed=np.zeros(len(speech))
    for n in range(math.ceil(cursor/8)):
        lo=n*8;hi=min(cursor,lo+8);a=round(lo*sr);b=min(len(t),round(hi*sr));tt=t[a:b]-lo;env=np.minimum(tt/1.0,1)*np.minimum((hi-lo-tt)/1.0,1)
        for f in [(110,130.81,164.81),(87.31,110,130.81),(130.81,164.81,196),(98,123.47,146.83)][n%4]:bed[a:b]+=.009*env*np.sin(2*np.pi*f*tt)
    mixed=speech+bed;assert max(np.abs(mixed))<1
    sf.write(out/'narration.wav',speech,sr);sf.write(out/'mixed.wav',mixed,sr,subtype='PCM_24')
    (out/'timing.json').write_text(json.dumps(rows,indent=2));(out/'captions.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{s}' for i,(a,b,s) in enumerate(subtitles))+'\n')
    (out/'script.txt').write_text('\n\n'.join(x['title']+'\n'+x['voice'] for x in rows))
    return cursor

def validate(path,duration,portrait):
    raw=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(path)]));v=next(x for x in raw['streams'] if x['codec_type']=='video');a=next(x for x in raw['streams'] if x['codec_type']=='audio')
    dimensions=(1080,1920) if portrait else (1920,1080)
    assert (v['width'],v['height'])==dimensions
    assert abs(float(v['duration'])-duration)<.08 and abs(float(v['duration'])-float(a['duration']))<.1
    assert v['r_frame_rate']=='24/1'
    subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'],check=True)
    return {'passed':True,'dimensions':list(dimensions),'duration':float(v['duration']),'audio_duration':float(a['duration']),'fps':24,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}

def render(a,rows,out,portrait,workers,intro=0):
    (out/'analysis.json').write_text(json.dumps(a,indent=2));(out/'chunks').mkdir(exist_ok=True)
    tasks=[]
    for i,row in enumerate(rows):
        count=math.ceil(row['duration']/14);frames=round(row['duration']*24)
        for k in range(count):tasks.append((str(out),i,round(frames*k/count)/24,round(frames*(k+1)/count)/24,portrait,len(tasks)))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        clips=[]
        for path in pool.map(visuals.render_piece,tasks):clips.append(path);print('Rendered',out.name,len(clips),'/',len(tasks),flush=True)
    if intro:clips.insert(0,str(visuals.ASSETS/'intro.mp4'))
    listing=out/'chunks'/'concat.txt';listing.write_text('\n'.join("file '"+x+"'" for x in clips)+'\n')
    silent=out/'chunks'/'silent.mp4';subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(silent)],check=True)
    dest=out/(out.name+'.mp4');subprocess.run(['ffmpeg','-v','error','-y','-i',str(silent),'-i',str(out/'mixed.wav'),'-c:v','copy','-c:a','aac','-b:a','128k','-movflags','+faststart',str(dest)],check=True)
    if dest.stat().st_size>94*1024*1024:
        smaller=out/'smaller.mp4';subprocess.run(['ffmpeg','-v','error','-y','-i',str(dest),'-c:v','libx264','-b:v','1400k','-maxrate','1800k','-bufsize','3600k','-preset','fast','-c:a','copy',str(smaller)],check=True);smaller.replace(dest)
    assert dest.stat().st_size<99*1024*1024,'GitHub individual file limit'
    duration=intro+sum(x['duration'] for x in rows);receipt=validate(dest,duration,portrait)
    # Pixel differences verify actual motion, independently of encoded frame count.
    f0=np.asarray(visuals.frame(a,rows[0],1.0,portrait),dtype=float);f1=np.asarray(visuals.frame(a,rows[0],3.0,portrait),dtype=float)
    receipt['motion_mean_absolute_difference']=float(np.abs(f0-f1).mean());assert receipt['motion_mean_absolute_difference']>.1
    receipt['caption_segments']=sum(len(x['captions']) for x in rows);assert receipt['caption_segments']>0
    (out/'validation.json').write_text(json.dumps(receipt,indent=2));return dest,receipt

def contact_sheet(a,rows,out):
    thumbs=[]
    for i,row in enumerate(rows):
        im=visuals.frame(a,row,min(4,row['duration']/2));im.save(out/f'check_{i:02}.jpg',quality=85);thumbs.append(im.resize((384,216)))
    sheet=Image.new('RGB',(384*4,240*math.ceil(len(thumbs)/4)),visuals.BG);d=ImageDraw.Draw(sheet)
    for i,im in enumerate(thumbs):x=i%4*384;y=i//4*240;sheet.paste(im,(x,y));d.text((x+6,y+220),f'{i+1}: {rows[i]["kind"]}',fill=visuals.WHITE)
    sheet.save(out/'contact-sheet.jpg',quality=90)

def main():
    p=argparse.ArgumentParser();p.add_argument('--date',required=True);p.add_argument('--out',required=True);p.add_argument('--attempts',type=int,default=1);p.add_argument('--model-cache',default=str(Path.home()/'.cache/stock-video'));p.add_argument('--reuse-data',action='store_true');p.add_argument('--data-only',action='store_true');p.add_argument('--smoke',action='store_true');p.add_argument('--workers',type=int,default=2);args=p.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    a=json.loads((out/'analysis.json').read_text()) if args.reuse_data else market.collect(out,args.date,args.attempts)
    assert a['date']==args.date
    rows=editorial.build(a);(out/'draft_script.json').write_text(json.dumps(rows,indent=2))
    if args.data_only:print(json.dumps({'date':a['date'],'markets':len(a['markets']),'headlines':len(a['news']),'calendar':a['calendar'],'supplemental':a['supplemental'],'errors':a['extra_errors']},indent=2));return
    voice=engine(Path(args.model_cache));outputs=[]
    long_name='Market_Mind_Weekly_2026-10-05_to_09';long_out=out/long_name;long_out.mkdir(exist_ok=True)
    if args.smoke:
        rows=[dict(rows[i]) for i in [0,7,10]]
        for r in rows:r['voice']='This is a production test. Moving graphics, English narration and synchronized captions.'
    duration=narration(rows,long_out,voice,1.18,intro=4)
    if not args.smoke:assert 300<=duration<=480,f'Weekly narration must be 5–8 minutes; got {duration:.1f}s'
    contact_sheet(a,rows,long_out);path,receipt=render(a,rows,long_out,False,args.workers,intro=4);outputs.append({'path':str(path.relative_to(out)),**receipt})
    for k,s in enumerate(editorial.short_scripts(a)):
        name=f'Market_Mind_Short_{k+1}';short_out=out/name;short_out.mkdir(exist_ok=True)
        if args.smoke:s['voice']='This is a portrait video test with English captions and moving visuals.'
        d=narration([s],short_out,voice,1.08)
        assert 3<d<=65
        path,receipt=render(a,[s],short_out,True,args.workers);outputs.append({'path':str(path.relative_to(out)),**receipt})
    thumb=Image.open(visuals.ASSETS/'newsroom.png').convert('RGB').resize((1920,1080));overlay=Image.new('RGBA',thumb.size,(0,0,0,65));thumb=Image.alpha_composite(thumb.convert('RGBA'),overlay).convert('RGB')
    visuals.text(thumb,(80,75),'MARKET MIND',70,visuals.GOLD,True);visuals.text(thumb,(80,205),'THE WEEK AHEAD',95,visuals.WHITE,True);visuals.text(thumb,(85,340),'OCT 12–16',67,visuals.GOLD,True);visuals.text(thumb,(85,955),'Weekly review: Oct 5–9, 2026',34,visuals.WHITE,True);thumb.save(out/'YouTube_thumbnail.png')
    sources=['# Sources and methods','',f'Review: October 5–9, 2026. Data used: {a["date"]}. Outlook: October 12–16, 2026.',f'Retrieved: {a["retrieved_utc"]}.','', 'Weekly equity returns: dated close / October 2 close minus 1. Bitcoin is a timestamped daily snapshot, not an equity closing print. Oil futures and foreign exchange use provider session conventions. Treasury yields are percentages, not bond prices. Moving averages: simple daily close averages. RSI/ATR: Wilder smoothing. CCI: 14-day typical-price mean deviation. Historical support/resistance references are not forecasts.','', 'October statistics: 2011–2025 adjusted monthly close, September month-end to October month-end. Dividends follow Yahoo adjustments; this is a total-return proxy, not an independently constructed reinvested portfolio. The incomplete October 2026 is excluded.','', 'News is attributed headline metadata, not independent full-article verification. Earnings from Nasdaq calendar are labelled estimated unless independently confirmed.','', 'Background is AI-generated illustration. English narration is synthetic, not an impersonation. Music is originally synthesized. All market labels and calculations are generated by code. Images and text do not represent breaking/live footage.','']
    sources += [f'- {s}: {r["source"]}' for s,r in a['markets'].items()]
    sources += [f'- October {x["symbol"]}: {x["source"]}' for x in a['seasonality']]
    sources += [f'- {x["published"]} | {x["publisher"]} | {x["title"]} | {x["url"]}' for x in a['news']]
    sources += [f'- {x["date"]} | {x.get("event",x.get("symbol"))} | {x["status"]} | {x["source"]}' for x in a['calendar']['macro']+a['calendar']['earnings']]
    sources += ['','## Unresolved source limitations']+a['news_errors']+a['calendar']['errors']+a['extra_errors'];(out/'Sources_and_methods.md').write_text('\n'.join(sources))
    title='Weekly Market Review: Stocks, Yields & October History | Oct 5–9, 2026'
    description='What changed during October 5–9, and what to watch October 12–16: SPY, QQQ, Dow Jones, VIX, Treasury yields, oil, the dollar, Bitcoin and market breadth. Plus 15 years of October returns and a technical watchlist: MSTR, IREN, AVGO and CIFR.\n\nAll scenarios are conditional. Earnings calendar estimates are labelled. Sources and data dates accompany the video.\n\nEducation only. Not financial advice. I am not a licensed advisor. Not a recommendation to buy or sell.\n\n#StockMarket #WeeklyMarketReview #SPY #QQQ #MarketMind'
    (out/'YouTube_title_and_description.txt').write_text(title+'\n\n'+description)
    (out/'TikTok_captions.txt').write_text('SHORT 1\nIs October really profitable? 15 years of SPY data, with the losing years included. Full weekly review on YouTube: @MarketMindTradingBasics. Education only, not financial advice. #SPY #StockMarket #TradingEducation\n\nSHORT 2\nNext week: connect support, breadth, yields and volatility. Full October 5–9 review and October 12–16 outlook on YouTube: @MarketMindTradingBasics. Education only, not financial advice. #MarketMind #QQQ #StockMarket\n')
    manifest={'passed':True,'smoke':args.smoke,'preview':a['preview'],'date':a['date'],'week':['2026-10-05','2026-10-09'],'next_week':['2026-10-12','2026-10-16'],'outputs':outputs,'completed_utc':dt.datetime.now(dt.timezone.utc).isoformat()};(out/'validation.json').write_text(json.dumps(manifest,indent=2));(out/'READY.txt').write_text('All three requested video files validated.\n');print('READY',json.dumps(manifest),flush=True)

if __name__=='__main__':main()
