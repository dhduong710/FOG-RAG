# Day 2 — Ranker v2 training

## Scope

- Train a more stable R-GCN coarse ranker v2 for Setting A.
- Keep graph source, relation, and drug-only candidate universe fixed.
- Improve optimization stability and score discrimination.

## Config decisions

- graph source: `dataset/setting_a/02_graph/train_enriched_deg1000_final.tsv`
- relation: `indication`
- candidate universe: `drug_only`
- learning rate: `5e-05`
- batch size: `512`
- negatives per query: `32`
- grad clip norm: `1.0`
- seed: `2025`

## Best checkpoint summary

- best_epoch = `17`
- valid_probe_recall20 = `0.260000`
- valid_probe_top1_hit_ratio = `0.010000`
- valid_probe_unique_top1_count = `3`
- valid_probe_top1_dominance_ratio = `0.500000`
- pos_score_mean = `0.319475`
- neg_score_mean = `-1.390278`
- score_gap_mean = `1.709752`
- stopped_early = `True`

## Last logged rows

- `{"epoch": 16, "global_step": 272, "avg_epoch_loss": 0.6207257313107557, "avg_grad_norm": 0.7387772763476652, "pos_score_mean": 0.31827133893966675, "pos_score_std": 1.1724880933761597, "neg_score_mean": -1.3185056447982788, "neg_score_std": 3.345008611679077, "score_gap_mean": 1.6367770433425903, "score_gap_std": 3.847839593887329, "valid_probe_recall20": 0.21, "valid_probe_top1_hit_ratio": 0.0, "valid_probe_unique_top1_count": 3, "valid_probe_top1_dominance_ratio": 0.48}`
- `{"epoch": 17, "global_step": 289, "avg_epoch_loss": 0.590851648370027, "avg_grad_norm": 0.749130575095906, "pos_score_mean": 0.31947460770606995, "pos_score_std": 1.122566819190979, "neg_score_mean": -1.390277624130249, "neg_score_std": 3.510223388671875, "score_gap_mean": 1.7097523212432861, "score_gap_std": 3.909850835800171, "valid_probe_recall20": 0.26, "valid_probe_top1_hit_ratio": 0.01, "valid_probe_unique_top1_count": 3, "valid_probe_top1_dominance_ratio": 0.5}`
- `{"epoch": 18, "global_step": 306, "avg_epoch_loss": 0.5567426716764029, "avg_grad_norm": 0.7527169024243074, "pos_score_mean": 0.3316386640071869, "pos_score_std": 1.11282217502594, "neg_score_mean": -1.4566960334777832, "neg_score_std": 3.595811605453491, "score_gap_mean": 1.7883347272872925, "score_gap_std": 3.921095848083496, "valid_probe_recall20": 0.19, "valid_probe_top1_hit_ratio": 0.0, "valid_probe_unique_top1_count": 3, "valid_probe_top1_dominance_ratio": 0.5}`
- `{"epoch": 19, "global_step": 323, "avg_epoch_loss": 0.5245711924095181, "avg_grad_norm": 0.7509807663805345, "pos_score_mean": 0.3464593291282654, "pos_score_std": 1.1500710248947144, "neg_score_mean": -1.4979565143585205, "neg_score_std": 3.6292145252227783, "score_gap_mean": 1.8444161415100098, "score_gap_std": 3.857356071472168, "valid_probe_recall20": 0.15, "valid_probe_top1_hit_ratio": 0.03, "valid_probe_unique_top1_count": 3, "valid_probe_top1_dominance_ratio": 0.47}`
- `{"epoch": 20, "global_step": 340, "avg_epoch_loss": 0.4957536057909728, "avg_grad_norm": 0.723185889861163, "pos_score_mean": 0.3498815596103668, "pos_score_std": 1.1918582916259766, "neg_score_mean": -1.557698369026184, "neg_score_std": 3.7360599040985107, "score_gap_mean": 1.9075798988342285, "score_gap_std": 3.7975001335144043, "valid_probe_recall20": 0.15, "valid_probe_top1_hit_ratio": 0.03, "valid_probe_unique_top1_count": 3, "valid_probe_top1_dominance_ratio": 0.52}`
- `{"epoch": 21, "global_step": 357, "avg_epoch_loss": 0.4697328780768426, "avg_grad_norm": 0.6712165229460773, "pos_score_mean": 0.3848683834075928, "pos_score_std": 1.266811490058899, "neg_score_mean": -1.5953487157821655, "neg_score_std": 3.8098812103271484, "score_gap_mean": 1.9802170991897583, "score_gap_std": 3.7385621070861816, "valid_probe_recall20": 0.2, "valid_probe_top1_hit_ratio": 0.02, "valid_probe_unique_top1_count": 4, "valid_probe_top1_dominance_ratio": 0.49}`
- `{"epoch": 22, "global_step": 374, "avg_epoch_loss": 0.45317773054086086, "avg_grad_norm": 0.6617027836687425, "pos_score_mean": 0.42153200507164, "pos_score_std": 1.4023481607437134, "neg_score_mean": -1.6462477445602417, "neg_score_std": 3.9116017818450928, "score_gap_mean": 2.067779541015625, "score_gap_std": 3.742837905883789, "valid_probe_recall20": 0.21, "valid_probe_top1_hit_ratio": 0.03, "valid_probe_unique_top1_count": 5, "valid_probe_top1_dominance_ratio": 0.44}`
- `{"epoch": 23, "global_step": 391, "avg_epoch_loss": 0.4362881573029911, "avg_grad_norm": 0.6438489030389225, "pos_score_mean": 0.4652668237686157, "pos_score_std": 1.5284885168075562, "neg_score_mean": -1.7098605632781982, "neg_score_std": 4.065587997436523, "score_gap_mean": 2.1751275062561035, "score_gap_std": 3.8217532634735107, "valid_probe_recall20": 0.21, "valid_probe_top1_hit_ratio": 0.02, "valid_probe_unique_top1_count": 6, "valid_probe_top1_dominance_ratio": 0.48}`
- `{"epoch": 24, "global_step": 408, "avg_epoch_loss": 0.42483278385616224, "avg_grad_norm": 0.6357017965877757, "pos_score_mean": 0.5026941299438477, "pos_score_std": 1.6555235385894775, "neg_score_mean": -1.7956510782241821, "neg_score_std": 4.32465934753418, "score_gap_mean": 2.2983450889587402, "score_gap_std": 3.996108055114746, "valid_probe_recall20": 0.21, "valid_probe_top1_hit_ratio": 0.01, "valid_probe_unique_top1_count": 5, "valid_probe_top1_dominance_ratio": 0.51}`
- `{"epoch": 25, "global_step": 425, "avg_epoch_loss": 0.41555015564419623, "avg_grad_norm": 0.6588086240431842, "pos_score_mean": 0.5488584041595459, "pos_score_std": 1.7629863023757935, "neg_score_mean": -1.8620705604553223, "neg_score_std": 4.531150817871094, "score_gap_mean": 2.410928726196289, "score_gap_std": 4.147103786468506, "valid_probe_recall20": 0.23, "valid_probe_top1_hit_ratio": 0.02, "valid_probe_unique_top1_count": 7, "valid_probe_top1_dominance_ratio": 0.45}`

## Conclusion

- Check whether train loss is cleaner than week 6.
- Check whether pos_score_mean is above neg_score_mean.
- Check whether top1 dominance on valid probe is lower than the collapsed week-6 pattern.
- If the checkpoint is stable and score stats are sensible, move to Day 3 to build candidate artifacts.
