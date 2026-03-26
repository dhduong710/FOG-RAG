# Schema Validation Report

## 1. Frozen schema rules
- indication: Drug -> Disease
- contraindication: Drug -> Disease
- target: Drug -> Protein_or_Gene
- associated_with: Protein_or_Gene -> Disease
- ppi: Protein_or_Gene -> Protein_or_Gene

## 2. Relation counts observed
- associated_with: 96542
- indication: 26164
- ppi: 147122
- target: 12262

## 3. Checked relation counts
- associated_with: 96542
- indication: 26164
- ppi: 147122
- target: 12262

## 4. Violation summary
- total checked triples: 282090
- total schema violations: 0

## 5. Path policy
- valid treatment evidence paths include target/associated_with and target/ppi/associated_with
- contraindication is retained for safety lookup but is invalid as supportive treatment explanation

## 6. Output files
- schema rules: `dataset/setting_b/01_annotations/schema_rules.json`
- path templates: `dataset/setting_b/01_annotations/path_templates.yaml`
- violations: `dataset/setting_b/01_annotations/schema_violations.tsv`