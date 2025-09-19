#!/usr/bin/env python3
from ost.mol.alg.ligand_scoring import PDBPrep
from ost.mol.alg.ligand_scoring_scrmsd import SCRMSDScorer
from ost.io import LoadEntity

def main():
    model_receptor  = PDBPrep("pred1_prot.pdb")
    target_receptor = PDBPrep("ref1_prot.pdb")
    pred_ent        = LoadEntity("pred1_lig.sdf", format="sdf")
    ref_ent         = LoadEntity("ref1_lig.sdf",  format="sdf")

    scorer = SCRMSDScorer(
        model_receptor,
        target_receptor,
        [pred_ent],
        [ref_ent],
        bs_radius=5.0,
        rename_ligand_chain=True,
        full_bs_search=True,
        substructure_match=True,
        coverage_delta=0.2
    )   

    state, details = scorer.get_model_ligand_state_report(0)

    coverage = scorer.coverage_matrix[0,0]
    rmsd     = scorer.score_matrix[0,0]

    if state == 0 and coverage >= 0.9 and rmsd == rmsd:
        print(f"{rmsd:.3f}")
    else:
        print("nan")

if __name__ == "__main__":
    main()