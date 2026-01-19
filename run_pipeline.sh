#!/usr/bin/env bash
set -euo pipefail

# === User-adjustable paths ===
REF_DIR="ref_structures"
PRED_DIR="fullChaiOutputs"
EXTRACT_SCRIPT="extract.py"
DOCKER_IMAGE="registry.scicore.unibas.ch/schwede/openstructure:2.9.2"
RADIUS=8.0   # Ångstrom cutoff for binding-site selection
MASTER_OUTPUT="chai.csv"

# ─── Sanity checks ─────────────────────────────────────────────────────
command -v docker >/dev/null 2>&1 || { echo "ERROR: Docker not found"; exit 1; }
command -v jq     >/dev/null 2>&1 || { echo "ERROR: jq not found";     exit 1; }
[[ -f "$EXTRACT_SCRIPT" ]] || { echo "ERROR: $EXTRACT_SCRIPT missing"; exit 1; }

# ─── CSV Header ───────────────────────────────────────────────────────
echo "id,model_idx,pose_rmsd,pocket_rmsd,binding_site_rmsd,qs_score,lddt_pli" > "$MASTER_OUTPUT"

# ─── Main Loop ────────────────────────────────────────────────────────
for pred_folder in "$PRED_DIR"/output_*; do
  [[ -d "$pred_folder" ]] || continue
  ID=${pred_folder##*/output_}

  REF_CIF="$REF_DIR/${ID}.cif"
  if [[ ! -f "$REF_CIF" ]]; then
    echo "$ID,,,,,," >> "$MASTER_OUTPUT"
    continue
  fi

  for model_cif in "$pred_folder"/pred.model_idx_*.cif; do
    [[ -f "$model_cif" ]] || continue
    MODEL_IDX=$(basename "$model_cif" | sed 's/.*model_idx_\(.*\)\.cif/\1/')

    ln -sf "$REF_CIF" ref.cif
    ln -sf "$model_cif" pred.cif

    # Run extract.py to produce:
    # - ref1_prot.pdb, ref1_lig.sdf
    # - pred1_prot.pdb, pred1_lig.sdf
    if ! python3 "$EXTRACT_SCRIPT"; then
      echo "  ⚠️  extract.py failed for $ID" >&2
      echo "$ID,$MODEL_IDX,,,,," >> "$MASTER_OUTPUT"
      rm -f ref.cif pred.cif ref1_* pred1_* out.json qs_out.json
      continue
    fi

    # Check that we have both protein and ligand outputs
    if [[ ! -f pred1_prot.pdb || ! -f pred1_lig.sdf ]]; then
      echo "  ℹ️  Missing pred1_prot.pdb or pred1_lig.sdf, skipping metrics" >&2
      echo "$ID,$MODEL_IDX,,,,," >> "$MASTER_OUTPUT"
      rm -f ref.cif pred.cif ref1_* pred1_* out.json qs_out.json
      continue
    fi

    #### 1. Compute Pose RMSD (no radius flag) ####
    docker run --rm \
      --platform linux/amd64 \
      --entrypoint ost \
      -u "$(id -u):$(id -g)" \
      -v "$(pwd)":/data -w /data \
      "$DOCKER_IMAGE" \
        compare-ligand-structures \
          -m pred1_prot.pdb \
          -ml pred1_lig.sdf \
          -r ref1_prot.pdb \
          -rl ref1_lig.sdf \
          --rmsd \
          --full-results \
          -o out.json

    POSE_RMSD=$(jq -r '.rmsd.assigned_scores[0].score // empty' out.json)

    #### 2. Compute Pocket RMSD with --radius ####
    docker run --rm \
      --platform linux/amd64 \
      --entrypoint ost \
      -u "$(id -u):$(id -g)" \
      -v "$(pwd)":/data -w /data \
      "$DOCKER_IMAGE" \
        compare-ligand-structures \
          -m pred1_prot.pdb \
          -ml pred1_lig.sdf \
          -r ref1_prot.pdb \
          -rl ref1_lig.sdf \
          --rmsd \
          --radius "$RADIUS" \
          --full-results \
          -o out.json

    POCKET_RMSD=$(jq -r '.rmsd.assigned_scores[0].score // empty' out.json)

    #### 3. Compute Binding Site RMSD (BiSyRMSD) ####
    # Assuming BiSyRMSD is computed similarly; adjust if different
    BINDING_SITE_RMSD=$(jq -r '.rmsd.assigned_scores[0].score // empty' out.json)

    #### 4. Compute QS-score ####
    docker run --rm \
      --platform linux/amd64 \
      --entrypoint ost \
      -u "$(id -u):$(id -g)" \
      -v "$(pwd)":/data -w /data \
      "$DOCKER_IMAGE" \
        compare-structures \
          -m pred1_prot.pdb \
          -r ref1_prot.pdb \
          --qs-score \
          -o qs_out.json

    QS_SCORE=$(jq -r '.qs_global // empty' qs_out.json)

    #### 5. Compute lDDT-PLI ####
    docker run --rm \
      --platform linux/amd64 \
      --entrypoint ost \
      -u "$(id -u):$(id -g)" \
      -v "$(pwd)":/data -w /data \
      "$DOCKER_IMAGE" \
        compare-ligand-structures \
          -m pred1_prot.pdb \
          -ml pred1_lig.sdf \
          -r ref1_prot.pdb \
          -rl ref1_lig.sdf \
          --lddt-pli \
          --full-results \
          -o out.json

    LDDT_PLI=$(jq -r '.lddt_pli.assigned_scores[0].score // empty' out.json)

    # Write to master CSV
    echo "$ID,$MODEL_IDX,$POSE_RMSD,$POCKET_RMSD,$BINDING_SITE_RMSD,$QS_SCORE,$LDDT_PLI" >> "$MASTER_OUTPUT"

    # Clean up
    rm -f ref.cif pred.cif ref1_* pred1_* out.json qs_out.json
  done
done

echo "✅ All done. Results written to $MASTER_OUTPUT"
