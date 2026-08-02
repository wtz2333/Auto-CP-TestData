# Intake and clarification gate

Complete this gate before changing the statement, generating formal data, or writing deliverables. Read-only inventory of the supplied directory is allowed first because it prevents questions whose answers are already present in the source.

## Preference facts that require explicit authority

The following fields must be resolved by the user or by explicit user delegation. Never fill them from the original problem merely because one choice looks conventional:

| Field | Accepted form |
|---|---|
| `original_problem_dir` | Existing directory path supplied by the user |
| `output_dir` | Exact delivery path, or a user-supplied parent plus explicit delegation to use the rewritten title as the folder name |
| `case_count_policy` | Fixed positive count, or the bounded strength-driven bundled policy |
| `deliverables` | Nonempty selection such as statement, data, programs, editorial, reports, or full package |
| `scoring_mode` | `per_case`, `bundled`, or `mixed` |
| `scoring_plan` | Whether units are user-supplied or delegated, and whether expected partial scores are exact values or ranges |
| `statement_style` | `formal`, `light-context`, or `themed` after delegation is resolved |
| `rewrite_scope` | `narrative-only`, `constraints-and-subtasks`, or `equivalent-interface` |
| `target_audience` | Named contest level or a concrete description of expected contestants |
| `package_format` | `luogu-markdown`, `tuack-noi`, `plain-directory`, or a named custom format |
| `archive_policy` | `none` by default; `user-requested` or `platform-required` only with a recorded reason |

Accept “you decide” for any preference except the original-problem path. Treat it as explicit delegation, choose a concrete value, record `source: delegated`, and write a short `decision_note`. For the output directory, delegation is valid only after the user supplies the parent directory; choose the rewritten title first, use that exact title as the folder name, and store the resolved absolute output path. Do not store a vague “adaptive” value: use the concrete bounded policy below.

## Statement-style choices

- `formal`: no narrative background; define the objects and required result directly.
- `light-context`: use at most a short, natural setup, then switch to precise mathematical wording. This is the normal neutral choice.
- `themed`: use the requested setting, characters, or vocabulary consistently without letting lore change or obscure the mathematics.
- “adaptive” is a questionnaire response, not a final stored mode. It authorizes choosing one of the three concrete modes.

For `themed`, also resolve the theme or characters, required and forbidden elements, title preference, whether generic names such as 小明 or 小红 are allowed, and whether theme terms may replace mathematical object names throughout the statement. If these details are omitted, ask; do not invent a specific franchise, person, or setting.

Store `statement_style.value.protagonist_aliases` as an object with `enabled` and `names`. Questionnaire option 10A resolves to `{"enabled":true,"names":["小 W","小 Z"]}`; option 10B resolves to `{"enabled":false,"names":[]}`; option 10C stores the supplied nonempty, distinct names. Enabled aliases are available narrative names, not a requirement to add an artificial actor paragraph to a formal statement.

## Archive policy

A complete problem package means a complete directory unless the user or target platform explicitly requires an archive. If neither does, store `archive_policy.value` as `none`, use `source: delegated`, record that this is the Skill default, and do not create a ZIP. If the user explicitly requests an archive, store `user-requested` with `source: user`. If the platform contract requires one, store `platform-required` and cite the platform evidence in `decision_note`. Do not infer that “完整题包”, “Tuack / NOI”, or a request for all deliverables implies ZIP packaging.

## Scoring choices

- `per_case`: every scoring unit contains exactly one case and earns its own points independently.
- `bundled`: every scoring unit is a bundle; its points are earned only when all member cases and all dependency units pass.
- `mixed`: at least one independent single-case unit and at least one multi-case bundle coexist.

When `bundled` or `mixed` is selected, resolve whether the user supplies grouping or delegates its design. Freeze unit ids, member case ids, points, and optional dependencies before formal generation. A case belongs to exactly one scoring unit. Dependencies form an acyclic graph and do not change case membership.

For `per_case` and `mixed`, require `case_count_policy.value` to be `{"mode":"fixed","count":N}` with a user-supplied positive `N`. For `bundled`, also allow `{"mode":"bounded_adaptive","min":20,"max":40,"retain_existing":true,"fill_by_hacks":true}`. Under that policy:

- preserve every supplied formal input in the final set after legality checking and answer repair;
- add only cases with a named boundary, hack, or stress purpose;
- derive the final exact count after running the wrong/partial solution suite;
- stop between 20 and 40 cases once the strength goals pass;
- treat more than 40 supplied formal inputs, or an unpreservable illegal supplied input, as a blocking conflict.

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

After read-only inventory, use [the fixed intake questionnaire](../assets/intake-questionnaire.md). Copy it verbatim and replace only bracketed discovered-value placeholders. Do not reorder, rename, add, remove, combine, or reinterpret questions or options. Let the user reply with codes such as `1B 2A 3C` plus any requested free-text values.

Do not begin mutating work while any required preference has `source: unresolved`. If the user changes an accepted preference later, reopen every affected gate.

The fixed template includes output location, delivery scope, scoring and count policy, grouping authority, statement style, rewrite scope, audience, package format, technical limits, protagonist aliases, and conditional custom details. Ask a second round only when the reply is contradictory or omits a value explicitly required by the selected option. For `per_case` and `mixed`, an exact count remains mandatory; for `bundled`, the fixed bounded policy is allowed. Resolve the archive policy from explicit user/platform requirements and otherwise store the fixed `none` default without an additional question.
