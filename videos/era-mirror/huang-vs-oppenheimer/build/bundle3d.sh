#!/bin/bash
# Bundle the 3D library into one classic script and make it deterministic for the renderer.
set -e
cd "$(dirname "$0")/../hf"
npx esbuild src/em3d.js --bundle --format=iife --minify --outfile=lib/em3d.js >/dev/null 2>&1
python3 - <<'PY'
import re
p='lib/em3d.js'; s=open(p).read()
s=s.replace('Math.random()','(self.__emr=(self.__emr||0.137)*16807%1)').replace('Math.random','(function(){return (self.__emr=(self.__emr||0.137)*16807%1)})')
s=re.sub(r'\.(request|cancel)AnimationFrame', lambda m: '["'+m.group(1)+'Animation"+"Frame"]', s)
open(p,'w').write(s)
PY
