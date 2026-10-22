# functions.py
from pathlib import Path
import numpy as np
import mrcfile, tifffile as tiff
import napari

def cargar_mrc(ruta):
    """Devuelve (volumen, voxel_size)."""
    with mrcfile.mmap(ruta, permissive=True) as m:
        tomo = np.asarray(m.data)
        vox = m.voxel_size
    return tomo, vox

def cargar_etiquetas(ruta, forma_esperada):
    """Lee un .tif de anotaciones y avisa si su forma no coincide con el tomograma."""
    etiquetas_validas = []
    for f in sorted(Path(ruta).glob("annotations*.tif")):
        a = tiff.imread(f)
        if a.shape != forma_esperada:
            print(f"{f.name}: shape {a.shape} ≠ tomograma {forma_esperada}, la salto")
            continue
        else: 
            etiquetas_validas.append(a)
            
    return etiquetas_validas

def contraste(volumen, percentiles=(1, 99), paso = 4):
    """Devuelve (lo, hi) calculados sobre una versión submuestreada."""
    lo, hi = np.percentile(volumen[::paso, ::paso, ::paso], percentiles)
    return lo, hi

def mostrar(volumen, lo, hi, etiquetas=None, ndisplay=3, escala=None):
    """Abre napari con el volumen y, si hay, las etiquetas encima."""
    viewer = napari.Viewer(ndisplay=ndisplay)     # arranca ya en modo 3D
    viewer.add_image(volumen, name="tomograma", contrast_limits=(lo, hi), colormap="gray", rendering="attenuated_mip", scale = escala)
    if etiquetas:
        for i, a in enumerate(etiquetas):
                mascara = (a < a.max() - 1e-6).astype(np.uint8)
                viewer.add_labels(mascara, name=f"etiqueta_{i}", opacity=0.5, scale=escala)
    return viewer



if __name__ == "__main__":
    DATOS = Path(r"C:\Users\pauum\Desktop\PAULA\uni\MASTER\TFM\CRYOEM\Proyecto\datos")

    ruta_mrc = next(DATOS.glob("*.mrc"), None)
    if ruta_mrc is None:
        raise SystemExit(f"No hay ningún .mrc en {DATOS}")

    tomo, vox = cargar_mrc(ruta_mrc)
    print(f"{ruta_mrc.name}: shape={tomo.shape} dtype={tomo.dtype} vóxel(Å)={vox.x:.2f}")

    etiquetas = cargar_etiquetas(DATOS, tomo.shape)
    print(f"Etiquetas válidas: {len(etiquetas)}")

    lo, hi = contraste(tomo)
    print(f"Contraste: lo={lo:.4g} hi={hi:.4g}")

    escala = (vox.z, vox.y, vox.x)       # el array es (z, y, x); mrcfile da (x, y, z)
    viewer = mostrar(tomo, lo, hi, etiquetas, ndisplay=3, escala=escala)
    napari.run()