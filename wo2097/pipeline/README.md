# STOCKHOLM WIPEOUT 2097 · Blender-byggda banan och skeppen

> **2026-09-29: en look, NEON.** USED-temat (sliten Stockholm, pappersaffischer, partiannonser med parodiloggor, grå asfalt)
> är pensionerat på Kims beslut. Neon-pipelinen ligger i `neon/` och `build.sh` bygger den. De gamla skripten på toppnivå
> (`make_textures.py`, `build.py`, `build_craft.py`, `faux_logos.py`) byggde USED och ligger kvar som referens; deras utdata
> (`assets/used/`) är borttagen. Sista commit med USED: `730a8f7`. Spelet börjar nu med en titelskärm som glider in i
> CHOOSE VEHICLE (inget temaval).


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
    blender -b --factory-startup -P build.py     # 4. banan, AO-bakad, Draco -> ../assets/track.glb
    blender -b --factory-startup -P build_craft.py [-- --only 3] [-- --nobake]   # 5. de sex skeppen -> ../assets/craft_<i>.glb (~16 s)
    node check_lap.cjs [utmapp]    # 6. spela igenom: svep var 8:e m + ett helt race med bot, rapport + skärmdumpar

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

## FEEL: berg-och-dalbanan (2026-09-30, `FEEL` i index.html)

Fortfarande räls. Profilen ovan är golvet utanför sex **dropfönster** (Slussen·Strömmen, Nybroviken, Norrmalm, Klara sjö,
Norr Mälarstrand, Söder). Inne i fönstren får linjen falla till stadens eget krav plus 1,5 m, med lutning upp till 19 % per sampel
(i praktiken 16,8 %) och vertikal radie ner till ~240 m: 18–26 m fall över vatten och öppna platser. `feelProfile` i
`designProfile`, allt räknas om med `node dump_track.cjs rebuild`.
- **Airtime** är bara visuell: skeppet lyfter när däckets vertikalacceleration v²·y″ understiger −g, men bara vid krönen i
  `FEEL.airAt` (Nybroviken, Klara sjö, Norr Mälarstrand). Övriga krön håller skeppet mot däcket. Landningen ger squash, skak
  och nosdipp. `t`, `lat` och farten påverkas inte. Utför ger `gv` (gravitationsbonus, högst +10 m/s).
- **Bank** 5–20° efter kurvans krökning (`frameAt` vrider right/up runt fwd), kameran lutar med till 75 %.
- **Tuber** vid Nybroviken och Norr Mälarstrand (där bågpelarna är fria): neonribbor var 5:e m, glas, ljusband och portaler
  i `neon/build.py`. Inne i tuben dämpas sol och himmelsljus och fartlinjerna tätnar. Halva bredden är 8 m där.
- **Rytm:** tre pads i kedja före varje krön, två i utförsbacken, jämna pads bort nära kedjorna. **Breda partier** (halva bredden
  10,5 m) där bågpelarna är fria över ±20 m: Strömmen och Klara sjö.
- Verktyg i `feel/`: `plot.py` (profil före/efter -> `out/profile_track.png`), `shots.cjs` (racekamera vid varje feature),
  `film.cjs <utmapp> <från m> <s>` (frame-stegad film, ett segment per mapp under `out/film/`), `stitch.py` (segmenten -> en mp4).

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
- Bloomtröskeln är 1.05 sedan used universe (se nedan): bara företagens skyltar, plattorna och skeppens dysor ska över.
- Typsnitt: Orbitron och Rajdhani (SIL Open Font License, `fonts/`), katakana från systemets Hiragino.

## Skeppen (build_craft.py) och hangaren (wo2097/showroom.html)

Sex egna konstruktioner för de påhittade lagen, modellerade som fasade hårdytor i Blender (superellipssektioner längs
skrovet, plattor för vingar och fenor, rör för dysor och master), AO-bakade i vertexfärger, klarlack på lacken.
Varje fil har noderna spelet styr: `flap_L`/`flap_R` (luftbromsgångjärn, plattan hänger bakom gångjärnet och
`rotation.x < 0` lyfter bakkanten) och `eng_L`/`eng_R` (dysornas mynning, där glöd, värme och spår sätts fast).

| # | Lag | Form |
|---|---|---|
| 0 | VOLVÖ SECURITY | brett platt skrov, pansrade sidopoddar med bultrader, stötfångare, störtbåge |
| 1 | SAAPH DEFENCE | diamantsektion med chines, intagsbommar, canarder, snedställda fenor, vapenbalkar, noskanon |
| 2 | SPOTIFAI NEURAL | organisk droppform, runda naceller, böjd vinge, vågformsribbor på ryggen |
| 3 | IKÖA FLATPACK | platta skivor med fasade kanter, insexbultar, slitsad stjärt, insexnyckel som antenn |
| 4 | KLARNÅ DEBT | nålnos, svart rygg, deltavinge med svarta spetsar, en bred dysa med två kärnor |
| 5 | ERIXON SIGNAL | katamaran, trappstegsfenor (signalstaplar), parabol, antennmaster med fyrar |

Hangaren: `http://localhost:8820/wo2097/showroom.html` (← → byt skepp, dra för att snurra, `?craft=N&still&view=side|front|top|rear|three`).

## Renderer: WebGL, not WebGPU (checked 2026-09-29)
`three.WebGPURenderer` was tried against the Google tiles and rejected:
- `3d-tiles-renderer` (0.4.28 in the game, and the latest 0.5.3) imports `WebGLRenderer` from `three`; three's WebGPU build
  (0.170 and 0.186) does not export it, so the tiles modules fail to load and there is no city. Mapping `three` to both builds
  would load two copies of three and break the tiles' materials.
- `TilesFadePlugin` injects its fade with `onBeforeCompile` (8 sites); node materials ignore that.
- The sky dome and the god rays are GLSL `ShaderMaterial`s and the post chain is `EffectComposer` + `UnrealBloomPass`: all WebGL-only,
  a TSL rewrite for no measurable gain.
- Headroom is already large: uncapped median 3.6 ms, p95 5.2 ms, p99 6.2 ms on this Mac (`node perf.cjs 40`).
`perf.cjs` measures uncapped frame time on a scripted stretch of the race (vsync off); use it before and after engine changes.

## Craft select and team stats
The hangar (state `select`) sits between loading and the countdown; `?check` skips it, `&team=N` preselects, the choice
is remembered in `localStorage.swTeam`. `STATS` (bars 0..1) and `physOf()` in index.html drive top speed, thrust,
steering and grip, wall drain and missile-hit loss for the player and the AI; SAAPH draws missiles 60 % of the time.
Balance check, craft alone (`?check&solo&team=N`, bot at full throttle in the middle, 11.4 km):
ERIXON 144.3 s · KLARNÅ 144.3 · SAAPH 144.6 · IKÖA 145.3 · SPOTIFAI 146.1 · VOLVÖ 146.5 (spread 1.5 %).
VOLVÖ's shield and SPOTIFAI's grip only pay when you touch walls or get hit, which the bot never does.

## Runes instead of katakana
Every secondary label is Younger Futhark (long-branch), Swedish words spelled the way a Viking-age carver would
(`runes.py`: 16 runes, no doubled consonants, ᛫ between words): VARV ᚠᛅᚱᚠ, PLATS ᛒᛚᛅᛏᛋ, TURBO ᛏᚢᚱᛒᚢ, SKÖLD ᛋᚴᚢᛚᛏ,
VAPEN ᚠᛅᛒᛁᚾ, STOCKHOLMS STORA PRIS ᛋᛏᚢᚴᚼᚢᛚᛘᛋ᛫ᛋᛏᚢᚱᛅ᛫ᛒᚱᛁᛋ. The font is Noto Sans Runic (SIL OFL 1.1, `../fonts/OFL.txt`),
embedded by the game and the showroom and used by make_textures.py, so bakes and web match. Billboards carry the
brand name in runes as a small tag; the gantry has a rune subtitle line.

## Switched off (Kim, 2026-09-29): flags in index.html, all `false` by default
The code stays; set a flag to `true` to bring an effect back.

| Flag | What it switches |
|---|---|
| `FX.particles` | both point clouds: exhaust, boost streams, the barrier scrape sparks, missile impacts and smoke, grit and leaves |
| `SFX.padSound` | the sound when you ride a speed chevron pad |
| `SFX.newPlayerEngine` | the spatial-pass player engine (boost raises pitch and level, reverb send) |
| `SFX.spatial` | everything the spatial-audio pass added: AI engines (HRTF, Doppler), street reverb and slapbacks, positional pad/weapon/hit/scrape sounds, bus compressor |
| `SFX.hangar` | the craft-select blips and lock-in sting |

With every flag off the audio is the deployed game's (8269ea8): the player's engine (two saws detuned 7 cents,
45 + 1.5·speed Hz, gain 0.026 + 0.0004·speed, 600 Hz lowpass straight to the output) and the big-beat music.
Checked by function-by-function comparison against `git show 8269ea8:index.html` and by counting the nodes the page
creates (no panner, convolver or compressor).

## USED UNIVERSE (2026-09-29): the look Kim chose
"det blir bättre med used universe och neoncorporate skyltar ja. cyber." Google's Stockholm stays untouched; everything
we built is a worn, lived-in 2097, and **the only saturated light in the world belongs to the corporations**.

- **Deck** (`make_textures.py` → `track.jpg`): old Slussen concrete and asphalt, newer and older patches, cracks,
  skid marks on the racing line, oil stains, faded kerb and centre paint, drain grates, the league stencil. Unlit.
- **Slab and footings** (`concrete.jpg`): formwork concrete with blowholes and rust runs. **Pylons, gantry and arch
  frames** (`pylon.jpg`): rusty steel with invented tags (SLSN, KRÅK, NOLL7, RÅTT, GRUS, MÖRK, ZON9, TUBE, BETONG, SÖDER:
  no real crews). World-scaled UVs via `MB.boxw`.
- **Walls**: tunnelbana tile (30 × 15 cm, grout, each tile its own tint) carrying the brands as LIT light boxes
  (`barrier_A/B` + `_e` emission maps), and a poster wall (`barrier_P`) with all eight parties as pasted-up paper
  posters. The three walls alternate every 104 m, the two sides out of step.
- **Light**: a fluorescent fitting on top of both walls every 3.2 m (7 126 of them; cold white on the left, sodium on
  the right; ~8 % dead, ~3.5 % flickering: `tube_flick_*`), a top rail with posts, two conduits on the outside, and
  178 sodium lamp posts every 64 m with an additive light pool on the deck (`pool_sodium`).
- **Signs** (superseded: the ads are printed paper now, see below): every brand is lit, in three kinds (`STYLES` in make_textures.py): LIGHTBOX (backlit acrylic), NEON
  (tube letters on a weathered panel), LED (pixel panel). Billboards emit 1.35 / 1.9 / 1.4, the arches' LED faces 1.35,
  the walls' light boxes 0.95, the tubes 0.62: the bloom threshold is 1.05, so the neon words glow and nothing else floods.
  Three boards glitch (`board_*_flk`). The arches carry a corporate neon bar in the brand's colour.
- **Craft**: duller paint, the clear coat worn thin, liveries and hull decals with chips, scratches and grime.
- **Game** (index.html): a dusty evening sky (slate, a brown-amber band), grey-brown cloud undersides, a sodium-warm
  key light, bloom 0.6 / radius 0.4 / threshold 1.05, a grade pass (desaturates the tired city but not the lit signs,
  warm, dust haze, lifted blacks, vignette, grain), `flickTick` for the failing tubes and glitching signs. The HUD is
  municipal equipment: sodium amber, tube white, worn red, scratched plates; the weapon slot moved under the lap box
  (at the top centre it hid the gantry sign). The hangar and the showroom are a depot: oil-stained concrete, a sodium
  work lamp, a tube behind; only the team rings keep their colour.

### Politics, 2097: the eight Riksdag parties
Satire of power, all eight treated alike: **exactly two neon billboards each** (dealt out evenly round the lap by
build.py; the build log prints the count) and **one poster each** on the poster wall. Parody names in the brand manner,
party colours, no party logos or symbols, no politicians, never a word about any group of people. Direktdemokraterna
and parties outside the Riksdag are not included (Kim's call).

| Parody | Party | Slogan |
|---|---|---|
| SOCIÅLDEMOKRATERNA | S | ALLA SKA MED. / FRIVILLIGT ELLER EJ. |
| MODERÅTERNA | M | SÄNKT SKATT. / HÖJD KONTROLL. |
| SVERIGEDEMOKRÄTERNA | SD | SVERIGE TILLBAKA. / TILL 1952. |
| CENTERPÅRTIET | C | GRÖN TILLVÄXT. / BARA TILLVÄXT. |
| VÄNSTERPÅRTIET | V | MAKTEN ÅT FOLKET. / FOLKET ÅT PARTIET. |
| KRISTDEMOKRÄTERNA | KD | TRYGGA FAMILJER. / ÖVERVAKADE FAMILJER. |
| LIBERÅLERNA | L | FRIHET. / MED PRENUMERATION. |
| MILJÖPÅRTIET | MP | KLIMATNEUTRALT. / ENLIGT OSS. |

(`PARTIES` in make_textures.py.)

## Two themes in one build (Kim, 2026-09-29): TITLE → THEME → CRAFT → go
"i början av spelet får man välja theme (neon eller used) och sen får man välja skepp och sen är det go time."

- The first screen (`#themesel` in index.html) picks **NEON** or **USED**; the choice is remembered (`localStorage.swTheme`).
  The theme is settled with a top-level `await` before anything is built, because the sky and fog colours compile into
  every shader, and only that theme's glbs are downloaded. `?theme=neon|used` skips the screen; `?check` uses the
  remembered one. The preview images are `wo2097/assets/theme_neon.jpg` and `theme_used.jpg` (Skeppsbron, from the game).
- `TH` in index.html holds everything that differs: bloom, sky, cloud shade, flare tints, sun and hemisphere light,
  grade pass (used only), engine light (used 0.5, neon 1.0), countdown light level, HUD canvas colours and the hangar.
  The HUD CSS for neon is `body.theme-neon` and restores b08a156 exactly (the weapon slot at the top centre included).
  The tiles, the track line (`assets/track.json`) and the physics are shared.
- Assets: `wo2097/assets/neon/` (track 3.6 MB + craft 1.2 MB) and `wo2097/assets/used/` (track 10.8 MB + craft 1.3 MB).
  NEON is built by the snapshot in `pipeline/neon/` (the b08a156 scripts with their paths moved; it rebuilds track.glb
  byte for byte), USED by `pipeline/`:

      cd wo2097/pipeline/neon && python3 make_textures.py && blender -b --factory-startup -P build.py && blender -b --factory-startup -P build_craft.py
      cd wo2097/pipeline      && python3 make_textures.py && blender -b --factory-startup -P build.py && blender -b --factory-startup -P build_craft.py

- The effect and audio flags above are the same in both themes (all off).
- Checks take the theme: `THEME=neon node check_lap.cjs out/` and `THEME=neon node perf.cjs 30`.
- The showroom follows the theme too: `wo2097/showroom.html?theme=neon`.

## USED: the ads are printed paper (replaces the light boxes above)
"jag tror vi bara kan köra pappersannonstavlor i used universe, dvs som dom i neonversionen men papper." Every ad,
corporate and party, is a matte printed paper poster in the neon version's layout and size (billboards 1024 × 512 with
the slogan at min 112 px, walls with the neon version's cell sizes, arches and gantry as printed banners). No neon, no
light boxes, no LED. The print is crisp; the wear is on the paper's edges, tape at its corners, the board and the wall.
Lighting: the tubes light the walls (`barrier_*` emission 0.5 of the whole wall), and every board has two worn
floodlights on arms (`lamp_flood`); their warm light is the paper's emission (0.55, under the bloom threshold 1.25).
Checked at race speed against the neon version at the same three points and on two party boards.

## Ads never break (2026-09-29)
Kim saw boards with the left half of the slogan missing ("…RSENAT / …N 1997"). Root cause: the ad faces sat 1–2 cm in
front of their frames, but the set-piece meshes span the whole ~4 km lap and Draco quantised positions to 16 bits of
that extent (about 6 cm a step). Corners snapped behind the frame and one triangle of the quad vanished. Measured in
Blender on the decoded glbs: 51 of 114 ad quads (used) and 46 of 116 (neon) had a corner in or behind the frame, as far
as 5.8 / 8.8 cm. Fix: positions at 20 bits (~4 mm), faces 8 cm proud of their frames (boards, arches, gantry, both
themes), and in the game every ad material gets polygonOffset. After: 0 of 116, the smallest gap 7.6 cm.
Ads also mark themselves in the scene target's alpha (0.25, `markAd` in index.html) so the speed blur and the boost
colour split skip the letters (`MotionPass` reads `tMark`).

## Faux party logos (faux_logos.py)
Every party board and poster (USED; the NEON theme is the b08a156 snapshot and carries no party ads) has a new mark
that evokes the party with a 2097 twist, never the real logo, no text, no real people, the same size for all eight:
S a rose in a camera iris with a barbed-wire stem · M a padlock whose shackle is an M · SD a flower sealed in a snow
globe · C a four-leaf clover with a barcode and a smokestack stem · V a fist gripping a remote control ·
KD a faceless family inside a CCTV housing · L a torch with a price tag (¤) · MP a dandelion whose seeds are drones.

## Mobile landscape (2026-09-29)
A touch-first phone (`pointer:coarse` and a short side ≤ 1000 px, or `?mobile`) gets `body.mobile`: everything else is
desktop as before. Portrait shows a "VÄND TELEFONEN" veil. Controls (Pointer Events, real multi-touch): the left thumb
steers on an analog pad (`TOUCH.steer`), with AB L / AB R over it; the right thumb has GAS, BRAKE, TURBO and FIRE; PAUSE
and TILT sit under the position box. Buttons press the same keys as the keyboard. TILT steers by tipping the phone
(DeviceMotion; iOS asks permission and only over HTTPS). Haptics via `navigator.vibrate` where it exists (not iOS).
Menus: swipe between themes and craft, tap to confirm; the first tap unlocks audio. The HUD shrinks into the safe area.
Render profile on phones: pixel ratio ≤ 1.5, MSAA 2, tiles errorTarget 20 and a tile cache of about 180–250 MB
(`lruCache` bytes, iOS kills tabs at ~1–1.5 GB), no speed blur, no god rays, bloom at quarter resolution.
`manifest.webmanifest` + apple meta: "Add to Home Screen" runs full screen in landscape.
Checked in Playwright emulation (iPhone 15 Pro and Pixel 8, landscape): a full lap driven with the touch pad and GAS only
(147 s, no errors), swipes, taps, pause, the portrait veil; desktop check_lap still passes in both themes.


## Grepp hårt: fri styrning (bara `?grepp=hart`, dold utvecklarflagga)

**2026-09-30:** Kim valde rälsen som spelet. G-växeln och det sparade valet är borttagna; fri styrning finns bara bakom flaggan.

Normalläget är den gamla rälsen: skeppet följer banans riktning och styrningen flyttar det bara i sidled. På det här varvet
(minsta radie 120 m) biter greppgränsen aldrig, så man behöver inte styra. **Grepp hårt** ger spelaren en egen kurs:
psi är vinkeln mellan skeppet och banans tangent, `t += v·cos psi`, `lat += v·sin psi`, och banan vrider sig under skeppet
(`psi' = omega + krökning·v − 0,25·psi`). Släpper man spaken i en kurva i full fart når man ytterväggen på 0,7–1,2 s
(uppmätt i kurvor på 160, 200 och 300 m). Greppet begränsar hur snävt man kan svänga (`k/v` rad/s, k = 40), luftbromsarna
ger extra gir och broms och lyfter taket 1,35 gånger. Väggen: rakt in studsar och kostar fart och sköld, snett glider längs.
Kameran följer skeppets riktiga kurs till 70 %. AI:n går kvar på räls men bromsar för samma snävare kurvor.
Konstanterna står i `FS` i index.html. `check_lap.cjs` tar `GREPP=hart` och kör då en styrande bot.

**HARD_EASE (2026-09-29):** en ratt i index.html för hur förlåtande hårt grepp är (0 = första versionen, 1 = mycket förlåtande, default 0,5). Den ger styrhjälp (skeppet tar 0,8·HARD_EASE av kurvan) och höjer grepptaket k = 40 + 12·HARD_EASE. Med 0,5: släppt spak når väggen på 0,88/1,08/1,77 s i 160/200/300 m-kurvor (var 0,68/0,88/1,23). Självrätningen (FS.align) höjdes först men bet inte i den farten.
