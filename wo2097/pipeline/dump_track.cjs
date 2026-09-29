// Lays the track over Google's tiles and writes ../assets/track.json (+ survey.json). Serve the REPO ROOT first:
//   python3 -m http.server 8820
//   node dump_track.cjs            # ?dump: survey the racing line against the tiles (~15 min), then profile it
//   node dump_track.cjs rebuild    # ?rebuild: no tiles, re-profile from the saved survey.json (seconds)
// The racing line comes from design_track.py (route_smooth.json); the profile rules are PROFILE in index.html.
const PW=process.env.PW||'/Users/kimdahlroth/.nvm/versions/node/v25.1.0/lib/node_modules/@playwright/cli/node_modules/playwright';
const {chromium}=require(PW); const fs=require('fs'); const path=require('path');
const MODE=process.argv[2]==='rebuild'?'rebuild':'dump', A=path.join(__dirname,'..','assets');
(async()=>{ const b=await chromium.launch({channel:'chrome',args:['--use-angle=metal','--enable-gpu']}); const p=await b.newPage({viewport:{width:1280,height:800}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{ if(m.type()==='error') errs.push(m.text()); });
  await p.goto('http://localhost:8820/index.html?'+MODE);
  let last='';
  for(let i=0;i<3600;i++){ const st=await p.evaluate(()=>({done:!!window.__dump, txt:document.getElementById('loadtxt').textContent}));
    if(st.txt!==last&&i%15===0){ console.log(st.txt); last=st.txt; } if(st.done) break; await p.waitForTimeout(1000); }
  const d=await p.evaluate(()=>window.__dump);
  if(!d){ console.log('NO DUMP', errs.slice(0,5)); process.exit(1); }
  if(d.survey){ if(MODE==='dump') fs.writeFileSync(path.join(A,'survey.json'),JSON.stringify(d.survey)); delete d.survey; }
  fs.writeFileSync(path.join(A,'track.json'),JSON.stringify(d));
  console.log(MODE,'cp',d.cp.length,'surveyed',d.snapped,'frames',d.frames.length,'len',Math.round(d.trackLen),'profile',JSON.stringify(d.profile),
    'arches',d.arches.map(a=>a.n+':'+Math.round(a.d)+'m').join(' '),'errors',errs.slice(0,5)); await b.close(); })();
