"""Publish validated Bitcoin deliverables; no social posting."""
import os,json,pathlib,shutil,subprocess
root=pathlib.Path(os.environ.get('BITCOIN_OUTPUT','/tmp/bitcoin-daily-2026-10-11'))
repo=pathlib.Path(os.environ['PUBLISH_REPO']);v=json.loads((root/'validation.json').read_text());a=json.loads((root/'analysis.json').read_text())
assert v['passed'] and v['publication_date']=='2026-10-11'
assert v['data_date']==a['date']
def git(*args):return subprocess.run(['git','-C',str(repo),*args],check=True)
branch='deliveries/BTC-2026-10-11'
refs=subprocess.check_output(['git','-C',str(repo),'ls-remote','--heads','origin',branch],text=True)
if refs:git('fetch','origin',branch);git('switch','-C',branch,'FETCH_HEAD')
else:git('switch','--orphan',branch)
video=repo/'video';video.mkdir(exist_ok=True)
for name in ['Bitcoin_cover_2026-10-11.png','validation.json','analysis.json','YouTube_title_and_description.txt','TikTok_caption.txt','YouTube_upload_settings.txt','Sources_and_methods.md']:shutil.copy2(root/name,video/name)
for path in (root/'Bitcoin_Daily_2026-10-11').iterdir():
 if path.suffix in ['.mp4','.srt','.txt','.json']:shutil.copy2(path,video/path.name)
shutil.copytree(root/'sources',video/'sources',dirs_exist_ok=True)
(repo/'README.md').write_text('# Bitcoin — October 11, 2026\n\n[Download video](video/Bitcoin_Daily_2026-10-11.mp4?raw=true) · [Cover](video/Bitcoin_cover_2026-10-11.png?raw=true)\n\nCurrent snapshot and completed UTC daily candle are labelled separately. Includes the IBIT explanation. No YouTube or TikTok posting was performed.\n')
git('config','user.name','github-actions[bot]');git('config','user.email','41898282+github-actions[bot]@users.noreply.github.com');git('add','--','README.md','video')
if subprocess.run(['git','-C',str(repo),'diff','--cached','--quiet']).returncode:git('commit','-m','Publish verified Bitcoin October 11 daily video')
git('push','origin','HEAD:refs/heads/'+branch)
