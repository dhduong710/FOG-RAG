# Day 1 Week 5 Decision

## 1. Week-5 role
Week 5 is the first full **Setting-A backbone reproduction** week.
This is **not** a metric-chasing week.

## 2. Locked decisions
- 1. Week-5 goal is full Setting-A backbone reproduction, not metric chasing.
- 2. Local machine is debug/pilot only.
- 3. Server is the only place for full backbone runs.
- 4. Primary week-5 LLM = Llama-3.2-3B.
- 5. Primary structural embedding source = R-GCN export for Setting A.
- 6. No fuzzy / safety module is enabled in the main training path this week.
- 7. No second LLM branch unless the first full run is stable.

## 3. Why these decisions are frozen today
- Month 1 already confirmed that the pilot pipeline works.
- Week 5 must now move from pilot artifacts to the first real full-Setting-A backbone path.
- Local and server must not be mixed.
- No fuzzy or safety extension should be enabled before the backbone path is stable.

## 4. Frozen compute split
### Local
- debug only
- dry run only
- small subset infer only
- bug reproduction only
- primary model: TinyLlama-1.1B

### Server
- full backbone train
- full valid infer
- real checkpointing
- primary model: Llama-3.2-3B

## 5. Month-1 prerequisite summary
- split sizes: {'train': 8388, 'valid': 500, 'test': 500}
- split seed: 2025
- candidate K: 20
- candidate type: drug
- pilot leak (valid/test): 0 / 0
- enriched graph triples: 136351
- enriched graph entities: 10453
- enriched graph relations: ['associated_with', 'indication', 'ppi', 'target']

## 6. Input-freeze checks
- [x] split_train_ok
- [x] split_valid_ok
- [x] split_test_ok
- [x] split_seed_ok
- [x] candidate_k_ok
- [x] candidate_type_drug_ok
- [x] candidate_gold_included_ok
- [x] pilot_valid_leak_zero_ok
- [x] pilot_test_leak_zero_ok
- [x] graph_total_triples_ok
- [x] graph_num_entities_ok
- [x] graph_num_rel_types_ok
- [x] graph_relations_ok

## 7. Current judgment
**READY** to enter week-5 day-2 backbone-ready packaging.

## 8. Next action for day 2
Create `dataset/setting_a/08_backbone_ready/` cleanly from the frozen month-1 artifacts,
without mixing pilot-ready and full-ready paths.
