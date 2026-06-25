"""
preset_loader.py — Carga presets desde múltiples archivos `presets_*.json`.

Permite tener 1 archivo por personaje (presets_P0004.json, ...) en vez de un
`presets.json` monolítico. `lists.json` queda como archivo compartido aparte.
"""
import os
import re
import json
import glob as _glob


def load_all_presets(presets_dir):
    """Mergea todos los `presets_*.json` del dir (orden estable), excluyendo
    lists.json y backups. `presets_general.json` se carga al final para que los
    presets sin personaje no pisen a los específicos. Devuelve un dict."""
    merged = {}
    files = sorted(
        f for f in _glob.glob(os.path.join(presets_dir, "presets_*.json"))
        if ".bak" not in os.path.basename(f)
        and not f.endswith("presets_general.json")
    )
    general = os.path.join(presets_dir, "presets_general.json")
    if os.path.isfile(general):
        files.append(general)

    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[just-nodes] ERROR leyendo {os.path.basename(fp)}: {e}")
            continue
        for k, v in data.items():
            if k in merged:
                print(f"[just-nodes] WARNING preset duplicado '{k}' ({os.path.basename(fp)})")
            merged[k] = v
    return merged


def migrate_presets_to_split_files(presets_dir):
    """Parte un `presets.json` monolítico en `presets_{P_ID}.json` +
    `presets_general.json` (presets sin P_ID). Hace backup y renombra el original.
    No corre si ya no hay presets.json (idempotente)."""
    import shutil
    src = os.path.join(presets_dir, "presets.json")
    if not os.path.isfile(src):
        print("[migrate] no hay presets.json — nada que partir")
        return
    with open(src, "r", encoding="utf-8") as f:
        presets = json.load(f)

    by_id, general = {}, {}
    for k, v in presets.items():
        m = re.search(r"\|\s*(P\d{3,4})\s*\|", k)
        (by_id.setdefault(m.group(1), {}) if m else general)[k] = v

    shutil.copy(src, src + ".bak-presplit")
    for pid in sorted(by_id):
        with open(os.path.join(presets_dir, f"presets_{pid}.json"), "w", encoding="utf-8") as f:
            json.dump(by_id[pid], f, indent=2, ensure_ascii=False)
        print(f"[migrate] presets_{pid}.json ({len(by_id[pid])} presets)")
    if general:
        with open(os.path.join(presets_dir, "presets_general.json"), "w", encoding="utf-8") as f:
            json.dump(general, f, indent=2, ensure_ascii=False)
        print(f"[migrate] presets_general.json ({len(general)} presets)")
    os.rename(src, src + ".old-monolitico")
    print("[migrate] presets.json -> presets.json.old-monolitico")
