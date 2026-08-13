# Solution suite and strength gates

## Table of contents

1. Program classes
2. Wrong-solution catalog
3. Close-complexity candidates
4. Three-round adversarial agents
5. Verdict and score expectations
6. Survivor diagnosis
7. Resource-safe candidate construction

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

Do not make a candidate easier to reject by giving it incidental resource hazards. In particular, do not materialize a full dense matrix or oversized `vector` when the intended defect is a wrong transition, greedy assumption, or excessive running time. Keep the defect isolated so a failing verdict identifies the data property being tested.

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

## Resource-safe candidate construction

For every representative, record estimated and measured peak memory, stack depth, output bound, and process/thread/file behavior. Apply [runtime-resource-policy.md](runtime-resource-policy.md) before execution.

If memory is not the attacked boundary, require a comfortable safety margin and replace incidental dense storage with bounded flat or rolling storage. `vector` is permitted, but its maximum capacity and all simultaneously live copies must be computed; nested vectors, reserve growth, and allocator overhead must be included.

If memory is the attacked boundary, separate proof from execution. Keep the mathematically faithful memory formula, but run an above-limit instance only under an effective hard cap that cannot exhaust the host. Otherwise provide formula plus bounded measurements and do not claim an observed MLE. Never accept a local system error, `bad_alloc` cascade, process-launch failure, host swap storm, or cleanup failure as a qualifying candidate result.

Before adding a candidate to the matrix, verify that it:

1. passes sample and tiny harness smoke tests;
2. has no unrelated undefined behavior under sanitizers when supported;
3. stays within the declared preflight caps on a scale ladder;
4. terminates its process tree and cleans temporary artifacts after timeout;
5. fails formal data only through its recorded semantic, time, or safely enforced memory boundary.
