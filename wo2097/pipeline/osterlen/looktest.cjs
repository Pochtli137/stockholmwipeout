// WIPEOUT ÖSTERLEN · LOOK TEST (2026-10-02): stills and a frame-stepped clip per segment from looktest.html.
// Serve the REPO ROOT first on your own port:  python3 -m http.server 8830 &
//   PORT=8830 node looktest.cjs <outdir> stills [seg,seg]     # the stills (6 Österlen + 1 Stockholm)
//   PORT=8830 node looktest.cjs <outdir> clip <seg> [seconds=11] [m/s=70]   # 30 fps frames + an mp4 (ffmpeg)
// The first run of a segment surveys its line against the tiles (about a minute) and saves test_assets/survey_<seg>.json.
const PW=process.env.PW||'/Users/kimdahlroth/.nvm/versions/node/v25.1.0/lib/node_modules/@playwright/cli/node_modules/playwright';
const {chromium}=require(PW); const fs=require('fs'); const path=require('path'); const {execFileSync}=require('child_process');
const OUT=process.argv[2], MODE=process.argv[3]||'stills', ARG=process.argv[4], PORT=process.env.PORT||8830, W=1920, H=1080;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
// where the craft is for each still: the point on the line nearest a place, minus a lead (m) so the place is ahead in frame
const STILLS=[
  ['1_kivik_byn_fran_havet','kivik',[55.6879,14.2278],-230,0], ['2_kiviks_musteri_odlingar','kivik',[55.6738,14.2655],70,0],
  ['3_stenshuvud_klipporna','kivik',[55.6631,14.2728],-60,0], ['4_kaseberga_hamn_fran_havet','kaseberga',[55.38317,14.06369],-260,0],
  ['5_ales_stenar_pa_klippan','kaseberga',[55.382688,14.054328],-150,0], ['6_glimmingehus','glimminge',[55.500905,14.230933],-150,0],
  ['5b_ales_stenar_lagt_pass_5m','kaseberga&dip=1',[55.382688,14.054328],-110,0],
  ['7_stockholm_skeppsbron_jamforelse','stockholm',[59.3240,18.0760],-120,0] ];
async function open(b,seg){ const p=await b.newPage({viewport:{width:W,height:H},deviceScaleFactor:1}); const errs=[];
  p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{ if(m.type()==='error') errs.push(m.text()); });
  await p.goto(`http://localhost:${PORT}/wo2097/pipeline/osterlen/looktest.html?seg=${seg}`);
  for(let i=0;i<900;i++){ if(await p.evaluate(()=>window.__lt&&__lt.ready).catch(()=>false)) break; await sleep(400); }
  const info=await p.evaluate(()=>({ len:Math.round(__lt.len), minR:__lt.minR, profile:__lt.profile, landmarks:__lt.landmarks, surveyed:!!__lt.survey }));
  if(info.surveyed){ const S=await p.evaluate(()=>__lt.survey); fs.writeFileSync(path.join(__dirname,'test_assets',`survey_${seg}.json`),JSON.stringify(S)); }
  console.log(seg,JSON.stringify(info),errs.slice(0,3)); return {p,errs}; }
const settle=async(p,ms)=>{ const s=Date.now(); await sleep(120); while(Date.now()-s<ms){ if(await p.evaluate(()=>__lt.idle())) break; await sleep(80); } await sleep(120); };
(async()=>{ fs.mkdirSync(OUT,{recursive:true}); const b=await chromium.launch({channel:'chrome',args:['--use-angle=metal','--enable-gpu']});
  if(MODE==='stills'){ const only=ARG?ARG.split(','):null; const segs=[...new Set(STILLS.map(s=>s[1]))].filter(s=>!only||only.includes(s));
    for(const seg of segs){ const {p}=await open(b,seg);
      for(const [name,sg,at,lead,lat] of STILLS){ if(sg!==seg) continue;
        const r=await p.evaluate(([at,lead,lat])=>__lt.place(__lt.sAt(at[0],at[1])+lead,70,lat),[at,lead,lat]);
        await settle(p,8000); await p.screenshot({path:path.join(OUT,name+'.png')}); console.log(name,JSON.stringify(r)); }
      await p.close(); } }
  if(MODE==='clip'){ const seg=ARG, SECS=+(process.argv[5]||11), V=+(process.argv[6]||70); const {p}=await open(b,seg);
    const START={ kivik:[[55.6879,14.2278],-470], kaseberga:[[55.382688,14.054328],-700] }[seg];
    const s0=await p.evaluate(([at,lead])=>__lt.sAt(at[0],at[1])+lead,START); const dir=path.join(OUT,'frames_'+seg); fs.mkdirSync(dir,{recursive:true});
    await p.evaluate(s=>__lt.place(s,70),s0); await settle(p,8000); const N=Math.round(SECS*30);
    for(let i=0;i<N;i++){ const r=await p.evaluate(([s,v])=>__lt.place(s,v),[s0+V*i/30,V]); await settle(p,900);
      await p.screenshot({path:path.join(dir,String(i).padStart(4,'0')+'.png')}); if(i%30===0) console.log(seg,i,JSON.stringify(r)); }
    await p.close();
    execFileSync('ffmpeg',['-y','-loglevel','error','-framerate','30','-i',path.join(dir,'%04d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-crf','18',path.join(OUT,`klipp_${seg}.mp4`)]);
    console.log('mp4',path.join(OUT,`klipp_${seg}.mp4`)); }
  await b.close(); })();
