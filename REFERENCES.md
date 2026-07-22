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

`prosail` — Python implementation of PROSPECT-D and 4SAIL by J. Gómez-Dans et al.
https://github.com/jgomezdans/prosail

## Planet Tanager

Planet Labs PBC — Tanager hyperspectral satellite constellation, Basic Radiance product documentation.
https://www.planet.com/products/hyperspectral/

---

Please cite the original PROSPECT-D and 4SAIL papers, and the `prosail` package, if you build on the code in this repository.
