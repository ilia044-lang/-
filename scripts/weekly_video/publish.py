"""Publish verified downloadable outputs to a dedicated delivery branch."""
import argparse,json,shutil,subprocess
from pathlib import Path
def git(repo,*args):return subprocess.run(['git','-C',str(repo),*args],check=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--repo',required=True);p.add_argument('--preview',action='store_true');a=p.parse_args();out=Path(a.out);repo=Path(a.repo)
    v=json.loads((out/'validation.json').read_text());assert v['passed'] and len(v['outputs'])==3
    if not a.preview:assert v['date']=='2026-10-09' and not v['smoke'] and not v['preview']
    branch=('previews' if a.preview else 'deliveries')+'/WEEKLY-2026-10-09'
    remote=subprocess.check_output(['git','-C',str(repo),'ls-remote','--heads','origin','refs/heads/'+branch],text=True)
    if remote:git(repo,'fetch','origin',branch);git(repo,'switch','-C',branch,'FETCH_HEAD')
    else:git(repo,'switch','--orphan',branch)
    dest=repo/'video';dest.mkdir(exist_ok=True);links=[]
    for item in v['outputs']:
        source=out/item['path'];shutil.copy2(source,dest/source.name);links.append(f'- [{source.name}](video/{source.name}?raw=1)')
        for name in ['captions.srt','script.txt','validation.json']:
            shutil.copy2(source.parent/name,dest/(source.stem+'_'+name))
    for name in ['YouTube_thumbnail.png','YouTube_title_and_description.txt','YouTube_upload_settings.txt','TikTok_captions.txt','Sources_and_methods.md','analysis.json','validation.json']:
        shutil.copy2(out/name,dest/name);links.append(f'- [{name}](video/{name}?raw=1)')
    shutil.copy2(out/'Market_Mind_Weekly_2026-10-05_to_09'/'contact-sheet.jpg',dest/'contact-sheet.jpg')
    if (out/'sources').exists():shutil.copytree(out/'sources',dest/'sources',dirs_exist_ok=True)
    prefix='AUTOMATION TEST — NOT THE FINAL EDITION' if a.preview else 'WEEKLY MARKET REVIEW — FINAL FILES'
    (repo/'README.md').write_text('# '+prefix+'\n\nReview: October 5–9, 2026. Outlook: October 12–16.\n\nMain video: 16:9. Two Shorts: 9:16. English narration and burned English captions.\n\n'+'\n'.join(links)+'\n\nUse Download raw on a GitHub file page. Files are not automatically uploaded to YouTube or TikTok. Source gaps are recorded in Sources_and_methods.md.\n')
    git(repo,'config','user.name','Market Mind cloud video');git(repo,'config','user.email','41898282+github-actions[bot]@users.noreply.github.com');git(repo,'add','README.md','video')
    if subprocess.run(['git','-C',str(repo),'diff','--cached','--quiet']).returncode:git(repo,'commit','-m',prefix)
    git(repo,'push','origin','HEAD:refs/heads/'+branch);print('DELIVERY_BRANCH='+branch)
if __name__=='__main__':main()
