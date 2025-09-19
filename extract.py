from pymol import cmd
from collections import defaultdict
import numpy as np
import os
from rdkit import Chem
from rdkit.Chem import AllChem, rdFMCS

PRED_CIF = "./pred.cif"
REF_CIF  = "./ref.cif"
CUTOFF = 5.0
DISTANCE_CUTOFF = 20.0
MIN_MATCH_ATOMS = 5

def extract_ligands(obj_name, out_prefix):
    sel_all = f"{obj_name}_ligands"
    cmd.select(sel_all, f"{obj_name} and organic within {CUTOFF} of {obj_name} and polymer")
    atoms = cmd.get_model(sel_all).atom
    if not atoms: 
        return []

    res_groups = defaultdict(list)
    for a in atoms:
        res_id = (a.resn, a.resi, a.chain)
        res_groups[res_id].append(a)

    ligand_files = []
    centroids = []

    for i, ((resn, resi, chain), atom_list) in enumerate(res_groups.items()):
        sel = f"{obj_name}_lig_{i}"
        cmd.select(sel, f"{obj_name} and resn {resn} and resi {resi} and chain {chain}")
        out_sdf = f"{out_prefix}_lig_{i}.sdf"
        cmd.save(out_sdf, sel)
        cmd.delete(sel)

        mol = Chem.MolFromMolFile(out_sdf, sanitize=False)
        if mol is None or not mol.GetNumConformers():
            continue
        conf = mol.GetConformer()
        coords = np.array([list(conf.GetAtomPosition(j)) for j in range(mol.GetNumAtoms())])
        centroid = coords.mean(axis=0)
        ligand_files.append(out_sdf)
        centroids.append(centroid)

    cmd.delete(sel_all)
    return list(zip(ligand_files, centroids))

def is_valid_match(mol1, mol2):
    try:
        mcs = rdFMCS.FindMCS([mol1, mol2], timeout=5,
                             ringMatchesRingOnly=False,
                             matchValences=False,
                             completeRingsOnly=False)
        if mcs.canceled or mcs.numAtoms == 0:
            return False
        patt = Chem.MolFromSmarts(mcs.smartsString)
        match1 = mol1.GetSubstructMatch(patt)
        match2 = mol2.GetSubstructMatch(patt)
        if not match1 or not match2 or len(match1) != len(match2):
            return False
        return len(match1) >= MIN_MATCH_ATOMS
    except:
        return False

def find_best_match(ref_ligs, pred_ligs):
    best_dist = float("inf")
    best_pair = (None, None)

    for ref_file, ref_centroid in ref_ligs:
        mol1 = Chem.MolFromMolFile(ref_file, sanitize=False)
        for pred_file, pred_centroid in pred_ligs:
            mol2 = Chem.MolFromMolFile(pred_file, sanitize=False)
            dist = np.linalg.norm(np.array(ref_centroid) - np.array(pred_centroid))
            if dist > DISTANCE_CUTOFF:
                continue
            if not is_valid_match(mol1, mol2):
                continue
            if dist < best_dist:
                best_dist = dist
                best_pair = (ref_file, pred_file)

    return best_pair

def main():
    if not os.path.exists(REF_CIF) or not os.path.exists(PRED_CIF):
        cmd.quit()

    cmd.load(REF_CIF, "ref")
    cmd.load(PRED_CIF, "pred")
    cmd.align("pred and polymer", "ref and polymer")

    ref_ligs = extract_ligands("ref", "ref")
    pred_ligs = extract_ligands("pred", "pred")

    if not ref_ligs or not pred_ligs:
        cmd.quit()

    ref_file, pred_file = find_best_match(ref_ligs, pred_ligs)
    if ref_file and pred_file:
        os.rename(ref_file, "ref1_lig.sdf")
        os.rename(pred_file, "pred1_lig.sdf")
        cmd.save("ref1_prot.pdb", "ref and polymer")
        cmd.save("pred1_prot.pdb", "pred and polymer")

    cmd.quit()

main()