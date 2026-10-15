"""One-date post-close NKE / USO production. No social-media posting."""
import argparse, datetime as dt, hashlib, inspect, json, os, subprocess, sys, time, urllib.parse, zipfile
from pathlib import Path
from zoneinfo import ZoneInfo
import data, render, run as stock
from PIL import ImageFont

HERE=Path(__file__).resolve().parent
NOW=lambda:dt.datetime.now(dt.timezone.utc)
base_load=data.load
base_scripts=stock.scripts
base_deliver=stock.deliver_text

def collect_news(ticker,out):
    queries=['NKE','Nike'] if ticker=='NKE' else ['USO','CL=F','oil Iran conflict']
    records=[];errors=[]
    for q in queries:
        url='https://query1.finance.yahoo.com/v1/finance/search?'+urllib.parse.urlencode({'q':q,'newsCount':50})
        try:
            raw=data.request_json(url)
            (out/('news_'+urllib.parse.quote(q,safe='')+'.json')).write_text(json.dumps(raw))
            for item in raw.get('news',[]):
                title=item.get('title','');lower=title.lower();stamp=item.get('providerPublishTime',0)
                if not 0<=NOW().timestamp()-stamp<=7*86400:continue
                if not any(w in lower for w in (['nike','nke'] if ticker=='NKE' else ['oil','crude','opec','hormuz','iran','petroleum'])):continue
                if not item.get('link') or not item.get('publisher'):continue
                if len(title)<18 or title.startswith('BC-'):continue
                if any(w in lower for w in ['high school','basketball scores','which stock is the better value','earnings preview']):continue
                if any(w in lower for w in ['should you buy','stocks to buy','best stocks','price prediction']):continue
                r={'headline':title,'publisher':item['publisher'],'url':item['link'],'published':dt.datetime.fromtimestamp(stamp,dt.timezone.utc).isoformat(),'source_query':url,'full_article_verified':False}
                if not any(x['headline']==title for x in records):records.append(r)
        except Exception as e:errors.append(type(e).__name__+': '+str(e))
    records.sort(key=lambda x:x['published'],reverse=True)
    # Preserve all relevant evidence; select two distinct dated items, not sentiment claims.
    (out/'news_review.json').write_text(json.dumps({'retrieved_utc':NOW().isoformat(),'items':records,'errors':errors},indent=2))
    if len(records)<2:raise RuntimeError('Fewer than two dated relevant headlines; refusing a news-free edition')
    reliable=['Reuters','Associated Press','The Wall Street Journal','MT Newswires','CNBC','Bloomberg','Barrons.com','Business Wire']
    chosen=sorted(records,key=lambda x:(x['publisher'] in reliable,x['published']),reverse=True)
    if ticker=='NKE':
        others=[x for x in records if x['publisher']!=chosen[0]['publisher']]
        if others:chosen=[chosen[0],others[0]]
    if ticker=='USO':
        geopolitical=[x for x in chosen if any(w in x['headline'].lower() for w in ['iran','hormuz','middle east','fighting','attack','sanction','houthi'])]
        if geopolitical and geopolitical[0]!=chosen[0]:chosen=[chosen[0],geopolitical[0]]
    return {'positive':chosen[0],'risk':chosen[1],'limitation':'Feed headlines are attributed; full article text not independently verified.'}

def load(ticker,expected,out,attempts=1):
    original_news=data.news;data.news=lambda *args:{'positive':None,'risk':None}
    try:a=base_load(ticker,expected,out,attempts)
    finally:data.news=original_news
    a['company']='Nike' if ticker=='NKE' else 'United States Oil Fund'
    # Local low is a reference, never a declaration that the final bottom is in.
    import pandas as pd
    d=pd.read_csv(out/'daily.csv');a['support']=float(d.low.tail(10).min())
    a['news']=collect_news(ticker,out)
    (out/'analysis.json').write_text(json.dumps(a,indent=2));return a

def scripts(a):
    rows=base_scripts(a);l=a['last'];r=a['resistance'];m=lambda v:f'{v:.2f} dollars'
    above=a['above_count'];support=a['support']
    if a['ticker']=='NKE':
        titles=['NIKE: TURNAROUND OR ANOTHER BOUNCE?','THE MOVE IN CONTEXT','WHAT WOULD CONFIRM A TURN?','PARTICIPATION MATTERS','THE LEVELS THAT MATTER','READ THE DAILY CANDLE','MOMENTUM IS NOT CONFIRMATION','NIKE: DATED NEWS CHECK','BOTTOM? TWO CONDITIONAL CASES','SUBSCRIBE · EDUCATION ONLY']
        voices=[
          f'Has Nike finally found a bottom, or is this another bounce inside a decline? The October fifteenth close is {m(l["close"])}. Here is what the chart confirms, and what it does not.',
          f'From the {a["anchor_date"]} local low at {m(a["anchor_price"])}, price has moved {a["advance_pct"]:.1f} percent. Price is above {above} of four moving averages. A recovery from a low is not by itself a trend reversal.',
          'A stronger reversal case needs a higher low, a break of a meaningful prior swing high, and follow through. The line on this chart is only a historical reference. A final bottom cannot be established from one candle.',
          f'Volume is {a["volume_ratio"]:.2f} times the twenty session average. '+('Participation is above that average, but still needs follow through.' if a['volume_ratio']>1 else 'Participation is below that average, so this is not a volume breakout confirmation.'),
          f'The nearest historical resistance references are {" and ".join(m(x) for x in r)}. The ten session low at {m(support)} is the downside reference. These levels frame the question; they do not answer it in advance.',
          f'The last candle opened at {m(l["open"])}, reached a low of {m(l["low"])}, and closed at {m(l["close"])}. The close sits {a["anatomy"]["close_position"]:.0f} percent up the daily range. Read the recovery or rejection without inventing buyer identities.',
          f'R S I is {l["rsi"]:.1f}. Average daily true range is {m(l["atr"])}. Momentum can improve before the wider trend turns. Neither an oversold reading nor a green candle guarantees that the decline is finished.',
          '',
          f'Above {m(r[-1])}, a sustained hold followed by a higher low would strengthen the reversal case. Below {m(support)}, the bottom thesis weakens. Until price confirms, a bottom is a scenario, not an established fact.',
          'Subscribe to Market Mind Trading Basics for the next chart breakdown. Education only. I am not a licensed financial advisor. This is not financial advice or a recommendation to buy, sell, or take investment action.'
        ]
    else:
        titles=['OIL: GEOPOLITICAL BREAKOUT RISK?','USO IS NOT SPOT OIL','PRICE FIRST · HEADLINES SECOND','VOLATILITY + PARTICIPATION','THE BREAKOUT REFERENCE','THE DAILY REACTION','MOMENTUM + RISK','OIL: DATED NEWS CHECK','ESCALATION OR DE-ESCALATION?','SUBSCRIBE · EDUCATION ONLY']
        voices=[
          f'Could a geopolitical shock trigger the next oil breakout? A renewed attack or fighting could change the supply risk premium. But that is a conditional risk scenario, not a claim that an attack has happened. U S O closed at {m(l["close"])}.',
          f'U S O is the United States Oil Fund. It mainly provides exposure through oil futures, rather than holding spot barrels. Futures curve effects, rolling contracts, fees, and tracking differences mean it will not move exactly like spot crude. Price is above {above} of four moving averages.',
          'A headline alone is not a confirmed breakout. Watch the marked resistance, the daily close, and whether the move holds. The trend reference on screen is historical support context, not a guaranteed floor.',
          f'Volume is {a["volume_ratio"]:.2f} times the twenty session average. Average true range is {m(l["atr"])}. A sudden risk premium can also reverse quickly when supply fears ease.',
          f'Resistance references on the U S O chart are {" and ".join(m(x) for x in r)}. Support is the ten session low at {m(support)}. These are fund price levels, not a dollar per barrel forecast.',
          f'The daily high was {m(l["high"])}, the low {m(l["low"])}, and the close {m(l["close"])}. The close is {a["anatomy"]["close_position"]:.0f} percent up the range. That describes the reaction without assigning a single cause.',
          f'R S I is {l["rsi"]:.1f}. Momentum needs to agree with price and participation. Even if the setup looks constructive, geopolitical news can cause gaps in either direction.',
          '',
          f'If verified escalation threatens supply and price holds above {m(r[-1])}, the breakout case strengthens. If tensions ease, or price loses {m(support)}, that case weakens. Neither escalation nor a breakout is guaranteed. Scenarios, not predictions.',
          'Subscribe to Market Mind Trading Basics for more market context. Education only. I am not a licensed financial advisor. This is not financial advice or a recommendation to buy, sell, or take investment action.'
        ]
    items=[a['news'][k] for k in ['positive','risk']]
    voices[7]='Here are two dated reported headlines. '+' '.join(f'On {x["published"][:10]}, {x["publisher"]} reported: {x["headline"]}.' for x in items)+' These are attributed feed headlines. Full articles were not independently verified, and price causality is not established.'
    for row,title,voice in zip(rows,titles,voices):row.update(title=title,voice=voice,subtitle='Completed October 15 session · Conditional analysis')
    return rows

def deliver(a,out):
    base_deliver(a,out)
    t=a['ticker'];l=a['last'];title='Nike Stock: Trend Reversal or Another Bounce?' if t=='NKE' else 'Oil Breakout Risk: What Could Geopolitics Change? | USO'
    angle='Has Nike found a bottom? Watch for a higher low, resistance clearance and follow through. A final bottom is not confirmed by one candle.' if t=='NKE' else 'A verified escalation that threatens supply could strengthen an oil breakout scenario. Escalation and a breakout are not guaranteed. USO holds futures exposure and does not track spot oil exactly.'
    text=f'{angle}\n\nClose: ${l["close"]:.2f} ({a["change_pct"]:+.2f}%). Resistance: '+', '.join(f'${r:.2f}' for r in a['resistance'])+f'. Support reference: ${a["support"]:.2f}.\nData: October 15, 2026 completed session.\n\n'
    text+='Reported headlines (feed text; full articles not independently verified):\n'+'\n'.join(f'- {a["news"][k]["publisher"]}, {a["news"][k]["published"][:10]}: {a["news"][k]["headline"]}\n{a["news"][k]["url"]}' for k in ['positive','risk'])
    text+='\n\nSubscribe to Market Mind Trading Basics. Scenarios, not predictions. Education only. Not financial advice. I am not a licensed advisor. Not a recommendation to buy or sell.\n\n#'+t+' #StockMarket #TechnicalAnalysis #MarketMind #Shorts\n'
    (out/'YouTube_title_and_description.txt').write_text(title+'\n\n'+text)
    (out/'TikTok_caption.txt').write_text(title+'\n\n'+angle+f'\nClose ${l["close"]:.2f} · Oct 15, 2026. Full news sources included in the publishing pack. Scenarios, not predictions. Education only. Not financial advice. I am not a licensed advisor.\n#'+t+' #StockMarket #TechnicalAnalysis #MarketMind\n')
    (out/'YouTube_upload_settings.txt').write_text('Vertical 1080x1920 Short. English. Category: Education. Audience: not made for kids. No paid promotion unless separately applicable. Review synthetic-content disclosure for the narration. No social posting performed by this job.\n')
    (out/'Sources_and_methods.md').write_text((out/'Sources_and_methods.md').read_text()+'\n\nEdition-specific corrections: support is the latest ten-session low, not an automatically confirmed bottom. News slots are ITEM 1 / ITEM 2, not positive / negative sentiment judgments. All relevant feed records and query sources are preserved in news_review.json. USO futures exposure differs from spot oil.\n')

def configure():
    data.load=load;stock.scripts=scripts;stock.deliver_text=deliver
    fonts=HERE.parent/'weekly_video/assets'
    render.font=lambda size,bold=False:ImageFont.truetype(str(fonts/('Inter-700.ttf' if bold else 'Inter-400.ttf')),size)
    src=inspect.getsource(stock.voice).replace("speed=1.13","speed=1.0")
    # Start speech in the intro; shift visual captions by the same amount.
    src=src.replace("sf.write(out/'narration.wav',np.concatenate(all_audio),24000)","joined=np.concatenate(all_audio);joined=np.concatenate([joined[32400:],np.zeros(32400)]);sf.write(out/'narration.wav',joined,24000)")
    exec(src,stock.__dict__)
    src=inspect.getsource(render.frame).replace("key.upper(),21,FG,True","('ITEM 1' if key=='positive' else 'ITEM 2'),21,FG,True")
    src=src.replace("panel(im,(110,964,800,131),[(f'Above {money(A[\"resistance\"][-1])}: hold + stronger volume?',27,GREEN,True),(f'Below {money(A[\"support\"])}: support fails?',27,RED,True)],1 if u>.5 else 0)","text(im,(95,1455),f'Above {money(A[\"resistance\"][-1])}: hold + volume?',22,GREEN,True)\n        if u>.5:text(im,(580,1455),f'Below {money(A[\"support\"])}: case weakens',22,RED,True)")
    exec(src,render.__dict__);original=render.frame
    def frame(i,t):
        moment=render.S[i]['start']+t+1.35
        for j,s in enumerate(render.S):
            if s['start']<=moment<s['end']:i=j;t=moment-s['start'];break
        else:i=len(render.S)-1;t=render.S[i]['duration']-.01
        im=original(i,t);s=render.S[i]
        render.box(im,(47,1498,1033,1738),'#191f28',s['color'],r=20,width=2)
        size=30
        while render.font(size,True).getlength(s['title'])>925:size-=1
        render.center(im,1518,s['title'],size,render.GOLD)
        words=s['voice'].split();parts=[' '.join(words[k:k+11]) for k in range(0,len(words),11)]
        msg=parts[min(len(parts)-1,int(max(0,min(.999,(t-.15)/max(.1,s['duration']-.5)))*len(parts)))];lines=[];line=''
        for word in msg.split():
            cand=(line+' '+word).strip()
            if line and render.font(32).getlength(cand)>900:lines.append(line);line=word
            else:line=cand
        if line:lines.append(line)
        for j,line in enumerate(lines):render.center(im,1576+j*43,line,32,render.FG)
        return im
    render.frame=frame
    src=inspect.getsource(render.cover).replace('▲','+').replace('▼','-')
    exec(src,render.__dict__)

def package(ticker,out):
    final=out/f'{ticker}_analysis_2026-10-15.mp4';v=json.loads((out/'validation.json').read_text());duration=float(v['video_duration'])
    rate=max(1,duration/177.2)
    if rate>1:
        temp=out/'retimed.mp4'
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(final),'-vf',f'setpts=PTS/{rate}','-af',f'atempo={rate}','-r','30','-c:v','libx264','-preset','fast','-crf','19','-threads','2','-c:a','aac','-b:a','192k','-movflags','+faststart',str(temp)],check=True)
        temp.replace(final)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(final)]))['streams'];vs=next(x for x in probe if x['codec_type']=='video');aud=next(x for x in probe if x['codec_type']=='audio')
    assert 120<=float(vs['duration'])<=180 and abs(float(vs['duration'])-float(aud['duration']))<.1
    subprocess.run(['ffmpeg','-v','error','-i',str(final),'-f','null','-'],check=True)
    v.update(video_duration=vs['duration'],audio_duration=aud['duration'],playback_rate=rate,sha256=hashlib.sha256(final.read_bytes()).hexdigest());(out/'validation.json').write_text(json.dumps(v,indent=2))
    rows=json.loads((out/'timing.json').read_text());subs=[]
    def stamp(t):
        ms=round(max(0,t/rate)*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    for row in rows:
        words=row['voice'].split();parts=[' '.join(words[k:k+11]) for k in range(0,len(words),11)]
        for j,part in enumerate(parts):
            start=row['start']-1.35+.15+j*(row['duration']-.5)/len(parts);end=start+(row['duration']-.5)/len(parts)
            subs.append(f'{len(subs)+1}\n{stamp(start)} --> {stamp(end)}\n{part}\n')
    (out/'Captions.srt').write_text('\n'.join(subs));(out/'Narration_script.txt').write_text('\n\n'.join(r['voice'] for r in rows))
    names=[final.name,ticker+'_cover.png','Captions.srt','Narration_script.txt','TikTok_caption.txt','YouTube_title_and_description.txt','YouTube_upload_settings.txt','Sources_and_methods.md','analysis.json','daily.csv','news_review.json','market_raw.json','validation.json']
    with zipfile.ZipFile(out/(ticker+'_Video_and_Publishing_Kit.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for name in names:z.write(out/name,arcname=name)

if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('--ticker',choices=['NKE','USO'],required=True);cli.add_argument('--out',required=True);cli.add_argument('--data-only',action='store_true');cli.add_argument('--date',default='2026-10-15');args=cli.parse_args()
    configure();out=Path(args.out).resolve()
    sys.argv=['close_pair.py','--ticker',args.ticker,'--date',args.date,'--out',str(out),'--attempts','5']+(['--data-only'] if args.data_only else [])
    stock.main()
    if not args.data_only:package(args.ticker,out)
