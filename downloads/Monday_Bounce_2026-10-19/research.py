from pathlib import Path
import sys,json,concurrent.futures,datetime as dt
import pandas as pd
sys.path.insert(0,'/workspace/download-delivery/scripts/weekly_video');import market
P=Path(__file__).parent;S=P/'sources';market.END='2026-10-19';market.START='2026-10-12'
def get(s):
 df,url,meta=market.chart(s,market.END,S,'1y','1d');df=df[df.date<='2026-10-19'];df.to_csv(S/(s.replace('^','')+'.csv'),index=False)
 assert df.date.iloc[-1]=='2026-10-19',(s,df.date.iloc[-1]);last=df.iloc[-1];fri=df.iloc[-2];thu=df.iloc[-3]
 r={'symbol':s,'close':float(last.close),'open':float(last.open),'high':float(last.high),'low':float(last.low),'daily_pct':float((last.close/fri.close-1)*100),'friday_pct':float((fri.close/thu.close-1)*100),'recovery_of_friday_loss_pct':float((last.close-fri.close)/(thu.close-fri.close)*100) if thu.close>fri.close else None,'two_day_pct':float((last.close/thu.close-1)*100),'friday_close':float(fri.close),'friday_high':float(fri.high),'friday_low':float(fri.low),'thursday_close':float(thu.close),'ma20':float(df.close.tail(20).mean()),'ma50':float(df.close.tail(50).mean()),'ma200':float(df.close.tail(200).mean()),'volume':int(last.volume),'friday_volume':int(fri.volume),'volume_vs_prior20':float(last.volume/df.volume.iloc[-21:-1].mean()),'close_position':float((last.close-last.low)/(last.high-last.low)) if last.high>last.low else None,'source':url,'history':df.tail(65).to_dict('records')}
 return s,r
with concurrent.futures.ThreadPoolExecutor(4) as ex:res=dict(ex.map(get,['SPY','QQQ','IWM','RSP','^DJI','^VIX','HYG','TLT']))
(P/'analysis.json').write_text(json.dumps(res,indent=2,default=str))
for s,r in res.items():print(s,{k:round(v,3) if isinstance(v,float) else v for k,v in r.items() if k not in ['history','source']},flush=True)
