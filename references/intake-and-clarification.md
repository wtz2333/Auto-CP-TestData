# Intake and clarification gate

Complete this gate before changing the statement, generating formal data, or writing deliverables. Read-only inventory of the supplied directory is allowed first because it prevents questions whose answers are already present in the source.

## Preference facts that require explicit authority

The following fields must be resolved by the user or by explicit user delegation. Never fill them from the original problem merely because one choice looks conventional:

| Field | Accepted form |
|---|---|
| `original_problem_dir` | Existing directory path supplied by the user |
| `output_dir` | Intended workspace or delivery path |
| `case_count` | Positive number of independent `.in/.ans` pairs |
| `deliverables` | Nonempty selection such as statement, data, programs, editorial, reports, or full package |
| `scoring_mode` | `per_case`, `bundled`, or `mixed` |
| `scoring_plan` | Whether units are user-supplied or delegated, and whether expected partial scores are exact values or ranges |
| `statement_style` | `formal`, `light-context`, or `themed` after delegation is resolved |
| `rewrite_scope` | `narrative-only`, `constraints-and-subtasks`, or `equivalent-interface` |
| `target_audience` | Named contest level or a concrete description of expected contestants |
| `package_format` | `luogu-markdown`, `tuack-noi`, `plain-directory`, or a named custom format |

Accept “you decide” for any preference except the original-problem path, output path, and exact case count. Treat it as explicit delegation, choose a concrete value, record `source: delegated`, and write a short `decision_note`. Do not store an unresolved “adaptive” value: resolve it to a concrete choice before closing this gate.

## Statement-style choices

- `formal`: no narrative background; define the objects and required result directly.
- `light-context`: use at most a short, natural setup, then switch to precise mathematical wording. This is the normal neutral choice.
- `themed`: use the requested setting, characters, or vocabulary consistently without letting lore change or obscure the mathematics.
- “adaptive” is a questionnaire response, not a final stored mode. It authorizes choosing one of the three concrete modes.

For `themed`, also resolve the theme or characters, required and forbidden elements, title preference, whether generic names such as 小明 or 小红 are allowed, and whether theme terms may replace mathematical object names throughout the statement. If these details are omitted, ask; do not invent a specific franchise, person, or setting.

## Scoring choices

- `per_case`: every scoring unit contains exactly one case and earns its own points independently.
- `bundled`: every scoring unit is a bundle; its points are earned only when all member cases and all dependency units pass.
- `mixed`: at least one independent single-case unit and at least one multi-case bundle coexist.

When `bundled` or `mixed` is selected, resolve whether the user supplies grouping or delegates its design. Freeze unit ids, member case ids, points, and optional dependencies before formal generation. A case belongs to exactly one scoring unit. Dependencies form an acyclic graph and do not change case membership.

Store `scoring_plan.value.unit_authority` as `user-supplied` or `delegated`, and `scoring_plan.value.expectation_mode` as `exact` or `range`. The `scoring_plan` choice itself must have `source: user`.

## Discoverable technical facts

Inspect the directory before asking about compiler standard, time and memory limits, input/output grammar, file-I/O names, judge mode, constraints, total-over-tests limits, subtasks, samples, checker need, and existing data. Record each recovered fact with source path and evidence.

Ask only when a technical fact is absent, unreliable, or contradictory. Quote conflicts rather than choosing whichever source was read last. A nonstandard judge mode, missing limit, ambiguous English clause, or incompatible statement/std interface is blocking until resolved.

Before running the executable pipeline, require concrete `language_standard`, `time_limit_ms`, `memory_limit_mib`, and `judge_mode` facts. Their values must match the compiler flags and pipeline configuration.

## Fixed workflow rules

Do not ask whether to:

- deliver the final statement in Chinese;
- audit supplied data before regeneration;
- recover and verify a missing or untrusted std;
- create an independently reasoned brute oracle;
- test accepted, partial, and wrong solutions;
- cover every distinct partial method in the editorial;
- rerun invalidated evidence after a repair.

These are invariants of the Skill.

## Question protocol

After read-only inventory, list all unresolved preference fields in one compact numbered questionnaire. Use short options and let the user reply with codes such as `1B 2A 3C`. Ask a second round only for conditional details such as a selected theme or custom package format.

Do not begin mutating work while any required preference has `source: unresolved`. If the user changes an accepted preference later, reopen every affected gate.

Suggested Chinese questionnaire:

```text
开始前还需要确认：
1. 交付范围：A 完整题包；B 仅题面；C 仅数据；D 自定义。
2. 计分方式：A 独立测试点；B 子任务捆绑；C 混合计分；D 由我决定。并说明分组由你提供还是委托我设计，以及预期得分采用精确值还是区间。
3. 题面风格：A 完全形式化；B 轻量背景；C 主题化背景；D 由我决定。
4. 改编权限：A 仅标题/叙述；B 可调整约束与部分分；C 可作等价输入改写。
5. 目标选手与题包格式：请给出比赛层级及洛谷、Tuack/NOI、普通目录或自定义格式。
```

Ask separately for any missing directory path, output path, or exact case count because those values are not safely delegated without an explicit target.
