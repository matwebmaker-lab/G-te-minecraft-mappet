"""Kjører alle ressursgeneratorene i riktig rekkefølge.

    python verktoy/bygg_ressurser.py

1. teksturer.py         – blokk-/gjenstand-/rustningsteksturer
2. ekstra_teksturer.py  – egg, effektikon, ikoner fra Blender
3. data.py              – all JSON (assets + data, inkl. dimensjonene)
4. vaapen3d.py          – 3D-våpenmodeller og teksturatlas (etter data.py, som tømmer modellmappa)
5. gevaer3d.py        – geværmodellene (Blender-ikonene lages med blender_gevaer.py via Blender MCP)
6. lyder.py           – syntetiserte gevær-lyder (.ogg via ffmpeg)
7. strukturer.py        – NBT-strukturer, strukturdefinisjoner og kiste-loot
8. grafikk.py         – den lyse grafikkpakken og biomfargene (etter data.py, som tømmer data/minecraft)
"""
import runpy
from pathlib import Path

HER = Path(__file__).resolve().parent
for skript in ("teksturer.py", "ekstra_teksturer.py", "glede_teksturer.py", "data.py", "vaapen3d.py", "gevaer3d.py", "lyder.py", "strukturer.py", "grafikk.py"):
    print(f"--- {skript}")
    runpy.run_path(str(HER / skript), run_name="__main__")
