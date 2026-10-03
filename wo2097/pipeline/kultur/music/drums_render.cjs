// Renders a drum event list with the game's own big-beat voices (lifted verbatim from index.html) in an OfflineAudioContext.
//   node drums_render.cjs <index.html> <plan.json> <out.wav> [kinds,comma]  -> 44.1 kHz stereo float WAV
const PW='/Users/kimdahlroth/.nvm/versions/node/v25.1.0/lib/node_modules/@playwright/cli/node_modules/playwright';
const {chromium}=require(PW); const fs=require('fs');
const [,,IDX,PLAN,OUT,KINDS]=process.argv;
const src=fs.readFileSync(IDX,'utf8');
const grab=n=>{ const i=src.indexOf('function '+n+'('); if(i<0) throw new Error('no '+n); let d=0,j=src.indexOf('{',i); for(;j<src.length;j++){ if(src[j]==='{') d++; else if(src[j]==='}'){ d--; if(d===0) break; } } return src.slice(i,j+1); };
const voices=['noiseSrc','mKick','mSnare','mHat','mRiser','mImpact'].map(grab).join('\n');
const plan=JSON.parse(fs.readFileSync(PLAN,'utf8')); const kinds=KINDS?KINDS.split(','):null;
const ev=plan.events.filter(e=>!kinds||kinds.includes(e.k)); const len=plan.fileEnd+1;
(async()=>{ const b=await chromium.launch({channel:'chrome',headless:true}); const p=await b.newPage();
  const res=await p.evaluate(async({voices,ev,len})=>{
    const SR=44100; let actx=new OfflineAudioContext(2,Math.ceil(SR*len),SR), musicGain=null, sharedNoise=null;
    eval(voices.replace(/function (\w+)\(/g,'var $1=function(').replace(/\}\nvar /g,'};\nvar ')+';');
    const L=actx.sampleRate, nb=actx.createBuffer(1,L,L), ch=nb.getChannelData(0); for(let i=0;i<L;i++) ch[i]=Math.random()*2-1; sharedNoise=nb;
    const bus=actx.createGain(); bus.connect(actx.destination);
    for(const e of ev){ const g=actx.createGain(); g.gain.value=e.k==='hat'?1:e.v; g.connect(bus); musicGain=g;
      if(e.k==='kick') mKick(e.t); else if(e.k==='snare') mSnare(e.t); else if(e.k==='hat') mHat(e.t,e.v); else if(e.k==='riser') mRiser(e.t); else if(e.k==='impact') mImpact(e.t); }
    const buf=await actx.startRendering(); const out=[];
    for(let c=0;c<2;c++){ const d=buf.getChannelData(c); const u8=new Uint8Array(d.buffer); let s=''; for(let i=0;i<u8.length;i+=0x8000) s+=String.fromCharCode.apply(null,u8.subarray(i,i+0x8000)); out.push(btoa(s)); }
    return { n:buf.length, ch:out };
  },{voices,ev,len});
  const L=Buffer.from(res.ch[0],'base64'), R=Buffer.from(res.ch[1],'base64'), n=res.n;
  const hdr=Buffer.alloc(44), data=Buffer.alloc(n*8);
  for(let i=0;i<n;i++){ data.writeFloatLE(L.readFloatLE(i*4),i*8); data.writeFloatLE(R.readFloatLE(i*4),i*8+4); }
  hdr.write('RIFF',0); hdr.writeUInt32LE(36+data.length,4); hdr.write('WAVE',8); hdr.write('fmt ',12); hdr.writeUInt32LE(16,16); hdr.writeUInt16LE(3,20); hdr.writeUInt16LE(2,22);
  hdr.writeUInt32LE(44100,24); hdr.writeUInt32LE(44100*8,28); hdr.writeUInt16LE(8,32); hdr.writeUInt16LE(32,34); hdr.write('data',36); hdr.writeUInt32LE(data.length,40);
  fs.writeFileSync(OUT,Buffer.concat([hdr,data])); console.log('wrote',OUT,n,'frames,',ev.length,'events'); await b.close(); })();
