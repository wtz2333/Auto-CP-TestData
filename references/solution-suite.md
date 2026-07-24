# Solution suite and strength gates

## Table of contents

1. Program classes
2. Wrong-solution catalog
3. Verdict and score expectations
4. Survivor diagnosis

## Program classes

Maintain `accepted`, `subtask`, and `wrong` directories. For every non-oracle program, record its algorithm, complexity, supported domain, known defect, expected verdicts, and expected score interval. Implement one representative for each distinct partial algorithm or complexity; do not duplicate programs merely because one algorithm covers several scoring rows. Prefer a minimal mutation isolating one defect over a noisy program containing many unrelated bugs.

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

## Verdict and score expectations

Use `must_pass` for every required case. Use `must_fail` only for specific constructed counterexamples. Use `must_fail_one_of` for a pool whose collective purpose is to kill the program. Add `score_min` and `score_max` when partial credit matters, and measure score using case points rather than inferred group names. A subtask solution passing one larger case is not automatically a weakness; require rejection only where its assumptions or resource limit are genuinely violated.

## Survivor diagnosis

Differential-test a survivor on exhaustive or random small inputs, minimize any counterexample, and reconsider whether the algorithm is actually correct. If wrong, add a named generator profile generalizing the counterexample, update expectations, and rerun the full matrix. Never use illegal input or weaken the validator to kill a solution.
