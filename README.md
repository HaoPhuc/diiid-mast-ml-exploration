# DIII-D & MAST ML Exploration

Learning to apply machine learning to open fusion data from two tokamaks: DIII-D (General Atomics, USA) and MAST (UKAEA, UK).

The main question to start with: can a model reconstruct the plasma's magnetic flux map ψ(R,Z) from coil currents and Thomson scattering alone, without magnetic sensors? And does what it learns on DIII-D carry over to MAST?

## Data

| Source | What it has |
|---|---|
| [Fusion Equilibrium Challenge dataset](https://huggingface.co/datasets/Sophelio/fusion-equilibrium-challenge) | 7,041 labeled DIII-D shots, 1,206 MAST shots (inputs only), cleaned and documented |
| [FAIR-MAST](https://mastapp.site) | 11,573 MAST shots with the full set of signals |

The challenge dataset (NeurIPS 2026) was released by Sophelio and General Atomics under CC BY 4.0. This repo is not a challenge entry. Its [starter kit](https://github.com/Sophelio/fusion-equilibrium-challenge-starter) and [modeling guide](https://github.com/Sophelio/fusion-equilibrium-challenge-starter/blob/main/MODELING_GUIDE.md) are where I start.

## Approach

No fixed plan. I start from the starter kit, then follow my own questions. Findings are added here as they turn into results.

## Status

Just getting started.

## Credits

DIII-D and MAST data via Sophelio / General Atomics (CC BY 4.0) and FAIR-MAST / UKAEA. Starter kit code: MIT.
