// Quick looks at Kulturstockholm from the chase camera, parked (no speed): node peek.cjs <outdir> <m,m,...> [query]
// Serve the repo root first (PORT, default 8830). Prints the page errors.
const PW=process.env.PW||'/Users/kimdahlroth/.nvm/versions/node/v25.1.0/lib/node_modules/@playwright/cli/node_modules/playwright';
const {chromium}=require(PW); const fs=require('fs'); const path=require('path');
const OUT=process.argv[2], MS=(process.argv[3]||'0').split(',').map(Number), Q=process.argv[4]||'', PORT=process.env.PORT||8830;
const W=+(process.env.W||1600), H=+(process.env.H||900);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{ fs.mkdirSync(OUT,{recursive:true}); const b=await chromium.launch({channel:'chrome',args:['--use-angle=metal','--enable-gpu']});
  const p=await b.newPage({viewport:{width:W,height:H}}); const errs=[];
  p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{ if(m.type()==='error') errs.push(m.text()); });
  await p.goto(`http://localhost:${PORT}/index.html?check&bana=kultur${Q}`);
  for(let i=0;i<240;i++){ if(await p.evaluate(()=>!!window.__sw&&__sw.state()!=='loading').catch(()=>false)) break; await sleep(500); }
  await p.evaluate(()=>{ __sw.setPaused(true); document.getElementById('msg').style.visibility='hidden'; });
  const L=await p.evaluate(()=>__sw.len());
  for(const m of MS){ await p.evaluate(t=>__sw.placeAt(t),((m/L)%1+1)%1); await sleep(400);
    for(let w=0;w<60;w++){ if(await p.evaluate(()=>__sw.tilesIdle())) break; await sleep(150); } await sleep(500);
    await p.screenshot({path:path.join(OUT,`peek_${m}.png`)}); console.log('shot',m); }
  console.log(JSON.stringify({len:Math.round(L),errs:errs.slice(0,6)})); await b.close(); })();
