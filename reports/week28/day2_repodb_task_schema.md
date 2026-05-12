# Week 28 Day 2  repoDB normalization and task schema freeze

- Decision: `DAY2_REPODB_TASK_SCHEMA_READY`
- Task: `(?, repoDB_approved_indication, disease)`
- Target relation: `repoDB::approved_indication::Compound:Disease`

## Normalization summary

```json
{
  "created_at": "2026-05-12T01:21:27.344899+00:00",
  "raw_rows": 10800,
  "raw_columns": [
    "Drug",
    "Indication",
    "drug_name",
    "drug_id",
    "ind_name",
    "ind_id",
    "sem_type",
    "TrialStatus",
    "status",
    "phase",
    "DetailedStatus"
  ],
  "label_counts_raw": {
    "approved": 6677,
    "failed_like": 4123
  },
  "valid_drugbank_and_cui_counts": {
    "True": 10800
  },
  "approved_unique_pairs": 6677,
  "failed_like_unique_pairs_before_conflict_removal": 3281,
  "failed_like_unique_pairs_after_conflict_removal": 3260,
  "conflict_pair_count": 21,
  "unique_approved_drugs": 1519,
  "unique_approved_diseases": 1229,
  "unique_failed_drugs": 458,
  "unique_failed_diseases": 989,
  "target_relation": "repoDB::approved_indication::Compound:Disease",
  "failed_diagnostic_relation": "repoDB::failed_or_suspended::Compound:Disease"
}
```

## Split feasibility

```json
{
  "decision": "SPLIT_SIZE_FEASIBLE",
  "recommended_valid_size": 500,
  "recommended_test_size": 500,
  "recommended_train_size": 5677,
  "attempts": [
    {
      "requested_valid_size": 500,
      "requested_test_size": 500,
      "requested_holdout": 1000,
      "feasible": true,
      "attempt_used": 0,
      "actual_holdout_possible": 1000,
      "projected_train_size": 5677,
      "projected_valid_size": 500,
      "projected_test_size": 500,
      "coverage_policy": "valid/test drugs and diseases remain in train approved target relation"
    }
  ]
}
```

## Mapping probe to DRKG

```json
{
  "drkg_entity_map_found": true,
  "drkg_num_entities": 13918,
  "num_unique_compounds_repodb": 1571,
  "num_unique_diseases_repodb": 2051,
  "num_unique_approved_compounds": 1519,
  "num_unique_approved_diseases": 1229,
  "compound_exact_hits_in_drkg": 1130,
  "compound_exact_hit_rate": 0.7192870782940802,
  "approved_compound_exact_hits_in_drkg": 1106,
  "approved_compound_exact_hit_rate": 0.728110599078341,
  "disease_exact_umls_hits_in_drkg": 0,
  "disease_any_exact_hits_in_drkg": 0,
  "disease_any_exact_hit_rate": 0.0,
  "sample_compound_hits": [
    "Compound::DB00003",
    "Compound::DB00004",
    "Compound::DB00005",
    "Compound::DB00007",
    "Compound::DB00008",
    "Compound::DB00009",
    "Compound::DB00012",
    "Compound::DB00013",
    "Compound::DB00014",
    "Compound::DB00015",
    "Compound::DB00016",
    "Compound::DB00017",
    "Compound::DB00019",
    "Compound::DB00020",
    "Compound::DB00022",
    "Compound::DB00023",
    "Compound::DB00026",
    "Compound::DB00027",
    "Compound::DB00030",
    "Compound::DB00031"
  ],
  "sample_compound_misses": [
    "Compound::DB00001",
    "Compound::DB00002",
    "Compound::DB00010",
    "Compound::DB00041",
    "Compound::DB00074",
    "Compound::DB00088",
    "Compound::DB00092",
    "Compound::DB00095",
    "Compound::DB00106",
    "Compound::DB00111",
    "Compound::DB00112",
    "Compound::DB00121",
    "Compound::DB00122",
    "Compound::DB00128",
    "Compound::DB00130",
    "Compound::DB00131",
    "Compound::DB00133",
    "Compound::DB00137",
    "Compound::DB00139",
    "Compound::DB00145"
  ],
  "sample_disease_hits": [],
  "sample_disease_misses": [
    "Disease::UMLS:C0000810",
    "Disease::UMLS:C0000814",
    "Disease::UMLS:C0001126",
    "Disease::UMLS:C0001127",
    "Disease::UMLS:C0001144",
    "Disease::UMLS:C0001206",
    "Disease::UMLS:C0001207",
    "Disease::UMLS:C0001261",
    "Disease::UMLS:C0001263",
    "Disease::UMLS:C0001264",
    "Disease::UMLS:C0001314",
    "Disease::UMLS:C0001403",
    "Disease::UMLS:C0001418",
    "Disease::UMLS:C0001622",
    "Disease::UMLS:C0001624",
    "Disease::UMLS:C0001627",
    "Disease::UMLS:C0001723",
    "Disease::UMLS:C0001815",
    "Disease::UMLS:C0001956",
    "Disease::UMLS:C0001957"
  ],
  "disease_form_hits_sample": {}
}
```

## Protocol decision

```text
Positive target = approved repoDB drug-indication pairs.
Failed-like pairs are reserved as diagnostic/negative evidence, not positive labels.
Candidate universe = approved-training DrugBank compounds.
Entity format = Compound::DBxxxxx and Disease::UMLS:Cxxxxxxx.
No valid/test gold injection.
```

## Day 3 next step

Day 3 should build the actual coverage-safe split and construct a repoDB evidence graph. If disease CUI mapping to DRKG is weak, use repoDB-local disease nodes and reuse DRKG evidence mainly on the drug side.
