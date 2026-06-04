# Week 17 Day 3 — Probe Design

## Theme
- Frozen retrieval main → one minimal fuzzy encoder probe v0

## Probe formula
- 0.45 * incident_norm
- 0.45 * bridge_norm
- 0.15 * band_bonus
- 0.30 * direct_norm
- 0.10 * contra_penalty

## Manifest summary
- **avg_gold_rank_probe**: `17.98`
- **avg_top5_direct_candidate_rate**: `0.01`
- **avg_probe_score**: `0.19096`

## Notes
- Day 3 builds the probe artifact only.
- Official compare is deferred to Day 4.
