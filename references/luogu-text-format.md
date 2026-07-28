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

## Shared Markdown syntax

These rules apply equally to statements and editorials:

- Use ordinary Markdown headings, paragraphs, lists, supported tables, fenced code blocks, inline code, and links.
- Put every mathematical variable, numeric expression, relation, subscript, superscript, and formula in Markdown math.
- Use `$...$` for inline formulas. Put each opening and closing `$$` delimiter for display math on its own line.
- Allow LaTeX commands only inside `$...$` or `$$...$$`. Do not use `\(...\)` or `\[...\]` as delimiters.
- Do not replace formulas with backticks. Reserve inline code for filenames, literal input or output strings, language identifiers, and code that readers must copy exactly.
- Do not use raw HTML, custom directives, or platform-specific fences unless the frozen package contract and target renderer explicitly support them.
- Use only info strings supported by the target renderer. Statements normally use `text`; editorials may additionally use `cpp` for C++ source.
- Balance math delimiters, backticks, and code fences. Check list indentation, table shape, link targets, escaping, and filenames.
- Render or preview the finished document with the target engine and inspect formulas, tables, code blocks, links, and line wrapping before freeze.

## Statement text

- Follow every rule in Shared typography and Shared Markdown syntax. Use `text` fences for displayed sample input and output unless the frozen renderer requires another supported form.
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

- Follow every rule in Shared typography and Shared Markdown syntax. Use `cpp` fences for C++ source and `text` fences for plain input, output, traces, or pseudocode when a fence is actually needed.
- Keep only problem-related content; omit chatter, self-promotion, and unrelated stories.
- Summarize a long statement instead of copying it.
- Explain the main algorithm or data structure concretely and justify important conclusions.
- Put the explanation outside code comments. Include readable code when the delivery requires it.
- Use Markdown links for cited material and keep images simple, clear, and necessary.
- Do not put formulas in inline code, use raw HTML for layout, or rely on code comments to carry an omitted proof.
- Apply [human-readable-contest-text.md](human-readable-contest-text.md) and reject canned openings, stock transitions, synonym cycling, vague efficiency claims, repeated summaries, and ceremonial conclusions.
