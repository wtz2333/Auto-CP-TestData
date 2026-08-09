# Acceptance, independent review, and timing

## Table of contents

1. Evidence package
2. Blind independent solutions
3. Subtask scoring audit
4. Adversarial strength audit
5. Time-limit calibration
6. Review disposition

## Evidence package

Keep one primary oracle source. Do not maintain divergent copies of `std.cpp`; when a delivery layout requires a copied solution, verify that its hash matches the workspace source. Preserve:

- The completed intake authority and frozen statement/contract revision.
- The source baseline, rewrite record, statement-risk classification, raw statement reviews, and sample hashes.
- Brute-force exhaustive range, random count, fixed seeds, directed families, and stopping reason.
- Generator modes and seeds, validator group arguments, input/answer hashes, and duplicate decisions.
- Validator positive/negative corpus and every expected/observed classification.
- Scoring-unit definition, candidate verdict matrix, per-unit score breakdown, and timing runs.
- Multi-test family composition, close-complexity frontier, and all adversarial-agent round reports.
- Raw reviewer reports, disposition records, fixes, and recheck evidence.

Separate build workspace, final deliverables, and internal reports when the surrounding project defines such directories. Never leak formal data, editorials, source mappings, or internal reports into a contestant download package.

## Blind independent solutions

After freezing the statement, give two independent reviewers only the statement, constraints, and necessary interfaces. Do not expose the main reasoning, primary `std.cpp`, or another reviewer's result before they submit their own mathematical interpretation, algorithm, complexity, and independently coded solution.

Cross-check the primary std, both independent stds, any original reference implementation, and the brute oracle where applicable. Run both independent stds on every sample and formal case. When results differ, locate the root cause with proof, brute force, or a minimized counterexample. A two-to-one vote is not evidence of correctness.

## Subtask scoring audit

Use a reviewer who did not design the data-strength expectations. Require every non-full scoring unit to identify a concrete correct-on-that-unit algorithm and representative program. If a row has no such method or exists only to increase subtask count, reopen statement and scoring design. One program may cover several units only when each unit still has a meaningful public constraint and the shared method is explicitly justified.

Run each representative on the complete formal set and compare its actual score and timeout pattern with the manifest. Recalculate with the frozen `per_case`, `bundled`, or `mixed` rule; a bundle earns no points unless all member cases and dependency units pass.

If a weaker algorithm earns too much, decide whether the statement's score explanation is wrong or the data is weak. Update the explanation or strengthen/regenerate data, then rerun the full regression.

## Adversarial strength audit

Require at least three qualifying rounds under [adversarial-agent-review.md](adversarial-agent-review.md). Reviewers must verify agent isolation, distinct defects or complexity classes, compilable candidates, per-unit scores, repairs, and final hashes. The final case set must be rerun against every candidate accumulated across all rounds.

Audit multi-test heterogeneity file by file. When multiple legal families exist, reject any formal multi-test input filled entirely from one family, and reject a formal set whose files differ only by seed. Require a clean adaptive round after the final repair. Missing agent capability, stale round evidence, or unresolved excess score blocks data acceptance.

## Time-limit calibration

Mark every maximum-scale case used for timing. Compile with the exact release compiler and flags. Run the primary std on each marked case at least three times, take the slowest single-case measurement, and apply the project's declared multiplier and rounding rule.

When following the supplied NOIP packaging convention, multiply the slowest time by three, round upward to a whole second, and clamp the result to 1 through 5 seconds. If the unclamped result exceeds 5 seconds, optimize the oracle or revise constraints rather than silently assigning more time. Record OS, CPU identifier, compiler version, flags, all raw runs, and the derived limit.

Treat timing as host-specific empirical evidence. Retain a comfortable separation between the oracle and intended TLE solutions.

For every plausible near-frontier complexity, benchmark a representative on the input shape that realizes its costly path. Record actual operation estimates, crossover scale, at least three raw runs per marked case, the slowest result, and the candidate-to-oracle ratio. If an extra-logarithmic or otherwise close algorithm remains safely inside the limit on all valid worst cases, treat it as a valid alternative or revise the constraint/limit design; do not declare it rejected from asymptotics alone.

## Review disposition

For every comment, retain the original text and record one of:

- Accepted: explain the defect, change, and successful recheck.
- Rejected: give concrete evidence or a proof, not preference.
- Superseded: link it to the later root-cause decision and recheck.

Close the acceptance gate only when no unresolved validator, answer, scoring, timing, or review issue remains.
Reopen earlier gates when a later fix changes statement semantics, interfaces, constraints, subtasks, or samples.

End the report with `decision`, `completed_gate`, `blocking_issues`, `evidence`, and `next_actions`. A final `go` requires an empty blocking list and current evidence for every gate.
