# Data

Tanager scenes are **not committed to this repository**. This directory only holds the download instructions and, once downloaded, your local copy of the scene (git-ignored).

## Obtaining a Tanager Basic Radiance / Surface Reflectance scene

Tanager Open Data is served as a public [STAC](https://stacspec.org/) catalog — no Planet Explorer login or account is required to browse or download it.

1. Browse the catalog: start at [`https://www.planet.com/data/stac/tanager-core-imagery/catalog.json`](https://www.planet.com/data/stac/tanager-core-imagery/catalog.json), then pick a collection (e.g. `agriculture/collection.json`) and an item JSON from its `item` links.
2. Each item's `assets` include, among others:
   - `basic_radiance_hdf5` — top-of-atmosphere radiance, native (unprojected) sensor geometry
   - `basic_sr_hdf5` — **surface reflectance**, already atmospherically corrected by Planet (see "Atmospheric correction" below)
   - `basic_beta_udm` — cloud / data-mask GeoTIFF
   - `geolocation_array` — per-pixel lat/lon GeoTIFF (needed since the "basic" products are unprojected)
   - `ortho_*` variants of the above, georectified to a map projection (larger files; not required for this project's pixel-array-based ROI/masking approach)
3. Download directly — asset `href` values are plain public HTTPS URLs (Google Cloud Storage), e.g.:
   ```bash
   curl -L -o data/scene_basic_radiance.h5 \
     "https://storage.googleapis.com/open-cogs/planet-stac/tanager1-release2-core-imagery/basic_radiance_hdf5/<ITEM_ID>_basic_radiance_hdf5.h5"
   curl -L -o data/scene_basic_sr.h5 \
     "https://storage.googleapis.com/open-cogs/planet-stac/tanager1-release2-core-imagery/basic_sr_hdf5/<ITEM_ID>_basic_sr_hdf5.h5"
   ```
4. Update the path in `notebooks/01_tanager_load_and_preprocess.ipynb` to point at your local scene.

### Scenes used in this repository

- **`tanager_scene_01`** — `20250918_112737_91_4001`, Rezonville, Metz, Grand Est, France (agriculture collection). 0% cloud, 33.67 m GSD, captured 2025-09-18, sun elevation 42.6°. Primary scene (notebooks 01-08). Chosen as a temperate-climate cereal/oilseed cropland analog (no Tanager Open Data scene currently covers Ukraine — the full 276-scene catalog was checked). Geography is not critical to the result — the physical transferability of PROSPECT-D/SAIL does not depend on location.
- **`tanager_scene_02`** — `20250224_145149_32_4001`, El Algarrobal, Salta, Argentina (agriculture collection). 0% cloud, 32.94 m GSD, captured 2025-02-24, sun elevation 63.6°. Used in the multi-scene generalisation check (notebook 08) for a contrasting hemisphere/season/sun-geometry.
- **`tanager_scene_03`** — `20250812_110905_82_4001`, Kleingartach, Baden-Württemberg, Germany (agriculture collection). 0% cloud, 33.82 m GSD, captured 2025-08-12, sun elevation 55.5°.
- **`tanager_scene_04`** — `20250510_112042_16_4001`, Ringkøbing-Skjern, Central Denmark Region, Denmark (agriculture collection). 0% cloud, 34.13 m GSD, captured 2025-05-10, sun elevation 51.5°.

Scenes 02-04 test whether the channel-selection findings (Sections "Results" in the README) replicate across different crop types, phenological stages, and sun-sensor geometries, per the external methods review's recommendation (`review/reviewer_report.md`, review of single-scene generalisation).

## File format

Tanager Basic Radiance/Surface Reflectance products are **HDF5**, not ENVI. Confirmed internal structure:

```
HDFEOS/SWATHS/HYP/Data Fields/
    toa_radiance                       (bands, rows, cols) float32
                                        attrs: wavelengths [nm], fwhm [nm], Unit="W/(m^2 sr um)"
    surface_reflectance                (bands, rows, cols) float32   [basic_sr_hdf5 only]
    surface_reflectance_uncertainty    (bands, rows, cols) float32   [basic_sr_hdf5 only]
    aerosol_optical_depth, column_water_vapour   (rows, cols)        [basic_sr_hdf5 only]
    beta_cloud_mask, beta_cirrus_mask, nodata_pixels   (rows, cols) uint8
    sun_zenith, sun_azimuth, sensor_zenith, sensor_azimuth, sensor_to_ground_path_length  (rows, cols) float32
HDFEOS/SWATHS/HYP/Geolocation Fields/
    Latitude, Longitude                (rows, cols) float64
```

`src/tanager_io.py` reads this directly via `h5py`.

## Atmospheric correction

Planet's `basic_sr_hdf5` product already provides atmospherically-corrected surface reflectance (`surface_reflectance` + a per-band `surface_reflectance_uncertainty`), so this repository uses it as the primary reflectance input rather than implementing radiance→reflectance correction from scratch. `src/atmospheric.py` retains a simplified empirical-line function as an optional secondary validation path, not a required pipeline step.

## Licensing of downloaded data

Tanager Open STAC data is licensed by Planet Labs PBC under **Creative Commons CC-BY 4.0** (confirmed in the STAC catalog's own `description` field). Required attribution for any redistribution:

> "Tanager STAC Data, available at www.planet.com/data/stac © [YEAR] Planet Labs PBC. All Rights Reserved" — prefaced with "Adapted from..." for any adapted material, where `[YEAR]` is the year the data was captured.

This repository does not commit raw scene files (see `.gitignore`); this attribution requirement applies to any figures, derived data, or maps produced from the imagery and published as part of the competition submission — see `REFERENCES.md`.
