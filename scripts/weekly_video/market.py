"""Dated, auditable inputs for the October 5–9 weekly edition."""
import concurrent.futures, datetime as dt, json, math, re, statistics, time, io, html
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

def clean_html(text):return ' '.join(html.unescape(re.sub('<[^>]*>',' ',text)).split())

def fed_yields(root,date):
    url='https://www.federalreserve.gov/releases/h15/';raw=fetch(url).decode();(root/'fed-h15.html').write_text(raw)
    dates={int(k):dt.datetime.strptime(clean_html(v),'%Y %b %d').date().isoformat() for k,v in re.findall(r'<th id="col(\d+)"[^>]*>(.*?)</th>',raw,re.S)}
    yields={}
    for year in [10,20,30]:
        row=re.search(r'<th[^>]*class="stub in4">'+str(year)+r'-year</th>(.*?)</tr>',raw,re.S);assert row
        yields[year]={int(k):float(clean_html(v)) for k,v in re.findall(r'<td[^>]*headers="[^"]*col(\d+)"[^>]*>(.*?)</td>',row[1],re.S) if re.fullmatch(r'\d+(?:\.\d+)?',clean_html(v))}
    valid=[k for k,d in dates.items() if d<=date and all(k in yields[y] for y in yields)];assert valid
    k=max(valid,key=lambda k:dates[k]);assert (dt.date.fromisoformat(date)-dt.date.fromisoformat(dates[k])).days<=4
    return {'latest':{'date':dates[k],**{str(y)+'y':yields[y][k] for y in yields}},'previous':None,'source':url}

def yahoo_macro(root):
    def day(n):
        date=(dt.date.fromisoformat(NEXT_START)+dt.timedelta(days=n)).isoformat();url=f'https://finance.yahoo.com/calendar/economic?from={NEXT_START}&to={NEXT_END}&day={date}&offset=0&size=100'
        raw=fetch(url).decode();(root/('economic-yahoo-'+date+'.html')).write_text(raw);events=[]
        for row in re.findall(r'<tr[^>]*>(.*?)</tr>',raw,re.S):
            cells={k:clean_html(v) for k,v in re.findall(r'<td[^>]*data-testid-cell="([^"]+)"[^>]*>(.*?)</td>',row,re.S)}
            if cells.get('country_code')=='US' and cells.get('econ_release'):
                name=cells['econ_release'];family=next((x for x in ['CPI','PPI','Retail Sales','Jobless','Industrial','Consumer Sentiment'] if x.lower() in name.lower()),None)
                if family:events.append({'date':date,'event':name,'family':family,'time':cells.get('startdatetime'),'source':url,'status':'Yahoo economic calendar; schedule subject to change'})
        return events
    events=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for rows in pool.map(day,range(5)):events.extend(rows)
    unique={}
    for e in events:unique.setdefault((e['date'],e['family']),e)
    return sorted(unique.values(),key=lambda e:e['date'])

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
                if any(x in title.lower() for x in ['should you','to buy','could make','price target','prediction','millionaire','best stock','motley fool','eyes entry','bc-most active','worth investing','undervalued','overvalued']):continue
                if publisher.lower() in ['motley fool','24/7 wall st.','simply wall st.']:continue
                resolutions=(n.get('thumbnail') or {}).get('resolutions',[])
                image_url=next((x.get('url') for x in resolutions if x.get('tag')=='original'),None)
                items[n['link']]={'title':title,'publisher':publisher,'url':n['link'],'published':dt.datetime.fromtimestamp(stamp,dt.timezone.utc).isoformat(),'symbol':term,'image_url':image_url,'verification':'Sourced headline metadata; not independent verification of the full article'}
        except Exception as e:errors.append(str(e))
    preferred=['Reuters','Associated Press','Bloomberg','Yahoo Finance','MT Newswires','Barrons.com','CNBC','Investing.com']
    result=sorted(items.values(),key=lambda x:(x['publisher'] in preferred,x['published']),reverse=True)[:8]
    for i,n in enumerate(result[:2]):
        if n.get('image_url'):
            try:
                from PIL import Image
                u=urllib.parse.urlsplit(n['image_url']);assert u.scheme=='https' and any((u.hostname or '').endswith('.'+host) or u.hostname==host for host in ['zenfs.com','yimg.com','yahoo.com'])
                content=fetch(n['image_url']);assert len(content)<12*1024*1024
                Image.open(io.BytesIO(content)).verify();name=f'news-image-{i}.jpg';(root/name).write_bytes(content);n['image_file']=name
            except Exception as e:n['image_error']=str(e)
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
    if not events:
        for n in range(5):
            date=(dt.date.fromisoformat(NEXT_START)+dt.timedelta(days=n)).isoformat();url='https://api.nasdaq.com/api/calendar/economic?date='+date
            try:
                raw=get_json(url);(root/('economic_'+date+'.json')).write_text(json.dumps(raw))
                data=raw.get('data') or {};rows=data.get('rows') or (data.get('table') or {}).get('rows') or []
                for r in rows:
                    country=str(r.get('country',r.get('countryName',''))).lower();event=r.get('event',r.get('eventName',''))
                    if event and country in ['united states','us','usa','united states of america']:
                        events.append({'date':date,'event':event,'source':url,'status':'Nasdaq economic calendar; schedule subject to change'})
            except Exception as e:errors.append('Economic calendar '+date+': '+str(e))
    if not events:
        try:events=yahoo_macro(root)
        except Exception as e:errors.append('Yahoo economic calendar: '+str(e))
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

def breadth_proxy(root,date):
    """Transparent fallback; explicitly NOT the licensed TradingView S5FI print."""
    url='https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv'
    raw=fetch(url).decode();(root/'sp500-constituents.csv').write_text(raw);members=pd.read_csv(io.StringIO(raw));symbols=[s.replace('.','-') for s in members['Symbol']]
    assert 450<=len(symbols)<=550 and len(set(symbols))==len(symbols)
    groups=[symbols[i:i+20] for i in range(0,len(symbols),20)]
    def group_fetch(pair):
        i,group=pair;u='https://query1.finance.yahoo.com/v7/finance/spark?'+urllib.parse.urlencode({'symbols':','.join(group),'range':'3mo','interval':'1d'})
        r=get_json(u);(root/f'breadth-group-{i:02}.json').write_text(json.dumps(r));result=[]
        for item in r.get('spark',{}).get('result',[]) or []:
            response=item['response'][0];values=[]
            for stamp,c in zip(response['timestamp'],response['indicators']['quote'][0]['close']):
                d=dt.datetime.fromtimestamp(stamp,NY).date().isoformat()
                if d<=date and c is not None:values.append((d,float(c)))
            if len(values)>=50 and values[-1][0]==date:
                ma=statistics.mean(c for _,c in values[-50:]);result.append({'symbol':item['symbol'],'date':date,'close':values[-1][1],'ma50':ma,'above':values[-1][1]>ma})
        return result
    all_rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for rows in pool.map(group_fetch,enumerate(groups)):all_rows.extend(rows)
    assert len({x['symbol'] for x in all_rows})==len(all_rows)
    coverage=len(all_rows)/len(symbols);assert coverage>=.98,f'Insufficient breadth coverage: {coverage:.1%}'
    (root/'breadth-components.json').write_text(json.dumps(all_rows,indent=2));above=sum(x['above'] for x in all_rows)
    return {'value':100*above/len(all_rows),'symbol':'S&P 500 breadth proxy','source':url,'market_source':'https://query1.finance.yahoo.com/v7/finance/spark','date':date,'retrieved_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'basis':'Independent current-constituent calculation, not the official S5FI print; close above simple 50-day average','coverage':coverage,'components':len(all_rows),'listed_components':len(symbols),'above':above,'proxy':True}

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
    if 'treasury' not in supplemental:
        try:supplemental['treasury']=fed_yields(root,date)
        except Exception as e:extra_errors.append('Federal Reserve H15: '+str(e))
    if 'treasury' not in supplemental:
        url='https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10,DGS20,DGS30&cosd=2026-09-25&coed='+date
        try:
            raw=fetch(url).decode();(root/'fred-yields.csv').write_text(raw);df=pd.read_csv(io.StringIO(raw),na_values='.').dropna();df=df[df.iloc[:,0]<=date];assert len(df)
            def record(row):return {'date':str(row.iloc[0]),'10y':float(row['DGS10']),'20y':float(row['DGS20']),'30y':float(row['DGS30'])}
            last=record(df.iloc[-1]);assert (dt.date.fromisoformat(date)-dt.date.fromisoformat(last['date'])).days<=4
            previous=df[df.iloc[:,0]<START];supplemental['treasury']={'latest':last,'previous':record(previous.iloc[-1]) if len(previous) else None,'source':url}
        except Exception as e:extra_errors.append('FRED official Treasury series: '+str(e))
    try:
        url='https://scanner.tradingview.com/america/scan';body=json.dumps({'symbols':{'tickers':['INDEX:S5FI'],'query':{'types':[]}},'columns':['close','change','description']}).encode()
        req=urllib.request.Request(url,data=body,headers={'User-Agent':'Mozilla/5.0','Content-Type':'application/json'})
        raw=json.load(urllib.request.urlopen(req,timeout=25));(root/'breadth.json').write_text(json.dumps(raw));row=raw['data'][0];v=float(row['d'][0]);assert 0<=v<=100
        supplemental['breadth']={'value':v,'source':url,'symbol':row['s'],'retrieved_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'basis':'Snapshot, not independently certified daily close'}
    except Exception as e:extra_errors.append('S5FI breadth: '+str(e))
    if 'breadth' not in supplemental:
        try:
            url='https://scanner.tradingview.com/global/scan';body=json.dumps({'symbols':{'tickers':['INDEX:S5FI'],'query':{'types':[]}},'columns':['close','change','description']}).encode()
            req=urllib.request.Request(url,data=body,headers={'User-Agent':'Mozilla/5.0','Content-Type':'application/json'})
            raw=json.load(urllib.request.urlopen(req,timeout=25));(root/'breadth-global.json').write_text(json.dumps(raw));row=raw['data'][0];v=float(row['d'][0]);assert 0<=v<=100
            supplemental['breadth']={'value':v,'source':url,'symbol':row['s'],'retrieved_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'basis':'Snapshot, not independently certified daily close'}
        except Exception as e:extra_errors.append('S5FI global snapshot: '+str(e))
    if 'breadth' not in supplemental:
        try:supplemental['breadth']=breadth_proxy(root,date)
        except Exception as e:extra_errors.append('Independent breadth calculation: '+str(e))
    result={'date':date,'week_start':START,'week_end':END,'next_start':NEXT_START,'next_end':NEXT_END,'preview':date!=END,'retrieved_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'markets':{x['symbol']:x for x in records},'seasonality':seasons,'news':headlines,'news_errors':errors,'calendar':upcoming,'supplemental':supplemental,'extra_errors':extra_errors}
    (out/'analysis.json').write_text(json.dumps(result,indent=2));return result
