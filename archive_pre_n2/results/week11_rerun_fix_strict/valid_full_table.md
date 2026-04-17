# Valid Full Evaluation Table

| Variant | MRR | Hits@1 | Hits@3 | Hits@10 | SafetyViolation@10 | Contra@10 | ConstraintViolationRate | QueryHasConstraintViolationRate | AvgCandidateSize | AvgSubgraphSize | GoldInTopKRate | GoldInjectedRate | PredInCandidateRate | MeanPredRank | CandidateCountFinal | SettingB_GoldInTopKRate | QueryHasContraCandidateRate | NumContraCandidates | StrictEmptyRate | FallbackRate | ΔMRR_vs_Backbone | ΔHits@10_vs_Backbone |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Backbone | 0.4242 | 0.3680 | 0.3940 | 0.5100 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 20.0000 | 60.4500 | 1.0000 | 0.8080 | 0.9920 | 10.7320 | 20.0000 | 1.0000 | 0.0140 | 0.0140 | - | - | 0.0000 | 0.0000 |
| + Ontology | 0.3687 | 0.1760 | 0.4540 | 0.8460 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 7.6500 | 60.4500 | 0.2360 | 0.8080 | 0.9920 | 6.2600 | 7.6500 | 0.2360 | 0.0100 | 0.0100 | - | - | -0.0555 | 0.3360 |
| + Ontology + Hard | 0.4675 | 0.2940 | 0.5380 | 0.9220 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 8.1840 | 10.5740 | 0.3120 | 0.8080 | 1.0000 | 4.7300 | 8.1840 | 0.3120 | 0.0000 | 0.0000 | 0.0000 | 0.0260 | 0.0432 | 0.4120 |
| + Ontology + Soft | 0.4322 | 0.2460 | 0.5180 | 0.9000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 7.8360 | 9.8500 | 0.2920 | 0.8080 | 1.0000 | 5.1220 | 7.8360 | 0.2920 | 0.0100 | 0.0100 | - | - | 0.0080 | 0.3900 |
