// VÄSTERBRON IS GONE (Kim 2026-10-02: "kan vi ändra på googlemappen så att det bara blir vatten?"). The game clips the
// bridge out of Google's tiles where it crosses Riddarfjärden and lays its own water in the hole; this script measures
// what that needs and writes track.json `water`:
//   level  Mälaren's surface in the game frame: the median of every column around the bridge that hits only water
//   hull   the corridor, four corners as [m along the lap, m right of the racing line]: the bridge's deck runs -4..+20
//          right of the line (parapets and lamps included at +-4 m), the ends sit on the shorelines (the Långholmen
//          shore crosses the bridge at a slant). Over open water a wider hull costs nothing, over land it would cut it.
//   stumpTop the deck's top just past each cut, on the kept side (north, south): the abutments close it
//   clipY  the height band that is cut away inside the hull: from 1.05 m over the level (Google's water mesh swells
//          ~0.7 m around it) to above the lamp posts
//   y      our water sheet, just over the cut: over the swell, so Google's bridge shadow on the water never pokes
//          through its soft edge, and under the boats' decks. core/feather (m): its solid core around the hull and the
//          soft edge into Google's water
// It also scans every column inside the hull and fails if any of it is land (its lowest hit 1.5 m over the level: the
// water mesh itself undulates ~0.7 m). index.html draws from `water`, neon/build.py stands the bridge's pylons on the sheet.
// Re-run after dump_track.cjs (which rewrites track.json without it). Serve the REPO ROOT first:
//   python3 -m http.server 8820 ;  node water_profile.cjs
const PW=process.env.PW||'/Users/kimdahlroth/.nvm/versions/node/v25.1.0/lib/node_modules/@playwright/cli/node_modules/playwright';
const {chromium}=require(PW); const fs=require('fs'); const path=require('path');
const HULL=[[7812,-8],[7806,24],[8228,24],[8248,-8]], CLIP_TOP=30, OVER=1.05, CORE=3, FEATHER=14;
const TJ=path.join(__dirname,'..','assets','track.json'); const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const inHull=(m,lat)=>{ const k=(lat-HULL[0][1])/(HULL[1][1]-HULL[0][1]), m0=HULL[0][0]+(HULL[1][0]-HULL[0][0])*k, m1=HULL[3][0]+(HULL[2][0]-HULL[3][0])*k;
  return lat>=HULL[0][1]&&lat<=HULL[1][1]&&m>=m0&&m<=m1; };
(async()=>{ const b=await chromium.launch({channel:'chrome',args:['--use-angle=metal','--enable-gpu']});
  const p=await b.newPage({viewport:{width:1280,height:800}}); await p.goto('http://localhost:'+(process.env.PORT||8820)+'/index.html?check&grepp=normal');
  for(let i=0;i<240;i++){ if(await p.evaluate(()=>!!window.__sw&&__sw.state()!=='loading')) break; await sleep(500); }
  await p.evaluate(()=>__sw.setPaused(true));
  const cols=[];   // [m, lat, top, lowest]
  for(let m0=7780;m0<8280;m0+=40){
    await p.evaluate(m=>__sw.placeAt(m/__sw.len()),m0+20); await sleep(300); for(let w=0;w<50;w++){ if(await p.evaluate(()=>__sw.tilesIdle())) break; await sleep(150); }
    cols.push(...await p.evaluate(m0=>{ const res=[], f=__sw.mkFrame();
      for(let m=m0;m<m0+40;m+=2){ __sw.frameAt(m/__sw.len(),f); const n=Math.hypot(f.right.x,f.right.z);
        for(let lat=-40;lat<=56;lat+=2){ const h=__sw.hitsAt(f.p.x+f.right.x/n*lat,f.p.z+f.right.z/n*lat); if(h.length) res.push([m,lat,h[0],h[h.length-1]]); } }
      return res; },m0)); }
  const wat=cols.filter(c=>c[2]<-15&&c[2]-c[3]<0.01&&(c[1]<-8||c[1]>24)).map(c=>c[2]).sort((a,b)=>a-b);
  const level=+wat[wat.length>>1].toFixed(2);
  const land=cols.filter(c=>inHull(c[0],c[1])&&c[3]>level+1.5);   // the water mesh itself undulates ~0.7 m; a cut swell is under our water
  // the stumps (neon/build.py): the deck's highest point just on the kept side of each cut, so the abutment closes it
  const edgeM=(a,b,lat)=>a[0]+(b[0]-a[0])*(lat-a[1])/(b[1]-a[1]);
  const deckTop=(a,b,side)=>{ let hi=-1e9; for(const c of cols){ if(c[1]<-6||c[1]>22) continue; const d=(c[0]-edgeM(a,b,c[1]))*side; if(d>=0&&d<=6&&c[2]>hi) hi=c[2]; } return +hi.toFixed(2); };
  const stumpTop=[deckTop(HULL[0],HULL[1],-1),deckTop(HULL[3],HULL[2],1)];   // [Kungsholmen side, Långholmen side]
  const W={ level, hull:HULL, clipY:[+(level+OVER).toFixed(2),CLIP_TOP], y:+(level+OVER+0.05).toFixed(2), core:CORE, feather:FEATHER, stumpTop };
  console.log('water level',level,'from',wat.length,'columns (p10',wat[Math.floor(wat.length*0.1)].toFixed(2),'p90',wat[Math.floor(wat.length*0.9)].toFixed(2)+')',
    '· land inside the hull:',land.length,land.map(c=>c[0]+'/'+c[1]+'@'+c[3].toFixed(1)).join(' '));
  if(land.length>3){ console.log('the hull reaches land: tighten HULL'); process.exit(1); }
  const D=JSON.parse(fs.readFileSync(TJ,'utf8')); D.water=W; fs.writeFileSync(TJ,JSON.stringify(D)); console.log(JSON.stringify(W)); await b.close(); })();
