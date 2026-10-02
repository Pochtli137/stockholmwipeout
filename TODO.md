# TODO

## Wipeout Österlen, stoppad i fas 0 (2026-10-02, grenen `osterlen`)
**Grinden föll:** Google har ingen fotogrammetri i Österlen. Alla 15 platser (Simrishamn hamn och centrum, Kivik hamn,
Kiviks musteri, Kungagraven, Kivik Art Centre, Stenshuvud, Vitemölla, Baskemölla, Brantevik, Skillinge, Glimmingehus,
Sandhammaren, Kåseberga, Ales stenar) är 2.5D: satellitbild draperad på terräng, inga hus, träd eller klippor med volym.
Mått (5 m-rutnät av strålar över 200 × 200 m): 0 % står upp i alla orter, högsta resning 0,9–1,5 m (Glimmingehus, 26 m hög
borg: 0,9 m). Stenshuvuds 38 % är bergets lutning i höjdmodellen. Referens: Slussen 54 % och 43 m, Malmö 26 % och 190 m,
Lund 52 % och 50 m. Ystad och Tomelilla är också platta. Verktyget: `wo2097/pipeline/osterlen/probe_tiles.cjs`.
Skärmdumpar och översikt: `~/Projects/_process/2026-10-02/stockholmwipeout-osterlen-phase0/` (privat, utanför repot).
**Inget byggt:** inget koncept, ingen bana, ingen upplåsning. Kim väljer väg.

**Utseendetest (samma kväll):** platt Google plus Blender-landmärken från racekameran, i middagssol. Fristående sida
`wo2097/pipeline/osterlen/looktest.html?seg=kivik|kaseberga|glimminge|stockholm` (+`&dip=1` för lågt pass vid Ales stenar),
`looktest.cjs` tar stillbilder och frame-stegade klipp, `build_landmarks.py` bygger Ales stenar (59 stenar efter OSM) och
Glimmingehus (OSM-fotavtryck, 26 m). Resultat i `~/Projects/_process/2026-10-02/stockholmwipeout-osterlen-test/`.
**Utfall:** havet och fälten håller, byarna läses som en karta och landmärkena som modeller på ett fotografi. Ales stenar syns
inte från 30 m (stenarna är 1 till 3 m höga), bara när banan går ner till cirka 8 m. Stenshuvud är en slät kulle utan klippor.
Stockholm från samma höjd har fasader och djup. Skyltarna läses i solen på cirka 100 m. Inget av detta rör `index.html`.

## Läge 2026-10-02
**Deployat:** grenen `vasterbron` inslagen i `main`: start mitt på Guldbron, ENTERING-titlar, ingen sköld i vila, nedräkningsbandet
borta, bullet time över Västerbron, bron bortklippt med vatten på Mälarens riktiga nivå, porten "DU HAR MYCKET ATT LEVA FÖR",
`?test=vasterbron`, studs vid landningen (1 m, två hopp, `BOUNCE`). Detaljer i CLAUDE.md.
**Kvar:** kilen under brons ände vid Långholmen (svag, accepterad tills vidare). Ion-tokenen. Musiken och skarpare stad nedan.
**Overifierat:** bullet time och vattnet på riktig iPhone.

## Idéer som väntar (2026-10-02)
- **Skarpare stad:** `tiles.errorTarget` står på 10 (dator) / 20 (mobil). Prova 4–6 på dator lokalt, mät fps, minne och laddtid före/efter. Mobil ska stå kvar. Kim: avvakta.
- **Musik:** ElevenLabs Music, provlyssning av tre riktningar först. Kontot behöver credits.

## Läge 2026-09-29, natt
**Tillbakarullat (Kim: "det här funkade inte"):** stadsdelsportar, ENTERING-titlar, flourishes/moves och Rez-musiken
(revert av `ae0b0bd` och `fd889c6`, historiken kvar). Mobilfixarna (`7052cc5`, kameran i `6be353c`) är kvar. Deployat.
**Lärdom:** Rez-idén provades rakt in i spelet utan jämförelse först; nästa gång en mock eller provsida innan bygget.

## Läge 2026-09-29, sent
**Live (`ae0b0bd`):** stadsdelsportar (9/varv, båda teman), ENTERING-titel, ett unikt move per stadsdel på takten, Rez-musik som
bygger ett lager per stadsdel ovanpå den deployade big beat-slingan (`SFX.rezLayers`). Ingen flourish vid upplockningar.
Mobil: responsiv HUD, spelbart stående.
**Fixat (`6be353c`):** skeppet syns på mobil i alla farter (kameran släpade till 25 m och FOV öppnades till 108°; nu fast avstånd
och tak på FOV i mobilläge). Undersidans glöd tonas ner under moves.
**Öppet:** Kims riktiga iPhone-test. Ion-tokenen. Maskinen mätte 30 fps 2026-09-29 kväll även på juni-versionen, alltså miljö,
inte regression: mät igen på vilad maskin.

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
