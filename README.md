# Benchmarking AI-Based Co-Folding and Docking Models for Predicting Structures of Orthosteric and Allosteric Ligand–Protein Complexes  
## Decoding the Allosteric Blind Spot Using a Landscape-Guided Interpretable AI Framework


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

.
├── 0_setup/ # Dataset acquisition and validation
├── 1_inputs/ # Model-specific input construction
├── 2_run_models/ # Model output collection and standardization
├── 3_postprocess_predictions/ # CIF parsing, ligand and pocket extraction
├── 4_score/ # Metric computation (OpenStructure-based)
├── 5_aggregate/ # Result aggregation and master tables
├── Figures/ # Final figures generated from analysis
├── evalspreadsheets/ # Intermediate and legacy evaluation CSVs
├── utils/ # Shared helper utilities
├── extract.py # Legacy extraction helper (superseded)
├── open.py # Legacy OpenStructure helper (superseded)
├── run_pipeline.sh # End-to-end pipeline launcher
└── README.md

pgsql
Copy code

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

- **`extract.py`, `open.py`**  
  Legacy helper scripts retained for reference; functionality has been superseded by modular scripts within the pipeline folders.

- **`run_pipeline.sh`**  
  Convenience script to execute the full pipeline end-to-end.

- lDDT-PLI (ligand–protein interaction accuracy)
