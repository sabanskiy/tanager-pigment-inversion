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

1. **Data preparation** (`01`) — load a Tanager scene (Planet's official atmospherically-corrected `surface_reflectance` product), clip to a vegetated ROI using NDVI plus Planet's own cloud/cirrus/nodata masks.
2. **Forward modelling** (`02`) — generate a Look-Up Table (LUT) spanning literature-standard parameter ranges for N, Cab, Car, Ant, Cw, Cm, LAI; simulate spectra at full Tanager spectral resolution via `prosail`, grounded in the scene's real solar geometry.
3. **Hyperspectral inversion baseline** (`03`) — invert against the full valid VSWIR spectrum; report RMSE, R², and bootstrap uncertainty per parameter via a synthetic self-consistency test (see "Results" below for why).
4. **Multispectral subset experiment** (`04`) — repeat the identical inversion restricted to bands matching a typical 5-band UAV multispectral sensor, and to that sensor with SWIR channels incrementally added around the 1450/1940 nm water absorption features.
5. **Final figures** (`05`) — RMSE/R² vs. band count for all seven parameters, and a side-by-side real-image comparison of multispectral-only vs. hyperspectral Cw retrieval.

---

## Results

**Validation approach:** this open dataset has no field-measured pigment ground truth for any scene, so retrieval quality is quantified through a synthetic self-consistency test — an independent set of "true" parameter combinations is drawn from the same physical ranges, simulated, given noise informed by the scene's own measured `surface_reflectance_uncertainty`, then inverted against a separate reference LUT and compared to the known truth. Full methodology in `notebooks/03_hyperspectral_inversion.ipynb`.

Scene: `20250918_112737_91_4001` (Rezonville, Metz, Grand Est, France — see `data/README.md` for why; geography is not physically load-bearing for this result).

| Parameter | 5-band multispectral, relative RMSE | Full hyperspectral, relative RMSE | Improvement |
|---|---|---|---|
| **Cw** (leaf water) | 40.6% | 10.4% | **−30.2 points** |
| **Cm** (dry matter) | 24.7% | 16.3% | −8.4 points |
| LAI | 27.4% | 20.6% | −6.8 points |
| Car (carotenoids) | 38.4% | 34.9% | −3.5 points |
| N (leaf structure) | 27.1% | 26.3% | −0.8 points |
| Cab (chlorophyll a+b) | 9.0% | 11.0% | +2.0 points (worse) |
| Ant (anthocyanins) | 19.2% | 28.2% | +9.0 points (worse) |

**Cw is where hyperspectral changes the result.** Relative RMSE falls from 40.6% (5-band multispectral) to 11.7% with just a ±50 nm SWIR window around the water-absorption features, plateauing near 8% beyond ±100 nm — the clearest, largest effect of any parameter, and the direct empirical answer to this project's core question. The real-image comparison in `notebooks/05_results_and_figures.ipynb` makes this visually unambiguous: multispectral-only Cw retrieval on a real vegetated crop is spatially incoherent noise, while the hyperspectral retrieval clearly resolves the scene's actual river/forest landscape structure.

**Car and Ant stay prior-dominated even with full hyperspectral VSWIR** (R² = −0.46 and 0.04 respectively in the self-consistency test — effectively unconstrained), confirming this is not merely a sensor-resolution problem: PROSPECT's carotenoid and anthocyanin absorption features overlap heavily with chlorophyll's in the visible range, an ill-posedness intrinsic to the leaf optical model itself. Cab, already well-constrained by the 5-band set's red/red-edge/NIR bands, does not benefit from (and is marginally hurt by) adding hyperspectral bands.

**A genuine nuance:** for Cw and Cm, the full hyperspectral band set (366 valid bands) performs slightly *worse* than a targeted ±100–200 nm SWIR subset (85–165 bands) in this nearest-neighbour LUT search — adding many spectrally redundant bands beyond the informative SWIR window dilutes rather than helps the match. **Targeted SWIR coverage, not raw band count, drives the improvement.**

Full tables: `results/tables/04_multispectral_subset_comparison.csv`, `results/tables/05_final_summary.csv`. Figures: `results/figures/05_*.png`.

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

All Python dependencies in `environment.yml` (numpy, scipy, pandas, matplotlib, rasterio, h5py, jupyter, numba) are BSD- or MIT-licensed — fully compatible with this repository's MIT license.

**One exception:** the Python `prosail` package ([jgomezdans/prosail](https://github.com/jgomezdans/prosail)) does not declare an explicit open-source license upstream (no `LICENSE` file, no PyPI classifier; its Zenodo archive is tagged only generic "other-open"). This repository uses `prosail` strictly as an **unmodified pip dependency** — installed by each user directly from PyPI via `environment.yml` — never vendored or redistributed as part of this repository's own source. No code from `prosail` is copied, embedded, or modified here. See [REFERENCES.md](REFERENCES.md) for the full note and for Féret's own MIT-licensed reference implementations (R packages `prospect`/`prosail`), which formally implement the same published models under a clear license.

**Tanager imagery itself** is licensed CC-BY 4.0 by Planet Labs PBC — see [REFERENCES.md](REFERENCES.md) for the exact required attribution text, separate from the code license above.

---

## Team

**Andriy Sabanskyy** — Founder & CEO, SilvaIQ. Technical lead: pipeline design, LUT construction, inversion implementation, analysis, repository preparation.

**Kyrylo Holoborodko, PhD** — Scientific Curator. Scientific advisor: methodological oversight and validation of the pigment diagnostic approach.

---

## License

MIT — see [LICENSE](LICENSE).
