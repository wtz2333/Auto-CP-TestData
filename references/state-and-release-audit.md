# Workflow state and release audit

Treat readiness as recorded evidence, not as the presence of files. A compilable `std.cpp`, nonempty `data/`, or successful build does not prove that a later gate may run.

## Canonical state

Choose one machine-readable problem contract as the authoritative source for user authority, statement style, rewrite scope, interface, limits, judge mode, scoring units, solution roles, and case plan. If `task.json` and `pipeline.json` are both used, assign every shared field one owner and store the owner's revision or hash in the derived file. Reject disagreement instead of choosing whichever file was read last.

At each checkpoint record:

- `decision`: `go` or `no_go` for the requested next stage.
- `completed_gate`: the latest gate backed by evidence.
- `blocking_issues`: concrete unmet requirements or failed checks.
- `evidence`: report paths, hashes, run counts, verdict matrices, and review ids.
- `next_actions`: the smallest exact repairs and reruns needed.

Do not advance on `no_go`. A failed command is not repaired by skipping the gate or weakening an expectation.

## Invalidation matrix

After a change, invalidate the changed artifact's gate and every dependent result:

| Changed artifact | Results that must be rerun |
|---|---|
| Required preference, delegation, target audience, or delivery scope | Intake gate and every design or delivery result affected by the changed choice |
| Statement style or narrative-only rewrite scope | Statement draft, style/equivalence review, rendering, and any sample passage changed with it |
| Mathematical definition, input/output, constraints, subtasks, or judge mode | Statement review, std/brute review, validator, generator plan, samples, all data, solution matrix, timing, editorial, release audit |
| Scoring mode, unit membership, points, or dependencies | Subtask table, manifest, candidate score calculation, partial-solution claims, editorial, and release audit; rerun data/validator gates too when membership constraints changed |
| Package format, archive policy, or output path | Packaging decision, directory allowlist or archive verification when applicable, delivery hashes, and release audit |
| Samples only | Sample validation, displayed/file consistency, statement review of the affected passage |
| `std.cpp` or answer semantics | Proof/code review, differential tests, all answers, candidate matrix, timing, editorial code correspondence |
| `brute.cpp` | Brute audit and every differential/stress result that used it |
| Validator or group promises | Validator positive/negative suite and legality audit of every sample/formal input |
| Generator, case plan, seed, or formal input | Reproducibility, validation, answer generation, hashes, duplicate checks, candidate matrix, timing where applicable |
| Adversarial candidate portfolio or round result | Complete candidate matrix, per-unit scores, excess-score decisions, final clean-round evidence, and release audit |
| Checker or comparison mode | Checker self-tests, answer consistency, std/brute comparison, candidate matrix |
| Time, memory, stack limits, runtime resource mechanism, or release flags | Generation, validation, oracle answers, differential tests, candidate matrix, independent acceptance, maximum-case benchmarks, and every resource-dependent verdict |
| Editorial | Editorial review only, unless it exposes a contradiction in an earlier artifact |

Do not reuse a downstream `passed` status after invalidation merely because filenames did not change.

## Retry and resume

Retry deterministic transient failures. Resume a long generation only from an atomic checkpoint whose configuration, source, seed plan, and accepted-case hashes still match. Otherwise restart the affected stage. Preserve the first failure log and record the retry count and reason; a fallback that changes generator arguments or semantics is a new run and requires revalidation.

## Final release audit

Issue `decision: go` only when all required gates are current and their evidence is available. The final audit must list:

- Completed intake authority, contract, and source revisions.
- Statement/sample review result.
- Oracle/brute proof and differential evidence.
- Validator positive/negative results.
- Data legality, answer, uniqueness, reproducibility, role coverage, and strength results.
- Multi-test family-composition evidence and confirmation that files are not single-family seed variants.
- At least three qualifying adversarial-agent rounds, the accumulated candidate ledger, final-hash regression, and a clean last adaptive round.
- Scoring-unit definition, candidate verdict/score breakdown, and timing evidence.
- A concrete tested solution for every non-full scoring unit and close-complexity operation/timing evidence.
- Requested stack limit, effective operating-system mechanism, and confirmation that every executable class used the same policy.
- Editorial review result.
- Archive policy and its authority; when policy is `none`, confirmation that no release ZIP/archive was created.
- Unresolved risks, which must be empty for `go`.

Reject release when TODO markers, unfilled statement-template markers, render directives such as `{{ ... }}`, empty implementations, stale reports, missing referenced files, unexpected package members, or internal-only materials remain. Directory delivery is the default. Only when `archive_policy` is `user-requested` or `platform-required`, verify the archive by extracting it to a temporary directory and comparing its contents with an explicit allowlist; when policy is `none`, creating a release archive is itself a blocking mismatch.
