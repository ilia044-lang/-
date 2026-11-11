const { chromium } = require('playwright');
const path = require('path');
const img = (s) => 'file://' + path.resolve(__dirname, '../../hf/assets/img/' + s);
const font = (f) => 'file://' + require('os').homedir() + '/.cache/hyperframes/fonts/' + f;
const variants = [
  { name: 'thumb-A-it-happened-before', top: 'IT HAPPENED', hi: 'BEFORE' },
  { name: 'thumb-B-loyal-ruined-anyway', top: 'LOYAL.', hi: 'RUINED ANYWAY' },
];
(async () => {
  const fs = require('fs');
  const fdir = require('os').homedir() + '/.cache/hyperframes/fonts/playfair-display';
  const ff = fs.readdirSync(fdir).filter(f => /woff2?$/.test(f));
  const faces = ff.map(f => `@font-face{font-family:'PF';src:url('file://${fdir}/${f}');font-weight:${/900/.test(f) ? 900 : /700/.test(f) ? 700 : 400};font-style:${/italic/i.test(f) ? 'italic' : 'normal'};}`).join('\n');
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  for (const v of variants) {
    const html = `<html><head><style>${faces}
      body{margin:0;width:1280px;height:720px;background:#0a0b0e;overflow:hidden;font-family:'PF',Georgia,serif}
      .h{position:absolute;top:0;width:640px;height:720px;overflow:hidden}
      .h img{position:absolute;width:100%;height:100%;object-fit:cover}
      .l{left:0}.r{left:640px}
      .l img{object-position:50% 18%;transform:scale(1.25);transform-origin:50% 25%}
      .r img{object-position:50% 12%;transform:scale(1.55);transform-origin:52% 18%}
      .tl{position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,11,14,0) 35%,rgba(10,11,14,.95) 88%)}
      .ca{position:absolute;inset:0;mix-blend-mode:soft-light}
      .mid{position:absolute;left:634px;top:0;width:12px;height:720px;background:#f3efe6}
      .y{position:absolute;top:34px;font:700 64px 'PF',serif;padding:4px 22px;color:#0a0b0e}
      .t{position:absolute;left:0;width:1280px;text-align:center;font-weight:900;letter-spacing:-.01em;text-shadow:0 6px 30px rgba(0,0,0,.9)}
    </style></head><body>
      <div class="h l"><img src="${img('opp_portrait_g.jpg')}"><div class="ca" style="background:#e6a94e;opacity:.35"></div><div class="tl"></div></div>
      <div class="h r"><img src="${img('huang_stanford_a_g.jpg')}"><div class="ca" style="background:#56c8f5;opacity:.45"></div><div class="tl"></div></div>
      <div class="mid"></div>
      <div class="y" style="left:34px;background:#e6a94e">1954</div>
      <div class="y" style="right:34px;background:#56c8f5">2026</div>
      <div class="t" style="top:${v.top.length > 8 ? 440 : 420}px;font-size:${v.top.length > 8 ? 112 : 128}px;color:#f3efe6">${v.top}</div>
      <div class="t" style="top:560px;font-size:${v.hi.length > 8 ? 112 : 132}px;color:#ff4b3a">${v.hi}</div>
    </body></html>`;
    const f = path.resolve(__dirname, v.name + '.html'); fs.writeFileSync(f, html); await p.goto('file://' + f);
    await p.waitForTimeout(900);
    await p.screenshot({ path: path.resolve(__dirname, '../../out/thumbnails/' + v.name + '.png') });
  }
  await b.close();
})();
