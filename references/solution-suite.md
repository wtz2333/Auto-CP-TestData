# Solution suite and strength gates

## Table of contents

1. Program classes
2. Wrong-solution catalog
3. Close-complexity candidates
4. Three-round adversarial agents
5. Verdict and score expectations
6. Survivor diagnosis

## Program classes

Maintain `accepted`, `subtask`, and `wrong` directories. For every non-oracle program, record its algorithm, complexity, supported domain, known defect, expected verdicts, and expected score interval. Implement one representative for each distinct partial algorithm or complexity; do not duplicate programs merely because one algorithm covers several scoring rows. Prefer a minimal mutation isolating one defect over a noisy program containing many unrelated bugs.

Every non-full public scoring unit must name a concrete correct-on-that-unit algorithm and an executable representative. If no such method exists, reopen subtask design and merge, remove, or replace the unit. Do not use a row whose only purpose is increasing the row count or catching an implementation mistake.

## Wrong-solution catalog

Organize plausible failures into three layers before choosing implementations:

- Conceptual errors: wrong lemma, invalid greedy exchange, missing condition, incorrect state meaning, or an unjustified structural assumption.
- Complexity errors: correct on small cases but too slow or too memory-heavy at the intended worst-case shape.
- Implementation errors: boundaries, overflow, reset, ties, parsing, indexing, recursion, or data-structure misuse.

For each selected wrong solution, record one isolated defect, the smallest known counterexample when available, the named formal profile intended to kill it, and the evidence that the program behaves as claimed. Cover every relevant layer; do not satisfy a numeric quota with superficial variants of the same bug.

Select only relevant defects:

- Off-by-one bounds, missed endpoints, wrong empty/base cases.
- Overflow before cast, signed/unsigned conversion, negative modulo.
- State not reset, stale arrays, reused visited marks.
- Duplicate/tie mistakes and strict versus non-strict comparisons.
- Wrong greedy exchange, DP initialization/transition order, or binary-search invariant.
- Graph assumptions about connectivity, edge order, simplicity, or roots.
- Recursion depth, floating comparison, and geometry orientation errors.
- Quadratic, pseudo-polynomial, excessive clearing, or memory-heavy algorithms.
- Parsing/output assumptions and unstable randomized algorithms.

Avoid undefined behavior unless it is the target; otherwise failure gives weak evidence about data quality.

## Close-complexity candidates

List the plausible complexity frontier around the full solution. Include candidates that add only one logarithmic factor, one extra data-structure operation, a larger state dimension, a close polynomial factor, pseudo-polynomial dependence, or excess memory when those approaches are realistic for contestants.

For each class, write one representative, estimate actual operations and crossover scale, and identify the formal structures that realize its worst path. Benchmark it beside the oracle under identical compiler and resource settings. A worse asymptotic label alone is not a wrong-solution proof; if the candidate passes every valid worst case with comfortable margin, reclassify it as accepted or revise the constraints and time limit fairly.

## Three-round adversarial agents

Run [adversarial-agent-review.md](adversarial-agent-review.md) for at least three qualifying rounds. Keep the adversarial agent blind to the oracle, generator, validator, formal data, manifest, and previous source code. Its objective is to maximize undeserved score using plausible non-full solutions.

Each round must add a new proved-wrong defect or complexity class, compile and run it on all formal cases, and record per-unit scores. Preserve every candidate in the regression suite. After a repair, rerun the accumulated portfolio on the final data hashes and require a clean adaptive round before closing the strength gate.

## Verdict and score expectations

Use `must_pass` for every required case. Use `must_fail` only for specific constructed counterexamples. Use `must_fail_one_of` for a pool whose collective purpose is to kill the program. Add `score_min` and `score_max` when partial credit matters, and calculate them from the frozen scoring units. Award a bundle only when all member cases and dependency units pass; never sum member cases independently. A subtask solution passing one larger case is not automatically a weakness; require rejection only where its assumptions or resource limit are genuinely violated.

## Survivor diagnosis

Differential-test a survivor on exhaustive or random small inputs, minimize any counterexample, and reconsider whether the algorithm is actually correct. If wrong, add a named generator profile generalizing the counterexample, update expectations, and rerun the full matrix. Never use illegal input or weaken the validator to kill a solution.
