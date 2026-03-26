# Setting B Decisions

## 1. Main task
The main benchmark task remains head prediction / indication ranking:

(?, indication, disease) -> rank drug

This main task is unchanged from Setting A.

## 2. Role of contraindication
Contraindication is NOT used as positive training triples for the main task.

Instead, contraindication is stored and used as auxiliary safety labels.

## 3. Setting A vs Setting B
### Setting A
- DrKGC-compatible benchmark
- ranking-only evaluation
- no contraindication-aware modification to the official benchmark

### Setting B
- reuse the same query disease and gold indication logic as Setting A
- add contraindication-aware safety analysis
- add ontology/schema validity analysis
- support grounded explanation analysis later

## 4. How contraindication is used in Setting B
Contraindication labels are used for:
- hard filtering
- soft penalization
- SafetyViolation@K
- Contra@K
- case-study safety flagging

Contraindication is NOT used for:
- changing gold labels
- redefining the benchmark task
- creating positive training triples for the main task

## 5. Conflict policy
If a pair (drug, disease) appears in both indication and contraindication sources:
- keep the pair in the raw annotation table
- mark conflict_flag = 1
- do not silently delete the pair
- analyze conflicts separately in reports and case studies if needed

## 6. Canonical safety annotation file
Safety metrics in Setting B are computed from:

dataset/setting_b/01_annotations/contraindication_pairs.tsv

## 7. Summary
- Setting A remains untouched for fairness to DrKGC.
- Setting B adds safety/constraint analysis without changing the core task.
- Contraindication is an auxiliary safety signal, not a main-task positive label.