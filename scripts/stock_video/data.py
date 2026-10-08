"""Fetch only completed, dated market bars and derive reproducible indicators."""
import datetime as dt
import json, time, urllib.request, urllib.parse, statistics
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

NY=ZoneInfo('America/New_York')
def request_json(url):
    request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
    with urllib.request.urlopen(request,timeout=40) as response:return json.load(response)

def wilder(values,n=14,begin=0):
    out=np.full(len(values),np.nan);seed=begin+n-1
    out[seed]=np.mean(values[begin:seed+1])
    for i in range(seed+1,len(values)):out[i]=(out[i-1]*(n-1)+values[i])/n
    return out

def load(ticker,expected,out,attempts=1):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    errors=[]
    for attempt in range(attempts):
        for host in ['query1.finance.yahoo.com','query2.finance.yahoo.com']:
            url=f'https://{host}/v8/finance/chart/{urllib.parse.quote(ticker)}?range=2y&interval=1d'
            try:
                raw=request_json(url);result=raw['chart']['result'][0]
                rows=pd.DataFrame(result['indicators']['quote'][0])
                rows['date']=[dt.datetime.fromtimestamp(x,NY).date().isoformat() for x in result['timestamp']]
                now=dt.datetime.now(NY)
                cutoff=now.date().isoformat()
                if now.hour<16:rows=rows[rows.date<cutoff]
                else:rows=rows[rows.date<=cutoff]
                if expected:rows=rows[rows.date<=expected]
                rows=rows.reset_index(drop=True)
                if len(rows)<220:raise ValueError('Fewer than 220 daily bars')
                if expected and rows.date.iloc[-1]!=expected:raise ValueError(f'Close for {expected} is not available; latest is {rows.date.iloc[-1]}')
                assert rows.date.is_unique and rows.date.is_monotonic_increasing
                assert not rows[['open','high','low','close','volume']].isna().any().any()
                assert (rows.volume>0).all()
                assert (rows.high>=rows[['open','low','close']].max(axis=1)).all()
                assert (rows.low<=rows[['open','high','close']].min(axis=1)).all()
                (out/'market_raw.json').write_text(json.dumps(raw))
                return derive(rows,result['meta'],url,out)
            except Exception as exc:
                errors.append(f'{host}: {type(exc).__name__}: {exc}')
                print(errors[-1],flush=True)
        if attempt+1<attempts:time.sleep(45)
    raise RuntimeError('No usable completed-session data. Refusing to render a stale/fabricated close. '+errors[-1])

def derive(d,meta,url,out):
    for n in [20,50,150,200]:d[f'ma{n}']=d.close.rolling(n).mean()
    changes=d.close.diff().to_numpy();g=wilder(np.maximum(changes,0),begin=1);l=wilder(np.maximum(-changes,0),begin=1)
    with np.errstate(divide='ignore',invalid='ignore'):d['rsi']=100-100/(1+g/l)
    d.loc[(g==0)&(l==0),'rsi']=50
    tr=pd.concat([d.high-d.low,(d.high-d.close.shift()).abs(),(d.low-d.close.shift()).abs()],axis=1).max(axis=1)
    d['atr']=wilder(tr.to_numpy())
    tp=(d.high+d.low+d.close)/3
    mad=tp.rolling(14).apply(lambda a:np.abs(a-a.mean()).mean(),raw=True)
    d['cci']=(tp-tp.rolling(14).mean())/(.015*mad)
    d['cci_avg']=d.cci.rolling(7).mean();d['vol20']=d.volume.rolling(20).mean()
    last=d.iloc[-1];prev=d.iloc[-2];n=len(d)
    lows=[i for i in range(n-90,n-3) if d.low.iloc[i]==d.low.iloc[i-3:i+4].min()]
    highs=[i for i in range(n-90,n-3) if d.high.iloc[i]==d.high.iloc[i-3:i+4].max()]
    anchor=int(d.tail(60).low.idxmin())
    candidate_hi=sorted({round(float(x),2) for x in d.high.tail(60) if x>last.close+.005})
    resist=[]
    for price in candidate_hi:
        if not resist or price-resist[-1]>=max(.02,last.atr*.2):resist.append(price)
        if len(resist)==2:break
    if not resist:resist=[float(last.high)]
    candidate_lo=sorted({round(float(d.low.iloc[i]),2) for i in lows if d.low.iloc[i]<last.close} | {round(float(d.low.tail(5).min()),2)},reverse=True)
    support=candidate_lo[0]
    trend=None
    for b in reversed(lows):
        for a in reversed([i for i in lows if i<b-5]):
            slope=(d.low.iloc[b]-d.low.iloc[a])/(b-a)
            if slope>0 and all(d.low.iloc[i]+1e-4>=d.low.iloc[a]+slope*(i-a) for i in range(a,n)):
                trend={'a':a,'b':b,'ya':float(d.low.iloc[a]),'yb':float(d.low.iloc[b]),'rising':True};break
        if trend:break
    if trend is None:
        a=lows[-1] if lows else int(d.tail(30).low.idxmin())
        trend={'a':a,'b':n-1,'ya':float(d.low.iloc[a]),'yb':float(d.low.iloc[a]),'rising':False}
    gap=None
    for i in range(n-1,max(n-21,1),-1):
        if d.low.iloc[i]>d.high.iloc[i-1] and d.low.iloc[i:].min()>d.high.iloc[i-1]:
            gap={'low':float(d.high.iloc[i-1]),'high':float(d.low.iloc[i:].min()),'index':i,'direction':'up'};break
        if d.high.iloc[i]<d.low.iloc[i-1] and d.high.iloc[i:].max()<d.low.iloc[i-1]:
            gap={'low':float(d.high.iloc[i:].max()),'high':float(d.low.iloc[i-1]),'index':i,'direction':'down'};break
    anatomy={'body':abs(float(last.close-last.open)),'range':float(last.high-last.low),'upper_wick':float(last.high-max(last.open,last.close)),'lower_wick':float(min(last.open,last.close)-last.low)}
    anatomy['body_pct']=anatomy['body']/anatomy['range']*100 if anatomy['range'] else 0
    anatomy['close_position']=(last.close-last.low)/anatomy['range']*100 if anatomy['range'] else 50
    above=sum(last.close>last[f'ma{x}'] for x in [20,50,150,200])
    a={'ticker':meta['symbol'],'company':'Palantir Technologies' if meta['symbol']=='PLTR' else meta.get('shortName',meta['symbol']),
       'exchange':meta.get('fullExchangeName','NASDAQ'),'date':last.date,'analysis_date':dt.datetime.now(ZoneInfo('Asia/Jerusalem')).date().isoformat(),
       'last':{k:float(last[k]) for k in ['open','high','low','close','volume','ma20','ma50','ma150','ma200','rsi','atr','cci','vol20']},
       'change':float(last.close-prev.close),'change_pct':float((last.close/prev.close-1)*100),'above_count':int(above),
       'volume_ratio':float(last.volume/last.vol20),'anchor':anchor,'anchor_price':float(d.low.iloc[anchor]),'anchor_date':d.date.iloc[anchor],
       'advance_pct':float((last.close/d.low.iloc[anchor]-1)*100),'advance_dollars':float(last.close-d.low.iloc[anchor]),
       'resistance':resist,'support':support,'trend':trend,'gap':gap,'anatomy':anatomy,'price_source':url,
       'retrieved_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'news':news(meta['symbol'],out)}
    # Independent final-window checks guard the numbers that appear in the film.
    for period in [20,50,150,200]:assert abs(a['last'][f'ma{period}']-statistics.mean(d.close.tail(period)))<1e-7
    samples=[(h+l+c)/3 for h,l,c in zip(d.high.tail(14),d.low.tail(14),d.close.tail(14))];m=statistics.mean(samples);dev=statistics.mean(abs(x-m) for x in samples)
    if dev:assert abs(last.cci-(samples[-1]-m)/(.015*dev))<1e-7
    assert all(np.isfinite(a['last'][x]) for x in a['last'])
    d.to_csv(out/'daily.csv',index=False);(out/'analysis.json').write_text(json.dumps(a,indent=2))
    return a

def news(ticker,out):
    result={'positive':None,'risk':None,'limitation':'Reported headlines only; full articles not verified. Earnings date unverified.'}
    try:
        source='https://query1.finance.yahoo.com/v1/finance/search?'+urllib.parse.urlencode({'q':ticker,'newsCount':100})
        raw=request_json(source);(Path(out)/'news_raw.json').write_text(json.dumps(raw));now=time.time()
        for item in raw.get('news',[]):
            title=item.get('title','');low=title.lower();stamp=item.get('providerPublishTime',0)
            if not (0<=now-stamp<=14*86400):continue
            if ticker.lower() not in low and 'palantir' not in low:continue
            if any(word in low for word in ['should you','to buy','prediction','price target','could','might']):continue
            kind='risk' if any(w in low for w in ['lawsuit','probe','investigation','concern','scrutiny','falls','drops','risk','weakens']) else 'positive' if any(w in low for w in ['contract','deal','partnership','expands','revenue rises','growth','award']) else None
            if kind and not result[kind]:result[kind]={'headline':title,'publisher':item.get('publisher','Source'),'url':item['link'],'published':dt.datetime.fromtimestamp(stamp,dt.timezone.utc).isoformat()}
        result['source']=source
    except Exception as exc:result['fetch_error']=f'{type(exc).__name__}: {exc}'
    return result
