"""Publish already validated output using a separate checkout managed by Actions."""
import argparse,json,os,pathlib,shutil,subprocess

def git(repo,*args,**kwargs):return subprocess.run(['git','-C',str(repo),*args],check=True,**kwargs)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--repo',required=True);ap.add_argument('--mode',choices=['preview','production'],required=True);a=ap.parse_args()
    out=pathlib.Path(a.out);repo=pathlib.Path(a.repo);data=json.loads((out/'analysis.json').read_text());valid=json.loads((out/'validation.json').read_text())
    assert valid['passed'] and valid['trade_date']==data['date']
    branch=('deliveries' if a.mode=='production' else 'previews')+'/'+data['ticker']+'-'+data['date']
    remote=subprocess.check_output(['git','-C',str(repo),'ls-remote','--heads','origin','refs/heads/'+branch],text=True)
    if remote:
        git(repo,'fetch','origin',branch);git(repo,'switch','-C',branch,'FETCH_HEAD')
    else:git(repo,'switch','--orphan',branch)
    destination=repo/'video';destination.mkdir(exist_ok=True)
    names=[f'{data["ticker"]}_analysis_{data["date"]}.mp4',data['ticker']+'_cover.png','TikTok_caption.txt','YouTube_title_and_description.txt','Sources_and_methods.md','analysis.json','validation.json']
    for name in names:shutil.copy2(out/name,destination/name)
    title=('FINAL VIDEO' if a.mode=='production' else 'PREVIEW / AUTOMATION TEST')
    readme=f'''# {data['ticker']} — {title}\n\nDaily close: **{data['date']}**. Analysis date: {data['analysis_date']}.\n\n- [Download animated MP4](video/{names[0]}?raw=1)\n- [Download cover PNG](video/{names[1]}?raw=1)\n- [TikTok caption](video/TikTok_caption.txt)\n- [YouTube title and description](video/YouTube_title_and_description.txt)\n- [Sources and methods](video/Sources_and_methods.md)\n\nOn a GitHub file page, use **Download raw**.\n\nThe workflow verified the requested daily bar, video decoding, 1080×1920 dimensions and audio/video duration. Publication to YouTube or TikTok is not performed by this workflow.\n'''
    if a.mode=='preview':readme+='\nThis is a test of the cloud workflow using the latest completed session. The scheduled final video will be published on the separate deliveries branch after the required October 8 close is available.\n'
    (repo/'README.md').write_text(readme)
    git(repo,'config','user.name','github-actions[bot]');git(repo,'config','user.email','41898282+github-actions[bot]@users.noreply.github.com')
    git(repo,'add','--','README.md','video')
    if subprocess.run(['git','-C',str(repo),'diff','--cached','--quiet']).returncode:
        git(repo,'commit','-m',f'Publish {data["ticker"]} {data["date"]} {a.mode} video')
    git(repo,'push','origin','HEAD:refs/heads/'+branch)
    url=f'https://github.com/{os.environ["GITHUB_REPOSITORY"]}/tree/{branch}'
    print('DELIVERY_URL='+url)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:f.write(f'## {title}\n\n[Open the video, cover and captions]({url})\n\nTrade date: {data["date"]}.\n')

if __name__=='__main__':main()
