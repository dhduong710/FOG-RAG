# Week 1 Problem Lock

## 1. Backbone task
Given (?, treats, disease), rank candidate drugs.

## 2. My extended task
Given (?, treats, disease), rank candidate drugs while discouraging contraindicated drugs and returning grounded evidence.

## 3. Prediction target
Rank likely treatment drugs for a query disease.

## 4. Input / query
An incomplete triple of the form (?, treats, disease), reformulated as a natural-language question.

## 5. Model output
- Top-K ranked drug candidates with scores
- An evidence subgraph or supporting paths
- A grounded natural-language explanation linked to retrieved evidence

## 6. Setting A vs Setting B
### Setting A
Direct-comparison with DrKGC-compatible indication ranking.
- Keep the backbone task unchanged
- Focus on ranking metrics only

### Setting B
Extended contraindication-aware ranking with safety, schema, and explanation metrics.
- Add contraindication-aware analysis
- Add schema / ontology validity analysis
- Add grounded evidence / explanation analysis