# Week 21 Paper Positioning Summary

## Headline

FOG-RAG main slightly leads locked-test MRR@20 while ComplEx leads Gold@20.

## Locked-test key numbers

| Row | Gold@20 | MRR@20 | H@1 | H@3 | H@10 |
|---|---:|---:|---:|---:|---:|
| Backbone raw | 0.240 | 0.064563 | - | - | - |
| ComplEx | 0.574 | 0.124731 | 0.032 | 0.118 | 0.384 |
| FOG-RAG main | 0.240 | 0.125326 | 0.072 | 0.166 | 0.222 |

## Main deltas

- FOG-RAG main minus backbone MRR@20: +0.060763
- FOG-RAG main minus ComplEx MRR@20: +0.000595
- FOG-RAG main minus ComplEx Gold@20: -0.334

## Graph efficiency

- Avg. subgraph size soft/backbone: 59.93
- Avg. subgraph size retrieval main: 32.34
- Reduction: 27.59 triples/query

## Safe paper stance

FOG-RAG main achieves the highest locked-test reviewer-safe MRR@20, slightly above ComplEx, while ComplEx has much higher Gold@20. Therefore, the paper should emphasize that FOG-RAG improves rank placement and evidence-aware retrieval within the DrKGC-compatible pipeline, not that it universally dominates structure-only retrievers.
