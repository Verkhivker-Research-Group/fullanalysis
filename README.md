# Benchmarking AI-Based Co-Folding and Docking Models for Predicting Structures of Orthosteric and Allosteric Ligand–Protein Complexes  
## Decoding the Allosteric Blind Spot Using a Landscape-Guided Interpretable AI Framework

## Pipeline Overview

![Benchmarking pipeline diagram](/flowchart.png)


## Models Evaluated
- AlphaFold 3 (AF3)
- Chai-1
- Boltz-2
- DynamicBind  


## Datasets
### 1. Orthosteric (Main) Dataset
- Canonical protein–ligand complexes derived from the DynamicBind benchmark
- Binding sites well represented in model training distributions
- Set of around 1100 complexes

### 2. Allosteric Dataset
- Obtained from Dunbrack Lab’s KinCoRe (Kinase Conformation Resource),
- Ligands bind to pockets that are conformationally dynamic and spatially remote from the canonical site
- Set of around 800 complexes


The utility of this benchmark rests on a multi-tier dataset architecture designed to isolate the physical determinants of AI failure. To establish a high-fidelity baseline, we utilized the Major Drug Targets (MDT) Mainset as our orthosteric reference. To ensure this dataset probed genuine structural reconstruction rather than database memorization, we applied three stringent filters: (1) Temporal decoupling, restricting selection to complexes deposited in the Protein Data Bank (PDB) after 2020 to ensure they post-date the training sets of AF3 and its contemporaries; (2) Biological relevance, focusing on four critical pharmaceutical families—kinases, GPCRs, nuclear receptors, and ion channels; and (3) Structural challenge, requiring that the initial AlphaFold-predicted apo-pocket differ from the experimental holo-conformation by a Pocket RMSD > 2.0 Å or a Pocket LDDT < 0.8.
To interrogate the "allosteric blind spot," we constructed an expanded Allosteric Ensemble representing the most diverse collection of regulatory sites benchmarked to date. This includes a kinase-centric subset from the Kinase Conformation Resource (KinCoRe), featuring 217 complexes of Type III (back-pocket) and Type IV (distal myristoyl-site) inhibitors. This was supplemented by a curated crystallographic dataset of 136 allosteric kinase inhibitors confirmed via X-ray diffraction.86 To ensure our findings transcend the kinome, we incorporated the Diversified Allosteric Subset, containing 1,613 structures and 1,277 unique ligands across non-kinase families, providing a statistically robust probe into the energetic heterogeneity of allostery.


## Evaluation Metrics
### Ligand-Level Accuracy
- **Ligand Pose RMSD**
  - Ligand-only RMSD computed using **OpenStructure**
  - Reference and predicted ligands extracted from CIF files
  - RMSD calculated after optimal superposition of ligand coordinates
  - Symmetry-aware matching supported where applicable
### Pocket and Interaction Fidelity
- Pocket RMSD
- Binding-site RMSD
- QS-score

## Repository Structure

The repository is organized as a modular, stage-based analysis pipeline. Each folder corresponds to a distinct step in the benchmarking workflow, from dataset preparation to evaluation and aggregation.

## Dependencies

### Python
- **Python 3.10+** (3.9+ may work but is not guaranteed)

### Core Python Packages
Install via `pip` or `conda`:
- `pandas`
- `pyyaml`
- `biopython`

### OpenStructure (Required for Postprocessing & Scoring)
This project relies heavily on **OpenStructure (OST)** and its Python bindings:
- `openstructure`
- `ost`
- `ost.mol.alg.scoring_base` (MMCIFPrep)
- `ost.mol.alg.ligand_scoring_scrmsd` (SCRMSDScorer)
- `ost.mol.alg.ligand_scoring_lddtpli` (LDDTPLIScorer)
- `ost.mol.alg.qsscore` (QS-score)
- `ost.mol.alg.superpose` (SuperposeSVD)

> **Note:** OpenStructure is used via a **Docker-based workflow**. All postprocessing and scoring steps are executed inside a container with OpenStructure preinstalled, so no local OpenStructure installation is required.

### Standard Library (No Installation Required)
- `argparse`
- `pathlib`
- `json`
- `csv`
- `re`
- `shutil`
- `dataclasses`
- `typing`


### Folder Descriptions

- **`0_setup/`**  
  Scripts for downloading structures, constructing orthosteric and allosteric datasets, and validating dataset integrity.

- **`1_inputs/`**  
  Construction of model-specific inputs, including FASTA files, ligand specifications, and AlphaFold 3 JSON requests.

- **`2_run_models/`**  
  Collection and standardization of prediction outputs from AlphaFold 3, Chai-1, Boltz-2, and DynamicBind into a unified `pred.cif` format.

- **`3_postprocess_predictions/`**  
  Post-processing of CIF structures, including ligand extraction, pocket and binding-site residue definition, and structure normalization.

- **`4_score/`**  
  Implementation of all evaluation metrics, including ligand pose RMSD (via OpenStructure), pocket RMSD, binding-site RMSD, QS-score, and lDDT-PLI.

- **`5_aggregate/`**  
  Aggregation of raw metric outputs into unified master tables and summary statistics used for analysis.

- **`Figures/`**  
  Publication-ready figures generated from aggregated results.

- **`evalspreadsheets/`**  
  Intermediate and legacy CSV files produced during evaluation and early analysis stages.

- **`utils/`**  
  Shared helper functions and utilities used across multiple pipeline stages.

- **`extract.py`**  
  Original helper script retained for reference; functionality has been superseded by modular scripts within the pipeline folders.

- **`run_pipeline.sh`**  
  Convenience script to execute the full pipeline end-to-end.

- lDDT-PLI (ligand–protein interaction accuracy)
