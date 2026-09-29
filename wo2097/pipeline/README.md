# STOCKHOLM WIPEOUT 2097 · Blender-byggda banan och skeppen

Staden är Googles Photorealistic 3D Tiles (via Cesium ion, som förut). Allt nytt ovanpå den är byggt i Blender
och laddas som glb i spelets egen koordinatram: banan, barriärerna, neonkanterna, fart- och vapenplattorna,
pylonerna ner till gatan, startportalen vid Slussen, sponsorbågarna, skyltarna och de sex skeppen.
Bara HUD:en, skärmeffekterna (fartstreck, blixtar, sköldkant), motorglöd, spår och bloom är three.js/DOM.

## Bygga om

    cd ~/Projects/stockholmwipeout && python3 -m http.server 8820 &      # repots rot, med config.js (ion-token)
    cd wo2097/pipeline
    python3 design_track.py        # 1. racinglinjen: OSM-rutten utjämnad till minsta radie 120 m -> assets/route_smooth.json (+ route_smooth.png)
    node dump_track.cjs            # 2. ?dump: surveyar linjen mot Googles tiles var 4:e m (±9 m bred, arkpelare ±11,5, skyltar ±18)
                                   #    -> assets/survey.json, sedan höjdprofilen -> assets/track.json
    node dump_track.cjs rebuild    #    (profilen om från sparad survey, utan tiles, sekunder)
    python3 make_textures.py       # 3. alla texturer med PIL -> tex/
    blender -b --factory-startup -P build.py     # 4. banan + skeppen, AO-bakade, Draco -> ../assets/track.glb, craft_<i>.glb
    node check_lap.cjs [utmapp]    # 5. spela igenom: svep var 8:e m + ett helt race med bot, rapport + skärmdumpar

**Racinglinjen (design_track.py):** minsta svängradie 120 m. Spelets greppgräns är v = √(70·R); toppfart 66 m/s
plus ~24 m/s boost ger R ≥ 116 m, så varje kurva kan tas i full fart med boost utan att dras in i väggen. Linjen
lämnar gatan i hörnen och kapar gatunätets ut-och-tillbaka-spikar (varvet 14,6 → 11,4 km).

**Höjdprofilen (`PROFILE` i index.html, `designProfile`):** banan är den lägsta mjuka linjen som ligger minst 6 m
över gatan och minst 2,6 m över allt som tilesen har inom banans bredd (träd, fasader, tak, brodäck), plus 2 m buffert,
med lutning högst 6 % (i praktiken 4,8 %), inga dalar kortare än ~200 m och vertikal radie över 1 km. Stockholms
innerstadsgator är 16–20 m mellan fasaderna och banan är 17 m bred med barriärer, så nästan hela varvet går som
upphöjd skyway över taknocken. Pylonerna står på det som finns rakt under (gata, tak eller däck).

**Set pieces:** bågar och skyltar placeras bara där surveyn säger att tilesen lämnar plats (bågpelarna ±11,5 m, skyltarna ±18 m);
en båge glider upp till 160 m längs varvet till närmaste fria plats, en skylt byter sida eller hoppas över.

## Himlen (index.html, blocket SKY · GOLDEN HOUR OVER MÄLAREN)

Sen kväll över Mälaren: solen i VNV (azimut 292°, 5,5° över horisonten, `SUN_AZ`/`SUN_EL`). En skydome-shader ritar
2097-gradienten (indigo zenit, magenta, guld mot solen, lila bort från den), solskivan (ljus nog för bloomen) och två
molnlager: ett solbelyst cumulusdäck på 1,8 km och cirrusstrimmor på 6 km, med en kort ljusmarsch mot solen för de varma
kanterna. Dimman är patchad i three.js fog-chunk så att färgen följer himlen bakom fragmentet (guld mot solen, lila bort),
och staden bleknar in i horisonten. Ett efterpass (`SkyRenderPass`) lägger god rays genom luckorna (djupmaskad radiell
marsch mot solen) och en linsflare som skalas med hur mycket av solen staden släpper igenom. Tilesen graderas inte om,
bara dimman rör dem. Solljuset, himmelsfyllnaden och miljökartan för blanka ytor kommer från samma sol och himmel.
Skärmdumpar: `node sky_shots.cjs <utmapp>` (mot solen, bort från solen, över vattnet vid Skeppsbron).

## Regler

- **Svenska varumärken, dystopi 2097:** parodier med ändrade namn, egen typografi och färger som bara påminner om
  förlagan, aldrig riktiga loggor: IKÖA, VOLVÖ, SAAPH, SPOTIFAI, H&N, ERIXON, KLARNÅ, SYSTEMBÖLAGET, SJ 2097, S/L, IKÅ,
  OATLÖ, ABSOLUTT, SECURITAZ, ELECTROLUXX, PRESSBYRÅ-N, FÖRSÄKRINGSKASSÅN, SKATTEVERK-X, BANK-ID+ (`BRANDS` i make_textures.py),
  lagen VOLVÖ SECURITY, SAAPH DEFENCE, SPOTIFAI NEURAL, IKÖA FLATPACK, KLARNÅ DEBT, ERIXON SIGNAL (samma färger i
  make_textures.py, build.py och index.html). Satir över företag och myndigheter, aldrig verkliga personer.
- Materialnamnen i Blender styr beteendet i spelet: `pad_speed`/`pad_weapon` blir additiva (farten rullar, glyfen snurrar),
  `neon_*`/`light_*`/`core_*` får gå över 1.0 för bloomen, `light_0..4` är nedräkningsljusen på portalen.
- Skeppens noder: `flap_L`/`flap_R` (luftbromsarnas gångjärn), `eng_L`/`eng_R` (munstyckena).
- Bloomtröskeln är 1.4: bara emission (neon 2.6, kärnor 3.0, plattor 1.6) ska över. Blanka ytor i lågt solljus blev en vit boll; banan är därför satin (roughness 0.62).
- Typsnitt: Orbitron och Rajdhani (SIL Open Font License, `fonts/`), katakana från systemets Hiragino.
