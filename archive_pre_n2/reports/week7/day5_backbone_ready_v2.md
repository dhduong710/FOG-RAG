# Day 5 — backbone-ready v2 packaging

## Scope

- Convert week7 drkgc-ready candidates into ranked_input JSON.
- Reuse prompt_subgraph.py to build final train/valid/test with prompt + subgraph.
- Preserve exact leakage checks in the same way as the stable earlier pipeline.

## Inputs

- train_candidate_ready_json: `dataset/setting_a/11_ranker_v2/train_top20_drkgc_ready.json`
- valid_candidate_ready_json: `dataset/setting_a/11_ranker_v2/valid_top20_drkgc_ready.json`
- test_candidate_ready_json: `dataset/setting_a/11_ranker_v2/test_top20_drkgc_ready.json`
- train_graph_tsv: `dataset/setting_a/02_graph/train_enriched_deg1000_final.tsv`
- valid_split_tsv: `dataset/setting_a/01_split/valid.tsv`
- test_split_tsv: `dataset/setting_a/01_split/test.tsv`
- graph_size: `100`

## Outputs

- `dataset/setting_a/12_backbone_ready_ranker_v2/train.json`
- `dataset/setting_a/12_backbone_ready_ranker_v2/valid.json`
- `dataset/setting_a/12_backbone_ready_ranker_v2/test.json`
- `dataset/setting_a/12_backbone_ready_ranker_v2/manifest.json`
- prompt_subgraph log: `reports/week7/day5_prepare_backbone_ready_v2.log`

## Notes

- Day 5 is a packaging day only.
- Exact leakage validation is delegated to prompt_subgraph.py.
- Day 6 will decide whether candidate improvement transfers to valid reranker behavior.
