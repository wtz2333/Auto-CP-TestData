# Workflow state and release audit

Treat readiness as recorded evidence, not as the presence of files. A compilable `std.cpp`, nonempty `data/`, or successful build does not prove that a later gate may run.

## Canonical state

Choose one machine-readable problem contract as the authoritative source for the interface, limits, judge mode, solution roles, and case plan. If `task.json` and `pipeline.json` are both used, assign every shared field one owner and store the owner's revision or hash in the derived file. Reject disagreement instead of choosing whichever file was read last.

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
| Mathematical definition, input/output, constraints, subtasks, or judge mode | Statement review, std/brute review, validator, generator plan, samples, all data, solution matrix, timing, editorial, release audit |
| Samples only | Sample validation, displayed/file consistency, statement review of the affected passage |
| `std.cpp` or answer semantics | Proof/code review, differential tests, all answers, candidate matrix, timing, editorial code correspondence |
| `brute.cpp` | Brute audit and every differential/stress result that used it |
| Validator or group promises | Validator positive/negative suite and legality audit of every sample/formal input |
| Generator, case plan, seed, or formal input | Reproducibility, validation, answer generation, hashes, duplicate checks, candidate matrix, timing where applicable |
| Checker or comparison mode | Checker self-tests, answer consistency, std/brute comparison, candidate matrix |
| Time/memory limits or release flags | Maximum-case benchmarks and every resource-dependent verdict |
| Editorial | Editorial review only, unless it exposes a contradiction in an earlier artifact |

Do not reuse a downstream `passed` status after invalidation merely because filenames did not change.

## Retry and resume

Retry deterministic transient failures. Resume a long generation only from an atomic checkpoint whose configuration, source, seed plan, and accepted-case hashes still match. Otherwise restart the affected stage. Preserve the first failure log and record the retry count and reason; a fallback that changes generator arguments or semantics is a new run and requires revalidation.

## Final release audit

Issue `decision: go` only when all required gates are current and their evidence is available. The final audit must list:

- Contract and source revisions.
- Statement/sample review result.
- Oracle/brute proof and differential evidence.
- Validator positive/negative results.
- Data legality, answer, uniqueness, reproducibility, role coverage, and strength results.
- Candidate verdict/score matrix and timing evidence.
- Editorial review result.
- Unresolved risks, which must be empty for `go`.

Reject release when TODO markers, placeholders, empty implementations, stale reports, missing referenced files, unexpected package members, or internal-only materials remain. When packaging is in scope, verify the archive by extracting it to a temporary directory and comparing its contents with an explicit allowlist.
