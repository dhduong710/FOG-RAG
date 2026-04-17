#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(".")
TABLE_DIR = ROOT / "results" / "week8" / "baseline_table_v0"
REPORT_DIR = ROOT / "reports" / "week8"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    structure_table = (TABLE_DIR / "setting_a_structure_table_v0.md").read_text(encoding="utf-8")
    reference_table = (TABLE_DIR / "setting_a_reference_rows.md").read_text(encoding="utf-8")
    sources = load_json(TABLE_DIR / "table_sources.json")

    experimental_setup = """# Experimental Setup for Setting A

## 1. Task formulation
We evaluate Setting A as a head-prediction task of the form `(?, indication, disease)`, where the goal is to rank candidate drugs for a given disease query.

## 2. Candidate universe and split policy
For the structure-only baselines, the evaluation universe is restricted to the drug-only entity set. We use the valid split as the primary decision split in this week, and report standard ranking metrics including MRR, Hits@1, Hits@3, and Hits@10.

## 3. Graph and evaluation protocol
All structure-only baselines are evaluated under the same clean valid-first protocol on the PrimeKG-based Setting A benchmark. The training graph is the enriched Setting-A graph, while validation is performed on the fixed valid split. This week focuses on establishing a clean comparison floor rather than introducing new novelty modules.

## 4. Table policy
We intentionally separate the main structure-only baseline table from the candidate-aware reranker reference rows. The latter are included only as supporting references and should not be interpreted as directly comparable under the exact same evaluation protocol without explicit caveats.
"""

    baselines_md = """# Baselines for Setting A

## 1. Structure-only baselines
We include four structure-only baselines in the first clean comparison table:
- **R-GCN**: currently a provisional row derived from the existing week7 ranker_v2 score dump under the clean structure-only evaluator.
- **HRGAT**: a minimal relation-aware graph attention baseline evaluated under the same valid-first protocol.
- **ComplEx**: the preferred third baseline and currently the strongest structure-only row in table v0.
- **TransE**: a bonus fourth baseline providing a simple translational reference.

## 2. Candidate-aware reranker reference rows
We additionally keep three reranker-based reference rows:
- **week7 3B**: the main backbone reference package.
- **week7 8B**: a capacity-check reference row.
- **week8 posthoc 3B**: supporting retrieval-side analysis only, not the main backbone package.

## 3. Current interpretation
At the current stage, ComplEx provides the strongest structure-only result, while HRGAT clearly improves over the provisional R-GCN row. The candidate-aware reranker rows remain useful references for the main backbone path, but are intentionally kept separate from the structure-only baseline section.
"""

    week_closeout = """# Day 7 Week 8 Closeout

## 1. Scope of the week
This week focused on freezing the Setting-A structural baseline protocol, running 2–4 structure-only baselines, building the first clean Setting-A result table v0, and drafting the corresponding Experimental Setup / Baselines writing.

## 2. What was completed
- Protocol freeze for Setting A structural baseline evaluation
- Clean structure-only evaluation row for R-GCN (provisional)
- Full HRGAT baseline training and valid evaluation
- Full ComplEx baseline training and valid evaluation
- Full TransE baseline training and valid evaluation
- First clean Setting-A table v0
- Separate reference section for candidate-aware reranker rows

## 3. Main result table status
The current structure-only ordering in table v0 is:
1. ComplEx
2. HRGAT
3. TransE
4. R-GCN (provisional)

The candidate-aware reranker rows are kept in a separate supporting section, with week7 3B remaining the main backbone reference.

## 4. Main technical conclusions
- The Setting-A protocol is now frozen cleanly for structural baseline comparison.
- ComplEx is currently the strongest structure-only row in the first table version.
- HRGAT substantially reduces collapse relative to the provisional R-GCN row.
- The reranker backbone path is already frozen enough to serve as a reference, so no further retrieval/backbone changes were needed this week.

## 5. GO decision
**GO (strong)**

Rationale:
- Four structure-only baselines are available.
- The first clean Setting-A table v0 is complete.
- Experimental Setup / Baselines drafts are available.
- The repo now has a cleaner comparison floor before entering the next novelty phase.
"""

    summary_md = """# Week 8 Summary for Paper Draft

This week established the first clean comparison floor for Setting A. We froze the structural baseline protocol, evaluated four structure-only baselines under a shared valid-first drug-only universe setting, and constructed the first result table v0. Among the current structure-only rows, ComplEx is the strongest, followed by HRGAT and TransE, while the current R-GCN row remains provisional. We also preserved the week7 3B, week7 8B, and week8 posthoc 3B rows as candidate-aware reranker references in a separate supporting section.
"""

    (TABLE_DIR / "experimental_setup_setting_a.md").write_text(experimental_setup, encoding="utf-8")
    (TABLE_DIR / "baselines_setting_a.md").write_text(baselines_md, encoding="utf-8")
    (REPORT_DIR / "day7_week8_closeout.md").write_text(week_closeout, encoding="utf-8")
    (TABLE_DIR / "week8_summary_for_paper.md").write_text(summary_md, encoding="utf-8")

    print("Saved:")
    print(f"- {TABLE_DIR / 'experimental_setup_setting_a.md'}")
    print(f"- {TABLE_DIR / 'baselines_setting_a.md'}")
    print(f"- {REPORT_DIR / 'day7_week8_closeout.md'}")
    print(f"- {TABLE_DIR / 'week8_summary_for_paper.md'}")
    print()
    print("Source files used:")
    print(f"- {TABLE_DIR / 'setting_a_structure_table_v0.md'}")
    print(f"- {TABLE_DIR / 'setting_a_reference_rows.md'}")
    print(f"- {TABLE_DIR / 'table_sources.json'}")


if __name__ == "__main__":
    main()