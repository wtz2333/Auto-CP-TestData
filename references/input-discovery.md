# Original-problem directory discovery

## Required artifacts

Recursively inspect the supplied directory before planning work. Read relevant Markdown, source code, input/answer files, configuration, and safely inspect archives when needed. Ignore version-control metadata, editor settings, build outputs, executables, caches, and unrelated files.

Require and identify:

- One original Markdown statement, selected by its content rather than filename alone.
- One standard solution, normally C++ source; verify that it implements the recovered problem instead of trusting a `std` filename.

If several candidates exist, read and compare them. Record the selected path and the reason. A missing statement or unresolved semantic conflict is blocking. A missing std follows the oracle-recovery branch in the main workflow.

## Optional artifacts

Search for and classify:

- Existing editorial or solution notes.
- Formal `.in/.ans` data and sample data.
- Known wrong solutions.
- Partial-score or subtask solutions.
- Existing subtask/score definitions in the statement or configuration.
- Validator, generator, checker, scripts, or an original reference solution.

Write an inventory with `present`, `missing`, `ambiguous`, and `ignored` sections. Record paths, language, apparent role, and whether each artifact agrees with the chosen statement/std. Do not ask the user to provide optional artifacts merely because they are absent; create or derive them in the later workflow.

## Language handling

Detect the language of every statement candidate. If the only reliable statement is English, recover its exact mathematics and produce a fully readable Chinese rewrite; do not leave untranslated clauses, headings, constraints, or sample explanations. If Chinese and English versions coexist, compare them and record discrepancies before choosing the authoritative interpretation.

Translation must preserve quantifiers, index conventions, inclusivity, order, duplicates, empty cases, tie rules, limits, and output semantics. Apply the same rewrite-risk review as any other high-risk wording change.

## Initial branch report

Before editing, report:

- Selected statement and std paths.
- Statement language and whether Chinese translation is required.
- Which optional artifact classes exist.
- Whether existing data will enter audit-first mode.
- Which missing artifacts the workflow will create.
