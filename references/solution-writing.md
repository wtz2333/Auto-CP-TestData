# Editorial writing

Follow the textual and formatting requirements of the [Luogu solution standard](https://help.luogu.com.cn/rules/academic/solution-standard) when Luogu-compatible Markdown is requested.

## Required structure

Write one coherent Markdown editorial. Use this order unless the problem needs a clearer local variation:

1. `直观理解`: explain the central obstacle and observation in ordinary language.
2. `部分分`: cover brute force and every distinct partial-score algorithm from simpler to stronger.
3. `标准解法`: derive the full algorithm rather than announcing it abruptly.
4. `正确性证明`: prove the important invariant, transition, exchange, or equivalence.
5. `复杂度分析`: give time and space complexity with defined parameters.
6. `实现细节`: connect mathematical objects to states, arrays, structures, operations, and boundaries.
7. `参考代码`: include the readable primary implementation or its verified delivery copy.

Merge sections only when the result is genuinely easier to read; never omit required substance.

## Every partial score

Cover every subtask-table row. If several rows use the same algorithm, explain that algorithm once and list all covered rows. For each distinct method, state:

- Applicable test points, constraints, or special property and obtainable score.
- Core observation and exact procedure.
- Why it is correct, with proof depth proportional to the claim.
- Time and space complexity.
- Why it cannot handle the next range, when relevant.
- Important implementation boundaries.

Ensure these claims match the tested partial programs and measured score matrix. Do not describe an intended score that the formal data does not enforce.

Use the same scoring units as the statement, manifest, pipeline, and verdict report. For bundled scoring, say that the unit's points require every member case and dependency unit; do not present a partially passed bundle as earned credit. For mixed scoring, distinguish independently awarded points from all-or-nothing bundles.

## Human-readable style

Write as an experienced contestant explaining the solution to another contestant. Prefer short declarative sentences and concrete logical transitions. Introduce notation only when it reduces repetition. Explain why an observation matters before giving a formula or code detail.

Avoid generic openings, ceremonial conclusions, repeated restatements, fake quotations, excessive headings, adjective-heavy praise, and phrases such as “显然” when the implication is not immediate. Do not narrate the writing process or mention prompts. Keep one purpose per paragraph and remove any sentence that neither clarifies, proves, analyzes, nor implements the solution.

Maintain a modest formal tone: define states and invariants precisely, but do not turn routine operations into long lemmas. Use small examples only when they resolve a likely conceptual jump.

## Luogu text and Markdown rules

- Use full-width Chinese punctuation and end complete sentences with punctuation.
- Put mathematical variables, constants, operators, and expressions in LaTeX; do not put ordinary English words, algorithm names, people, or titles in LaTeX.
- Insert a half-width space between Chinese and adjacent English, digits, or formulas; do not insert one before Chinese punctuation.
- Use `\text{}` for prose inside formulas and `\texttt{}` for literal strings inside formulas.
- Keep variable capitalization and terminology consistent.
- Keep content relevant. Summarize long statements instead of copying the whole statement.
- Explain the algorithm outside code comments. Code comments may supplement but never replace analysis.
- Use ordinary Markdown links for cited material and record sources without copying protected content.
- Keep images simple and readable; avoid them when text or a small formula is clearer.

## Correctness and code correspondence

For every nontrivial claim, show the implication needed by the algorithm. State base cases, maintained invariants, transition completeness, and why the reported answer equals the required quantity. Cover ties, empty/extreme states, overflow, indexing, and multi-test reset when relevant.

Use the same notation in prose, formulas, and code. Map each important state or structure to its implementation. Keep the main routine clean and use procedural C++ plus STL or small focused structs. Verify that the delivered reference code hashes to the accepted primary std when the package requires an exact copy.

## Editorial review

Review against the frozen statement, subtask table, manifest, score matrix, and std. Reject the editorial if it skips a distinct partial method, claims an untested score, contains a proof gap, contradicts code, overexplains routine syntax, or reads like a reusable generic answer rather than this problem's reasoning.
