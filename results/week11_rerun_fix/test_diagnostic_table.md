# Test Diagnostic Table

| Variant | AvgCandidateSize | AvgSubgraphSize | GoldInTopKRate | GoldInjectedRate | PredInCandidateRate | MeanPredRank | SafetyViolation@10 | Contra@10 | ConstraintViolationRate | QueryHasConstraintViolationRate | NumContraCandidates | QueryHasContraCandidateRate | StrictEmptyRate | FallbackRate | CandidateSummary_AvgSize | CandidateSummary_GoldInTopKRate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Backbone | 20.0000 | 59.9320 | 1.0000 | 0.7620 | 0.9840 | 10.8720 | - | - | - | - | - | 0.0000 | - | - | - | - |
| + Ontology | 7.7300 | 9.2340 | 0.2800 | 0.7620 | 0.9960 | 4.8760 | - | - | - | - | - | 0.0000 | - | - | - | - |
| + Ontology + Hard | 8.2780 | 10.2840 | 0.3100 | 0.7620 | 0.9960 | 4.9240 | - | - | - | - | - | 0.0000 | - | - | - | - |
| + Ontology + Soft | 7.7300 | 9.2340 | 0.2800 | 0.7620 | 0.9960 | 5.1760 | - | - | - | - | - | 0.0740 | - | - | - | - |
