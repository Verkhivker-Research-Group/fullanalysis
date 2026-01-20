"""Build AlphaFold3-style JSON request files from chain PDBs and a ligand annotation CSV.

Derived from: cif.ipynb

Expected inputs:
- --chains-dir: folder containing chain PDB files like 1CKJ_A.pdb
- --csv: a CSV with at least columns: PDB, Ligand, LigandType
  where Ligand and LigandType are whitespace-separated lists aligned by position.
  Ligand entries may look like 'Y3I:...'; we take the substring before ':' as comp_id.

Behavior (matches notebook):
- For each chain PDB, extract the protein sequence (Biopython PPBuilder)
- Find the row in CSV where df['PDB'] == pdb_id
- Collect ligands where LigandType == 'Allosteric'
- Write data/<PDB>.json with:
  {
    "sequences": [
      {"proteinChain": {"sequence": "...", "count": 1}},
      {"ligand": {"ligand": "Y3I", "count": 1}},
      ...
    ],
    "name": "1CKJ"
  }
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from Bio import PDB
from Bio.PDB.Polypeptide import PPBuilder


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument('--chains-dir', required=True, help='Directory with chain PDBs (e.g., content/Chains)')
    p.add_argument('--csv', required=True, help='CSV with columns PDB, Ligand, LigandType')
    p.add_argument('--out-dir', default='data/af3_requests', help='Where to write per-PDB JSON request files')
    p.add_argument('--ligand-type', default='Allosteric', help='Which LigandType entries to include')
    p.add_argument('--include-empty', action='store_true', help='Write JSON even if no matching row/ligands found')
    return p.parse_args()


def pdb_to_sequence(pdb_path: Path) -> str:
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure('protein', str(pdb_path))
    ppb = PPBuilder()
    seq = ''
    for model in structure:
        for chain in model:
            peptides = ppb.build_peptides(chain)
            for pep in peptides:
                seq += str(pep.get_sequence())
    return seq


def infer_pdb_id_from_filename(name: str) -> str:
    stem = Path(name).stem
    if '_' in stem:
        return stem.split('_')[0].upper()
    # fallback
    return stem[:4].upper()


def extract_allosteric_ligands(row: pd.Series, ligand_type: str) -> list[str]:
    ligands = str(row['Ligand']).split()
    ligand_types = str(row['LigandType']).split()
    out = []
    for lig, ltyp in zip(ligands, ligand_types):
        if ltyp == ligand_type:
            comp = lig.split(':')[0]
            out.append(comp)
    return out


def write_request_json(pdb_id: str, sequence: str, ligands: list[str], out_path: Path) -> None:
    data = {
        'sequences': [
            {
                'proteinChain': {
                    'sequence': sequence,
                    'count': 1,
                }
            }
        ],
        'name': pdb_id,
    }
    for lig in ligands:
        data['sequences'].append({'ligand': {'ligand': lig, 'count': 1}})

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w') as f:
        json.dump(data, f, indent=2)


def main() -> int:
    args = parse_args()
    chains_dir = Path(args.chains_dir)
    out_dir = Path(args.out_dir)
    df = pd.read_csv(args.csv)

    required = {'PDB', 'Ligand', 'LigandType'}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns in CSV: {sorted(missing)}")

    # normalize PDB column to uppercase for matching
    df['PDB'] = df['PDB'].astype(str).str.upper().str.strip()

    wrote = 0
    skipped = 0
    for pdb_file in sorted(chains_dir.glob('*.pdb')):
        pdb_id = infer_pdb_id_from_filename(pdb_file.name)
        seq = pdb_to_sequence(pdb_file)

        match = df[df['PDB'] == pdb_id]
        if match.empty:
            if args.include_empty:
                write_request_json(pdb_id, seq, [], out_dir / f'{pdb_id}.json')
                wrote += 1
            else:
                skipped += 1
            continue

        row = match.iloc[0]
        ligids = extract_allosteric_ligands(row, args.ligand_type)
        if not ligids and not args.include_empty:
            skipped += 1
            continue

        write_request_json(pdb_id, seq, ligids, out_dir / f'{pdb_id}.json')
        wrote += 1

    print(f"Done. Wrote {wrote} JSON files. Skipped {skipped}. Out: {out_dir}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
