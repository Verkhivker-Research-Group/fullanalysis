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
- lDDT-PLI (ligand–protein interaction accuracy)
