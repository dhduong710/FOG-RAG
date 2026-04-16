# Day 3 — Schema Validity

## 1. Goal
Check schema validity for candidate / path / evidence on the valid split.

## 2. Candidate validity summary
- total_queries_checked: 500
- total_candidates_checked: 10000
- candidate_type_violations: 0
- unknown_candidate_types: 0

## 3. Evidence triple validity summary
- total_queries_checked: 500
- total_evidence_triples_checked: 16594
- valid_evidence_triples: 10549
- invalid_evidence_triples: 6045
- missing_relation_rules: 0
- incomplete_relation_rules: 0

### Top invalid evidence patterns
- Disease -[indication]-> Drug: 3872
- Disease -[associated_with]-> Protein_or_Gene: 1828
- Protein_or_Gene -[target]-> Drug: 345

## 4. Path validity summary
- valid_mechanism_templates_loaded: 2
- invalid_explanation_relations_loaded: 0
- total_path_sequences_checked: 14862
- valid_mechanism_path_sequences: 86
- direct_task_edge_sequences: 1301
- blocked_explanation_sequences: 0
- unsupported_path_sequences: 13475
- queries_with_no_candidate_to_query_path: 4

### Top unsupported path patterns
- indication -> indication -> indication: 7818
- indication -> associated_with -> associated_with: 5626
- target -> target -> indication: 31

### Sample unsupported paths
- query=leukemia, lymphocytic, susceptibility to | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=leukemia, lymphocytic, susceptibility to | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=leukemia, lymphocytic, susceptibility to | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=leukemia, lymphocytic, susceptibility to | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Cortisone acetate | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Hydrocortisone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Dexamethasone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Dexamethasone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Dexamethasone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Dexamethasone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Dexamethasone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Dexamethasone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Dexamethasone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Dexamethasone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Dexamethasone | path=indication -> indication -> indication
- query=streptococcal infection | candidate=Dexamethasone | path=indication -> indication -> indication

## 5. Interpretation
- Direct indication edge is counted separately from mechanism paths.
- Contraindication-style relations are blocked as treatment explanation evidence.
- Unsupported path sequences are not necessarily schema-invalid triples; they are template-unapproved explanation paths.
