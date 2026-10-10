"""Snapshot bitcoin at execution time; technical analysis uses completed UTC days."""
import os,sys,json,datetime as dt
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'weekly_video'))
import market

def collect(out,now=None):
 now=now or dt.datetime.now(dt.timezone.utc)
 out=Path(out);sources=out/'sources';sources.mkdir(parents=True,exist_ok=True)
 url='https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?range=2y&interval=1d'
 raw=market.get_json(url);result=raw['chart']['result'][0];meta=result['meta']
 stamp=dt.datetime.fromtimestamp(meta['regularMarketTime'],dt.timezone.utc)
 assert -300<=(now-stamp).total_seconds()<=10800,f'Quote stale or future-dated: {stamp}'
 last_date=(now.date()-dt.timedelta(days=1)).isoformat()
 (sources/'bitcoin-raw.json').write_text(json.dumps(raw))
 original=market.get_json
 try:
  market.get_json=lambda _:raw
  r=market.describe('BTC-USD',last_date,sources)
 finally:market.get_json=original
 r['daily_pct']=(r['close']/r['history'][-2]['close']-1)*100
 r['weekly_pct']=r['daily_pct'] # Daily chart compatibility; labelled Day, never Week.
 r['close_position_pct']=(r['ohlc']['close']-r['ohlc']['low'])/(r['ohlc']['high']-r['ohlc']['low'])*100
 r['recent_low']=min(x['low'] for x in r['history'][-3:])
 a={'date':last_date,'publication_date':'2026-10-11','retrieved_utc':now.isoformat(),'snapshot':{'price':meta['regularMarketPrice'],'asof_utc':stamp.isoformat()},'markets':{'BTC-USD':r},'data_basis':'Completed UTC daily candle; current snapshot is separately timestamped.','ibit_source':'https://www.ishares.com/us/products/333011/ishares-bitcoin-trust-etf','ibit_source_status':'General product explanation, not a claim of current fees or holdings. Issuer page could not be fetched in the preparation environment.'}
 try:
  nurl='https://query1.finance.yahoo.com/v1/finance/search?q=bitcoin&newsCount=6&quotesCount=1'
  n=original(nurl);(sources/'news.json').write_text(json.dumps(n,indent=2))
  a['news']=[x for x in n.get('news',[]) if 0<=(now-dt.datetime.fromtimestamp(x['providerPublishTime'],dt.timezone.utc)).total_seconds()<14*86400]
 except Exception as e:a['news_error']=str(e)
 (out/'analysis.json').write_text(json.dumps(a,indent=2));print('DATA READY',last_date,stamp.isoformat())
 return a
if __name__=='__main__':collect(os.environ.get('BITCOIN_OUTPUT','/tmp/bitcoin-daily-2026-10-11'))
