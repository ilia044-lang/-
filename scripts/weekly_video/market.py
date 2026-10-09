"""Dated, auditable inputs for the October 5–9 weekly edition."""
import concurrent.futures, datetime as dt, json, math, re, statistics, time
import urllib.request, urllib.parse, xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

NY=ZoneInfo('America/New_York')
SYMBOLS={'SPY':'S&P 500 ETF','QQQ':'Nasdaq 100 ETF','^DJI':'Dow Jones','^VIX':'VIX','^TNX':'US 10-year yield','^TYX':'US 30-year yield','CL=F':'WTI oil futures','DX-Y.NYB':'US dollar index','BTC-USD':'Bitcoin / USD','MSTR':'Strategy','IREN':'IREN','AVGO':'Broadcom','CIFR':'Cipher Digital'}
START='2026-10-05'; END='2026-10-09'; NEXT_START='2026-10-12'; NEXT_END='2026-10-16'

def fetch(url, timeout=35):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json,text/html,text/calendar,*/*','Accept-Language':'en-US,en;q=0.9'})
    with urllib.request.urlopen(req,timeout=timeout) as r:return r.read()

def get_json(url):return json.loads(fetch(url))

def chart(symbol, date, root, history='2y', interval='1d'):
    failures=[]
    for host in ['query1.finance.yahoo.com','query2.finance.yahoo.com']:
        url=f'https://{host}/v8/finance/chart/{urllib.parse.quote(symbol)}?range={history}&interval={interval}'
        try:
            raw=get_json(url);r=raw['chart']['result'][0]
            q=pd.DataFrame(r['indicators']['quote'][0]);zone=dt.timezone.utc if symbol=='BTC-USD' else NY
            q['date']=[dt.datetime.fromtimestamp(t,zone).date().isoformat() for t in r['timestamp']]
            if 'adjclose' in r['indicators']:q['adjclose']=r['indicators']['adjclose'][0]['adjclose']
            q=q.dropna(subset=['open','high','low','close']).reset_index(drop=True)
            q=q[q.date<=date].copy()
            assert q.date.is_unique and q.date.is_monotonic_increasing
            assert len(q)>200 if interval=='1d' else len(q)>180
            assert (q.high+1e-5>=q[['open','close','low']].max(axis=1)).all()
            assert (q.low-1e-5<=q[['open','close','high']].min(axis=1)).all()
            if interval=='1d':assert q.date.iloc[-1]==date, f'{symbol}: requested {date}, got {q.date.iloc[-1]}'
            stem=symbol.replace('^','').replace('=','_')+'_'+interval
            (root/(stem+'.json')).write_text(json.dumps(raw));q.to_csv(root/(stem+'.csv'),index=False)
            return q,url,r['meta']
        except Exception as exc:failures.append(str(exc))
    raise RuntimeError(f'{symbol}: no valid dated data: {failures}')

def describe(symbol,date,root):
    q,url,meta=chart(symbol,date,root);c=q.close
    for n in (20,50,150,200):q[f'ma{n}']=c.rolling(n).mean()
    change=c.diff();up=change.clip(lower=0);down=-change.clip(upper=0)
    def wilder(s):
        a=np.full(len(s),np.nan);a[14]=s.iloc[1:15].mean()
        for i in range(15,len(s)):a[i]=(a[i-1]*13+s.iloc[i])/14
        return a
    g,l=wilder(up),wilder(down)
    with np.errstate(divide='ignore',invalid='ignore'):q['rsi']=np.where(l==0,100,100-100/(1+g/l))
    q.loc[(g==0)&(l==0),'rsi']=50
    tr=pd.concat([q.high-q.low,(q.high-c.shift()).abs(),(q.low-c.shift()).abs()],axis=1).max(axis=1)
    q['atr']=wilder(tr);tp=(q.high+q.low+c)/3;avg=tp.rolling(14).mean();mad=tp.rolling(14).apply(lambda a:np.abs(a-a.mean()).mean(),raw=True);q['cci']=(tp-avg)/(.015*mad)
    last=q.iloc[-1];before=q[q.date<START].iloc[-1];week=q[q.date>=START]
    assert len(week)>0
    highs=[float(q.high.iloc[i]) for i in range(len(q)-65,len(q)-3) if q.high.iloc[i]>=q.high.iloc[i-3:i+4].max() and q.high.iloc[i]>last.close]
    lows=[float(q.low.iloc[i]) for i in range(len(q)-65,len(q)-3) if q.low.iloc[i]<=q.low.iloc[i-3:i+4].min() and q.low.iloc[i]<last.close]
    resistance=min(highs) if highs else float(q.high.tail(20).max());support=max(lows) if lows else float(q.low.tail(20).min())
    assert support<=last.close+1e-6 and resistance>=last.close-1e-6
    vol=float(last.volume/q.volume.tail(20).mean()) if q.volume.tail(20).mean()>0 else None
    record={'symbol':symbol,'name':SYMBOLS[symbol],'date':date,'close':float(last.close),'weekly_pct':float((last.close/before.close-1)*100),'prior_friday':before.date,'week_high':float(week.high.max()),'week_low':float(week.low.min()),'support':support,'resistance':resistance,'rsi':float(last.rsi),'atr':float(last.atr),'cci':float(last.cci),'relative_volume':vol,'source':url,'ma':{str(n):float(last[f'ma{n}']) for n in (20,50,150,200)},'ohlc':{x:float(last[x]) for x in ['open','high','low','close']},'history':q.tail(65).replace({np.nan:None}).to_dict(orient='records')}
    for n in (20,50,150,200):assert abs(record['ma'][str(n)]-statistics.mean(c.tail(n)))<1e-7
    assert all(math.isfinite(record[x]) for x in ['close','weekly_pct','support','resistance','rsi','atr','cci'])
    return record

def seasonality(symbol,root):
    q,url,_=chart(symbol,END,root,'20y','1mo')
    assert 'adjclose' in q,'Adjusted close required for monthly total-return proxy'
    q['month']=q.date.str[:7];values=[]
    for year in range(2011,2026):
        sep=q[q.month==f'{year}-09'];october=q[q.month==f'{year}-10']
        assert len(sep)==len(october)==1,f'Missing monthly data for {year}'
        a=float(sep.adjclose.iloc[0]);b=float(october.adjclose.iloc[0]);assert a>0 and b>0
        values.append({'year':year,'return_pct':(b/a-1)*100})
    returns=[x['return_pct'] for x in values]
    return {'symbol':symbol,'years':values,'positive':sum(v>0 for v in returns),'negative':sum(v<0 for v in returns),'flat':sum(v==0 for v in returns),'mean':statistics.mean(returns),'median':statistics.median(returns),'best':max(returns),'worst':min(returns),'source':url,'basis':'Yahoo adjusted monthly close, September month-end to October month-end; 2011–2025; 2026 excluded'}

def news(root,date):
    now=dt.datetime.now(dt.timezone.utc);begin=dt.datetime.fromisoformat(START).replace(tzinfo=NY).timestamp()
    items={};errors=[]
    for term in ['SPY','QQQ','MSTR','IREN','AVGO','CIFR']:
        url='https://query1.finance.yahoo.com/v1/finance/search?'+urllib.parse.urlencode({'q':term,'newsCount':20})
        try:
            raw=get_json(url);(root/('news_'+term+'.json')).write_text(json.dumps(raw))
            for n in raw.get('news',[]):
                stamp=n.get('providerPublishTime',0);title=n.get('title','');publisher=n.get('publisher','')
                if not begin<=stamp<=now.timestamp() or not n.get('link') or not publisher:continue
                if any(x in title.lower() for x in ['should you','stocks to buy','could make','price target','prediction','millionaire','best stock','motley fool']):continue
                if publisher.lower() in ['motley fool','24/7 wall st.','simply wall st.']:continue
                items[n['link']]={'title':title,'publisher':publisher,'url':n['link'],'published':dt.datetime.fromtimestamp(stamp,dt.timezone.utc).isoformat(),'symbol':term,'verification':'Sourced headline metadata; not independent verification of the full article'}
        except Exception as e:errors.append(str(e))
    result=sorted(items.values(),key=lambda x:x['published'],reverse=True)[:8]
    return result,errors

def calendar(root):
    events=[];errors=[]
    url='https://www.bls.gov/schedule/news_release/bls.ics'
    try:
        raw=fetch(url).decode();(root/'bls.ics').write_text(raw)
        raw=re.sub(r'\r?\n[ \t]','',raw)
        for e in raw.split('BEGIN:VEVENT')[1:]:
            day=re.search(r'DTSTART[^:]*:(\d{8})',e);summary=re.search(r'^SUMMARY:(.+)',e,re.M)
            if day and summary:
                date=dt.datetime.strptime(day[1],'%Y%m%d').date().isoformat()
                if NEXT_START<=date<=NEXT_END:events.append({'date':date,'event':summary[1].strip().replace('\\,',','),'source':url,'status':'BLS calendar'})
    except Exception as e:errors.append('BLS calendar: '+str(e))
    earnings=[]
    for n in range(5):
        date=(dt.date.fromisoformat(NEXT_START)+dt.timedelta(days=n)).isoformat();url='https://api.nasdaq.com/api/calendar/earnings?date='+date
        try:
            raw=get_json(url);(root/('earnings_'+date+'.json')).write_text(json.dumps(raw));rows=(raw.get('data') or {}).get('rows') or []
            for r in rows:
                if r.get('symbol') and r.get('name'):earnings.append({'date':date,'symbol':r['symbol'],'name':r['name'],'time':r.get('time'),'market_cap':r.get('marketCap',''),'source':url,'status':'est. — Nasdaq calendar; issuer confirmation not independently checked'})
        except Exception as e:errors.append('Earnings '+date+': '+str(e))
    def cap(x):
        try:return float(re.sub(r'[^0-9.]','',str(x['market_cap'])))
        except ValueError:return 0
    earnings=sorted(earnings,key=cap,reverse=True)[:8];earnings.sort(key=lambda x:(x['date'],x['symbol']))
    return {'macro':events,'earnings':earnings,'errors':errors}

def collect(out,date,attempts=1):
    root=out/'sources';root.mkdir(parents=True,exist_ok=True)
    assert START<=date<=END
    now=dt.datetime.now(NY)
    if date==now.date().isoformat() and now.hour<16:raise RuntimeError('Requested US equity session is not closed yet')
    for attempt in range(attempts):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(lambda s:describe(s,date,root),SYMBOLS))
            break
        except Exception:
            if attempt+1==attempts:raise
            time.sleep(45)
    seasons=[seasonality(s,root) for s in ['SPY','QQQ']];headlines,errors=news(root,date);upcoming=calendar(root)
    supplemental={};extra_errors=[]
    treasury_url='https://home.treasury.gov/resource-center-data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value=2026'
    try:
        raw=fetch(treasury_url);(root/'treasury.xml').write_bytes(raw);tree=ET.fromstring(raw);observations=[]
        for props in tree.iter():
            if props.tag.endswith('}properties'):
                row={x.tag.split('}')[-1]:x.text for x in props};d=(row.get('NEW_DATE') or '')[:10]
                if d and d<=date and row.get('BC_20YEAR'):observations.append({'date':d,'10y':float(row['BC_10YEAR']),'20y':float(row['BC_20YEAR']),'30y':float(row['BC_30YEAR'])})
        assert observations
        observations.sort(key=lambda x:x['date']);supplemental['treasury']={'latest':observations[-1],'previous':next((x for x in reversed(observations) if x['date']<START),None),'source':treasury_url}
    except Exception as e:extra_errors.append('Treasury official daily yields: '+str(e))
    try:
        url='https://scanner.tradingview.com/america/scan';body=json.dumps({'symbols':{'tickers':['INDEX:S5FI'],'query':{'types':[]}},'columns':['close','change','description']}).encode()
        req=urllib.request.Request(url,data=body,headers={'User-Agent':'Mozilla/5.0','Content-Type':'application/json'})
        raw=json.load(urllib.request.urlopen(req,timeout=25));(root/'breadth.json').write_text(json.dumps(raw));row=raw['data'][0];v=float(row['d'][0]);assert 0<=v<=100
        supplemental['breadth']={'value':v,'source':url,'symbol':row['s'],'retrieved_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'basis':'Snapshot, not independently certified daily close'}
    except Exception as e:extra_errors.append('S5FI breadth: '+str(e))
    result={'date':date,'week_start':START,'week_end':END,'next_start':NEXT_START,'next_end':NEXT_END,'preview':date!=END,'retrieved_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'markets':{x['symbol']:x for x in records},'seasonality':seasons,'news':headlines,'news_errors':errors,'calendar':upcoming,'supplemental':supplemental,'extra_errors':extra_errors}
    (out/'analysis.json').write_text(json.dumps(result,indent=2));return result
