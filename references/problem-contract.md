# Problem contract and workspace

## Table of contents

1. Required facts
2. Recommended workspace
3. Pipeline configuration
4. Text and source-of-truth rules
5. Judge modes

## Required facts

Record the title, C++ standard, release compiler flags, limits, exact input grammar, every scalar range, total-over-tests constraints, cross-field invariants, output semantics, subtasks with point allocation, and exact `case_count`. One case means one independent input/answer pair, even when the file contains multiple test instances.

When prose and formal constraints conflict, pause for resolution and quote the conflict in the report.

Choose one machine-readable contract as the source of truth. If a descriptive `task.json` and executable `pipeline.json` coexist, assign shared fields a single owner and record the owner revision/hash in the derived file. Never resolve disagreement by whichever file is newer or read last.

## Recommended workspace

```text
problem/
  original-statement/
  inventory.md
  statement.md
  rewrite-record.md
  task.json
  pipeline.json
  std.cpp
  brute.cpp
  valid.cpp
  gen.cpp
  solutions/{accepted,subtask,wrong}/
  data/001.in, data/001.ans, ...
  examples/
  build/
  logs/
  manifest.json
  verdicts.json
  report.md
  solution.md
```

Keep sources and declarative case plans under version control. Do not put generated problem artifacts inside the Skill folder.

Keep the source baseline, directory inventory, and rewrite record internal. Put only the rewritten Chinese statement and intended samples in contestant-facing locations. Record accepted data provenance and hashes in the report. Add statement, editorial, rewrite record, and sample files to `text_files` when the pipeline enforces LF.

Adapt the layout to the surrounding package. If it requires `src/std.cpp`, `src/gen.cpp`, `src/val.cpp`, `src/brute.cpp`, a root `run.sh`, and separate `cases/examples` and `cases/data`, use that layout consistently; do not create a second conflicting hierarchy.

## Pipeline configuration

Start from `assets/pipeline.example.json`. Paths are relative to the configuration file. Require:

- `case_count`: exact number of pairs.
- `cases`: exactly that many objects with unique `id`, integer `seed`, `profile`, group, and optional points.
- `sources.generator`, `sources.validator`, and `sources.oracle`.

Each case must also provide nonempty semantic `tags` and a written `purpose` explaining what the point proves or attacks.

Optional fields include `compiler`, `cxxflags`, output directories, timeouts, `output_compare` (`tokens` or `exact`), `max_output_bytes`, `generator_args`, `validator_args`, `text_files`, timing controls, and `solutions`.

Each solution expectation may contain:

```json
{
  "must_pass": ["001", "002"],
  "must_fail": ["004"],
  "must_fail_one_of": ["003", "004", "005"],
  "score_min": 25,
  "score_max": 35
}
```

Use `["*"]` for all configured cases. `must_fail_one_of` means at least one listed case must produce a non-AC verdict.

For every candidate solution, also record its role, algorithm, complexity, and supported domain. A wrong solution additionally records `defect_layer` (`conceptual`, `complexity`, or `implementation`), the isolated defect, and the intended killing profile.

## Text and source-of-truth rules

Keep `std.cpp` as the single primary answer source. Verify hashes when copying it into a delivery tree. Require LF line endings for source, configuration, shell, Markdown, input, and answer files when the project specifies LF; configure extra files through `text_files`. On Windows, normalize generated CRLF to LF before validation, hashing, and storage, while rejecting isolated carriage returns.

Use fixed seeds and explicit modes in the declarative case list or `run.sh`. Do not copy original formal inputs; use them only as coverage references or differential-test material.

## Judge modes

- Use `tokens` for ordinary integer/string output where whitespace is insignificant.
- Use `exact` only when whitespace is semantically significant.
- Extend the runner with a checker before handling multiple answers or numerical tolerance.
- Do not use the ordinary pipeline unchanged for interactive or output-only tasks.
- Prefer ordinary batch problems. If a checker is unavoidable, use the project's fixed `testlib.h` version, record its source/version, and test both accepted and rejected outputs.
- For checker-based judging, use the checker for sample answers, formal answer consistency, differential tests, and candidate scoring. Test malformed, incomplete, extra-token, boundary-tolerance, and valid alternative outputs; verify all relevant streams reach EOF.
- If a checker is used to compare two independently generated valid answers and the relation should be symmetric, run both answer directions and investigate any difference.
