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
- Designed to interrogate the allosteric blind spot in protein–ligand structure prediction
- Ligands bind to conformationally dynamic pockets spatially remote from canonical active sites

**Components:**
- **Kinase-Centric Subset (KinCoRe):**
  - Obtained from Dunbrack Lab’s Kinase Conformation Resource (KinCoRe)
  - 217 complexes of Type III (back-pocket) and Type IV (distal myristoyl-site) kinase inhibitors

- **Curated Allosteric Kinase Set:**
  - 136 experimentally validated allosteric kinase inhibitors
  - Confirmed via X-ray crystallography (Hu et al., 2021)

- **Diversified Allosteric Subset (Non-Kinase):**
  - 1,613 structures spanning non-kinase protein families
  - 1,277 unique ligands
  - Derived from a large-scale ligand binding pocket dataset for drug discovery (Moine-Franel et al., 2024)
  - Provides a statistically robust probe into the energetic heterogeneity of allostery

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


## References

1. **Hu H, Laufkötter O, Miljković F, Bajorath J.**  
   *Data set of competitive and allosteric protein kinase inhibitors confirmed by X-ray crystallography.*  
   Data Brief, 2021, **35**:106816.  
   https://doi.org/10.1016/j.dib.2021.106816

2. **Moine-Franel A, Mareuil F, Nilges M, Ciambur CB, Sperandio O.**  
   *A comprehensive dataset of protein–protein interactions and ligand binding pockets for advancing drug discovery.*  
   Scientific Data, 2024, **11**(1):402.  
   https://doi.org/10.1038/s41597-024-03233-z

