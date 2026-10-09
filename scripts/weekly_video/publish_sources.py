"""Expose only public-source diagnostics, without publishing a final video."""
import argparse,json,shutil,subprocess
from pathlib import Path
def git(repo,*args):return subprocess.run(['git','-C',str(repo),*args],check=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--repo',required=True);a=p.parse_args();out=Path(a.out);repo=Path(a.repo)
    data=json.loads((out/'analysis.json').read_text());branch='diagnostics/WEEKLY-2026-10-09'
    remote=subprocess.check_output(['git','-C',str(repo),'ls-remote','--heads','origin','refs/heads/'+branch],text=True)
    if remote:git(repo,'fetch','origin',branch);git(repo,'switch','-C',branch,'FETCH_HEAD')
    else:git(repo,'switch','--orphan',branch)
    for name in ['analysis.json','draft_script.json']:shutil.copy2(out/name,repo/name)
    shutil.copytree(out/'sources',repo/'sources',dirs_exist_ok=True)
    (repo/'README.md').write_text('# Public-source production diagnostics\n\nThese are input checks, not a completed video.\n\nData date: '+data['date']+'\n')
    git(repo,'config','user.name','Market Mind cloud video');git(repo,'config','user.email','41898282+github-actions[bot]@users.noreply.github.com');git(repo,'add','README.md','analysis.json','draft_script.json','sources')
    if subprocess.run(['git','-C',str(repo),'diff','--cached','--quiet']).returncode:git(repo,'commit','-m','Save public-source checks for weekly production')
    git(repo,'push','origin','HEAD:refs/heads/'+branch)
if __name__=='__main__':main()
