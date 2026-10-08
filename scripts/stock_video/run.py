#!/usr/bin/env python3
import argparse,concurrent.futures,datetime as dt,hashlib,json,math,os,subprocess,urllib.request
from pathlib import Path
import numpy as np
import soundfile as sf
import data,render

def scripts(a):
    l=a['last'];m=render.money;r=a['resistance'];an=a['anatomy']
    title=f'ABOVE {a["above_count"]} OF 4 MOVING AVERAGES'
    trend=a['trend'];gap=a['gap']
    news=a['news'];news_voice=[]
    for kind in ['positive','risk']:
        item=news[kind]
        if item:news_voice.append(f'On {kind}, {item["publisher"]} reports: {item["headline"]}.')
        else:news_voice.append(f'No source verified {kind} news item was available for this review.')
    rows=[
      (title,'Completed daily bar · not a live quote',render.GOLD,f'{a["company"]} closed at {m(l["close"])}, a {abs(a["change_pct"]):.2f} percent {"gain" if a["change_pct"]>=0 else "decline"}. Price is above {a["above_count"]} of four moving averages. This is the {render.date(a["date"])} daily close.'),
      (f'+{a["advance_pct"]:.1f}% FROM {render.short(a["anchor_date"]).upper()}',f'Recent 60-session low: {m(a["anchor_price"])}',render.BLUE,f'From the {render.short(a["anchor_date"])} low of {m(a["anchor_price"])}, the advance is {a["advance_pct"]:.1f} percent. That measures the move from a recent low, not a prediction.'),
      ('RISING SWING-LOW REFERENCE' if trend['rising'] else 'A RECENT SWING-LOW REFERENCE','Historical anchors · no guaranteed support',render.GREEN,f'{"These two confirmed swing lows define a rising reference line" if trend["rising"] else "This confirmed historical low provides a horizontal reference"}. Watch how price behaves around it. A drawn line does not guarantee support.'),
      ('A REMAINING PRICE GAP' if gap else 'VOLUME IN CONTEXT',f'{m(gap["low"])}–{m(gap["high"])}' if gap else f'{a["volume_ratio"]:.2f}× the 20-session average',render.GREEN if gap else render.CYAN,
       f'A gap remains between {m(gap["low"])} and {m(gap["high"])}. The reviewed daily bars have not fully filled that zone.' if gap else f'Volume is {a["volume_ratio"]:.2f} times its twenty session average. The daily true range average is {m(l["atr"])}. That is the activity and volatility context.'),
      ('THE LEVELS TO WATCH','Resistance '+ ' / '.join(m(x) for x in r)+' · Support '+m(a['support']),render.RED,f'Resistance references are {" and ".join(m(x) for x in r)}. Below price, {m(a["support"])} is a support reference. These are observed historical levels, not promised turning points.'),
      ('INSIDE THE LAST DAILY CANDLE',f'Body: {an["body_pct"]:.1f}% of range · Volume: {a["volume_ratio"]:.2f}×',render.GOLD,f'Zoom in on the last candle. The body occupies {an["body_pct"]:.1f} percent of the full range. The upper wick is {m(an["upper_wick"])} and the lower wick is {m(an["lower_wick"])}. The close is at {an["close_position"]:.1f} percent of the daily range.'),
      (f'RSI(14): {l["rsi"]:.1f}',f'ATR(14): {m(l["atr"])} · CCI(14): {l["cci"]:+.1f}',render.CYAN,f'R S I is {l["rsi"]:.1f}, {"above seventy" if l["rsi"]>70 else "below thirty" if l["rsi"]<30 else "between thirty and seventy"}. A T R is {m(l["atr"])}. Read momentum together with price and volume; an indicator alone is not a trade instruction.'),
      ('REPORTED NEWS · '+a['ticker'],'Source and publication dates are shown',render.GOLD,' '.join(news_voice)+' These are reported headlines, not an explanation for every price move.'),
      ('TWO SCENARIOS. PLAN BOTH.','Scenarios, not predictions.',render.FG,f'Above {m(r[-1])}, watch whether price holds with stronger volume. Below {m(a["support"])}, watch whether support fails. These are conditional scenarios, not predictions.'),
      ('EDUCATION ONLY','Not a recommendation to buy or sell.',render.GOLD,'Education, not financial advice. Follow for the next daily chart.')]
    return [dict(title=x,subtitle=y,color=z,voice=v) for x,y,z,v in rows]

def model_file(cache,name,url):
    path=cache/name
    if not path.exists():
        print('Downloading speech model',name,flush=True)
        urllib.request.urlretrieve(url,path)
    expected={'kokoro-v1.0.onnx':'7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5','voices-v1.0.bin':'bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d'}
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest!=expected[name]:raise RuntimeError(f'Speech model checksum mismatch: {name}')
    return path,digest

def voice(rows,out,cache):
    import onnxruntime as ort
    from kokoro_onnx import Kokoro
    cache.mkdir(parents=True,exist_ok=True)
    model,hm=model_file(cache,'kokoro-v1.0.onnx','https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx')
    voices,hv=model_file(cache,'voices-v1.0.bin','https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin')
    (out/'speech_model_hashes.json').write_text(json.dumps({model.name:hm,voices.name:hv},indent=2))
    original=ort.InferenceSession
    def session(*args,**kwargs):
        options=ort.SessionOptions();options.intra_op_num_threads=2;options.inter_op_num_threads=1;kwargs['sess_options']=options
        return original(*args,**kwargs)
    ort.InferenceSession=session
    engine=Kokoro(str(model),str(voices));all_audio=[np.zeros(28800)];cursor=1.2
    for i,s in enumerate(rows):
        samples,sr=engine.create(s['voice'],voice='am_michael',speed=1.13,lang='en-us')
        samples=np.concatenate([np.zeros(round(.15*sr)),samples,np.zeros(round(.35*sr))])
        seconds=math.ceil(len(samples)/(sr/30))/30
        samples=np.pad(samples,(0,round(seconds*sr)-len(samples)))
        s.update(duration=seconds,start=cursor,end=cursor+seconds);cursor+=seconds;all_audio.append(samples)
        print('Narration',i,round(seconds,2),'seconds',flush=True)
    sf.write(out/'narration.wav',np.concatenate(all_audio),24000)
    (out/'timing.json').write_text(json.dumps(rows,indent=2))
    return cursor

def music(out,duration):
    sr=24000;t=np.arange(round(duration*sr))/sr;result=np.zeros(len(t))
    chords=[(110,130.8128,164.8138),(87.3071,110,130.8128),(130.8128,164.8138,195.9977),(97.9989,123.4708,146.8324)]
    for k in range(math.ceil(duration/8)):
        a=k*8;b=min(duration,(k+1)*8+.7);i0=round(a*sr);i1=min(len(t),round(b*sr));tt=t[i0:i1]-a
        env=np.clip(np.minimum(tt/1.2,1)*np.minimum((b-a-tt)/1.2,1),0,1)
        for f in chords[k%4]:result[i0:i1]+=.032*env*(np.sin(2*np.pi*f*tt)+.15*np.sin(2*np.pi*f*2*tt))
    result*=np.clip((duration-t)/2,0,1);sf.write(out/'music.wav',result,sr)

def deliver_text(a,out):
    l=a['last'];levels=' / '.join(render.money(x) for x in a['resistance'])
    title=f'{a["ticker"]} Daily Chart: Key Levels & Candle Signals | {a["date"]}'
    description=f'''{a['ticker']} closed at ${l['close']:.2f} ({a['change_pct']:+.2f}%).\n\nResistance: {levels}\nSupport reference: ${a['support']:.2f}\nRSI(14): {l['rsi']:.1f} | ATR(14): ${l['atr']:.2f}\nVolume: {a['volume_ratio']:.2f}× the 20-session average.\n\nAbove ${a['resistance'][-1]:.2f}: watch whether price holds with stronger volume. Below ${a['support']:.2f}: watch whether support fails. Scenarios, not predictions.\n\nData: {a['date']} daily close · Yahoo Finance. Analysis date: {a['analysis_date']}. News dates are labelled separately.\n\nEducation only. Not financial advice. I am not a licensed advisor. Not a recommendation to buy or sell.\n\n#{a['ticker']} #Palantir #StockAnalysis #TechnicalAnalysis #StockMarket'''
    (out/'TikTok_caption.txt').write_text(title+'\n\n'+description)
    (out/'YouTube_title_and_description.txt').write_text('TITLE\n'+title+'\n\nDESCRIPTION\n'+description+'\n\nSubscribe for more daily chart breakdowns.\n')
    sources=f'''# Sources and methods\n\nTrade date: {a['date']}. Analysis date: {a['analysis_date']}.\n\nMarket source: {a['price_source']}\nRetrieved: {a['retrieved_utc']}\n\nThe required dated historical daily bar is used consistently for OHLCV. SMA20/50/150/200 are arithmetic means of complete daily closes. RSI14 and ATR14 use Wilder smoothing initialized by 14-period arithmetic averages. CCI14 uses typical price and mean absolute deviation with scale constant 0.015. All calculations use two years of history. The candle body, wicks and close position are computed directly from OHLC. Relative volume uses the last 20 sessions including this session. Confirmed swings compare three bars on each side. A rising support line is shown only if observed subsequent lows do not cross below it; otherwise a labelled horizontal historical-low reference is used.\n\nNews: reported headlines in the last 14 days with title, publisher and publication timestamp; full articles are not independently verified. Missing positive/risk items and an unverified earnings date are disclosed. The headline categories are editorial, not assertions of price causality.\n\nAnimated camera and drawing tools do not represent real-time ticks. Historical data remains fixed. English narration is synthetic, with no voice cloning. Music is an original synthesized ambient bed. All text and numbers are drawn in code; the bull/bear background contains no numeric data.\n\nRaw market data, reviewed daily.csv, analysis.json and timing.json are retained in the workflow artifact.\n'''
    for kind in ['positive','risk']:
        item=a['news'][kind]
        if item:sources+=f'\n- {kind}: [{item["headline"]}]({item["url"]}), {item["publisher"]}, {item["published"]}.\n'
    (out/'Sources_and_methods.md').write_text(sources)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--ticker',default='PLTR');parser.add_argument('--date');parser.add_argument('--out',required=True);parser.add_argument('--model-cache',default=str(Path.home()/'.cache/stock-video'));parser.add_argument('--attempts',type=int,default=1);parser.add_argument('--data-only',action='store_true')
    args=parser.parse_args();out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    a=data.load(args.ticker,args.date,out,args.attempts);deliver_text(a,out)
    rows=scripts(a)
    if args.data_only:print(json.dumps(a,indent=2));return
    duration=voice(rows,out,Path(args.model_cache));render.init(out)
    render.cover(Path(__file__).parent/'assets/bg_bullbear.png')
    # Render representative image checks before encoding. Each frame still uses real reviewed prices.
    for i in range(len(rows)):render.frame(i,rows[i]['duration']*.7).save(out/f'check_{i:02d}.png')
    chunks=out/'chunks';chunks.mkdir(exist_ok=True)
    pieces=[]
    for i,s in enumerate(rows):
        count=math.ceil(s['duration']/14)
        total_frames=round(s['duration']*30)
        for part in range(count):
            lo=round(total_frames*part/count)/30;hi=round(total_frames*(part+1)/count)/30
            pieces.append((i,lo,hi,len(pieces)))
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:clips=list(pool.map(render.render_piece,pieces))
    intro=chunks/'intro.mp4';cover=out/(args.ticker+'_cover.png')
    vf="scale=2160:3840,zoompan=z='1+0.025*on/35':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=36:s=1080x1920:fps=30,fade=t=out:st=1.13:d=0.07:color=white"
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(cover),'-vf',vf,'-frames:v','36','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-threads','2','-video_track_timescale','15360',str(intro)],check=True)
    listing=chunks/'concat.txt';listing.write_text('\n'.join("file '"+str(p)+"'" for p in [intro]+clips)+'\n')
    silent=chunks/'silent.mp4';subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(silent)],check=True)
    music(out,duration);final=out/f'{args.ticker}_analysis_{a["date"]}.mp4'
    af=f'[1:a]loudnorm=I=-16:TP=-1.5:LRA=7[voice];[2:a]volume=0.22[music];[voice][music]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95,aresample=48000,atrim=duration={duration:.9f},asetpts=PTS-STARTPTS[a]'
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(silent),'-i',str(out/'narration.wav'),'-i',str(out/'music.wav'),'-filter_complex',af,'-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(final)],check=True)
    streams=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(final)]))['streams'];video=next(s for s in streams if s['codec_type']=='video');audio=next(s for s in streams if s['codec_type']=='audio')
    assert (video['width'],video['height'],video['r_frame_rate'])==(1080,1920,'30/1'), f'Video format: {video}'
    assert abs(float(video['duration'])-duration)<.04, f'Video duration {video["duration"]}; expected {duration}'
    assert abs(float(video['duration'])-float(audio['duration']))<.06, f'Video duration {video["duration"]}; audio {audio["duration"]}'
    subprocess.run(['ffmpeg','-v','error','-i',str(final),'-f','null','-'],check=True)
    (out/'validation.json').write_text(json.dumps({'passed':True,'trade_date':a['date'],'video_duration':video['duration'],'audio_duration':audio['duration'],'dimensions':[1080,1920],'frame_rate':30,'sha256':hashlib.sha256(final.read_bytes()).hexdigest()},indent=2))
    (out/'READY.txt').write_text(f'{final.name}\nTrade date: {a["date"]}\nValidated {dt.datetime.now(dt.timezone.utc).isoformat()}\n')
    print('READY',final,flush=True)

if __name__=='__main__':
    try:main()
    except Exception:
        import traceback
        message=traceback.format_exc().replace('%','%25').replace('\r','%0D').replace('\n','%0A')
        print('::error title=Video production failed::'+message,flush=True)
        raise
