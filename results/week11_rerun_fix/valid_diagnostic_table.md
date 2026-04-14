# Valid Diagnostic Table

| Variant | AvgCandidateSize | AvgSubgraphSize | GoldInTopKRate | GoldInjectedRate | PredInCandidateRate | MeanPredRank | SafetyViolation@10 | Contra@10 | ConstraintViolationRate | QueryHasConstraintViolationRate | NumContraCandidates | QueryHasContraCandidateRate | StrictEmptyRate | FallbackRate | CandidateSummary_AvgSize | CandidateSummary_GoldInTopKRate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Backbone | 20.0000 | 60.4500 | 1.0000 | 0.8080 | 0.9920 | 10.7320 | - | - | - | - | - | - | - | - | - | - |
| + Ontology | 7.6500 | 60.4500 | 0.2360 | 0.8080 | 0.9920 | 6.2600 | - | - | - | - | - | - | - | - | - | - |
| + Ontology + Hard | 8.1840 | 10.5740 | 0.3120 | 0.8080 | 1.0000 | 4.7300 | - | - | - | - | - | - | - | - | - | - |
| + Ontology + Soft | 7.8360 | 9.8500 | 0.2920 | 0.8080 | 1.0000 | 5.1220 | - | - | - | - | - | - | - | - | - | - |
