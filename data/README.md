# Data

Tanager scenes are **not committed to this repository**. This directory only holds the download instructions and, once downloaded, your local copy of the scene (git-ignored).

## Obtaining a Tanager Basic Radiance scene

1. Sign in to [Planet Explorer](https://www.planet.com/explorer/) with an account that has access to Tanager Open Data (competition participants receive access instructions from Planet).
2. Search for a scene over a vegetated area (crop field, orchard, or grassland). Geography is not critical — the physical transferability of the PROSPECT-D/SAIL model does not depend on location.
3. Filter to the **Tanager** satellite and select a scene with low cloud cover.
4. Select the **Basic Radiance** product (not orthorectified surface reflectance — this project performs its own atmospheric correction as part of the methodology).
5. Download the scene. Depending on delivery format this will be either:
   - ENVI format (`.hdr` header + `.bil`/`.img` binary), or
   - GeoTIFF, or
   - HDF5.
6. Place the downloaded files in this directory, e.g.:
   ```
   data/
   └── tanager_scene_01/
       ├── scene.hdr
       └── scene.bil
   ```
7. Update the path in `notebooks/01_tanager_load_and_preprocess.ipynb` to point at your local scene.

## Format notes

`src/tanager_io.py` supports ENVI (via the `spectral` package) and GeoTIFF (via `rasterio`). If your scene is delivered as HDF5, convert it to GeoTIFF first or extend `tanager_io.py` accordingly.

## Licensing of downloaded data

Tanager Open Data is provided by Planet Labs PBC under the competition's data access terms. Redistribution of raw scene data is not covered by this repository's MIT license — only the analysis code is. Do not commit raw scene files to this repository.
