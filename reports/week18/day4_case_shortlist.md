# Week 18 Day 4 — Case-study Shortlist

## Bucket counts
- **backbone_to_retrieval_improved_total**: `80`
- **ontology_failure_retrieval_success_total**: `94`
- **same_rank_cleaner_graph_total**: `101`
- **encoder_appendix_cases_total**: `17`

## Selected shortlist
### backbone_to_retrieval_improved
- `mantle cell lymphoma` | gold=`Mechlorethamine` | backbone=20, ontology=21, soft=3, retrieval=3
- `vernal conjunctivitis` | gold=`Phenylephrine` | backbone=20, ontology=21, soft=8, retrieval=8
- `Langerhans cell histiocytosis` | gold=`Bleomycin` | backbone=14, ontology=21, soft=3, retrieval=3
- `primary cutaneous T-cell lymphoma` | gold=`Methotrexate` | backbone=19, ontology=21, soft=8, retrieval=8
- `primary cutaneous T-cell lymphoma` | gold=`Mechlorethamine` | backbone=20, ontology=21, soft=9, retrieval=9

### ontology_failure_retrieval_success
- `leukemia, lymphocytic, susceptibility to` | gold=`Cortisone acetate` | backbone=1, ontology=21, soft=1, retrieval=1
- `acquired thrombocytopenia` | gold=`Cortisone acetate` | backbone=1, ontology=21, soft=1, retrieval=1
- `aspiration pneumonia (disease)` | gold=`Cortisone acetate` | backbone=1, ontology=21, soft=1, retrieval=1
- `psoriasis` | gold=`Cortisone acetate` | backbone=1, ontology=21, soft=1, retrieval=1
- `multiple sclerosis` | gold=`Cortisone acetate` | backbone=1, ontology=21, soft=1, retrieval=1

### same_rank_cleaner_graph
- `punctate epithelial keratoconjunctivitis` | gold=`Fusidic acid` | backbone=1, ontology=1, soft=1, retrieval=1
- `gonorrhea` | gold=`Fusidic acid` | backbone=1, ontology=21, soft=1, retrieval=1
- `dermatophytosis of groin and perianal area` | gold=`Hydrocortisone` | backbone=4, ontology=21, soft=2, retrieval=2
- `infectious anterior uveitis` | gold=`Dexamethasone` | backbone=4, ontology=21, soft=2, retrieval=2
- `conjunctivitis` | gold=`Fusidic acid` | backbone=1, ontology=21, soft=1, retrieval=1

### encoder_appendix_deferred
- `leukemia, lymphocytic, susceptibility to` | gold=`Cortisone acetate` | backbone=NA, ontology=NA, soft=1, retrieval=1
- `diffuse large B-cell lymphoma` | gold=`Doxorubicin` | backbone=NA, ontology=NA, soft=8, retrieval=8
- `infectious anterior uveitis` | gold=`Dexamethasone` | backbone=NA, ontology=NA, soft=2, retrieval=2
- `acquired thrombocytopenia` | gold=`Cortisone acetate` | backbone=NA, ontology=NA, soft=1, retrieval=1
- `aspiration pneumonia (disease)` | gold=`Cortisone acetate` | backbone=NA, ontology=NA, soft=1, retrieval=1

## Notes
- Bucket A highlights cases where the frozen retrieval main row improves over backbone_raw.
- Bucket B highlights ontology-negative-control failure cases rescued by retrieval main.
- Bucket C highlights same-rank cases where retrieval main supports a cleaner graph/evidence narrative.
- Bucket D highlights appendix cases explaining why encoder was deferred after week 17.
