// Uncapped frame time on a scripted stretch of the race (vsync off), so renderer/post/particle changes can be compared.
// Serve the REPO ROOT first (python3 -m http.server 8820), then: node perf.cjs [seconds=45] [label]
const PW=process.env.PW||'/Users/kimdahlroth/.nvm/versions/node/v25.1.0/lib/node_modules/@playwright/cli/node_modules/playwright';
const {chromium}=require(PW); const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const SECS=+(process.argv[2]||45), LABEL=process.argv[3]||'run', PORT=process.env.PORT||8820;
(async()=>{ const b=await chromium.launch({channel:'chrome',args:['--use-angle=metal','--enable-gpu','--disable-gpu-vsync','--disable-frame-rate-limit']});
  const p=await b.newPage({viewport:{width:1440,height:900}}); const errs=[];
  p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{ if(m.type()==='error'&&!/404/.test(m.text())) errs.push(m.text()); });
  await p.goto(`http://localhost:${PORT}/index.html?check&theme=${process.env.THEME||'used'}`);   // THEME=neon|used
  for(let i=0;i<120;i++){ if(await p.evaluate(()=>!!window.__sw&&window.__sw.state()!=='loading')) break; await sleep(500); }
  await p.evaluate(()=>{ const S=window.__pf={ ft:[], last:performance.now(), on:false };
    const tick=()=>{ const now=performance.now(); if(S.on) S.ft.push(now-S.last); S.last=now;
      const pl=__sw.player(); if(pl&&__sw.state()==='race'){ S.on=true; __sw.keys['ArrowUp']=true; __sw.keys['ArrowLeft']=pl.lat>0.8; __sw.keys['ArrowRight']=pl.lat<-0.8; }
      requestAnimationFrame(tick); }; requestAnimationFrame(tick); });
  for(let i=0;i<60;i++){ if(await p.evaluate(()=>__pf.on)) break; await sleep(500); }
  await sleep(SECS*1000);
  const r=await p.evaluate(()=>{ const f=__pf.ft.slice(20).sort((a,b)=>a-b), q=x=>+f[Math.floor(x*(f.length-1))].toFixed(2);
    return { frames:f.length, medianMs:q(0.5), p95Ms:q(0.95), p99Ms:q(0.99), progress:+(__sw.player().t*100).toFixed(1) }; });
  console.log(JSON.stringify({label:LABEL,...r,errors:errs.slice(0,5)})); await b.close(); })();
