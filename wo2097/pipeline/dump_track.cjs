// Flies the game over the whole lap with the Google tiles (?dump), snaps every control point to the street and
// writes the calibrated track to ../assets/track.json. Serve the REPO ROOT first: python3 -m http.server 8820
const PW=process.env.PW||'/Users/kimdahlroth/.nvm/versions/node/v25.1.0/lib/node_modules/@playwright/cli/node_modules/playwright';
const {chromium}=require(PW); const fs=require('fs'); const path=require('path');
(async()=>{ const b=await chromium.launch({channel:'chrome',args:['--use-angle=metal','--enable-gpu']}); const p=await b.newPage({viewport:{width:1280,height:800}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{ if(m.type()==='error') errs.push(m.text()); });
  await p.goto('http://localhost:8820/index.html?dump');
  let last='';
  for(let i=0;i<900;i++){ const st=await p.evaluate(()=>({done:!!window.__dump, txt:document.getElementById('loadtxt').textContent}));
    if(st.txt!==last&&i%10===0){ console.log(st.txt); last=st.txt; } if(st.done) break; await p.waitForTimeout(1000); }
  const d=await p.evaluate(()=>window.__dump);
  if(!d){ console.log('NO DUMP', errs.slice(0,5)); process.exit(1); }
  fs.writeFileSync(path.join(__dirname,'..','assets','track.json'),JSON.stringify(d));
  console.log('cp',d.cp.length,'snapped',d.snapped,'frames',d.frames.length,'len',Math.round(d.trackLen),'arches',d.arches.map(a=>a.n+':'+Math.round(a.d)+'m').join(' '),'errors',errs.slice(0,5)); await b.close(); })();
