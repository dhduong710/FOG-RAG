# Week 1 Data Spec

## 1. Overall task framing
This project follows the DrKGC-style knowledge graph completion pipeline for biomedical drug repurposing.

Core query form:
(?, treats, disease)

Main objective:
rank candidate drugs for a query disease.

Important framing:
- Setting A is kept as close as possible to the DrKGC-style indication ranking benchmark.
- Setting B extends the task with contraindication-awareness, schema validity, and grounded explanation analysis.

---

## 2. Shared backbone assumptions

### 2.1 Query type
The main query is:
(?, treats, disease)

This means:
- the missing entity is a drug
- the known entity is a disease
- the target relation is treats / indication-like treatment relation

### 2.2 Question reformulation
Each incomplete triple is converted into a natural-language question.

Example:
(?, treats, Hypertension)
-> "What drug can be used to treat hypertension?"

### 2.3 Minimum JSON fields required by the current DrKGC pipeline
Each example must contain at least:
- input
- output
- query_entity_id
- rank_entities_id
- subgraph

### 2.4 Meaning of required fields
- input: prompt text / question
- output: gold target drug
- query_entity_id: disease entity ID
- rank_entities_id: candidate drug ID list
- subgraph: retrieved evidence triples or paths

---

## 3. Setting A — DrKGC-compatible indication ranking

### 3.1 Goal
Keep the benchmark as close as possible to the DrKGC backbone for fair comparison.

### 3.2 Task definition
Given a query of the form:
(?, treats, disease)

the model ranks candidate drugs.

### 3.3 Candidate space
- candidate entities should be drug entities only
- no broad expansion to non-drug biomedical entities
- no extra benchmark-changing exclusion unless clearly reported

### 3.4 Contraindication handling
For official fairness comparison:
- do not rely on aggressive hard exclusion unless explicitly stated in the experiment section
- a neutral or minimally changed candidate protocol is preferred

### 3.5 Output
Primary output:
- Top-K ranked drug list

Optional output:
- retrieved evidence subgraph
- explanation text

But the official comparison emphasis is still ranking quality.

### 3.6 Evaluation metrics
Use standard ranking metrics:
- MRR
- Hits@1
- Hits@3
- Hits@10

### 3.7 Why Setting A exists
If FOG-RAG improves in Setting A, the gain cannot be dismissed as coming from benchmark change.

### 3.8 Conclusion for Setting A
Setting A is the benchmark-compatible part of the project.

---

## 4. Setting B — Extended contraindication-aware ranking

### 4.1 Goal
Extend the task to better reflect biomedical usefulness.

### 4.2 Added information
Setting B may additionally use:
- contraindication relation
- ontology type constraints
- schema/domain-range checks
- evidence-grounding information

### 4.3 Candidate retrieval
Candidate generation is no longer purely score-based.

Possible variants:
- hard filtering of contraindicated drugs
- soft penalization of contraindicated drugs

Candidate selection should remain restricted to drug entities.

### 4.4 Evidence requirements
Retrieved evidence should ideally be:
- type-valid
- schema-valid
- relevant to the drug-disease query
- suitable for grounded explanation

### 4.5 Output
Setting B returns:
- Top-K ranked drug list
- evidence subgraph or supporting paths
- grounded explanation
- optional safety-related flags for candidates

### 4.6 Evaluation metrics

#### Ranking metrics
- MRR
- Hits@1
- Hits@3
- Hits@10

#### Safety metrics
- SafetyViolation@10
- Contra@10

#### Constraint metrics
- ConstraintViolationRate

#### Explanation metrics
- Grounding Rate
- Path Faithfulness
- Evidence Density

#### Efficiency metrics
- inference time per query
- average subgraph size
- average number of retrieved paths
- GPU memory usage

### 4.7 Conclusion for Setting B
Setting B is the extension part of the project.

---

## 5. Difference between Setting A and Setting B

### Setting A
- benchmark-compatible
- direct comparison with DrKGC
- ranking-focused
- minimal task change

### Setting B
- biomedical extension
- contraindication-aware
- schema-aware
- explanation-aware
- evaluates safety and grounding in addition to ranking

---

## 6. Minimal example data schema

```json
{
  "input": "What drug can be used to treat hypertension?",
  "output": "Losartan",
  "query_entity_id": 1024,
  "rank_entities_id": [45, 81, 120, 155],
  "subgraph": [
    ["Losartan", "targets", "AGTR1"],
    ["AGTR1", "associated_with", "Hypertension"],
    ["Losartan", "indicated_for", "Hypertension"]
  ]
}

## 7. FOG-RAG extension fields to consider later
These are not required in week 1, but should be noted for later implementation:
- candidate_scores_base
- candidate_scores_safety
- contra_flags
- path_confidence
- schema_validity

---

## 8. Final lock for week 1
- Setting A = fair comparison with DrKGC-compatible indication ranking
- Setting B = contraindication-aware and grounding-aware extension
- week 1 only locks the spec
- implementation of fuzzy and safety modules comes later