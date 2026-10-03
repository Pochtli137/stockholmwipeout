# WIPEOUT KULTURSTOCKHOLM · koncept

Andra banan i samma spel, på Googles riktiga 3D-Stockholm, en sommareftermiddag år 2097. Kulturetablissemanget kör hemma:
samma anti-grav-liga, samma räls, men allt är omklätt. Rutt, farkoster, förmåner, annonser, ljus och HUD-texter.
Satiren är GTA-skarp mot typer och institutioner, aldrig mot verkliga personer, och på krogarna mot gästerna, aldrig mot
verksamheten. Inga partiannonser på den här banan.

**All text ligger i en fil:** `wo2097/assets/kultur/copy.json`. Spelet läser den direkt (titel, HUD, lag, förmåner,
depåer, ENTERING, resultat, upplåsning). Skyltar, vepor, väggar och plattor bakas ur samma fil med
`wo2097/pipeline/kultur/build.sh`. Kim kan skriva om allt där utan att röra koden.

## Rutten: 8,2 km, ett varv, cirka 110 s

Ett varv som vänder runt Saltsjön, laddat med landmärken, med start och mål vid **Börshuset på Stortorget**, Akademiens hem.
Linjen är handlagd i stora bågar (minsta radie 132 m, regeln är 120 m), går runt Tyska kyrkans och Klara kyrkas torn och kalibreras mot gatan och taken av samma dump som
Stockholmsbanan. Ingen Västerbron.

| m | Plats | Vad som händer |
|---|---|---|
| 0 | Börshuset, Stortorget | start under portalen *Kulturstockholms stora pris* |
| 150 | Gamla stan söderut | över taknockarna; Den Gyldene Freden till vänster, privat depå för DE ADERTON |
| 550 | Slussen, Gondolen | kurvan ut mot Stadsgårdskajen |
| 1 300 | Fotografiska | kajen, sedan fall ut över Saltsjön |
| 2 050 | af Chapman, Moderna museet | Skeppsholmen |
| 3 050 | Gröna Lund | över vattnet från Skeppsholmen, fall mot Djurgårdsbrunnsviken |
| 3 400 | Skansen, Hasselbacken | uppför berget, krön |
| 4 250 | Nordiska museet, Vasamuseet | Djurgården norrut |
| 4 970 | Strandvägen | raka sträckan mot Nybroviken |
| 5 340 | Nybroplan, Dramaten, Teatergrillen, Berns | **PITSTOP RICHE** längs kanten |
| 5 790 | Nationalmuseum | Blasieholmen, fall mot Strömmen |
| 6 240 | Kungliga Operan, Operakällaren | Strömkajen |
| 6 670 | Kulturhuset, Sergels torg | krön över plattan |
| 7 430 | Stadshuset | Nobelmiddagen; fall ut över Riddarfjärden |
| 8 010 | Riddarholmen | tillbaka till Stortorget |

Mariatorget och Vasamuseets entré ligger utanför linjen (650 m och 230 m). Jag valde flöde före fullständighet.

**Fall och krön:** Saltsjön efter Fotografiska, vattnet mot Gröna Lund, Nybroviken, Strömmen vid Nationalmuseum och
Riddarfjärden efter Stadshuset. Krön över Skansen, Strandvägen och Sergels torg.

## Farkosterna: sex lag, sex egna Blender-farkoster

| # | Lag | Farkost | Slogan | Roll |
|---|---|---|---|---|
| 0 | **DE ADERTON** | flygande mahognykammare, arton numrerade stolar, förgylld krona | VI HAR SUTTIT HÄR SEDAN 1786. | **bossen**: fart och anseende, och som AI snabbare än alla |
| 1 | SOMMARPRATARNA | rörradio i valnöt med tyghögtalare, skalratt, antenn | NITTIO MINUTER OM MIG. SEN DIG. | dragkraft |
| 2 | KULTURSIDAN | vikt broadsheet med recensionsvingar och en röd penna | VI TYCKER. DU KÖR. | snabb, sågningarna kommer till den |
| 3 | NATURVINSBAREN | liggande amfora med kork och orange bränsle | OFILTRERAT. OFÖRSÄKRAT. | väghållning |
| 4 | VERNISSAGEN | vit kub med takskenor och en osåld tavla | FRI ENTRÉ. DYR ÅSIKT. | toppfart, skör |
| 5 | STIPENDIATERNA | trave ansökningar med gem och avslagsstämplar | SÖKT FYRTIOEN GÅNGER. FÅTT NOLL. | balanserad |

Förarna heter efter typer: STOL 18, SOMMARRÖSTEN, RECENSENTEN, SOMMELIEREN, KURATORN, SÖKANDEN. Inga verkliga personer.
Statistiken återanvänder Stockholmsbanans balans; bara DE ADERTON är starkare.

## Förmånerna: samma mekanik, nya namn

| Mekanik | Kulturstockholm | Ser ut som |
|---|---|---|
| Turbo | **STIPENDIUM** | ett förseglat kuvert som brister i guld |
| Sköld | **LIVSTIDSSTOL** | ett förgyllt fält, stolen ingen kan ta |
| Missil | **SÅGNING** | en röd recension som flyger, träffen blinkar DU BLEV SÅGAD |

Spelet har inga minor, så REPLIK blir inget eget vapen. Hämtplattorna heter *FÖRMÅN · BEVILJAS AV NÄMND*, fartplattorna
*KULTURBIDRAG · BETALAS ALDRIG TILLBAKA*. HUD:en: AKT, PLACERING, FÖRMÅN, STIPENDIUM, ANSEENDE, och latin i stället för runor
(ACTUS, LOCUS, BENEFICIUM).

## Depåerna och krogarna

- **PITSTOP RICHE** vid Nybroplan: en markerad fil längs kanten under en markis. Styr in i den och anseendet (sköldenergin)
  fylls på medan farten hålls nere; ut igen och du är tillbaka. Flash in: *PITSTOP RICHE · ANSEENDET FYLLS PÅ*, ut:
  *SEDD AV RÄTT BORD · TILLBAKA I LOPPET*. AI:n svänger in ibland.
- **DEN GYLDENE FREDEN** i Gamla stan, Akademiens krog: en privat fil med skylten **ENDAST DE ADERTON**. Bara DE ADERTON
  fylls på där; alla andra får *FÖRSÖK IGEN OM 200 ÅR*.
- Skyltar längs linjen, i egen typografi, skämten riktade mot gästerna: **Gondolen** (UTSIKT ÖVER DEM SOM INTE FICK BORD),
  **Operakällaren** (NOTAN TAR NÅGON ANNAN), **Teatergrillen** (EFTER PREMIÄREN BÖRJAR PREMIÄREN), **Berns** (DU VAR INTE HÄR.
  ALLA SÅG DIG.), **Hasselbacken** (LUNCH FÖR DEM SOM ÄR LEDIGA). Sturehof, Prinsen, KB och Pelikan ligger för långt från linjen.

## Annonsernas look and feel

Ingen neonkorporatism. Kultureliten 2097: seriffer (Playfair Display, DM Serif Display) och Inter, allt OFL och inbäddat;
gräddvitt papper och linne, galleriets väggetiketter, festivalvepor, skandinavisk minimalism, pasteller, guld i stället för
neon. Annonserna läses i full fart i sol: två korta rader, cirka 1 m höga bokstäver, mörk text på ljust eller tvärtom, aldrig
under 112 px på en 1024 px skylt. Exempel ur `copy.json`:

- HEMNÄT · 3 ROK SÖDER. 19 MKR. EJ SJÄL.
- KULTURRÅDET 2097 · STIPENDIUM FÖR REDAN KÄNDA
- SOMMAR I P1+ · MIN BARNDOM. DIN SEMESTER.
- SKANSÉN · SE EN RIKTIG STOCKHOLMARE.
- LOKALBEFOLKNINGEN™ · VISAS VARDAGAR. MATA EJ.
- NÄSTA AVGÅNG: ÖSTERLEN · SLUTSÅLD.
- NOBELMIDDAGEN · 1300 KUVERT. NOLL FÖR DIG.
- KONSTRUNDAN · KÖP KONST. KÖP RÄTT ÅSIKT.

26 skyltar, fem vepor över banan, portalen vid Börshuset och åtta galleriväggetiketter på barriärerna
(*OBETITLAD (STOCKHOLMARE), 2097 · OLJA PÅ ARV · PRIS PÅ BEGÄRAN*).

**ENTERING:** Gamla stan (BEFOLKNING 3 000 · KÖANDE 3 000 000), Södermalm, Skeppsholmen, Djurgården (KULTURARV, NU MED ENTRÉ),
Östermalm, Norrmalm, Kungsholmen (STADSHUSET · NOBELMIDDAG, EJ FÖR DIG).

## Ljuset

Sommareftermiddag: solen i sydväst, 42 grader upp, blå himmel med vita cumulus, varmt ljus. En graderingspass ger kontrast,
lite värme och mättnad, så att staden inte ser ut som testsidans platta karta, och vattnet glittrar där solen speglas.
Bloom bara för guld och glas. Skyltarna hålls under bloomtröskeln så att de aldrig smetar ut i solen.

## Flödet

Titel *WIPEOUT KULTURSTOCKHOLM* med S:t Erik och kreditraden kvar, en vit galleri-hangar med de nya farkosterna, loppet.
Upplåsningen sitter på Stockholmsbanans RACE COMPLETE: *DU HAR LÅST UPP WIPEOUT KULTURSTOCKHOLM · KLICKA HÄR* (K), sparas i
localStorage och laddar `?bana=kultur`. Kulturstockholms resultat har en länk tillbaka till Stockholm (S).
Stockholmsbanan ska bete sig exakt som nu; check_lap körs före och efter.

## Musiken (2026-10-03)

Högkulturens kanon i full fart: Vivaldis *Sommaren*, tredje satsen (Presto, sommarstormen), i John Harrisons livetagning med
Wichita State University Chamber Players, lagd på rakt tempo med spelets egna big beat-trummor under. Stormen ensam i fyra takter
vid RIDÅ, trumvirvel i fermaten, sedan drop. Nedräkningen är tyst, som salongen före ridån. Inspelningen är CC BY-SA och krediteras
på titeln. Provsidan med alternativen (orörd Presto, Bachs Brandenburgkonsert nr 3) ligger i `kultur/musikprov/`.
