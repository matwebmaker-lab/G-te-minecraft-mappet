"""Kjører alle ressursgeneratorene i riktig rekkefølge.

    python verktoy/bygg_ressurser.py

1. teksturer.py         – blokk-/gjenstand-/rustningsteksturer
2. ekstra_teksturer.py  – egg, effektikon, ikoner fra Blender
3. data.py              – all JSON (assets + data, inkl. dimensjonene)
4. vaapen3d.py          – 3D-våpenmodeller og teksturatlas (etter data.py, som tømmer modellmappa)
5. strukturer.py        – NBT-strukturer, strukturdefinisjoner og kiste-loot
"""
import runpy
from pathlib import Path

HER = Path(__file__).resolve().parent
for skript in ("teksturer.py", "ekstra_teksturer.py", "data.py", "vaapen3d.py", "strukturer.py"):
    print(f"--- {skript}")
    runpy.run_path(str(HER / skript), run_name="__main__")
