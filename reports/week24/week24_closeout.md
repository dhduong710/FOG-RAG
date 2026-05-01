# Week 24 Closeout — PrimeKG and PharmKG E2E Finalization

## Final decision

**GO_PAPER_E2E_WITH_LIMITATION**

PrimeKG E2E and PharmKG transfer both show reviewer-safe FOG-RAG improvements over the DrKGC-style raw backbone, and fuzzy retrieval preserves the soft-support gains while reducing subgraph size. However, unconstrained generation and top-1-copy behavior remain important limitations.

## 1. PrimeKG final E2E result

Primary E2E model: **Llama-3.2-3B**

| Row | Gold@20 | Cand MRR | E2E MRR | H@3 | H@10 | Pred-in-cand | Invalid | Top1-copy | Avg graph |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| backbone_raw | 0.240 | 0.064563 | 0.047636 | 0.048 | 0.178 | 0.980 | 0.020 | 0.038 | 59.93 |
| soft_support_raw | 0.240 | 0.125326 | 0.074676 | 0.132 | 0.218 | 0.980 | 0.020 | 0.008 | 59.93 |
| retrieval_main | 0.240 | 0.125326 | 0.074687 | 0.132 | 0.218 | 0.998 | 0.002 | 0.010 | 32.34 |

PrimeKG locked-test E2E MRR improves from `0.047636` on `backbone_raw` to `0.074687` on `retrieval_main`. The retrieved evidence graph is reduced from `59.93` to `32.34` triples.

## 2. PrimeKG model-comparison interpretation

- Metric-best model: `llama3_8b`
- Primary paper E2E model: `llama3_2_3b`
- Larger 8B models are diagnostic because they reach candidate-ceiling behavior through top-1-copy.
- Model comparison tables must include `Top1-copy`.

## 3. PrimeKG retrieval diagnostics

- Same candidate order rate: `1.0`
- Same rank cleaner graph count: `500` / 500
- Average subgraph reduction: `27.592` triples

## 4. PharmKG secondary transfer result

Primary E2E model: **Llama-3.2-3B**

| Row | Gold@20 | Cand MRR | E2E MRR | H@3 | H@10 | Pred-in-cand | Invalid | List-frag | Avg graph |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| backbone_raw | 0.092 | 0.020481 | 0.015575 | 0.018 | 0.044 | 0.504 | 0.496 | 0.490 | 100.00 |
| soft_support_raw | 0.092 | 0.028159 | 0.020587 | 0.030 | 0.062 | 0.390 | 0.610 | 0.604 | 100.00 |
| fuzzy_retrieval_main | 0.092 | 0.028159 | 0.020971 | 0.030 | 0.062 | 0.412 | 0.588 | 0.582 | 55.00 |

On the PharmKG therapeutic-association proxy task, soft support improves the locked-test candidate MRR@20 from 0.020481 to 0.028159. In reviewer-safe E2E evaluation with Llama-3.2-3B, the backbone obtains MRR@20=0.015575, while soft support and fuzzy retrieval reach 0.020587 and 0.020971, respectively. Fuzzy retrieval preserves the ranking trend while reducing the evidence subgraph from 100.00 to 55.00 triples.

## 5. PharmKG limitation

PharmKG remains a difficult secondary transfer benchmark. The top-20 candidate bottleneck is strong, and unconstrained generation frequently produces invalid or fragmentary outputs for the Llama-3.2-3B run. Therefore, PharmKG is reported as transfer evidence for the direction of FOG-RAG improvements, not as a full-universe PharmKG KGC superiority claim.

## 6. What to claim

- FOG-RAG improves reviewer-safe E2E MRR over the DrKGC-style raw backbone on PrimeKG.
- Soft support provides the main ranking gain.
- Fuzzy retrieval preserves the soft-support gain while substantially reducing subgraph size.
- PharmKG supports transferability under a stricter secondary benchmark.
- Larger/base biomedical models need diagnostics because top-1-copy and invalid generation can distort interpretation.

## 7. What not to claim

- Do not claim FOG-RAG improves Gold@20.
- Do not claim full-universe PharmKG superiority.
- Do not call PharmKG relation `T` a clinical indication label.
- Do not select Llama-3-8B as the main E2E model solely because adjusted MRR is highest.
- Do not use raw `infer.py` MRR in the paper.

## 8. Week 25 recommendation

Week 25 should be a sensitivity/robustness week, not a new novelty week:

1. **Rule sensitivity**: hard-coded rules vs no-rules vs random-rule negative control.
2. **Question-template sensitivity**: indication prompt variants.
3. **Small noise robustness**: perturb candidate order/support scores/subgraph edges lightly if time permits.

Expected Week 25 output: robustness table + appendix-ready sensitivity paragraph.

## 9. Next action

Proceed to Week 25 only after saving this closeout and backing up Week 24 results.
