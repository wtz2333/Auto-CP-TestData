# Judge test data configuration

Generate `data/config.yaml` for every standard batch package. Treat it as a
derived judge artifact, never as an independent source of scoring truth.

## Source mapping

Use `pipeline.json` as the only source:

- Write top-level `type: default`.
- Map each `scoring.units` entry to one YAML subtask, preserving unit order.
- Assign YAML `id` values `1, 2, ...` in that order.
- Copy `unit.points` to `score` without changing the total.
- Map a `bundle` unit to `type: min`.
- Map a single-case `case` unit to `type: sum`.
- Convert every `depends_on` unit id to its generated numeric YAML id and write
  the result as `if: [...]`; write `if: []` when there is no dependency.
- Write `memory: <memory_limit_mib>MB` on every generated subtask.
- Copy every unit member to `input: NNN.in` and `output: NNN.ans`, preserving
  the declared member order.
- Preserve the judge-facing field order exactly as
  `memory`, `score`, `if`, `id`, `type`, `cases`; under `cases`, write
  `input` before `output`. Keep the top-level order as `type`, then `subtasks`.
- Render the full expanded YAML. Do not use YAML anchors, aliases, merge keys,
  inline case objects, or omitted empty dependency lists.

Do not copy scores, case ranges, memory, dependency lists, or zero-score
subtasks from an example. Do not synthesize an unscored final case. A
zero-score subtask belongs in the YAML only when it is an explicit scoring unit.
Validator `group` values are legality promises and must not be used to infer
score grouping.

See [the output-shape example](../assets/testdata-config.example.yaml). Its
values correspond only to [the pipeline example](../assets/pipeline.example.json).

## Generation and checks

Declare:

```json
"testdata_config": {
  "path": "data/config.yaml"
}
```

The pipeline writes the YAML during `generate` and `all`. For accepted existing
data that does not need regeneration, run:

```text
python scripts/run_pipeline.py pipeline.json config
```

Before release, require all of the following:

1. Every referenced `.in` and `.ans` file exists.
2. Every formal case appears exactly once because the scoring-unit partition is
   already validated.
3. YAML scores, aggregation types, dependencies, member order, and memory are
   byte-for-byte derivable from the current pipeline.
4. The generated ids are unique and dependency references resolve.
5. The file is UTF-8 without a BOM, uses LF line endings, and ends with one
   newline.
6. `manifest.json` records the generated config path, hash, and unit mapping.
7. The delivered directory includes `data/config.yaml`. If and only if
   `archive_policy` is `user-requested` or `platform-required`, the release
   allowlist and archive also include it.

For interactive, output-only, multiple-answer, or custom-scored tasks, adapt
the runner and freeze the platform-specific mapping before generating this
file.
