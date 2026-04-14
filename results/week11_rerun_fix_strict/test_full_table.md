# Test Full Evaluation Table

| Variant | MRR | Hits@1 | Hits@3 | Hits@10 | SafetyViolation@10 | Contra@10 | ConstraintViolationRate | QueryHasConstraintViolationRate | AvgCandidateSize | AvgSubgraphSize | GoldInTopKRate | GoldInjectedRate | PredInCandidateRate | MeanPredRank | CandidateCountFinal | SettingB_GoldInTopKRate | QueryHasContraCandidateRate | NumContraCandidates | StrictEmptyRate | FallbackRate | ΔMRR_vs_Backbone | ΔHits@10_vs_Backbone |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Backbone | 0.3931 | 0.3300 | 0.3580 | 0.5240 | 0.0060 | 0.0060 | 0.0000 | 0.0000 | 20.0000 | 59.9320 | 1.0000 | 0.7620 | 0.9840 | 10.8720 | 20.0000 | 1.0000 | 0.0000 | 0.0140 | - | - | 0.0000 | 0.0000 |
| + Ontology | 0.4355 | 0.2600 | 0.4860 | 0.9360 | 0.0060 | 0.0060 | 0.0000 | 0.0000 | 7.7300 | 9.2340 | 0.2800 | 0.7620 | 0.9960 | 4.8760 | 7.7300 | 0.2800 | 0.0000 | 0.0120 | - | - | 0.0424 | 0.4120 |
| + Ontology + Hard | 0.4489 | 0.2900 | 0.4800 | 0.9320 | 0.0020 | 0.0020 | 0.0000 | 0.0000 | 8.2780 | 10.2840 | 0.3100 | 0.7620 | 0.9960 | 4.9240 | 8.2780 | 0.3100 | 0.0000 | 0.0020 | - | - | 0.0558 | 0.4080 |
| + Ontology + Soft | 0.4172 | 0.2400 | 0.4680 | 0.9180 | 0.0020 | 0.0020 | 0.0000 | 0.0000 | 7.7300 | 9.2340 | 0.2800 | 0.7620 | 0.9960 | 5.1760 | 7.7300 | 0.2800 | 0.0000 | 0.0120 | - | - | 0.0241 | 0.3940 |
