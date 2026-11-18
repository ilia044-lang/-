const { chromium } = require('playwright');
(async () => {
  const [,, html, outDir, ...times] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({viewport:{width:1080,height:1920}});
  const errs=[]; p.on('pageerror', e=>errs.push(String(e)));
  await p.goto('file://'+html); await p.evaluate(()=>document.fonts.ready);
  for (const t of times) { await p.evaluate(t=>window.render(+t), t); await p.screenshot({path:`${outDir}/still_${t}.png`}); }
  if(errs.length) console.log('ERR', errs.join('\n'));
  await b.close();
})();
