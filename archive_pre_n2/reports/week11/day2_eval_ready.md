# Week 11 - Day 2 Eval-Ready Build

## Sources built
### backbone
- num_rows_input: 500
- num_rows_matched: 500
- num_rows_unmatched: 0
- avg_candidate_size: 20.000000
- rows_with_gold_in_topk: 500
- rows_with_any_contra_candidate_final: 7
- candidate_type_distribution_top: [('Drug', 10000)]

### ontology
- num_rows_input: 500
- num_rows_matched: 500
- num_rows_unmatched: 0
- avg_candidate_size: 7.650000
- rows_with_gold_in_topk: 118
- rows_with_any_contra_candidate_final: 5
- candidate_type_distribution_top: [('Drug', 3825)]

### hard_main
- num_rows_input: 500
- num_rows_matched: 500
- num_rows_unmatched: 0
- avg_candidate_size: 8.184000
- rows_with_gold_in_topk: 156
- rows_with_any_contra_candidate_final: 0
- candidate_type_distribution_top: [('Drug', 4092)]

### soft_best
- num_rows_input: 500
- num_rows_matched: 500
- num_rows_unmatched: 0
- avg_candidate_size: 7.836000
- rows_with_gold_in_topk: 146
- rows_with_any_contra_candidate_final: 5
- candidate_type_distribution_top: [('Drug', 3918)]

## Notes
- Day 2 only builds Setting B eval-ready inputs.
- Day 3 will prioritize hard_main valid evaluation.
- Day 4 will evaluate soft_best valid under the same Setting B protocol.
