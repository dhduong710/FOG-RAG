# Week 11 Strict Fresh Rerun Report

## 1. Evaluation policy
- This report does not reuse old metric files from `results/week11` or `results/week11_test`.
- Ranking metrics are read from rerun outputs after the inference split fix.
- Safety and constraint metrics are recomputed directly from Setting B eval JSON files.

## 2. Official valid summary
- **Backbone**: MRR=0.4242, Hits@1=0.3680, Hits@3=0.3940, Hits@10=0.5100, SafetyViolation@10=0.0000, Contra@10=0.0000, ConstraintViolationRate=0.0000
- **+ Ontology**: MRR=0.3687, Hits@1=0.1760, Hits@3=0.4540, Hits@10=0.8460, SafetyViolation@10=0.0000, Contra@10=0.0000, ConstraintViolationRate=0.0000
- **+ Ontology + Hard**: MRR=0.4675, Hits@1=0.2940, Hits@3=0.5380, Hits@10=0.9220, SafetyViolation@10=0.0000, Contra@10=0.0000, ConstraintViolationRate=0.0000
- **+ Ontology + Soft**: MRR=0.4322, Hits@1=0.2460, Hits@3=0.5180, Hits@10=0.9000, SafetyViolation@10=0.0000, Contra@10=0.0000, ConstraintViolationRate=0.0000

## 3. Official test summary
- **Backbone**: MRR=0.3931, Hits@1=0.3300, Hits@3=0.3580, Hits@10=0.5240, SafetyViolation@10=0.0060, Contra@10=0.0060, ConstraintViolationRate=0.0000
- **+ Ontology**: MRR=0.4355, Hits@1=0.2600, Hits@3=0.4860, Hits@10=0.9360, SafetyViolation@10=0.0060, Contra@10=0.0060, ConstraintViolationRate=0.0000
- **+ Ontology + Hard**: MRR=0.4489, Hits@1=0.2900, Hits@3=0.4800, Hits@10=0.9320, SafetyViolation@10=0.0020, Contra@10=0.0020, ConstraintViolationRate=0.0000
- **+ Ontology + Soft**: MRR=0.4172, Hits@1=0.2400, Hits@3=0.4680, Hits@10=0.9180, SafetyViolation@10=0.0020, Contra@10=0.0020, ConstraintViolationRate=0.0000

## 4. Main decision
- Main row: **+ Ontology + Hard**
- Supporting row: **+ Ontology + Soft**

## 5. Reason
- `+ Ontology + Hard` remains the strongest main row by overall ranking trade-off after the split fix.
- All numbers in this report are regenerated after the fix.
