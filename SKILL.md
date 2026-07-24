---
name: build-cp-testdata
description: Rewrite and freeze algorithm-contest statements, audit or build adversarial test data, and write concise human-readable editorials covering every partial solution. Use when Codex must preserve a problem's mathematics while replacing its title, wording, samples, constraints, or subtasks; inspect supplied data before deciding whether to regenerate it; or create std.cpp, brute.cpp, validators, generators, scored .in/.ans files, buggy solutions, timing evidence, independent checks, and formal solution documents compliant with a specified OI or Luogu format.
---

# Build Competitive Programming Statements and Test Data

Create a mathematically faithful rewritten statement and a problem-specific data package whose inputs are legal, answers are trustworthy, generation is reproducible, and intended wrong or out-of-scope solutions are rejected by appropriate cases.

## Required contract

Accept an original-problem directory plus the requested number `N` of independent pairs. Recursively inventory the directory according to [references/input-discovery.md](references/input-discovery.md). Require a Markdown statement and one standard solution; detect rather than assume the presence of an editorial, data, wrong solutions, partial solutions, or a subtask table. Treat ambiguity in critical semantics as blocking, but continue by creating optional artifacts that are simply absent.

The source statement may be Chinese, English, or bilingual. Always deliver a complete Chinese statement. Never override a stated language standard; otherwise record the chosen default.

Use `valid.cpp` by default. Honor `src/val.cpp` or another project-required name when specified and point the pipeline configuration to it. Name pairs according to the package contract; otherwise use `data/001.in`, `data/001.ans`, and so on.

## Acceptance gates

Enforce five gates:

1. Recover a reliable source baseline and internal change record before rewriting.
2. Freeze the rewritten mathematical definition, interface, constraints, subtasks, samples, and judge mode before formal data generation.
3. Freeze the primary `std.cpp` only after proof review, brute-force comparison, and boundary checks.
4. Accept data only after validation, duplicate/LF checks, answer cross-checking, subtask-score tests, timing calibration, and review records pass.
5. Freeze the editorial only after it covers every declared partial algorithm, the full proof, complexity, boundaries, and implementation correspondence without contradicting accepted artifacts.

Do not finalize an editorial or downstream package while a data-acceptance issue remains open.

## Workflow

Follow every gate in order. Never generate final answers before the oracle gate passes.

### 1. Normalize the contract

Inventory the supplied directory first and record selected/missing artifacts. Read every plausible statement and std candidate, plus all optional artifacts that can constrain later decisions. Create one canonical machine-readable contract for input grammar, ranges, cross-field constraints, subtasks, limits, judge mode, solution roles, case plan, and `N`. Read [references/problem-contract.md](references/problem-contract.md) and [references/state-and-release-audit.md](references/state-and-release-audit.md). Resolve contradictions explicitly; do not infer readiness from file presence.

### 2. Rewrite and freeze the statement

Read [references/statement-rewrite.md](references/statement-rewrite.md) and [references/luogu-text-format.md](references/luogu-text-format.md), then adapt [assets/statement-template.md](assets/statement-template.md). Recover the complete original mathematical problem first; if its definition, interface, or constraints remain unreliable, mark it unusable instead of inventing semantics.

Replace the displayed title, background, variable names, and exposition while preserving the mathematical problem and indispensable full-score algorithm. Record every material change internally. Design entirely new sample instances and a mutually exclusive subtask table tied to planned formal cases. Make ambiguity-sensitive boundaries explicit in prose or samples.

Use one independent source-comparison review for title/background/narrative-only changes. Use two blind reviewers for input representation/order, constraints, output, or wording that could alter mathematical understanding. Freeze only after reviewers recover the same definition and accepted comments are rechecked.

### 3. Establish the oracle

If `std.cpp` is missing, dispatch the strongest available independent solver subagent. Give it only the statement and request an algorithm, proof, complexity analysis, and `std.cpp`; do not combine this with data design. If independent-agent capability is unavailable, stop and tell the user instead of silently substituting an unreviewed solution.

Whether supplied or generated:

Read [references/oracle-and-complexity-audit.md](references/oracle-and-complexity-audit.md), then:

1. Review algorithm and complexity against full constraints.
2. Compile with strict warnings and use sanitizers when supported.
3. Create a separately reasoned `brute.cpp` that directly models the mathematical contract rather than simplifying `std.cpp`; exhaust small parameters where possible.
4. Differential-test exhaustive tiny cases plus deterministic random and directed cases. Record ranges, counts, seeds, and the stopping reason.
5. Test minimum, maximum, degenerate, overflow, reset, and recursion boundaries.
6. If an original reference solution exists, adapt its interface and cross-check it too.
7. Fix and repeat after discrepancies. Preserve the original when modifying user source.

Freeze `std.cpp` only after passing. If brute force is infeasible, require an independent implementation or review and record the limitation.

### 4. Audit supplied data or design exactly N cases

If input/answer files are supplied, read [references/existing-data-audit.md](references/existing-data-audit.md) and inspect them before generating anything. Validate file count, names, LF, syntax, global and group constraints, uniqueness, answer correctness, subtask coverage, boundary/maximum coverage, candidate-solution strength, and timing. If all requirements pass, adopt the existing files by hash and do not regenerate them. If only some fail, preserve passing files and replace only affected points unless the data design is fundamentally inconsistent.

When data is missing or rejected, assign every case an id, seed, generation profile, subtask group, score, semantic-role tags, written purpose, structural features, and intended kills. Maintain a group-level manifest mapping mutually exclusive case ids to constraints, strategy, critical properties, and expected attacked mistakes. Read [references/test-design.md](references/test-design.md). Cover deterministic boundaries before random cases, and distinguish correctness extremes from complexity worst cases. With fixed `N`, replace weak slots instead of adding cases.

### 5. Implement and attack valid.cpp

Check parse success, global bounds, counts, cross-field relations, structure, forbidden forms, and strict EOF; then check the case's declared subtask-group constraints. Pass the group id explicitly from the runner. Return nonzero with a useful stderr message for invalid input. Use range helpers or assertions only in a configuration where checks cannot be compiled out, and avoid overflow inside validation.

Test the validator as a classifier, not only as a parser. The positive suite must include ordinary, boundary, maximum, and every group-specific legal form. The negative suite must include near-valid missing/extra tokens, range violations, broken counts, malformed separators where formatting is strict, illegal structures, cross-field contradictions, and wrong group claims. Require every curated example to receive its expected result; generated inputs alone cannot establish validator quality. Adapt [assets/valid.cpp](assets/valid.cpp) and remove customization markers.

### 6. Implement deterministic gen.cpp

Accept `--case`, `--seed`, and `--profile`, and emit one complete file on stdout. Never seed from time, `random_device`, process id, or ambient state. Encode every hand-built counterexample as a named profile. Adapt [assets/gen.cpp](assets/gen.cpp) and remove customization markers.

### 7. Generate, validate, and answer

Create `pipeline.json` from [assets/pipeline.example.json](assets/pipeline.example.json), then run:

```text
python scripts/run_pipeline.py pipeline.json all
```

Use the bundled Python runtime if needed. Treat generator failure, validator rejection, oracle timeout/crash, missing output, non-reproducibility, CRLF in required-LF artifacts, or unexplained duplicate inputs as a hard failure. Write answers atomically. If a portable project requires `run.sh`, make it a fail-fast orchestration wrapper around the same declared case list and fixed seeds rather than a second source of test design.

For adopted existing data, skip the generation command. Preserve the original `.in` files, recompute and compare answers without overwriting first, record hashes and provenance as `existing`, then continue with the same strength, scoring, and acceptance tests. Create or retain `gen.cpp` only when the delivery contract requires it or future maintenance needs it.

### 8. Build the solution suite

Create accepted, subtask, and proven-wrong solutions. Implement at least one representative program for every distinct partial-score algorithm or complexity class. Read [references/solution-suite.md](references/solution-suite.md). Classify wrong solutions by conceptual, complexity, or implementation defect; give every candidate verdict and score expectations plus a named killing profile. Do not call an unexpected algorithm wrong without a defect proof or counterexample.

### 9. Evaluate and close the loop

Run every candidate on every pair and produce AC/WA/TLE/RE/CE verdicts. For an unexpected survivor:

1. Decide whether it is actually correct.
2. If wrong, minimize or explain a counterexample with the brute oracle.
3. Map the defect to a missing data feature.
4. Update the plan and `gen.cpp`; never hand-patch `.in`.
5. Regenerate inputs and answers, revalidate all cases, and rerun the full matrix.

Repeat until all gates pass. Random retries without a stated hypothesis do not count as strengthening.

After every repair, apply the invalidation matrix in [references/state-and-release-audit.md](references/state-and-release-audit.md) and rerun all dependent evidence. Preserve failure logs and resume only from checkpoints whose source and configuration hashes still match.

### 10. Run independent acceptance

Read [references/acceptance-and-review.md](references/acceptance-and-review.md). After the statement is frozen, have two independent reviewers derive and code solutions without seeing the main analysis or `std.cpp`. Cross-check the primary std, both independent solutions, any original std, and `brute.cpp` on their applicable domains; run both independent solutions over every sample and formal case. Resolve disagreements with a proof, oracle, or minimized counterexample, never by majority vote.

Have a separate reviewer audit the subtask algorithms and measured scores. Benchmark every maximum-scale case at least three times when calibrating the time limit, retain the slowest single-case run, record the CPU/compiler, and apply the project formula. Save raw reviews, disposition of every comment, fixes, and recheck results.

Before release, write the structured `go`/`no_go` report required by [references/state-and-release-audit.md](references/state-and-release-audit.md). Its evidence must be current; a directory containing all expected filenames is not sufficient.

### 11. Write and review the editorial

Proceed only after data acceptance. Read [references/solution-writing.md](references/solution-writing.md) and [references/luogu-text-format.md](references/luogu-text-format.md), then adapt [assets/solution-template.md](assets/solution-template.md). Begin with a short intuitive explanation, then cover brute force and every distinct partial-score method before the full solution. For each method, state applicable cases, algorithm, correctness, time/space complexity, boundaries, and implementation correspondence.

Write for a human reader: connect observations concretely, avoid canned introductions and repeated summaries, keep paragraphs focused, define notation before use, and retain only formalism that proves or implements something. Check every claim against the frozen statement, manifest, measured scores, and primary std.

## Exit criteria

Finish only when the inventory is resolved; the final statement is fully Chinese and passes format/equivalence review; every sample is legal and answer-checked; accepted existing data or generated data satisfies the same gates; exactly `N` formal pairs exist; correct and partial solutions receive intended scores; maximum cases apply measured pressure; and the final audit says `go` with no blocking issue. Reject TODO markers, placeholders, empty implementations, stale evidence, or missing references. When an editorial is requested, require coverage of every distinct partial method, full correctness and complexity analysis, code correspondence, and a human-readability review.

Preserve unrelated files and do not delete unconfigured data. Adapt the runner before using it for interactive, output-only, multiple-answer, floating-tolerance, or custom-checker problems.
