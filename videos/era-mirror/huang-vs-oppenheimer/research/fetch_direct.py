"""Download Commons files by title through thumb.php (the upload host throttles this network). Usage: fetch_direct.py list.tsv"""
import urllib.request, urllib.parse, time, os, sys
UA={'User-Agent':'EraMirrorResearch/1.0 (documentary archive fetch)'}
have={os.path.splitext(f)[0] for f in os.listdir('assets/images')}
for line in open(sys.argv[1],encoding='utf-8'):
    if not line.strip() or line.startswith('#'): continue
    slug,title=line.rstrip('\n').split('\t')
    if slug in have: continue
    fn=urllib.parse.quote(title.split(':',1)[1].replace(' ','_'))
    ext='.png' if title.lower().endswith('.png') else '.jpg'
    last=''
    for w in (1600,1200,1000,800,600,400):
        try:
            data=urllib.request.urlopen(urllib.request.Request(f'https://commons.wikimedia.org/w/thumb.php?f={fn}&w={w}',headers=UA),timeout=60).read()
            if len(data)<3000: raise ValueError('tiny')
            open(f'assets/images/{slug}{ext}','wb').write(data); print('OK',slug,w,len(data)//1024,flush=True); break
        except Exception as e:
            last=str(e)
            if '429' in last: time.sleep(20)
    else: print('FAIL',slug,last,flush=True)
    time.sleep(2.5)
