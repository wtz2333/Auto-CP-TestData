# Editorial writing

Follow the textual and formatting requirements of the [Luogu solution standard](https://help.luogu.com.cn/rules/academic/solution-standard) when Luogu-compatible Markdown is requested.

Read [luogu-text-format.md](luogu-text-format.md) and [human-readable-contest-text.md](human-readable-contest-text.md) before drafting or reviewing. The editorial inherits every Markdown syntax, mathematics, typography, and render requirement used for the statement unless this reference gives a stricter editorial-specific rule.

## Default structure

Write one coherent Markdown editorial. Unless the user requests another structure, use this order:

1. `简化题意`: retain only the objects, operation, and required answer needed to understand the solution.
2. `子任务` or `部分分`: follow the statement order and explain only genuine algorithmic differences.
3. `完整做法`: derive the full algorithm and its core states, formulas, or data structures.
4. `实现细节`: include only boundaries that materially affect a correct implementation.
5. `参考代码`: include the readable primary implementation or its verified delivery copy.

Do not add a generic `直观理解` section when `简化题意` and the first algorithmic observation already cover it. Correctness and complexity are optional sections governed by the rules below, not mandatory headings.

## Every partial score

Follow every subtask-table row in order, but distinguish a scoring row from an algorithm. If several rows use the same algorithm, explain that algorithm once and briefly point the other rows to it. For each genuine partial method, state only what is useful:

- Applicable test points, constraints, or special property and obtainable score.
- Core observation and exact procedure.
- A short correctness justification only when the method contains a non-obvious step.
- A one-sentence time or space bound when it helps explain why the method fits the constraint.
- Why it cannot handle the next range, when relevant.
- Important implementation boundaries.

Do not invent a partial solution for a subtask or score level whose only purpose is to catch a correct solution written incorrectly or implemented inefficiently. Examples include excessive constants, deep recursion, insufficient array sizes, missing multi-test reset, overflow, and a small local omission in the full solution. Such a row may receive a short implementation note or simply point to the complete method; it does not need its own algorithm exposition.

Ensure these claims match the tested partial programs and measured score matrix. Do not describe an intended score that the formal data does not enforce.

Use the same scoring units as the statement, manifest, pipeline, and verdict report. For bundled scoring, say that the unit's points require every member case and dependency unit; do not present a partially passed bundle as earned credit. For mixed scoring, distinguish independently awarded points from all-or-nothing bundles.

## Proof and complexity restraint

Do not create standalone correctness and complexity sections by default.

- Give a separate proof only when correctness depends on a genuine conceptual step: a greedy exchange, maintained invariant, complete DP transition, unique decomposition, transformed-problem equivalence, or similarly non-obvious claim.
- For enumeration, direct simulation, straightforward recurrence execution, or a formula whose derivation is already shown, do not append a ceremonial correctness proof.
- Give a separate complexity analysis only when the bound needs amortization, a global sum, several parameters, or a nontrivial data-structure argument.
- When the bound follows immediately from the loops or state count, state it once beside the method. Do not repeat the same complexity for every subtask that shares the method.

## Human-readable style

Write as an experienced contestant explaining the solution to another contestant. Prefer short declarative sentences and concrete logical transitions. Introduce notation only when it reduces repetition. Explain why an observation matters before giving a formula or code detail.

Begin with the problem-specific obstacle or observation. Avoid generic openings, ceremonial conclusions, repeated restatements, fake quotations, excessive headings, adjective-heavy praise, and phrases such as “显然” when the implication is not immediate. Do not narrate the writing process or mention prompts. Keep one purpose per paragraph and remove any sentence that neither clarifies, proves, analyzes, nor implements the solution.

Maintain a modest formal tone: define states and invariants precisely, but do not turn routine operations into long lemmas. Use small examples only when they resolve a likely conceptual jump.

Keep one stable name for each object; do not cycle through synonyms for variety. Prefer exact operations and complexity changes over vague claims such as “显著提升效率”. Use a transition only when it marks a real logical relation. Do not force every method into a three-step list or repeat the same sentence pattern across sections. Stop after the last necessary proof, implementation, or complexity point instead of appending encouragement or a generic summary.

## Luogu text and Markdown rules

- Apply every rule in Shared typography and Shared Markdown syntax in [luogu-text-format.md](luogu-text-format.md); none of the statement's delimiter, raw-HTML, custom-directive, fence-balance, link, table, or render checks may be skipped for an editorial.
- Put mathematical variables, constants, operators, and expressions in `$...$` or `$$...$$`; do not put ordinary English words, algorithm names, people, or titles in math.
- Put display-math delimiters on their own lines. Forbid `\(...\)`, `\[...\]`, LaTeX commands outside math, and formulas disguised as inline code.
- Use `\text{}` for prose inside formulas and `\texttt{}` for literal strings inside formulas.
- Reserve backticks for filenames, literal strings, identifiers, and code. Use `cpp` fenced blocks for C++ and `text` fenced blocks for plain input, output, traces, or pseudocode.
- Use ordinary Markdown headings, paragraphs, lists, supported tables, and links. Do not use raw HTML, custom directives, decorative layout tricks, or unsupported sample/code fences.
- Balance math delimiters, backticks, and code fences. Validate list indentation, table shape, links, escaping, and filenames, then render with the target engine and inspect every formula, table, and code block.
- Use full-width Chinese punctuation, required half-width spacing, consistent capitalization, and stable terminology throughout.
- Keep content relevant. Summarize long statements instead of copying the whole statement.
- Explain the algorithm outside code comments. Code comments may supplement but never replace analysis.
- Use ordinary Markdown links for cited material and record sources without copying protected content.
- Keep images simple and readable; avoid them when text or a small formula is clearer.

## Necessary correctness and code correspondence

For every nontrivial claim, show the implication needed by the algorithm at the point where it is used. State base cases, maintained invariants, transition completeness, or final-answer correspondence only when they are not already immediate from the derivation. Cover ties, empty or extreme states, overflow, indexing, and multi-test reset when relevant.

Use the same notation in prose, formulas, and code. Map each important state or structure to its implementation. Keep the main routine clean and use procedural C++ plus STL or small focused structs. Verify that the delivered reference code hashes to the accepted primary std when the package requires an exact copy.

## Editorial review

Review against the frozen statement, subtask table, manifest, score matrix, and std. Run the revision pass in [human-readable-contest-text.md](human-readable-contest-text.md), then render the Markdown with the target engine. Reject the editorial if it skips a genuine partial algorithm, invents a method for an implementation-only scoring boundary, claims an untested score, leaves a non-obvious proof gap, contradicts code, fails any shared statement/editorial Markdown check, overexplains routine syntax, or reads like a reusable generic answer rather than this problem's reasoning.
