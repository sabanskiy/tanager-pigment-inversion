# References

This project applies published, open-source radiative transfer models to Planet Tanager VSWIR data. No originality is claimed for the models themselves.

## PROSPECT-D (leaf optical properties model)

Féret, J.-B., Gitelson, A. A., Noble, S. D., & Jacquemoud, S. (2017). PROSPECT-D: Towards modeling leaf optical properties through a complete lifecycle. *Remote Sensing of Environment*, 193, 204–215.
https://doi.org/10.1016/j.rse.2017.03.004

Original PROSPECT model:

Jacquemoud, S., & Baret, F. (1990). PROSPECT: A model of leaf optical properties spectra. *Remote Sensing of Environment*, 34(2), 75–91.
https://doi.org/10.1016/0034-4257(90)90100-Z

## 4SAIL (canopy bidirectional reflectance model)

Verhoef, W., Jia, L., Xiao, Q., & Su, Z. (2007). Unified optical-thermal four-stream radiative transfer theory for homogeneous vegetation canopies. *IEEE Transactions on Geoscience and Remote Sensing*, 45(6), 1808–1822.
https://doi.org/10.1109/TGRS.2007.895844

## Software implementation

**Python (used in this repository):** `prosail` — Python implementation of PROSPECT-D and 4SAIL by J. Gómez-Dans (NCEO & UCL).
https://github.com/jgomezdans/prosail

**License status (checked 2026-07-22):** the Python `prosail` package does not declare an explicit open-source license — no `LICENSE` file in the GitHub repository (checked at HEAD of `master`, last pushed 2025-03-11), no license classifier on PyPI (empty `license` field, JSON metadata), and its Zenodo archive (DOI [10.5281/zenodo.2574925](https://doi.org/10.5281/zenodo.2574925)) is tagged only as generic "other-open," not a specific SPDX license.

**How this repository handles that:** `prosail` is used strictly as an **unmodified pip dependency**, installed by each user directly from PyPI via `environment.yml`. No `prosail` source code is copied, vendored, embedded, or redistributed inside this repository — this repository's own MIT license covers only the code written here (`src/`, notebooks). This is a transparency note, not a claim that the dependency's licensing gap has been resolved; we have reached out to the author to request an explicit license be added upstream.

**Reference implementations with a clear license (not used directly in this repo, cited for completeness):** Jean-Baptiste Féret (the PROSPECT-D paper's lead author) maintains his own official R implementations, both MIT-licensed:
- [`jbferet/prospect`](https://github.com/jbferet/prospect) — PROSPECT leaf model (incl. PROSPECT-D/PRO) + inversion routines. MIT License (confirmed via repository `LICENSE.md` and `DESCRIPTION`).
- [`jbferet/prosail`](https://github.com/jbferet/prosail) — coupled PROSPECT+SAIL canopy model + inversion routines. `License: MIT + file LICENSE` (R packaging convention; confirmed via `DESCRIPTION`).

These are the author's own reference implementations of the exact models this project cites, cleanly licensed — a valid alternative or cross-validation source if the Python `prosail` licensing gap becomes a blocker.

## Planet Tanager

Planet Labs PBC — Tanager hyperspectral satellite constellation, Basic Radiance product documentation.
https://www.planet.com/products/hyperspectral/

**Data license and required attribution (confirmed 2026-07-22, from the STAC catalog's own `description` field at [tanager-core-imagery/catalog.json](https://www.planet.com/data/stac/tanager-core-imagery/catalog.json)):** Tanager Open STAC data is licensed under [Creative Commons CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/). Required attribution for any redistribution:

> "Tanager STAC Data, available at www.planet.com/data/stac © [YEAR] Planet Labs PBC. All Rights Reserved" — prefaced with "Adapted from..." for any adapted material, where `[YEAR]` is the year the data was captured.

Scene used in this repository: `20250918_112737_91_4001` (captured 2025-09-18, Rezonville, Metz, Grand Est, France) → **"Adapted from Tanager STAC Data, available at www.planet.com/data/stac © 2025 Planet Labs PBC. All Rights Reserved."**

---

Please cite the original PROSPECT-D and 4SAIL papers, and the `prosail` package, if you build on the code in this repository.
