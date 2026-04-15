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
- seed: `3407`

## Best checkpoint summary

- best_epoch = `16`
- valid_probe_recall20 = `0.270000`
- valid_probe_top1_hit_ratio = `0.050000`
- valid_probe_unique_top1_count = `3`
- valid_probe_top1_dominance_ratio = `0.630000`
- pos_score_mean = `1.286772`
- neg_score_mean = `-0.362830`
- score_gap_mean = `1.649602`
- stopped_early = `True`

## Last logged rows

- `{"epoch": 15, "global_step": 255, "avg_epoch_loss": 0.6344824109295748, "avg_grad_norm": 0.74289089791915, "pos_score_mean": 1.2197201251983643, "pos_score_std": 2.270641565322876, "neg_score_mean": -0.32351091504096985, "neg_score_std": 2.227996349334717, "score_gap_mean": 1.5432310104370117, "score_gap_std": 3.6172022819519043, "valid_probe_recall20": 0.2, "valid_probe_top1_hit_ratio": 0.0, "valid_probe_unique_top1_count": 3, "valid_probe_top1_dominance_ratio": 0.53}`
- `{"epoch": 16, "global_step": 272, "avg_epoch_loss": 0.5981656073330127, "avg_grad_norm": 0.7604339333141551, "pos_score_mean": 1.2867722511291504, "pos_score_std": 2.2431352138519287, "neg_score_mean": -0.36282971501350403, "neg_score_std": 2.375532388687134, "score_gap_mean": 1.6496020555496216, "score_gap_std": 3.7302446365356445, "valid_probe_recall20": 0.27, "valid_probe_top1_hit_ratio": 0.05, "valid_probe_unique_top1_count": 3, "valid_probe_top1_dominance_ratio": 0.63}`
- `{"epoch": 17, "global_step": 289, "avg_epoch_loss": 0.5568083086125215, "avg_grad_norm": 0.758965411606957, "pos_score_mean": 1.3022905588150024, "pos_score_std": 2.0426321029663086, "neg_score_mean": -0.4117915630340576, "neg_score_std": 2.455678701400757, "score_gap_mean": 1.71408212184906, "score_gap_std": 3.6750118732452393, "valid_probe_recall20": 0.25, "valid_probe_top1_hit_ratio": 0.06, "valid_probe_unique_top1_count": 2, "valid_probe_top1_dominance_ratio": 0.7}`
- `{"epoch": 18, "global_step": 306, "avg_epoch_loss": 0.517876442040383, "avg_grad_norm": 0.7328256473821753, "pos_score_mean": 1.3078802824020386, "pos_score_std": 1.876640796661377, "neg_score_mean": -0.47747549414634705, "neg_score_std": 2.5608880519866943, "score_gap_mean": 1.785356044769287, "score_gap_std": 3.6728711128234863, "valid_probe_recall20": 0.15, "valid_probe_top1_hit_ratio": 0.01, "valid_probe_unique_top1_count": 3, "valid_probe_top1_dominance_ratio": 0.54}`
- `{"epoch": 19, "global_step": 323, "avg_epoch_loss": 0.48711220981907605, "avg_grad_norm": 0.6776244149488562, "pos_score_mean": 1.3115967512130737, "pos_score_std": 1.663659691810608, "neg_score_mean": -0.5386749505996704, "neg_score_std": 2.6657373905181885, "score_gap_mean": 1.8502715826034546, "score_gap_std": 3.54957914352417, "valid_probe_recall20": 0.22, "valid_probe_top1_hit_ratio": 0.04, "valid_probe_unique_top1_count": 4, "valid_probe_top1_dominance_ratio": 0.34}`
- `{"epoch": 20, "global_step": 340, "avg_epoch_loss": 0.46659982514256343, "avg_grad_norm": 0.6726639095474692, "pos_score_mean": 1.300459384918213, "pos_score_std": 1.5695860385894775, "neg_score_mean": -0.6238352656364441, "neg_score_std": 2.829481840133667, "score_gap_mean": 1.9242944717407227, "score_gap_std": 3.5019004344940186, "valid_probe_recall20": 0.18, "valid_probe_top1_hit_ratio": 0.02, "valid_probe_unique_top1_count": 4, "valid_probe_top1_dominance_ratio": 0.43}`
- `{"epoch": 21, "global_step": 357, "avg_epoch_loss": 0.44889619862629676, "avg_grad_norm": 0.6572008097873014, "pos_score_mean": 1.3460252285003662, "pos_score_std": 1.6005655527114868, "neg_score_mean": -0.6964244246482849, "neg_score_std": 3.079850196838379, "score_gap_mean": 2.042449712753296, "score_gap_std": 3.6332521438598633, "valid_probe_recall20": 0.21, "valid_probe_top1_hit_ratio": 0.01, "valid_probe_unique_top1_count": 5, "valid_probe_top1_dominance_ratio": 0.44}`
- `{"epoch": 22, "global_step": 374, "avg_epoch_loss": 0.4336697746869434, "avg_grad_norm": 0.6535235433017507, "pos_score_mean": 1.401702642440796, "pos_score_std": 1.6898612976074219, "neg_score_mean": -0.7513540983200073, "neg_score_std": 3.2782580852508545, "score_gap_mean": 2.1530566215515137, "score_gap_std": 3.7393805980682373, "valid_probe_recall20": 0.16, "valid_probe_top1_hit_ratio": 0.01, "valid_probe_unique_top1_count": 5, "valid_probe_top1_dominance_ratio": 0.46}`
- `{"epoch": 23, "global_step": 391, "avg_epoch_loss": 0.42036458218899236, "avg_grad_norm": 0.637163916054894, "pos_score_mean": 1.458877444267273, "pos_score_std": 1.7755751609802246, "neg_score_mean": -0.8276078701019287, "neg_score_std": 3.537557363510132, "score_gap_mean": 2.286485433578491, "score_gap_std": 3.9313411712646484, "valid_probe_recall20": 0.25, "valid_probe_top1_hit_ratio": 0.0, "valid_probe_unique_top1_count": 5, "valid_probe_top1_dominance_ratio": 0.44}`
- `{"epoch": 24, "global_step": 408, "avg_epoch_loss": 0.4130897710848605, "avg_grad_norm": 0.6604143275934107, "pos_score_mean": 1.5390444993972778, "pos_score_std": 1.8775219917297363, "neg_score_mean": -0.8828331828117371, "neg_score_std": 3.791593313217163, "score_gap_mean": 2.421877384185791, "score_gap_std": 4.13254451751709, "valid_probe_recall20": 0.25, "valid_probe_top1_hit_ratio": 0.01, "valid_probe_unique_top1_count": 6, "valid_probe_top1_dominance_ratio": 0.46}`

## Conclusion

- Check whether train loss is cleaner than week 6.
- Check whether pos_score_mean is above neg_score_mean.
- Check whether top1 dominance on valid probe is lower than the collapsed week-6 pattern.
- If the checkpoint is stable and score stats are sensible, move to Day 3 to build candidate artifacts.
