"""Publish validated downloads and a GitHub Actions completion summary."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
repo=Path(os.environ['PUBLISH_REPO']);root=Path(os.environ.get('PAIR_OUTPUT','/tmp/close-pair-2026-10-15'))
def git(*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
branch='deliveries/NKE-USO-2026-10-15'
if git('ls-remote','--heads','origin',branch):git('fetch','origin',branch);git('switch','-C',branch,'FETCH_HEAD')
else:git('switch','--orphan',branch)
selected=[]
for ticker in ['NKE','USO']:
    src=root/ticker;v=json.loads((src/'validation.json').read_text());a=json.loads((src/'analysis.json').read_text())
    video=src/f'{ticker}_analysis_2026-10-15.mp4'
    assert v['passed'] and v['trade_date']==a['date']=='2026-10-15'
    assert 120<=float(v['video_duration'])<=180 and hashlib.sha256(video.read_bytes()).hexdigest()==v['sha256']
    dst=repo/'video'/ticker;dst.mkdir(parents=True,exist_ok=True)
    names=[video.name,ticker+'_cover.png',ticker+'_Video_and_Publishing_Kit.zip','Captions.srt','Narration_script.txt','TikTok_caption.txt','YouTube_title_and_description.txt','YouTube_upload_settings.txt','Sources_and_methods.md','analysis.json','daily.csv','news_review.json','market_raw.json','validation.json']
    for name in names:shutil.copy2(src/name,dst/name);selected.append(str(Path('video')/ticker/name))
text='# NKE and USO — October 15, 2026 close\n\nTwo validated English vertical Shorts with Michael, animated charts, embedded covers, subtitles and publishing copy. No YouTube/TikTok posting performed.\n\n'
for t in ['NKE','USO']:text+=f'- **{t}**: [Video](video/{t}/{t}_analysis_2026-10-15.mp4?raw=true) · [Download ZIP](video/{t}/{t}_Video_and_Publishing_Kit.zip?raw=true) · [YouTube copy](video/{t}/YouTube_title_and_description.txt) · [TikTok copy](video/{t}/TikTok_caption.txt)\n'
(repo/'README.md').write_text(text)
git('config','user.name','github-actions[bot]');git('config','user.email','41898282+github-actions[bot]@users.noreply.github.com');git('add','--','README.md',*selected)
if subprocess.run(['git','-C',str(repo),'diff','--cached','--quiet']).returncode:git('commit','-m','Publish verified NKE and USO October 15 shorts')
git('push','origin','HEAD:refs/heads/'+branch)
sha=git('rev-parse','HEAD');base=f'https://github.com/ilia044-lang/-/raw/{sha}/video'
summary='# Videos ready\n\n'
for t in ['NKE','USO']:summary+=f'- [{t} MP4]({base}/{t}/{t}_analysis_2026-10-15.mp4) · [{t} ZIP]({base}/{t}/{t}_Video_and_Publishing_Kit.zip)\n'
if os.environ.get('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text(summary)
print(summary)
