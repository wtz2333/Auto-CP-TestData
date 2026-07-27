# Luogu text format

Apply this reference when Luogu-compatible Markdown is requested.

Official references: [problem standard](https://help.luogu.com.cn/rules/academic/problem-standard) and [solution standard](https://help.luogu.com.cn/rules/academic/solution-standard).

The official pages are normative. When internet access is available, open the current problem-standard page before drafting and record its displayed update version in the rewrite evidence; this local file is an execution checklist, not a replacement for the official text. If the official text and this summary differ, follow the official text and update this reference.

## Shared typography

- Use full-width Chinese punctuation and end complete sentences with punctuation.
- Put variables, numeric constants, operators, and expressions in Markdown math: `$...$` for inline formulas and `$$...$$` for display formulas.
- Use LaTeX mathematical commands only inside Markdown math delimiters. Do not use `\(...\)` or `\[...\]` delimiters.
- Keep ordinary English, algorithm names, titles, people, filenames, and literal output outside math; use inline code only when the text is literal.
- Insert a half-width space between Chinese and adjacent English, digits, formulas, or inline code, but not before Chinese punctuation.
- Keep terminology and variable capitalization consistent.

## Statement text

- Use Luogu-compatible Markdown. Mathematical notation must remain as formulas written with `$...$` and `$$...$$`; do not flatten formulas into code spans. Forbid unsupported `\(...\)` and `\[...\]` math delimiters, LaTeX commands outside math spans, raw HTML, custom directives, and unsupported sample fences.
- Keep the background helpful and short; it must not obstruct the mathematics.
- Make the description concise, rigorous, and understandable without relying on samples.
- Prefer ordinary, direct Chinese over invented conventions. Do not write “称……是指……” when a familiar idea can be stated plainly in the sentence or table cell that uses it.
- Introduce definitions next to their first use and only when they reduce repetition or resolve a real ambiguity.
- Keep one native object model throughout the statement. Do not introduce a solution transformation or auxiliary graph solely for one subtask constraint.
- Express public subtask properties as short predicates over objects already defined in the description. Keep generator profiles, intended algorithms, semantic tags, and internal graph invariants in the manifest.
- If a special property needs a long glossary, first try to rewrite it directly in the original input vocabulary. If that remains awkward, redesign the property. Only adopt an equivalent representation when it improves the whole statement and the authorized rewrite scope permits updating every affected section.
- Define ambiguous terms precisely, including empty objects, continuity, equivalence, and ties.
- In input format, state data types and combine parallel variables in one formula.
- Put literal output strings in inline code and mention Special Judge when needed.
- If an answer is taken modulo a value, say so in both description and output format.
- Give lower and upper bounds, string alphabets, real precision, and aggregate limits explicitly.
- State bundled testing prominently and avoid ambiguous overlapping percentages.
- Do not publish formal case ids or case ranges in the subtask table.
- Merge rows with identical contestant-visible additional constraints into one public subtask and one executable scoring unit. Internal data sources, seeds, profiles, and attack purposes must not split one problem scale into several subtasks.
- Derive limits from measured worst cases; use the stricter project timing formula when present.
- Always produce complete Chinese. Translate and review every definition, constraint, and sample explanation from an English source.

## Naturalness gate

Before freeze, require all of the following:

- A contestant can understand the task without reading samples or the subtask table.
- Every named term is used meaningfully after its definition; no definition exists only to decode one row.
- Every subtask row is understandable in one short reading and uses established vocabulary.
- No paragraph between the global constraints and scoring table acts as a one-off glossary.
- No solution lemma, transformed graph, DP state, or data-generation profile leaks into the statement unless it is genuinely the native problem definition.
- Removing redundant qualifiers does not change the legal input set or answer semantics.

Have a reviewer read only the final statement for fluency and concision. Semantic equivalence review cannot substitute for this gate.

## Editorial text

- Keep only problem-related content; omit chatter, self-promotion, and unrelated stories.
- Summarize a long statement instead of copying it.
- Explain the main algorithm or data structure concretely and justify important conclusions.
- Put the explanation outside code comments. Include readable code when the delivery requires it.
- Use Markdown links for cited material and keep images simple, clear, and necessary.
