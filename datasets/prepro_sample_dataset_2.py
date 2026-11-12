import json
from pathlib import Path

import mrcfile
import numpy as np
import tifffile

# --- Ajusta estas rutas ---
TOMO = Path("../datasets_publicos/sample_dataset2/25oct20a_Position_10.mrc")
CARPETA = Path("../datasets_publicos/sample_dataset2/annotations")
ARCHIVOS = {   # etiqueta: (archivo, radio aproximado en Å)
    1: (CARPETA / "pseudomonas_phage_pp7_vlp-1.0_orientedpoint.ndjson", 140),
    2: (CARPETA / "chaperonin_groel-1.0_orientedpoint_GT.ndjson", 75),
}
SALIDA = CARPETA.parent / "mascara_anotaciones.tif"
EN_ANGSTROM = False   # True si las coordenadas no caben en el tomograma

# --- Cabecera del tomograma (sin cargar el volumen) ---
with mrcfile.mmap(TOMO, permissive=True) as m:
    SHAPE = m.data.shape                 # (z, y, x)
    voxel = float(m.voxel_size.x)        # Å por vóxel
print("forma (z,y,x):", SHAPE, "| vóxel:", voxel, "Å")

# --- Máscara ---
mask = np.zeros(SHAPE, dtype=np.uint8)
for etiqueta, (ruta, radio_A) in ARCHIVOS.items():
    r = int(round(radio_A / voxel))
    pts = []
    with open(ruta) as f:
        for linea in f:
            if not linea.strip():
                continue
            loc = json.loads(linea)["location"]
            x, y, z = loc["x"], loc["y"], loc["z"]
            if EN_ANGSTROM:
                x, y, z = x / voxel, y / voxel, z / voxel
            pts.append((x, y, z))
            z0, z1 = max(int(z) - r, 0), min(int(z) + r + 1, SHAPE[0])
            y0, y1 = max(int(y) - r, 0), min(int(y) + r + 1, SHAPE[1])
            x0, x1 = max(int(x) - r, 0), min(int(x) + r + 1, SHAPE[2])
            if z1 <= z0 or y1 <= y0 or x1 <= x0:
                continue
            zz, yy, xx = np.ogrid[z0:z1, y0:y1, x0:x1]
            esfera = (zz - z) ** 2 + (yy - y) ** 2 + (xx - x) ** 2 <= r ** 2
            mask[z0:z1, y0:y1, x0:x1][esfera] = etiqueta
    p = np.array(pts)
    print(f"etiqueta {etiqueta}: {len(p)} puntos | radio {r} vox | máx x,y,z = {p.max(axis=0).round(0)}")

print("vóxeles por etiqueta:", np.bincount(mask.ravel()))
tifffile.imwrite(SALIDA, mask)
print("guardado en", SALIDA)