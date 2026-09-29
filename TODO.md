# TODO

## Läge 2026-09-29, sent
**Live (`ae0b0bd`):** stadsdelsportar (9/varv, båda teman), ENTERING-titel, ett unikt move per stadsdel på takten, Rez-musik som
bygger ett lager per stadsdel ovanpå den deployade big beat-slingan (`SFX.rezLayers`). Ingen flourish vid upplockningar.
Mobil: responsiv HUD, spelbart stående.
**Öppet:** eget skepp syns inte i full fart på mobil (kamera eller pekkontroller, ej undersökt). Långholmens halvrulle visar
undersidans emitters ljust ett ögonblick. Kims riktiga iPhone-test. Ion-tokenen.

## Läge 2026-09-29, kväll
**Deployat:** `crafts` sammanslagen till `main` (`fd889c6`), pushad och live på stockholmwipeout.vercel.app. Båda temana
verifierade i produktion utan fel; `CLAUDE.md`, `TODO.md`, `blender/` och pipelinen ger 404. Punkt 1 och 2 nedan är klara.
**Kvar:** Kim provar mobilen på riktig iPhone via livesajten (HTTPS, så TILT går). Rotera ion-tokenen. Flourish-blixten
kan vara för stark (skeppet blir helvitt ett ögonblick), bedöms av Kim.

## Läge 2026-09-29 (överlämning)
**Gjort:** Blender-bygge ovanpå Googles Stockholm: bana (120 m minsta radie, lyft fri från tiles, 0 intrång), sex Blender-skepp,
temaval NEON/USED, skeppsval, used universe med pappersaffischer, svenska varumärkes- och partiparodier, runor i stället för
katakana, himmel. Ljud, partiklar och gnistor tillbaka till det deployade (flaggor av). Allt på grenen `crafts`, inte pushat.
**Beslutat (Kim):** staden är Google; två teman väljs först; used = papper, ingen neon; läsbarhet som neonbanan; de åtta
riksdagspartierna lika, utan Direktdemokraterna; ljudet som deployat; **"deploya sen allting"** när agentkön är klar.
**Nästa steg:**
1. Agentkön (startad 2026-09-29 i sessionen, pågår): skeppsvalskameran +25° (klar, `235803f`), avskurna annonser + parodiloggor
   på partiannonserna (pågår, ocommittat: `faux_logos.py`, `make_textures.py`, `build.py`, `neon/build.py`, `index.html`),
   PAUSE-texten som ligger kvar, landskapsmobil, stadsdelstitlar "ENTERING KUNGSHOLMEN" + Rez-segerpose (inget nytt ljud).
   Om sessionen dog: läs `git log crafts` och diffen, fortsätt där det slutade.
2. Kontrollera själv (skärmdumpar, `node wo2097/pipeline/check_lap.cjs` i båda temana), slå ihop `crafts` → `main`, pusha,
   `vercel --prod --yes`, verifiera att livesidan är identisk och att `blender/` ger 404.
3. Kim provar mobilen på riktig iPhone (på livesajten, HTTPS gör lutningsstyrning möjlig).
**Overifierat:** motorljud och 3D-ljud är bara kontrollerade via parametrar, ingen har lyssnat. Tiles-minnet på riktig iPhone.
Lutningsstyrning bara via HTTPS.
**Kim gör:** rotera Cesium ion-tokenen i `config.js` (publikt repo sedan juni).
