# SoftFuse-KGC

SoftFuse-KGC is a research codebase for biomedical knowledge graph completion with
three progressively richer candidate packages:

- `backbone_raw`: structure-only top-20 candidates and graph context.
- `soft_support_raw`: re-ranked candidates using typed, contradiction-aware soft support.
- `fuzzy_retrieval_main`: the SoftFuse retrieval row, which keeps the candidate order stable while selecting a smaller confidence-aware subgraph for E2E LLM inference.

The repository keeps reusable code and release-facing artifacts. Generated logs,
checkpoints, and tables are written under `outputs/`, which is ignored by git.

## Repository Layout

```text
configs/
  backbone/            PrimeKG backbone ranker config
  soft_support/        PrimeKG soft-support formulas
  fuzzy_retrieval/     PrimeKG retrieval scoring formulas

data/raw/pharmkg/      PharmKG-8k raw split files used by the PharmKG pipeline

dataset/
  setting_a/           PrimeKG main setting
  setting_b/           PrimeKG annotation and evaluation rows
  setting_c_pharmkg/   PharmKG transfer setting
  setting_d_hetionet/  Hetionet transfer setting
  setting_e_drkg/      DRKG transfer setting
  setting_f_repodb/    repoDB transfer setting

scripts/
  backbone/            PrimeKG backbone helper scripts
  soft_support/        PrimeKG soft-support build and selection
  fuzzy_retrieval/     PrimeKG fuzzy retrieval build and selection
  evaluation/          PrimeKG candidate-stage evaluation tables
  e2e/                 PrimeKG E2E package, inference, and reporting scripts
  pharmkg/             PharmKG transfer pipeline
  hetionet/            Hetionet transfer pipeline
  drkg/                DRKG transfer pipeline
  repodb/              repoDB transfer pipeline
  sensitivity/         Optional robustness checks

main.py                LoRA training for the graph-enhanced LLM
infer.py               E2E inference and ranking metrics
```

Important PrimeKG paths after cleanup:

- `dataset/setting_a/raw_triples/primekg_indication_only.tsv`
- `dataset/setting_a/splits/{train,valid,test}.tsv`
- `dataset/setting_a/graph/train_enriched_deg1000_final.tsv`
- `dataset/setting_a/drkgc_json/`
- `dataset/setting_a/backbone_ready/`
- `dataset/setting_b/annotations/`
- `dataset/setting_b/contra_checked/`
- `dataset/setting_b/eval_valid/` and `dataset/setting_b/eval_test/`

## Environment

Use Python 3.10 or 3.11 for the least friction with the CUDA stack.

```bash
conda create -n softfuse-kgc python=3.10 -y
conda activate softfuse-kgc

pip install numpy pandas networkx tqdm pyyaml pyreadr
pip install transformers==4.38.2 peft==0.4.0 accelerate==0.27.2 \
  bitsandbytes==0.40.2 safetensors==0.4.3 tokenizers==0.15.2 \
  datasets==2.20.0

# Install the PyTorch build that matches your CUDA driver.
# Example for CUDA 11.8:
pip install torch==2.3.1 --index-url https://download.pytorch.org/whl/cu118
```

`pyreadr` is only needed for the repoDB downloader. If `pyreadr` cannot read the
RData file, `scripts/repodb/inventory_raw.py` also tries `Rscript` when it is
available on `PATH`.

## Download Raw Datasets

Run all commands from the repository root.

### PrimeKG

PrimeKG is the main setting. The release already includes the processed
PrimeKG artifacts used by the paper-facing pipeline. To audit or rebuild from
raw data, download the official PrimeKG CSV:

```bash
mkdir -p dataset/raw/primekg
curl -L -o dataset/raw/primekg/kg.csv \
  https://dataverse.harvard.edu/api/access/datafile/6180620
```

The current pipeline expects the indication-only raw triple file at:

```text
dataset/setting_a/raw_triples/primekg_indication_only.tsv
```

If you regenerate it from `kg.csv`, keep a three-column TSV with header:

```text
head    relation    tail
```

where `relation` is `indication`, `head` is the drug, and `tail` is the disease.
The checked-in `splits`, `graph`, `drkgc_json`, and `backbone_ready` directories
are the release snapshot for this setting.

### PharmKG

The PharmKG pipeline can download PharmKG-8k split files and optional Zenodo raw
files:

```bash
python scripts/pharmkg/inventory_raw.py

# Optional: also download the official raw archive from Zenodo.
python scripts/pharmkg/inventory_raw.py --download-zenodo
```

Expected PharmKG-8k files:

```text
data/raw/pharmkg/PharmKG-8k/train.tsv
data/raw/pharmkg/PharmKG-8k/valid.tsv
data/raw/pharmkg/PharmKG-8k/test.tsv
```

### Hetionet, DRKG, repoDB

These scripts download and inventory their raw sources under the corresponding
`dataset/setting_*/*raw_inventory*` directories:

```bash
python scripts/hetionet/inventory_raw.py
python scripts/drkg/inventory_raw.py
python scripts/repodb/inventory_raw.py
```

For offline machines, run the same scripts once on a machine with network
access, then copy the created `raw_inventory` directories into the same paths.

## PrimeKG Pipeline

The PrimeKG release snapshot starts from checked-in preprocessing artifacts. The
commands below rebuild all downstream SoftFuse artifacts from those artifacts.

### 1. Data Preprocessing And Backbone Inputs

The core preprocessed inputs are already in:

```text
dataset/setting_a/raw_triples/
dataset/setting_a/splits/
dataset/setting_a/graph/
dataset/setting_a/drkgc_json/
dataset/setting_a/backbone_ready/
dataset/setting_a/aligned_evidence/
dataset/setting_a/backbone_candidates/
dataset/setting_a/ontology_control/
```

If a script or ablation asks for
`dataset/setting_a/backbone_candidates/train_top20_raw.json`, create it from the
included aligned train evidence:

```bash
python scripts/backbone/export_primekg_train_candidates.py
```

To rerun structure baselines from the release artifacts:

```bash
python scripts/baselines/rerun_structure_baselines.py \
  --models transe distmult complex rotate rgcn hrgat

python scripts/baselines/recompute_reviewer_safe_metrics.py
python scripts/baselines/build_baseline_comparison.py
```

### 2. Soft Support

Build support features on validation, score soft-support variants, compare
them, select the main validation row, then build the locked test row:

```bash
python scripts/soft_support/build_support_features.py
python scripts/soft_support/build_soft_support_variants.py
python scripts/soft_support/compare_soft_support_variants.py
python scripts/soft_support/collect_soft_support_variant_cases.py
python scripts/soft_support/select_soft_support_main.py
python scripts/soft_support/build_soft_support_test.py
```

Main outputs:

```text
dataset/setting_a/support_features/valid_support_features.json
dataset/setting_a/soft_support_ranked_candidates/valid_top20_soft_support_main.json
dataset/setting_a/soft_support_ranked_candidates/test_top20_soft_support_main.json
```

### 3. Fuzzy Retrieval

Build path features, score retrieval variants, select the main validation row,
and build the locked test row:

```bash
python scripts/fuzzy_retrieval/build_path_features.py
python scripts/fuzzy_retrieval/build_fuzzy_retrieval_v1.py
python scripts/fuzzy_retrieval/compare_fuzzy_retrieval_v1.py
python scripts/fuzzy_retrieval/collect_fuzzy_retrieval_v1_cases.py
python scripts/fuzzy_retrieval/build_fuzzy_retrieval_variants.py
python scripts/fuzzy_retrieval/compare_fuzzy_retrieval_variants.py
python scripts/fuzzy_retrieval/collect_fuzzy_retrieval_variant_cases.py
python scripts/fuzzy_retrieval/select_fuzzy_retrieval_main.py
python scripts/fuzzy_retrieval/build_fuzzy_retrieval_test.py
```

Main outputs:

```text
dataset/setting_a/fuzzy_retrieval/valid_fuzzy_retrieval_main.json
dataset/setting_a/fuzzy_retrieval/test_fuzzy_retrieval_main.json
```

### 4. Candidate-Stage Evaluation

Build validation and test evaluation rows, then write the main comparison
tables:

```bash
python scripts/evaluation/build_valid_eval_ready.py
python scripts/evaluation/build_valid_main_table.py
python scripts/evaluation/build_test_eval_ready.py
python scripts/evaluation/build_test_main_table.py
python scripts/evaluation/collect_test_cases.py
```

Main outputs:

```text
dataset/setting_b/eval_valid/
dataset/setting_b/eval_test/
outputs/evaluation/
```

### 5. E2E Training And Inference

First build the three `infer.py`-ready PrimeKG packages:

```bash
python scripts/e2e/build_infer_ready.py
```

This creates:

```text
dataset/setting_a/e2e_infer_ready/backbone_raw/
dataset/setting_a/e2e_infer_ready/soft_support_raw/
dataset/setting_a/e2e_infer_ready/retrieval_main/
```

Train one graph-enhanced LoRA checkpoint on the backbone row:

```bash
export MODEL_NAME_OR_PATH=meta-llama/Llama-3.2-3B

python main.py \
  --dataset_path dataset/setting_a/e2e_infer_ready/backbone_raw \
  --model_name_or_path "$MODEL_NAME_OR_PATH" \
  --model_type llama \
  --kge_embedding_path dataset/setting_a/backbone_ready/entity_embeddings_rgcn.pt \
  --graph_num_rels 4 \
  --output_dir outputs/e2e/e2e_primary_checkpoint \
  --source_max_len 768 \
  --target_max_len 64 \
  --use_quant False \
  --num_train_epochs 1 \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 16 \
  --learning_rate 0.0002 \
  --lr_scheduler_type constant \
  --warmup_ratio 0.03 \
  --lora_r 32 \
  --lora_alpha 32 \
  --lora_dropout 0.1 \
  --remove_unused_columns False \
  --dataloader_num_workers 4 \
  --save_steps 500 \
  --logging_steps 10 \
  --bf16 True \
  --tf32 True \
  --report_to none
```

The checkpoint used by inference is:

```text
outputs/e2e/e2e_primary_checkpoint/checkpoint-final
```

Run E2E inference for all PrimeKG rows:

```bash
bash scripts/e2e/run_backbone_soft_e2e.sh
bash scripts/e2e/run_retrieval_e2e.sh
python scripts/e2e/collect_backbone_soft_e2e.py
python scripts/e2e/collect_retrieval_e2e.py
python scripts/e2e/build_e2e_table.py
```

Optional decoding sweep:

```bash
python scripts/e2e/make_decoding_sweep_configs.py
bash scripts/e2e/run_valid_decoding_sweep.sh
python scripts/e2e/collect_valid_decoding_sweep.py
bash scripts/e2e/run_selected_decode_test.sh
python scripts/e2e/collect_selected_decode_metrics.py
```

## Transfer Pipelines

The transfer settings follow the same order: raw inventory, preprocessing,
backbone candidates, SoftFuse package, soft support, fuzzy retrieval, then E2E.

### PharmKG

```bash
python scripts/pharmkg/inventory_raw.py
python scripts/pharmkg/select_task_schema.py
python scripts/pharmkg/build_splits_and_graph.py

python scripts/pharmkg/rerun_kge_baselines.py
python scripts/pharmkg/rerun_gnn_baselines.py
python scripts/pharmkg/build_transfer_eval_backbone.py
python scripts/pharmkg/build_softfuse_ready_package.py

python scripts/pharmkg/build_support_features.py
python scripts/pharmkg/build_soft_support_transfer.py
python scripts/pharmkg/build_fuzzy_retrieval_transfer.py
python scripts/pharmkg/build_eval_tables.py

python scripts/pharmkg/e2e/prepare_e2e_ready.py
MODEL_NAME=meta-llama/Llama-3.2-3B bash scripts/pharmkg/e2e/run_train_infer.sh
python scripts/pharmkg/e2e/reviewer_safe_e2e_metrics.py
```

Main E2E package:

```text
dataset/setting_c_pharmkg/e2e_infer_ready/
```

### Hetionet

```bash
python scripts/hetionet/inventory_raw.py
python scripts/hetionet/build_splits_and_graph.py

python scripts/hetionet/rerun_kge_baselines.py
python scripts/hetionet/rerun_gnn_baselines.py
python scripts/hetionet/select_backbone_source.py
python scripts/hetionet/build_softfuse_ready.py

python scripts/hetionet/build_soft_support.py
python scripts/hetionet/build_fuzzy_retrieval.py

export MODEL_NAME_OR_PATH=meta-llama/Llama-3.2-3B
bash scripts/hetionet/e2e/run_all_rows.sh
python scripts/hetionet/e2e/collect_metrics.py
```

### DRKG

```bash
python scripts/drkg/inventory_raw.py
python scripts/drkg/select_task_schema.py
python scripts/drkg/build_splits_and_graph.py

python scripts/drkg/rerun_kge_baselines.py
python scripts/drkg/rerun_gnn_baselines.py
python scripts/drkg/select_backbone_source.py
python scripts/drkg/build_softfuse_ready.py

python scripts/drkg/build_soft_support.py --source distmult
python scripts/drkg/build_soft_support.py --source rgcn
python scripts/drkg/sweep_soft_support.py
python scripts/drkg/build_fuzzy_retrieval.py

export MODEL_NAME_OR_PATH=meta-llama/Llama-3.2-3B
bash scripts/drkg/e2e/run_rgcn_rows.sh
python scripts/drkg/e2e/collect_metrics.py
```

### repoDB

```bash
python scripts/repodb/inventory_raw.py
python scripts/repodb/select_task_schema.py
python scripts/repodb/build_splits_and_graph.py

python scripts/repodb/rerun_kge_baselines.py
python scripts/repodb/rerun_gnn_baselines.py
python scripts/repodb/select_backbone_source.py
python scripts/repodb/build_softfuse_ready.py

python scripts/repodb/build_soft_support.py
python scripts/repodb/build_raw_display_control.py
python scripts/repodb/build_fuzzy_retrieval.py

export MODEL_NAME_OR_PATH=meta-llama/Llama-3.2-3B
bash scripts/repodb/e2e/run_all_rows.sh
python scripts/repodb/e2e/collect_metrics.py
```

## Generated And Large Files

The following files are generated and can be rebuilt:

- `outputs/**`
- E2E `train.json` packages under `dataset/setting_a/e2e_infer_ready/*/`
- transfer E2E train packages listed in `.gitignore`
- model checkpoints under `checkpoints/` or `outputs/**/checkpoint-*`

If a required train package is missing, rerun the package builder for that
setting:

- PrimeKG: `python scripts/e2e/build_infer_ready.py`
- PharmKG: `python scripts/pharmkg/e2e/prepare_e2e_ready.py`
- Hetionet: `python scripts/hetionet/build_softfuse_ready.py`, then the soft support and fuzzy retrieval builders
- DRKG: `python scripts/drkg/build_softfuse_ready.py`, then the soft support sweep and fuzzy retrieval builders
- repoDB: `python scripts/repodb/build_softfuse_ready.py`, then the soft support, display-control, and fuzzy retrieval builders

## Sanity Checks

Run these after editing code or moving artifacts:

```bash
python -m py_compile $(find scripts -name '*.py' | sort)
find scripts -name '*.sh' -print0 | xargs -0 -n1 bash -n
```

## Data Source Links

- PrimeKG project: https://zitniklab.hms.harvard.edu/projects/PrimeKG/
- PrimeKG GitHub: https://github.com/mims-harvard/PrimeKG
- PrimeKG Dataverse: https://doi.org/10.7910/DVN/IXA7BM
- PharmKG GitHub mirror: https://github.com/biomed-AI/PharmKG
- PharmKG Zenodo raw archive: https://zenodo.org/records/4077338
- Hetionet Zenodo: https://zenodo.org/records/268568
- DRKG DGL data: https://dgl-data.s3-us-west-2.amazonaws.com/dataset/DRKG/drkg.tar.gz
- repoDB source repository: https://github.com/adam-sam-brown/repoDB
