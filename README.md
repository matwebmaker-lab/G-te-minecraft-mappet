# Dødsfjellet

Et Minecraft-kart med et gigantisk felle-fangehull, en egen mod med en ny dimensjon, vakter som oppfører seg som spillere,
oppgraderbare våpen og rustning, evner – og en PvP-øvingsverden. Alt på norsk, alt i samme mørke stemning.

**Versjon:** Minecraft **26.3** · Fabric Loader 0.19.5 · Fabric API 0.161.0+26.3 · Java 25
(Mappa `dodsfjellet-mod/` og 1.21.1-generatorene er den eldre versjonen for Minecraft 1.21.1.)

## Innhold

| Del | Hva |
|---|---|
| **Dødstrappa** (`generer_datapack.py`) | Den "helt trygge" trappa inn i fjellet – fire dødelige feller og en falsk skatt |
| **Dødsfjellet** (`generer_dodsfjellet.py` → `verktoy_port26.py` → `generer_dodsfjellet_26.py`) | Fangehull i fem etasjer: gåtehall, lavasjø, labyrint, vannkammer, warden-hule, arena, lysgåte, usynlig bro, tallgåte, bølgegulv, kodelås og skattkammer med bossen Skattevokteren. Inngangen lukker seg bak dere, dør noen starter alt på nytt, og admin-kontrollrommet (`/function df:admin`) følger med på spillerne |
| **PvP-øya** (`generer_pvp.py`) | Egen dimensjon: duell-arena med kits, bot-trening, buebane, bridge med tidtaking, MLG-tårn, parkour, alle-mot-alle |
| **Modden** (`dodsfjellet-mod-26/`) | Dødsriket-dimensjonen, vakter, våpen, rustning, oppgraderingssmia, runer, dødsnøkkel og reisekompass |

### Modden

- **Dødsriket** – ny dimensjon med evig lilla skumring, lavahav, fem biomer (Askeødet, Dødsskogen, Krystallmarkene,
  Blodmyra, Dødsgrotta) og strukturer som genereres naturlig: **Dødslandsbyen**, **Dødsgrotta**, **Bentårnet**, **Sjelealteret**.
  Kom dit med **Dødsnøkkelen** (ligger i skattkammeret) eller reisemenyen.
- **Vakter** som ser ut og oppfører seg som spillere: spillernavn, skins, sprint, hopp-krit, strafing, bue på avstand,
  gulleple, chat ("ez", "gg"). Kan også være allierte Åndevakter.
- **Våpen** (3D-modeller laget i Blender): Sjelesigden, Dødsklingen, Vokterknuseren, Skyggedolken.
- **Rustning**: Fjellvokter og Sjeleplate – fullt sett gir bonuser.
- **Oppgraderingssmia**: oppgrader våpen og rustning til +10 med dødskrystaller – sterkere enn spillet ellers tillater
  (Skarphet X, Beskyttelse X, ekstra liv). +5 våpen: livstyveri. +10 våpen: Dødsstøt. Rustning sum +20: fart, +40: Udødelighet.
- **Runer (evner)**: Skyggesprang, Sjeleskjold, Dødsnova, Blodhøst, Åndesprang, Vokterkall.
- **Reisekompass / `/reise`**: klikkbar meny som teleporterer alle spillere (også ikke-op) til Dødsfjellet, Dødsriket og PvP-øya.
- Egne teksturer for alle blokker og gjenstander (prosedyrisk pikselkunst, `verktoy/teksturer.py`).

## Bygge

```bash
# ressurser (teksturer, JSON, 3D-våpen, strukturer)
python dodsfjellet-mod-26/verktoy/bygg_ressurser.py
# modden (JAVA_HOME = JDK 25)
cd dodsfjellet-mod-26 && ./gradlew build          # -> build/libs/dodsfjellet-2.0.0.jar
# datapackene
python generer_datapack.py
python verktoy_port26.py && python generer_dodsfjellet_26.py
python generer_pvp.py
```

Verdenen bygges i spillet med `/function dt:bygg` (som en byggmester som ser østover på -892 128 452),
`/function df:bygg` og `/function pvp:bygg` (seed 8675309).

## Installere (for spillere)

Last ned fra **[Releases](https://github.com/matwebmaker-lab/G-te-minecraft-mappet/releases/latest)**:

| Fil | Hvem trenger den |
|---|---|
| `dodsfjellet-2.0.0.jar` | **Alle** som skal spille (verten og alle vennene) |
| `Dodsfjellet-verden-26.3.zip` | Bare **verten** (den som åpner verdenen) |

**Alle:**
1. CurseForge → **Create Custom Profile** → Minecraft **26.3** → **Fabric**.
2. *Add More Content* → legg til **Fabric API** og **Essential Mod**.
3. Høyreklikk profilen → **Open Folder** → legg `dodsfjellet-2.0.0.jar` i mappa `mods`.

**Verten i tillegg:**

4. Pakk ut `Dodsfjellet-verden-26.3.zip` i mappa `saves` (så det blir `saves/Dodsfjellet/level.dat`).
5. Start → **Singleplayer** → **Dødsfjellet** → `Esc` → **Invite** (Essential) for å invitere vennene.

Skriv `/reise` (eller høyreklikk Reisekompasset) for å reise mellom Dødsfjellet, Dødsriket og PvP-øya.
Verten kan følge med fra kontrollrommet med `/function df:admin`.
