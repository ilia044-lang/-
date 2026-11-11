import json, sys, urllib.request, urllib.parse
UA={'User-Agent':'research-script/1.0 (media license lookup)'}
def api(params):
    url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)
    import time
    for i in range(6):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30))
        except Exception as e:
            time.sleep(15*(i+1))
    return {}
import time
for q in sys.argv[1:]:
    time.sleep(4)
    r=api({'action':'query','format':'json','generator':'search','gsrsearch':q+' filetype:bitmap|video','gsrnamespace':6,'gsrlimit':8,'prop':'imageinfo','iiprop':'url|size|extmetadata|mime','iiextmetadatafilter':'LicenseShortName|Artist|DateTimeOriginal|Credit'})
    print('\n###',q)
    for p in sorted(r.get('query',{}).get('pages',{}).values(), key=lambda p:p.get('index',0)):
        ii=p['imageinfo'][0]; m=ii.get('extmetadata',{})
        import re
        clean=lambda s: re.sub('<[^>]+>','',s or '')[:60].replace('\n',' ')
        print(f"{p['title']} | {ii['width']}x{ii['height']} {ii['mime']} | {clean(m.get('LicenseShortName',{}).get('value'))} | {clean(m.get('Artist',{}).get('value'))} | {clean(m.get('DateTimeOriginal',{}).get('value'))}")
