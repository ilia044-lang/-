"""Download Commons files (max 2400px wide) with license metadata. Usage: commons_get.py list.tsv  (slug<TAB>File:Title)"""
import json, sys, time, re, urllib.request, urllib.parse, os
UA={'User-Agent':'EraMirrorResearch/1.0 (documentary archive fetch)'}
def get(url, binary=False):
    for i in range(7):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=60).read()
            return r if binary else json.loads(r)
        except Exception as e:
            time.sleep(10*(i+1))
    print('FAILED',url,flush=True); return None
clean=lambda s: re.sub(r'\s+',' ',re.sub('<[^>]+>','',s or '')).strip()
out='assets/images'; cred=[]
credp='assets/credits.json'
old=json.load(open(credp)) if os.path.exists(credp) else {}
for line in open(sys.argv[1],encoding='utf-8'):
    line=line.strip()
    if not line or line.startswith('#'): continue
    slug,title=line.split('\t')
    if slug in old and any(os.path.exists(f'{out}/{slug}{e}') for e in ('.jpg','.png','.gif','.webm','.ogv')): continue
    q={'action':'query','format':'json','titles':title,'prop':'imageinfo','iiprop':'url|size|extmetadata|mime','iiurlwidth':2400}
    r=get('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(q))
    if r is None: continue
    p=list(r['query']['pages'].values())[0]
    if 'imageinfo' not in p: print('MISSING',title); continue
    ii=p['imageinfo'][0]; m=ii['extmetadata']
    is_img=ii['mime'].startswith('image/')
    url=ii.get('thumburl') if is_img and ii['width']>2400 else ii['url']
    ext={'image/jpeg':'.jpg','image/png':'.png','image/gif':'.gif','image/tiff':'.jpg','video/webm':'.webm','application/ogg':'.ogv'}.get(ii['mime'],'.bin')
    if ii['mime']=='image/tiff': url=ii.get('thumburl',url)
    time.sleep(3)
    fn=urllib.parse.quote(title.split(':',1)[1].replace(' ','_'))
    w=min(ii['width'],2000)
    url=(f'https://commons.wikimedia.org/w/thumb.php?f={fn}&w={w}' if ii['mime'] in ('image/jpeg','image/png','image/tiff') else f'https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/{fn}')
    data=get(url,binary=True)
    if data is None: continue
    open(f'{out}/{slug}{ext}','wb').write(data)
    old[slug]={'file':slug+ext,'title':title,'license':clean(m.get('LicenseShortName',{}).get('value')),'artist':clean(m.get('Artist',{}).get('value'))[:120],'date':clean(m.get('DateTimeOriginal',{}).get('value'))[:40],'credit':clean(m.get('Credit',{}).get('value'))[:160],'source':ii['descriptionurl'],'size':f"{ii['width']}x{ii['height']}"}
    json.dump(old,open(credp,'w'),indent=1,ensure_ascii=False)
    print('OK',slug,old[slug]['license'],len(data)//1024,'KB',flush=True)
    time.sleep(3)
