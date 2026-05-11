# Week 27 Day 1  DRKG raw inventory

- Created at: `2026-05-11T16:07:17.521891+00:00`
- Setting: `setting_e_drkg`
- Dataset: `DRKG`

## Download / raw files

- Archive path: `/home/anhlq/Documents/2026-dhd/FOG-RAG/dataset/setting_e_drkg/00_raw_inventory/drkg.tar.gz`
- Archive size MB: `206.614`
- `drkg.tsv`: `/home/anhlq/Documents/2026-dhd/FOG-RAG/dataset/setting_e_drkg/00_raw_inventory/extracted/drkg.tsv`
- `entity2src.tsv`: `/home/anhlq/Documents/2026-dhd/FOG-RAG/dataset/setting_e_drkg/00_raw_inventory/extracted/entity2src.tsv`
- `relation_glossary.tsv`: `/home/anhlq/Documents/2026-dhd/FOG-RAG/dataset/setting_e_drkg/00_raw_inventory/extracted/relation_glossary.tsv`
- Embeddings found: `True`

## Graph inventory

- Triples: `5874261`
- Relations: `107`

## Unique entity type counts

- `Anatomy`: 400
- `Atc`: 4048
- `Biological Process`: 11381
- `Cellular Component`: 1391
- `Compound`: 24313
- `Disease`: 5103
- `Gene`: 39220
- `Molecular Function`: 2884
- `Pathway`: 1822
- `Pharmacologic Class`: 345
- `Side Effect`: 5701
- `Symptom`: 415
- `Tax`: 215

## Top entity-pair counts

- `Gene->Gene`: 2350931
- `Compound->Compound`: 1385757
- `Anatomy->Gene`: 726495
- `Gene->Biological Process`: 559504
- `Compound->Gene`: 184504
- `Compound->Side Effect`: 138944
- `Gene->Molecular Function`: 97222
- `Gene->Disease`: 95399
- `Gene->Pathway`: 84372
- `Compound->Disease`: 83895
- `Gene->Cellular Component`: 73566
- `Disease->Gene`: 28438
- `Gene->Compound`: 26290
- `Compound->Atc`: 15750
- `Gene->Tax`: 14663
- `Disease->Anatomy`: 3602
- `Disease->Symptom`: 3357
- `Pharmacologic Class->Compound`: 1029
- `Disease->Disease`: 543

## CompoundDisease relation candidates

| Relation | Direction | Count | Compounds | Diseases | Source | Treat hint | Association hint | Contra hint |
|---|---|---:|---:|---:|---|---:|---:|---:|
| `GNBR::T::Compound:Disease` | `Compound->Disease` | 54020 | 6628 | 3300 | `GNBR` | False | False | False |
| `GNBR::Sa::Compound:Disease` | `Compound->Disease` | 16923 | 3833 | 1666 | `GNBR` | False | False | False |
| `DRUGBANK::treats::Compound:Disease` | `Compound->Disease` | 4968 | 1542 | 1182 | `DRUGBANK` | True | False | False |
| `GNBR::Pa::Compound:Disease` | `Compound->Disease` | 2619 | 1498 | 513 | `GNBR` | False | False | False |
| `GNBR::C::Compound:Disease` | `Compound->Disease` | 1739 | 1225 | 213 | `GNBR` | False | False | False |
| `GNBR::J::Compound:Disease` | `Compound->Disease` | 1020 | 388 | 642 | `GNBR` | False | False | False |
| `GNBR::Pr::Compound:Disease` | `Compound->Disease` | 966 | 760 | 274 | `GNBR` | False | False | False |
| `Hetionet::CtD::Compound:Disease` | `Compound->Disease` | 755 | 387 | 77 | `Hetionet` | False | False | False |
| `GNBR::Mp::Compound:Disease` | `Compound->Disease` | 495 | 425 | 154 | `GNBR` | False | False | False |
| `Hetionet::CpD::Compound:Disease` | `Compound->Disease` | 390 | 221 | 50 | `Hetionet` | False | False | False |

## Day 2 recommendation

Do not freeze the task yet. Day 2 should choose one target relation based on:

1. Clear Compound�Disease or reversible Disease�Compound semantics.
2. Enough edges after coverage-safe split.
3. No overclaiming: use treatment-like / therapeutic-association proxy wording unless relation semantics are explicit.
4. Candidate universe must remain Compound-only.
