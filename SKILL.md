---
name: build-cp-testdata
description: Clarify required problem-package preferences, rewrite and freeze algorithm-contest statements, audit or build adversarial test data, derive judge data configuration from scoring units, evaluate independent/bundled/mixed scoring, and write concise human-readable editorials covering every partial solution. Use when Codex must preserve a problem's mathematics while replacing its title, wording, samples, constraints, or subtasks; inspect supplied data before deciding whether to regenerate it; or create std.cpp, brute.cpp, validators, generators, scored .in/.ans files, config.yaml, buggy solutions, timing evidence, independent checks, formal solution documents, or an optional Polyhedron 项目 ZIP/导入包 compliant with a specified OI or Luogu format.
---

# Build Competitive Programming Statements and Test Data

Create a mathematically faithful rewritten statement and a problem-specific data package whose inputs are legal, answers are trustworthy, generation and judge configuration are reproducible, and intended wrong or out-of-scope solutions are rejected by appropriate cases.

## Required contract

Before mutating work, complete [references/intake-and-clarification.md](references/intake-and-clarification.md), ask the fixed [intake questionnaire](assets/intake-questionnaire.md), and adapt [assets/task.example.json](assets/task.example.json). Use the questionnaire verbatim: replace only bracketed discovered-value placeholders, and do not change its field order, numbering, options, or reply format. Require the user to supply the original-problem path and either an exact output path or a parent directory with explicit authority to choose the rewritten title and same-named output folder. Require an exact number `N` of independent pairs for `per_case` and `mixed`; for `bundled`, permit the bounded strength-driven policy defined below instead. Explicitly resolve deliverables, scoring mode and design authority, statement style, rewrite scope, target audience, and package format; accept “you decide” as recorded delegation, never as a silent default. Also require `intake.preferences.polyhedron_zip` to be a user-sourced Boolean. The user must explicitly choose whether to generate `polyhedron.zip`; never infer this choice or record it as delegated.

Inventory the supplied directory read-only according to [references/input-discovery.md](references/input-discovery.md) before asking about discoverable technical facts. Require a Markdown statement and one standard solution; detect rather than assume the presence of an editorial, data, wrong solutions, partial solutions, or a subtask table. Treat ambiguity in critical semantics as blocking, but continue by creating optional artifacts that are simply absent.

The source statement may be Chinese, English, or bilingual. Always deliver a complete Chinese statement. Never override a stated language standard; otherwise record the chosen default.

Use `valid.cpp` by default. Honor `src/val.cpp` or another project-required name when specified and point the pipeline configuration to it. Name pairs according to the package contract; otherwise use `data/001.in`, `data/001.ans`, and so on.

For a standard batch package, generate `data/config.yaml` from the frozen `scoring.units` and `memory_limit_mib` according to [references/testdata-config.md](references/testdata-config.md). Never copy a sample config's scores or case membership into another problem.

For every human-facing Markdown artifact—including statements, editorials, sample explanations, manifests, and review or acceptance reports—apply [references/human-readable-contest-text.md](references/human-readable-contest-text.md). Keep machine-readable contracts and raw evidence literal; do not “humanize” identifiers, commands, verdicts, hashes, or quoted reviewer text.

## Acceptance gates

Enforce six gates:

1. Complete the intake contract before any mutating step; no required preference or technical fact may remain unresolved.
2. Recover a reliable source baseline and internal change record before rewriting.
3. Freeze the rewritten mathematical definition, interface, constraints, scoring, samples, and judge mode before formal data generation.
4. Freeze the primary `std.cpp` only after proof review, brute-force comparison, and boundary checks.
5. Accept data only after validation, duplicate/LF checks, answer cross-checking, scoring-unit tests, derived `data/config.yaml` checks, timing calibration, and review records pass.
6. Freeze the editorial only after it covers every declared partial algorithm, the full proof, complexity, boundaries, and implementation correspondence without contradicting accepted artifacts.

Do not finalize an editorial or downstream package while a data-acceptance issue remains open.

## Workflow

Follow every gate in order. Never generate final answers before the oracle gate passes.

### 0. Complete intake and clarification

Read the directory without modifying it, inventory recoverable facts, and then present [assets/intake-questionnaire.md](assets/intake-questionnaire.md) with only its bracketed discovered-value placeholders filled. Keep the template text, numbering, option letters, option meanings, and field order unchanged. The template already contains conditional free-text fields for themes, custom formats, and user-supplied grouping, so ask a second round only when the reply is contradictory or omits a conditionally required value. Do not infer a scoring mode or statement style from the original problem.

Store concrete values and provenance in `task.json`. Require `source: user` for the original path, output path, `N`, and `polyhedron_zip`; permit `source: delegated` for other preferences only with a decision note. Resolve delegated “adaptive” choices to concrete stored values. Stop before mutation while any required field is absent, contradictory, or marked unresolved.

### 1. Normalize the contract

Record selected/missing artifacts. Read every plausible statement and std candidate, plus all optional artifacts that can constrain later decisions. Create one canonical machine-readable contract for user preferences, input grammar, ranges, cross-field constraints, scoring units, limits, judge mode, solution roles, case plan, and `N`. Read [references/problem-contract.md](references/problem-contract.md) and [references/state-and-release-audit.md](references/state-and-release-audit.md). Resolve contradictions explicitly; do not infer readiness from file presence.

### 2. Rewrite and freeze the statement

Read [references/statement-rewrite.md](references/statement-rewrite.md), [references/luogu-text-format.md](references/luogu-text-format.md), and [references/human-readable-contest-text.md](references/human-readable-contest-text.md), then adapt [assets/statement-template-strict.md](assets/statement-template-strict.md). Recover the complete original mathematical problem first; if its definition, interface, or constraints remain unreliable, mark it unusable instead of inventing semantics.

Replace the displayed title, background, variable names, and exposition while preserving the mathematical problem and indispensable full-score algorithm. Record every material change internally. Design entirely new sample instances and a mutually exclusive subtask table tied internally to planned formal cases. The public statement must not list test-case ids. Merge all rows with the same contestant-visible constraint predicate into one public subtask and one executable scoring unit; internal generator profiles, sources, or attack purposes never justify splitting the same problem scale into multiple subtasks. Make ambiguity-sensitive boundaries explicit in prose or samples.

Apply the frozen `formal`, `light-context`, or `themed` style. Stay within the authorized rewrite scope. For a themed statement, use only approved theme elements and keep the mathematical definition independently readable.

For `luogu-markdown`, treat the current [洛谷主题库题目规范](https://help.luogu.com.cn/rules/academic/problem-standard) as normative, not merely advisory. Verify the current official page when internet access is available and record its displayed update version in the rewrite evidence. A locally correct mathematical definition still fails this gate if it is verbose, awkward, solution-oriented, or difficult to read.

Use one coherent contestant-facing vocabulary. State core objects and relations naturally in the description, then express subtask properties with those existing terms. Do not insert an isolated glossary paragraph before a subtask table, coin a term for ordinary counting, or introduce an auxiliary graph, state, transformation, or lemma only to describe one scoring row. If a useful special property cannot be stated in one short clause with the existing objects, either redesign that property or—when the authorized rewrite scope permits—rewrite the entire statement around a clearer equivalent representation and revalidate every affected artifact.

Write `statement.md` in the selected platform's Markdown dialect. Preserve mathematical notation: use `$...$` for inline formulas and put `$$...$$` display formulas on separate lines. LaTeX commands such as `\le`, `\times`, `\sum`, subscripts, superscripts, and set notation belong inside those Markdown math delimiters. Never use `\(...\)` or `\[...\]` as delimiters, never leave LaTeX commands outside a math span, and never replace genuine formulas with inline code merely to avoid LaTeX. Reserve backticks for literal strings, filenames, identifiers that must be copied exactly, and code. Use ordinary Markdown headings, paragraphs, lists, tables when supported by the frozen platform, fenced `text` blocks, and links; avoid raw HTML, custom directives, and platform-only sample fences unless the package contract explicitly requires them. Render or preview the final statement with the target Markdown engine before freeze.

Use one independent source-comparison review for title/background/narrative-only changes. Use two blind reviewers for input representation/order, constraints, output, or wording that could alter mathematical understanding. Freeze only after reviewers recover the same definition and accepted comments are rechecked.

Also require a contestant-facing prose review that is separate from semantic equivalence. Apply the contest-text revision pass: give the reviewer only the final statement and ask whether every definition is necessary, introduced near first use, and phrased naturally; whether the background helps; whether the description is concise without relying on samples; whether terminology stays stable; whether transitions or caveats are formulaic; and whether every subtask row is understandable without decoding a one-off formalism. Treat a technically precise but unnatural passage as a blocking issue.

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

### 4. Audit supplied data and freeze the formal case set

If input/answer files are supplied, read [references/existing-data-audit.md](references/existing-data-audit.md) and inspect them before generating anything. Validate file count, names, LF, syntax, global and group constraints, uniqueness, answer correctness, subtask coverage, boundary/maximum coverage, candidate-solution strength, and timing. If all requirements pass, adopt the existing files by hash and do not regenerate them. If only some fail, preserve passing files and replace only affected points unless the data design is fundamentally inconsistent.

When data is missing or rejected, assign every case an id, seed, generation profile, validator group, scoring unit, semantic-role tags, written purpose, structural features, and intended kills. Maintain a manifest mapping case ids and scoring units to constraints, strategy, critical properties, and expected attacked mistakes. Read [references/test-design.md](references/test-design.md). Cover deterministic boundaries before random cases, and distinguish correctness extremes from complexity worst cases. With fixed `N`, replace weak slots instead of adding cases.

For bounded strength-driven `bundled` scoring, retain every supplied formal input in the delivered set, subject to legality and answer repair, then add named hack or stress cases only when they attack an evidenced wrong or out-of-scope solution. Keep at least 20 and at most 40 formal pairs. Stop adding cases once every planned defect and complexity class is rejected; the final exact count is a result of the strength audit, not an intake preference. If more than 40 supplied formal inputs exist, or a supplied input is illegal and cannot be preserved without changing the mathematical contract, stop for user resolution.

Freeze one explicit scoring definition: `per_case`, `bundled`, or `mixed`. Put every case in exactly one scoring unit, make unit points sum to the total, and keep dependencies acyclic. Treat validator groups and scoring units as separate concepts. Award a bundle only when all member cases and dependency units pass. For bundled scoring, normalize each public additional-constraint predicate and merge identical predicates into one scoring unit, combining all of their cases and points. Never split “no additional constraints” or any other identical problem scale into several public subtasks merely to separate seeds, sources, stress profiles, or intended kills.

### 5. Implement and attack valid.cpp

Check parse success, global bounds, counts, cross-field relations, structure, forbidden forms, and strict EOF; then check the case's declared subtask-group constraints. Pass the group id explicitly from the runner. Return nonzero with a useful stderr message for invalid input. Use range helpers or assertions only in a configuration where checks cannot be compiled out, and avoid overflow inside validation.

Test the validator as a classifier, not only as a parser. The positive suite must include ordinary, boundary, maximum, and every group-specific legal form. The negative suite must include near-valid missing/extra tokens, range violations, broken counts, malformed separators where formatting is strict, illegal structures, cross-field contradictions, and wrong group claims. Require every curated example to receive its expected result; generated inputs alone cannot establish validator quality. Adapt [assets/valid.cpp](assets/valid.cpp) and remove customization markers.

### 6. Implement deterministic gen.cpp

Accept `--case`, `--seed`, and `--profile`, and emit one complete file on stdout. Never seed from time, `random_device`, process id, or ambient state. Encode every hand-built counterexample as a named profile. Adapt [assets/gen.cpp](assets/gen.cpp) and remove customization markers.

### 7. Generate, validate, and answer

Create `task.json` from [assets/task.example.json](assets/task.example.json) and `pipeline.json` from [assets/pipeline.example.json](assets/pipeline.example.json). Declare `testdata_config.path` as `data/config.yaml`, read [references/testdata-config.md](references/testdata-config.md), and then run:

```text
python scripts/run_pipeline.py pipeline.json all
```

Use the bundled Python runtime if needed. The runner must derive every YAML subtask from the current `scoring.units`; it must not copy the output-shape example's values. Treat generator failure, validator rejection, oracle timeout/crash, missing output, non-reproducibility, a stale or mismatched judge config, CRLF in required-LF artifacts, or unexplained duplicate inputs as a hard failure. Write answers and `data/config.yaml` atomically. If a portable project requires `run.sh`, make it a fail-fast orchestration wrapper around the same declared case list and fixed seeds rather than a second source of test design.

For adopted existing data, skip the generation command. Preserve the original `.in` files, recompute and compare answers without overwriting first, record hashes and provenance as `existing`, then run `python scripts/run_pipeline.py pipeline.json config` to derive the judge config and continue with the same strength, scoring, and acceptance tests. Create or retain `gen.cpp` only when the delivery contract requires it or future maintenance needs it.

### 8. Build the solution suite

Create accepted, subtask, and proven-wrong solutions. Implement at least one representative program for every distinct partial-score algorithm or complexity class. Read [references/solution-suite.md](references/solution-suite.md). Classify wrong solutions by conceptual, complexity, or implementation defect; give every candidate verdict and score expectations plus a named killing profile. Do not call an unexpected algorithm wrong without a defect proof or counterexample.

Express expected score ranges under the frozen scoring units. Do not estimate a bundled subtask by summing the member cases that happened to pass.

### 9. Evaluate and close the loop

Run every candidate on every pair and produce AC/WA/TLE/RE/CE verdicts. For an unexpected survivor:

1. Decide whether it is actually correct.
2. If wrong, minimize or explain a counterexample with the brute oracle.
3. Map the defect to a missing data feature.
4. Update the plan and `gen.cpp`; never hand-patch `.in`.
5. Regenerate inputs and answers, revalidate all cases, and rerun the full matrix.

Repeat until all gates pass. Random retries without a stated hypothesis do not count as strengthening.

Retain a per-unit score breakdown for every candidate. For a dependency failure, distinguish “member cases passed” from “points awarded” so the report explains why a bundle received zero.

After every repair, apply the invalidation matrix in [references/state-and-release-audit.md](references/state-and-release-audit.md) and rerun all dependent evidence. Preserve failure logs and resume only from checkpoints whose source and configuration hashes still match.

### 10. Run independent acceptance

Read [references/acceptance-and-review.md](references/acceptance-and-review.md). After the statement is frozen, have two independent reviewers derive and code solutions without seeing the main analysis or `std.cpp`. Cross-check the primary std, both independent solutions, any original std, and `brute.cpp` on their applicable domains; run both independent solutions over every sample and formal case. Resolve disagreements with a proof, oracle, or minimized counterexample, never by majority vote.

Have a separate reviewer audit the subtask algorithms and measured scores. Benchmark every maximum-scale case at least three times when calibrating the time limit, retain the slowest single-case run, record the CPU/compiler, and apply the project formula. Save raw reviews, disposition of every comment, fixes, and recheck results.

Before release, write the structured `go`/`no_go` report required by [references/state-and-release-audit.md](references/state-and-release-audit.md). Its evidence must be current; a directory containing all expected filenames is not sufficient.

### 11. Package the optional Polyhedron project ZIP

After acceptance passes, follow the recorded `polyhedron_zip` choice and [references/polyhedron-package.md](references/polyhedron-package.md). The runner exposes `package` and `all`; use the reference for supported judge modes, build semantics, deterministic publication, stale-package reporting, and the offline package contract.

```text
python scripts/run_pipeline.py pipeline.json package
python scripts/run_pipeline.py pipeline.json all
```

### 12. Write and review the editorial

Proceed only after data acceptance. Read [references/solution-writing.md](references/solution-writing.md), [references/luogu-text-format.md](references/luogu-text-format.md), and [references/human-readable-contest-text.md](references/human-readable-contest-text.md), then adapt [assets/solution-template.md](assets/solution-template.md). Begin with a short intuitive explanation, then cover brute force and every distinct partial-score method before the full solution. For each method, state applicable cases, algorithm, correctness, time/space complexity, boundaries, and implementation correspondence.

Write for a human reader: connect observations concretely, avoid canned introductions, stock transitions, vague praise, synonym cycling, and repeated summaries; keep paragraphs focused, define notation before use, and retain only formalism that proves or implements something. Apply the same shared Markdown syntax and render checks required of the statement, plus editorial-specific `cpp` code fences. Check every claim against the frozen statement, scoring units, manifest, measured scores, and primary std.

## Exit criteria

Finish only when the intake contract is complete; the inventory is resolved; the final statement is fully Chinese, follows the frozen style and rewrite scope, uses the target Markdown renderer's `$...$` and `$$...$$` math syntax without unsupported `\(...\)` or `\[...\]` delimiters, strictly conforms to the selected platform standard, renders successfully, and passes both semantic and natural-prose review; every sample is legal and answer-checked; accepted existing data or generated data satisfies the same gates; the final pair count satisfies the frozen fixed or bounded policy and matches the executable pipeline; scoring units are valid; `data/config.yaml` is current, derived from those units, references every formal pair exactly once, and is included in the release; identical public constraint predicates have been merged and the public statement exposes no case ids; correct and partial solutions receive intended bundled or independent scores; maximum cases apply measured pressure; and the final audit says `go` with no blocking issue. When `polyhedron_zip` is `true`, also require package-root `polyhedron.zip` to exist, its path, SHA-256, members, and built status to be recorded in the report, its score structure to match the accepted scoring units, and no gate failure to remain. When the choice is `false`, do not treat an old `polyhedron.zip` as a result of the current run. Reject TODO markers, placeholders, empty implementations, stale evidence, missing references, unsupported math delimiters, unbalanced math spans, LaTeX commands outside math spans, one-off glossary paragraphs, formulaic filler, unstable terminology, or subtask constraints that require solution-oriented terminology to understand. When an editorial is requested, require coverage of every distinct partial method, full correctness and complexity analysis, code correspondence, the same shared Markdown/render checks as the statement, and a human-readability review.

Preserve unrelated files and do not delete unconfigured data. Adapt the runner before using it for interactive, output-only, multiple-answer, floating-tolerance, or custom-checker problems.
