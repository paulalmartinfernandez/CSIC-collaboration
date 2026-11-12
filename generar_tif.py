import mrcfile, tifffile, numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent        # carpeta Proyecto
DS = BASE / "datasets_publicos" / "sample_dataset2"
TOMO = DS / "25oct20a_Position_10.mrc"
MASK = DS / "mascara_anotaciones.tif"
OUT = BASE / "datasets_publicos" / "sample_dataset2"
NZ, NY, NX = 64, 512, 512

mask = tifffile.imread(MASK)                       # (z, y, x) uint8

# Busca la ventana con más partículas, en resolución gruesa (1/4)
g = mask[::4, ::4, ::4] > 0
wz, wy, wx = NZ // 4, NY // 4, NX // 4
mejor, pos = -1, None
for z in range(0, g.shape[0] - wz + 1, 4):
    for y in range(0, g.shape[1] - wy + 1, 8):
        for x in range(0, g.shape[2] - wx + 1, 8):
            n = np.count_nonzero(g[z:z + wz, y:y + wy, x:x + wx])
            if n > mejor:
                mejor, pos = n, (z * 4, y * 4, x * 4)
z0, y0, x0 = pos
print("ventana elegida (z0,y0,x0):", pos)

# Recorte del tomograma, reescalado a uint8 con percentiles
with mrcfile.mmap(TOMO, permissive=True) as m:
    vol = np.array(m.data[z0:z0 + NZ, y0:y0 + NY, x0:x0 + NX], dtype=np.float32)
lo, hi = np.percentile(vol, [1, 99])
vol8 = (np.clip((vol - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)

tifffile.imwrite(OUT / "crop_volumen.tif", vol8)
tifffile.imwrite(OUT / "crop_clases.tif", mask[z0:z0 + NZ, y0:y0 + NY, x0:x0 + NX])
print("guardados:", vol8.shape, np.bincount(mask[z0:z0 + NZ, y0:y0 + NY, x0:x0 + NX].ravel()))