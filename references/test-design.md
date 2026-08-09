# Adversarial test design

## Table of contents

1. Case planning
2. Group manifest
3. Multi-test heterogeneity
4. Semantic roles
5. General features
6. Structure-specific features
7. Complexity frontier and pressure
8. Reproducibility
9. Bounded bundled sets

## Case planning

Give every case a written purpose. Allocate limited slots in this order: boundaries, deterministic counterexamples, subtask transitions, maximum-scale pressure, and seeded random diversity. Combine compatible hazards, but retain a small diagnostic case when it makes a bug easy to attribute. A different seed is not a different purpose or structure.

## Group manifest

Separate validator groups from scoring units. A validator group names the extra legality promise checked for a case. A scoring unit names how points are awarded. They may use similar labels, but neither is inferred from the other.

Generate judge subtasks only from scoring units. Never derive `data/config.yaml` from validator groups, filename ranges in a sample, or a copied example configuration.

Make scoring-unit membership mutually exclusive: every formal case belongs to exactly one unit. For each unit, state its case ids, type (`case` or `bundle`), points, dependencies, extra constraints, intended algorithm, representative tested program, generator modes, critical properties, and expected attacked mistakes. Put concrete seeds and parameters in the executable case list.

Every non-full scoring unit must have a concrete algorithm that is correct under its stated additional constraint and an executable representative that earns its intended score. Do not create a row merely to increase the number of subtasks or split one method into decorative score levels. If a proposed unit has no specific solvable method, merge it with another unit, replace its constraint, or remove it before statement freeze. An implementation-only failure boundary is an attack target, not a partial algorithm.

Require every declared validator group and scoring unit to contain at least one formal case. Pass the validator group id to the validator so it checks both global legality and the group's extra promise. Score a bundle only when every member case and dependency unit passes.

## Multi-test heterogeneity

When one formal input contains several test instances, design the input as a deterministic mixture rather than repeating one generator family. If the scoring predicate admits at least two legal structural families, every multi-test formal input must contain at least two, and preferably three, distinct families. Vary scale, values, topology or ordering, tie behavior, reset pressure, and expected execution path.

Record each file's family names, counts, size bands, order policy, aggregate-bound accounting, and intended kills. Across files, change the family-count vector and relative order; changing only the seed while retaining the same composition is insufficient. Use fixed-seed shuffling when order diversity is useful.

If a subtask predicate mathematically permits only one structural family, document why and diversify dimensions that remain legal, such as size, labels, values, local boundaries, and order. Review every multi-test case under [adversarial-agent-review.md](adversarial-agent-review.md).

## Semantic roles

Tag every case by purpose, not only by size. Use a problem-specific subset of these roles:

- `sanity`: tiny hand-checkable or exhaustive behavior.
- `coverage`: seeded random diversity and ordinary mixed structures.
- `boundary`: minimum/maximum values and subtask-transition edges.
- `adversarial`: a directed counterexample to a named conceptual or implementation defect.
- `stress`: a worst-case shape for a named time or memory complexity.

The profile and manifest must explain the semantics behind each tag. A stress case is not merely a boundary case with all parameters maximized: construct the shape that realizes the candidate algorithm's costly path. Conversely, keep a boundary case even when it is computationally easy. Do not impose a universal role percentage when the fixed test count or subtask table requires another allocation, but leave no required role uncovered.

## General features

- Smallest and largest legal dimensions and values.
- Values around zero, one, powers of two, modulus boundaries, and type limits.
- All equal, all distinct, many duplicates, alternating extremes.
- Sorted, reversed, nearly sorted, periodic, and block-structured sequences.
- Unique optimum, tied optima, and optimum at either endpoint.
- Empty optional components, saturated components, and cases just beyond subtask boundaries.

Verify generator-side intermediate types when constructing overflow cases.

## Structure-specific features

- Graphs: paths, stars, cliques, bipartite extremes, components, long shortest paths, equal paths, and adversarial edge order; include loops or parallel edges only when legal.
- Trees: one vertex, path, star, balanced tree, high-degree hub, maximum depth, and relabelings that break index assumptions.
- Grids: one row/column, checkerboards, corridors, uniform areas, boundary paths, and symmetric ties.
- Strings: unary, maximal runs, periodic strings, near matches, prefix/suffix overlap, and full alphabet coverage.
- Geometry: collinearity, coincident points when legal, extreme coordinates, ties, and near-overflow cross products.
- DP: unreachable states, tied transitions, transition-order traps, and values around capacity boundaries.

## Complexity frontier and pressure

Build a problem-specific frontier containing the accepted complexity and every plausible nearby alternative, including an extra logarithmic factor, one additional data-structure factor, a larger state dimension, a close polynomial exponent, pseudo-polynomial dependence, or higher memory. Implement and measure a representative for each relevant class.

Match the shape to the suspected complexity. Stress the dimension actually squared, combine count and value bounds against pseudo-polynomial algorithms, create maximum depth for recursion, and defeat pruning with inputs where its conditions remain ineffective. For close classes, derive operation counts and crossover scales, then include more than one maximum or near-maximum composition when their worst cases differ.

Benchmark the oracle and close candidates with the release compiler and resource policy at least three times on every marked case. Retain raw runs, the slowest measurement, candidate-to-oracle ratios, and a safety margin. If a slower asymptotic solution remains safely within the frozen limits on all valid worst cases, reclassify it as an accepted alternative or revise constraints fairly; do not force a TLE through timing noise.

## Reproducibility

Record case id, validator group, scoring unit, profile, seed, generator hash, input hash, and answer hash. Record points and dependencies once on the scoring unit rather than copying them onto member cases. Reject duplicate formal inputs by hash unless a case explicitly declares a defensible evaluation reason. If a random seed kills a program, keep that seed and explain the responsible feature.

## Bounded bundled sets

When the intake selects bounded strength-driven `bundled` scoring, start with every supplied formal input and do not remove a legal one. Keep at least 20 and at most 40 cases. Add a case only for a named uncovered boundary, a minimized or structured hack against an evidenced defect, or a measured complexity stress. Re-run the complete solution matrix after each addition and stop once every planned defect and partial complexity class has the intended bundled score range. Record the final exact count in `pipeline.json` and the release report.
