# Week 6 - Day 1 Protocol Lock

## 1. Day-1 objective
Replace the current mock-like candidate source **at the protocol level first**,
while keeping the backbone path fixed.

## 2. Frozen backbone from week 5
- LLM: `meta-llama/Llama-3.2-3B`
- Graph branch: `existing week5 graph branch`
- Entity embeddings: `dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt`
- K: `20`
- tau: `100`
- LR: `0.0002`
- LoRA: `32/32/0.1`

## 3. Fixed decisions
1. Week-6 goal is to replace the current mock-like candidate source.
2. Primary coarse ranker = R-GCN-based scorer on Setting A.
3. Candidate universe is Drug-only.
4. Candidate size remains K = 20.
5. Backbone path remains Llama-3.2-3B + existing graph branch.
6. Fuzzy and safety modules remain disabled in the main path.
7. Valid is the only split used for scientific checking this week.
8. Test remains untouched until valid becomes non-degenerate.

## 4. Candidate artifact separation
### top20_raw
- direct artifact for candidate retrieval quality
- no gold injection
- used for recall@20, top1 ratio, rank distribution, type purity

### top20_drkgc_ready
- artifact for DrKGC-style reranking
- gold injection allowed when necessary
- inject count / inject ratio must be logged clearly

## 5. Scientific checking policy
- valid only for scientific checking this week
- test untouched until valid becomes non-degenerate
- fuzzy disabled in main path
- safety disabled in main path

## 6. Required input audit
| name | path | exists | required | note |
|---|---|---|---|---|
| train_graph | `dataset/setting_a/02_graph/train_enriched.tsv` | OK | yes | Training graph thật dùng để train/export coarse ranker. |
| split_train | `dataset/setting_a/01_split/train.tsv` | OK | yes | Split train của Setting A. |
| split_valid | `dataset/setting_a/01_split/valid.tsv` | OK | yes | Split valid của Setting A. |
| split_test | `dataset/setting_a/01_split/test.tsv` | OK | yes | Split test của Setting A (không dùng để tuning tuần 6). |
| entity2id | `dataset/setting_a/04_drkgc_json/entity2id.pkl` | OK | yes | ID map đã khóa từ tuần 2/5. |
| id2entity | `dataset/setting_a/04_drkgc_json/id2entity.pkl` | OK | yes | ID map ngược. |
| relation2id | `dataset/setting_a/04_drkgc_json/relation2id.pkl` | OK | yes | Relation map. |
| id2relation | `dataset/setting_a/04_drkgc_json/id2relation.pkl` | OK | yes | Relation map ngược. |
| week5_backbone_train_json | `dataset/setting_a/08_backbone_ready/train.json` | OK | yes | Backbone-ready package tuần 5 để đối chiếu. |
| week5_backbone_valid_json | `dataset/setting_a/08_backbone_ready/valid.json` | OK | yes | Backbone-ready package tuần 5 để đối chiếu. |
| week5_backbone_test_json | `dataset/setting_a/08_backbone_ready/test.json` | OK | yes | Backbone-ready package tuần 5 để đối chiếu. |
| week5_rgcn_embedding | `dataset/setting_a/08_backbone_ready/entity_embeddings_rgcn.pt` | OK | yes | Embedding thật tuần 5, tuần 6 vẫn reuse. |
| week5_manifest | `dataset/setting_a/08_backbone_ready/backbone_ready_manifest.json` | OK | no | Nếu có thì đọc để tham khảo metadata. |

## 7. Day-1 outputs
- `reports/week6/day1_week6_protocol.md`
- `dataset/setting_a/09_real_coarse_ranker/week6_protocol.json`

## 8. Expected week-6 outputs
- `dataset/setting_a/09_real_coarse_ranker/train_scores.pt`
- `dataset/setting_a/09_real_coarse_ranker/valid_scores.pt`
- `dataset/setting_a/09_real_coarse_ranker/test_scores.pt`
- `dataset/setting_a/09_real_coarse_ranker/train_top20_raw.json`
- `dataset/setting_a/09_real_coarse_ranker/valid_top20_raw.json`
- `dataset/setting_a/09_real_coarse_ranker/test_top20_raw.json`
- `dataset/setting_a/09_real_coarse_ranker/train_top20_drkgc_ready.json`
- `dataset/setting_a/09_real_coarse_ranker/valid_top20_drkgc_ready.json`
- `dataset/setting_a/09_real_coarse_ranker/test_top20_drkgc_ready.json`
- `dataset/setting_a/09_real_coarse_ranker/candidate_recall_report.json`
- `dataset/setting_a/10_backbone_ready_real/train.json`
- `dataset/setting_a/10_backbone_ready_real/valid.json`
- `dataset/setting_a/10_backbone_ready_real/test.json`
- `dataset/setting_a/10_backbone_ready_real/backbone_ready_real_manifest.json`

## 9. End-of-day self-check
- Can I explain the difference between `top20_raw` and `top20_drkgc_ready`?
- Am I keeping the backbone path unchanged from week 5?
- Am I using valid only for scientific checking?
- Is test still untouched?
- Have I stated explicitly whether gold injection is allowed, where, and how it will be logged?

## 10. Warning conditions
- Mixing candidate retrieval evaluation with reranker evaluation
- Rebuilding JSON without preserving a raw top20 artifact
- Touching test before valid becomes non-degenerate
- Changing LLM / graph branch / hyperparameters at the same time as candidate source
