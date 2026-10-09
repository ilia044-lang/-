"""One-off public-source compatibility probe; not part of scheduled production."""
import concurrent.futures,json,subprocess,urllib.request
from pathlib import Path
URLS={
 'treasury_csv':'https://home.treasury.gov/resource-center-data-chart-center/interest-rates/daily-treasury-rates.csv/2026/all?type=daily_treasury_yield_curve&field_tdr_date_value=2026&page&_format=csv',
 'fred20':'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS20',
 'fred20txt':'https://fred.stlouisfed.org/data/DGS20.txt',
 'fed_h15':'https://www.federalreserve.gov/releases/h15/',
 'bls_month':'https://www.bls.gov/schedule/2026/10_sched.htm',
 'bls_list':'https://www.bls.gov/schedule/2026/10_sched_list.htm',
 'fed_calendar':'https://www.federalreserve.gov/newsevents/2026-october.htm',
 'yahoo_economic':'https://finance.yahoo.com/calendar/economic?from=2026-10-12&to=2026-10-16&day=2026-10-12',
 'tv_search':'https://symbol-search.tradingview.com/symbol_search/v3/?text=S5FI&hl=0&exchange=&lang=en&search_type=undefined&domain=production',
}
def probe(item):
 name,url=item
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'text/html,application/json,*/*'}),timeout=30) as r:body=r.read(1500000).decode(errors='replace');status=r.status
  return name,{'url':url,'status':status,'body':body}
 except Exception as e:return name,{'url':url,'error':str(e)}
def main():
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:result=dict(pool.map(probe,URLS.items()))
 print(json.dumps({k:{z:v for z,v in x.items() if z!='body'} for k,x in result.items()},indent=2))
 repo=Path('probe-publish');branch='diagnostics/weekly-source-probe'
 def git(*args):subprocess.run(['git','-C',str(repo),*args],check=True)
 refs=subprocess.check_output(['git','-C',str(repo),'ls-remote','--heads','origin','refs/heads/'+branch],text=True)
 if refs:git('fetch','origin',branch);git('switch','-C',branch,'FETCH_HEAD')
 else:git('switch','--orphan',branch)
 (repo/'public-source-probe.json').write_text(json.dumps(result,indent=2));git('config','user.name','Market Mind cloud video');git('config','user.email','41898282+github-actions[bot]@users.noreply.github.com');git('add','public-source-probe.json')
 if subprocess.run(['git','-C',str(repo),'diff','--cached','--quiet']).returncode:git('commit','-m','Inspect public economic-calendar and yield sources')
 git('push','origin','HEAD:refs/heads/'+branch)
if __name__=='__main__':main()
