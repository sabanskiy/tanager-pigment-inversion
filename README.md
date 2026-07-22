# tanager-pigment-inversion

**From Multispectral to Hyperspectral: Resolving Pigment Inversion Ambiguity with Tanager VSWIR Data**

Submission for the [Planet Tanager Open Data Competition](https://www.planet.com/) — Technical Analysis category.

**Organisation:** [SilvaIQ](https://silvaiq.com) — Ukrainian remote sensing R&D company
**Contact:** Andriy Sabanskyy — andriy@silvaiq.com
**Scientific advisor:** Kyrylo Holoborodko, PhD — ORCID [0000-0001-7857-1119](https://orcid.org/0000-0001-7857-1119) — methodological oversight and validation of the pigment diagnostic approach

---

## The problem this project quantifies

Physics-based retrieval of plant biochemical parameters — chlorophyll *a+b* (Cab), carotenoids (Car), anthocyanins (Ant), Leaf Area Index (LAI), leaf water content (Cw), and dry matter (Cm) — from multispectral imagery is an **ill-posed inverse problem**.

When the PROSPECT-D/SAIL model is inverted against 4–5 spectral bands (a typical UAV multispectral sensor), multiple parameter combinations produce an equally close spectral match. Cw and Cm cannot be measured directly from such data and must be assigned via prior distributions; Car and Ant retrievals remain prior-dominated. This is a fundamental consequence of spectral information content, not a modelling failure.

> *"Physics-based pigment diagnostics only goes as far as your sensor's spectral resolution allows — Tanager's full VSWIR range lets us test where that limit actually is."*

**Question this repository answers:** how much does the additional spectral information from a ~426-band VSWIR sensor (380–2500 nm) reduce this ambiguity, and which parameters become directly measurable rather than prior-constrained? Tanager's coverage of the **1450 nm and 1940 nm water absorption features** is the direct physical signal this analysis tests against.

---

## Scientific foundation and attribution

This project applies **published, open-source physical models** to a new data type. No originality is claimed for the radiative transfer methodology — see [REFERENCES.md](REFERENCES.md) for full citations.

- **PROSPECT-D** — leaf optical properties model including anthocyanins (Féret et al. 2017).
- **4SAIL** — canopy bidirectional reflectance model (Verhoef et al. 2007).
- **Implementation** — the open-source Python package [`prosail`](https://github.com/jgomezdans/prosail), which implements both models following the original publications.

Our contribution is the **application methodology**: pipeline design for Tanager data, the hyperspectral-vs-multispectral channel selection experiment, uncertainty quantification, and interpretation in the context of operational multispectral precision agriculture.

---

## Analysis design

1. **Data preparation** — load a Tanager Basic Radiance scene over a vegetated area, convert to surface reflectance, clip to a vegetated ROI, mask soil/shadow/water.
2. **Forward modelling** — generate a Look-Up Table (LUT) spanning literature-standard parameter ranges for Cab, Car, Ant, LAI, Cw, Cm, and canopy structure; simulate spectra at full Tanager spectral resolution.
3. **Hyperspectral inversion baseline** — invert against the full VSWIR spectrum; report RMSE, R², and bootstrap uncertainty per parameter.
4. **Multispectral subset experiment** — repeat the inversion restricted to bands matching a typical 4–5 band UAV multispectral sensor; quantify the degradation per parameter.
5. **SWIR contribution analysis** — incrementally add SWIR channels (1400–2500 nm) to the multispectral subset and track the change in Cw/Cm retrieval quality.

**Output:** a quantitative, reproducible answer to *"for which plant biochemical parameters does hyperspectral data change the result, and by how much?"*

---

## Repository structure

```
tanager-pigment-inversion/
├── README.md
├── LICENSE
├── REFERENCES.md
├── environment.yml
├── data/            # Tanager scenes are not committed — see data/README.md
├── notebooks/        # 01–05, numbered analysis pipeline
├── src/              # reusable modules imported by the notebooks
└── results/
    ├── figures/
    └── tables/
```

## Getting started

```bash
conda env create -f environment.yml
conda activate tanager-pigment
jupyter lab notebooks/
```

See [data/README.md](data/README.md) for instructions on obtaining a Tanager Basic Radiance scene from Planet Explorer.

---

## What this repository deliberately does not include

This is a competition submission built from scratch for this analysis — it is not a branch or export of SilvaIQ's production pipeline. Specifically excluded:

- Production-calibrated LUT parameter ranges (this repo uses literature-standard ranges only).
- SilvaIQ's production surrogate model architecture (MLP/GPR) — this repo uses direct LUT-based inversion.
- Crop- and phenology-specific prior calibration.
- Any field data, ground-truth measurements, or coordinates from research or farm partners.

---

## Third-party licenses

All Python dependencies in `environment.yml` (numpy, scipy, pandas, matplotlib, rasterio, spectral, jupyter, numba) are BSD- or MIT-licensed — fully compatible with this repository's MIT license.

**One exception:** the Python `prosail` package ([jgomezdans/prosail](https://github.com/jgomezdans/prosail)) does not declare an explicit open-source license upstream (no `LICENSE` file, no PyPI classifier; its Zenodo archive is tagged only generic "other-open"). This repository uses `prosail` strictly as an **unmodified pip dependency** — installed by each user directly from PyPI via `environment.yml` — never vendored or redistributed as part of this repository's own source. No code from `prosail` is copied, embedded, or modified here. See [REFERENCES.md](REFERENCES.md) for the full note and for Féret's own MIT-licensed reference implementations (R packages `prospect`/`prosail`), which formally implement the same published models under a clear license.

**Tanager imagery itself** is licensed CC-BY 4.0 by Planet Labs PBC — see [REFERENCES.md](REFERENCES.md) for the exact required attribution text, separate from the code license above.

---

## Team

**Andriy Sabanskyy** — Founder & CEO, SilvaIQ. Technical lead: pipeline design, LUT construction, inversion implementation, analysis, repository preparation.

**Kyrylo Holoborodko, PhD** — Scientific Curator. Scientific advisor: methodological oversight and validation of the pigment diagnostic approach.

---

## License

MIT — see [LICENSE](LICENSE).
