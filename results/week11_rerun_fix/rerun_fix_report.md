# Week 11 Rerun Fix Report

## 1. Root cause
- The original inference path had a split-selection issue and the ranking rerun was required to separate valid and test cleanly.
- After the fix, valid and test were rerun with split-aware inference and clean test packages.

## 2. Official ranking source after the fix
- Ranking metrics in this report use the rerun outputs:
  - `ranking_metrics_valid_rerun*.json` for valid
  - `ranking_metrics_test_rerun_clean.json` for test

## 3. Official valid summary

- **Backbone**: MRR=0.4242, Hits@1=0.3680, Hits@3=0.3940, Hits@10=0.5100
- **+ Ontology**: MRR=0.3687, Hits@1=0.1760, Hits@3=0.4540, Hits@10=0.8460
- **+ Ontology + Hard**: MRR=0.4675, Hits@1=0.2940, Hits@3=0.5380, Hits@10=0.9220
- **+ Ontology + Soft**: MRR=0.4322, Hits@1=0.2460, Hits@3=0.5180, Hits@10=0.9000

## 4. Official test summary

- **Backbone**: MRR=0.3931, Hits@1=0.3300, Hits@3=0.3580, Hits@10=0.5240
- **+ Ontology**: MRR=0.4355, Hits@1=0.2600, Hits@3=0.4860, Hits@10=0.9360
- **+ Ontology + Hard**: MRR=0.4489, Hits@1=0.2900, Hits@3=0.4800, Hits@10=0.9320
- **+ Ontology + Soft**: MRR=0.4172, Hits@1=0.2400, Hits@3=0.4680, Hits@10=0.9180

## 5. Main observations
- Best valid MRR row: **+ Ontology + Hard** (0.4675)
- Best test MRR row: **+ Ontology + Hard** (0.4489)
- The rerun removes the previous test-side collapse where all variants produced the same ranking metrics.
- The current test numbers are suitable to replace the pre-fix test ranking results in slides and paper tables.

## 6. Interpretation
- Novelty rows should be compared against the backbone within the same candidate-aware protocol.
- Structure-only baselines should remain in a separate table.
