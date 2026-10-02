// THE WATER OVER VÄSTERBRON (Kim 2026-10-02: "googlebron syns där under så lägg glittrande vatten där så att vi döljer den
// i hoppet"). Measures Google's bridge under the jump corridor and writes track.json `water`: the sheet's extent along the
// lap (fromM..toM) and across it (latL..latR, soft over edgeM; fadeM at the ends), and its height every stepM: the highest
// tile top within +-runM (deck, parapets and the lamp posts, which stand ~8 m over the deck) plus `clear`. index.html
// draws the sheet from it, neon/build.py stands the bridge's pylons on it. Re-run after dump_track.cjs (which rewrites
// track.json without it). Serve the REPO ROOT first:   python3 -m http.server 8820 ;  node water_profile.cjs
const PW=process.env.PW||'/Users/kimdahlroth/.nvm/versions/node/v25.1.0/lib/node_modules/@playwright/cli/node_modules/playwright';
const {chromium}=require(PW); const fs=require('fs'); const path=require('path');
const W={ fromM:7790, toM:8350, latL:-16, latR:34, edgeM:8, fadeM:36, stepM:5, runM:25, avgM:10, clear:3.5 };
const SCAN=[-10,28];   // the bridge with its parapets runs about -5..+21 m right of the racing line
const TJ=path.join(__dirname,'..','assets','track.json'); const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{ const b=await chromium.launch({channel:'chrome',args:['--use-angle=metal','--enable-gpu']});
  const p=await b.newPage({viewport:{width:1280,height:800}}); await p.goto('http://localhost:'+(process.env.PORT||8820)+'/index.html?check&grepp=normal');
  for(let i=0;i<240;i++){ if(await p.evaluate(()=>!!window.__sw&&__sw.state()!=='loading')) break; await sleep(500); }
  await p.evaluate(()=>__sw.setPaused(true));
  const top={};   // m -> highest tile top across the scan
  for(let m0=W.fromM-W.runM;m0<W.toM+W.runM;m0+=40){
    await p.evaluate(m=>__sw.placeAt(m/__sw.len()),m0+20); await sleep(300); for(let w=0;w<40;w++){ if(await p.evaluate(()=>__sw.tilesIdle())) break; await sleep(150); }
    Object.assign(top,await p.evaluate(([m0,S])=>{ const res={}, f=__sw.mkFrame();
      for(let m=m0;m<m0+40;m++){ __sw.frameAt(m/__sw.len(),f); const n=Math.hypot(f.right.x,f.right.z); let hi=-1e9;
        for(let lat=S[0];lat<=S[1];lat+=0.5){ const h=__sw.hitsAt(f.p.x+f.right.x/n*lat,f.p.z+f.right.z/n*lat); if(h.length&&h[0]>hi) hi=h[0]; }
        res[m]=hi; } return res; },[m0,SCAN])); }
  const run=m=>{ let hi=-1e9; for(let k=-W.runM;k<=W.runM;k++){ const v=top[m+k]; if(v!==undefined&&v>hi) hi=v; } return hi; };
  const h=[]; for(let m=W.fromM;m<=W.toM;m+=W.stepM){ let s=0,c=0; for(let k=-W.avgM;k<=W.avgM;k++){ s+=run(m+k); c++; } h.push(+(s/c+W.clear).toFixed(2)); }
  const D=JSON.parse(fs.readFileSync(TJ,'utf8')); D.water={ ...W, h }; fs.writeFileSync(TJ,JSON.stringify(D));
  console.log('water',W.fromM,'..',W.toM,'m, height',Math.min(...h).toFixed(1),'..',Math.max(...h).toFixed(1)); await b.close(); })();
