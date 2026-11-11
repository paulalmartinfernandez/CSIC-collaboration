# Anotaciones del dataset 10490

## Contexto

No se pueden hacer pruebas con el notebook original de `vjepa2_encoding.ipynb` porque se basa en la existencia de ficheros de formato **TIFF**. Previamente se necesita ejecutar otro fichero:
`align_tif_to_mrc.py` que se escribió para alinear anotaciones en formato **TIFF** (`.tif`) con un tomograma `.mrc`: buscaba por correlación cruzada en qué posición (z, y, x) encaja cada volumen y luego los fusionaba en un único volumen (`output/merged_from_annotations.tif` y `output/merged_from_annotations_classes.tif`).

## Formato del dataset 10490

El tomograma es `datasets_publicos/10490/sample_1_10490.mrc`. Las anotaciones están en `datasets_publicos/10490/annotations/` y **no vienen en `.tif`**. Contenido de la carpeta:

| Extensión | Nº de ficheros | Qué es |
|-----------|----------------|--------|
| `.mrc`    | 102 | Máscaras de segmentación 3D, una por complejo |
| `.zarr`   | 102 | Las mismas máscaras en formato zarr |
| `.json`   | 100 | Metadatos |
| `.ndjson` | 97  | Puntos / anotaciones en formato ndjson |

Cada complejo tiene su propio fichero, con el tipo de máscara en el nombre:

- `<complejo>-1.0_instancesegmentationmask`: máscara de instancias.
- `<complejo>-1.0_segmentationmask`: máscara binaria (p. ej. `actin_filament`).

## Por qué no funciona el script de align

El script busca `*.tif` (`TIF_PATTERN = "*.tif"`) y en esta carpeta no hay ninguno.

Además, el script asume pocos volúmenes TIFF que se fusionan en uno. Aquí hay ~100 máscaras `.mrc` independientes (más sus equivalentes `.zarr`), con varias variantes por complejo, así que el merge no tiene el mismo sentido: mezclaría variantes y generaría un volumen de clases con unos 100 valores.

## Por qué no se puede usar el notebook original `vjepa2_encoding.ipynb`

El notebook codifica un volumen con V-JEPA 2 (`facebook/vjepa2-vitg-fpc64-384`, cortes en z como frames de un vídeo) y luego hace UMAP y una segmentación de una sola clase con Normalized Cut (NCut) usando prioris del ground truth. Con este dataset no se puede usar tal cual por lo siguiente:

1. **Depende de ficheros que no se pueden generar.** Lee `output/merged_from_annotations.tif` (entrada) y `output/merged_from_annotations_classes.tif` (ground truth), que produce `align_tif_to_mrc.py`, y ese script necesita anotaciones `.tif`. Sin esos ficheros el notebook no arranca.
2. **La entrada no es el tomograma.** Lo que codifica V-JEPA es la fusión de las anotaciones, no `sample_1_10490.mrc`. Por eso solo se conservan "72/200 cortes informativos": los que tienen anotación. El objetivo es codificar el tomograma crudo.
3. **El ground truth no sirve para entrenar con ~100 clases.** El volumen de clases usa `np.linspace(32, 224, N)` en uint8: con ~100 clases los valores quedan casi consecutivos, y donde dos máscaras se solapan gana la última. Además `TARGET_CLASS = 224` está fijado a mano y corresponde a la última clase por orden alfabético. Hace falta un volumen de etiquetas enteras `1..N` con un CSV `id -> complejo`.
4. **Preprocesado pensado para otro tipo de dato.** `.astype(np.uint8)` directo sobre un `.mrc` en float32 estropearía el volumen: hay que normalizar antes (por percentiles).