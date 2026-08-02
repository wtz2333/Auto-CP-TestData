# Human-readable contest text

Apply this reference to contestant statements, editorials, sample explanations, and human-facing review reports. It adapts useful editing principles from [Humanizer-zh](https://github.com/op7418/Humanizer-zh) to formal algorithm-contest writing.

The goal is clear, natural technical Chinese. It is not to evade detection, imitate casual speech, or add personality for its own sake. Mathematical precision, proof completeness, frozen terminology, and platform rules always take priority.

## Core editing principles

- State the fact, definition, observation, or conclusion directly. Delete ceremonial openings, motivational filler, and sentences that merely announce what the next paragraph will do.
- Give each paragraph one main job. Put definitions near first use and put the reason for a formula before or immediately after it.
- Use stable names for the same object. Do not rotate synonyms merely to avoid repetition; in technical writing, controlled repetition is usually clearer.
- Prefer concrete subjects and actions. Replace vague claims such as “this greatly improves efficiency” with the exact complexity change, maintained property, or eliminated work.
- Trust the reader. Explain genuine conceptual jumps, but do not restate a clear sentence in two weaker forms or defend routine choices with repeated caveats.
- Keep qualifiers only when they change the claim. Words such as “通常”“一般来说”“在某种意义上” must identify a real exception or be removed.
- Use ordinary verbs such as “是”“有”“可以”“维护”“枚举”“合并” when they are exact. Avoid inflated phrasing that makes a simple operation sound abstract.
- Vary sentence length only when it improves rhythm. Do not mechanically force every paragraph into the same pattern, and do not manufacture three-item lists or binary contrasts.
- Use transitions only when the logical relation needs marking. Do not begin successive paragraphs with stock connectors such as “此外”“然而”“值得注意的是”.
- Remove slogan-like conclusions, exaggerated importance, marketing language, fake quotations, vague attributions, chatbot courtesies, and generic positive endings.
- Use bold, block quotations, dashes, and parenthetical remarks sparingly. Structure should come mainly from clear headings and paragraph order.

## Statement adaptation

- Background exists to establish objects or motivation, not to perform a dramatic introduction. End it as soon as the mathematical task can be stated.
- Prefer one direct definition over a story followed by a second formal restatement of the same definition.
- Do not hint at algorithms through phrases such as “cleverly maintain”, “efficiently calculate”, or “find an optimal strategy” unless that wording is part of the actual objective.
- State legality, ties, empty cases, and other semantic boundaries once, in the section where contestants need them.
- Keep sample explanations factual. Explain how the shown answer follows from the instance without turning the explanation into a miniature solution.
- A themed statement may have a recognizable voice, but jokes, lore, and named entities must not interrupt the input model or force contestants to translate theme terms back into mathematical objects.

## Editorial adaptation

- Begin with the obstacle or observation specific to this problem, not with “这是一道……” or a generic classification of the topic.
- Derive each method from the previous limitation. Do not use a fixed template of “first, second, finally” when the reasoning has a different shape.
- State what a data structure or recurrence stores before listing operations or formulas.
- Pair every nontrivial formula with its role in the algorithm. Do not translate a formula word for word after it is already clear.
- Give proof at the first point where correctness becomes non-obvious. Routine implementation steps do not need theorem-like packaging.
- For partial solutions, explain why each method fits its range and where it stops. Avoid repeating the full problem statement for every subtask.
- Do not turn implementation-only scoring boundaries, such as excessive constants, recursion depth, array bounds, missing reset, or overflow, into artificial partial algorithms.
- Do not add standalone correctness or complexity sections when a local sentence already settles the point. Reserve them for genuinely difficult proofs or bounds.
- End after the final necessary implementation or complexity point. Do not add a ceremonial summary, encouragement, or claim about how “elegant” the solution is.

## What not to import

- Do not add first-person opinions, feelings, humor, tangents, deliberate imperfections, or unfinished thoughts to simulate an individual voice.
- Do not weaken definitions, omit proof steps, or replace exact terminology with colloquial synonyms for “naturalness”.
- Do not maintain a blacklist of supposedly artificial words. Judge a phrase by whether it carries necessary meaning in this document.
- Do not optimize text for an AI-detection score. Review it for correctness, directness, rhythm, trust in the reader, and concision.

## Revision pass

Read the finished document aloud or sentence by sentence and check:

1. Does the opening reach problem-specific content immediately?
2. Does every paragraph add a definition, inference, proof, complexity fact, boundary, or implementation fact?
3. Are sentence lengths and structures needlessly repetitive?
4. Are connectors, dashes, parentheses, bold text, or three-item lists being used as decoration?
5. Is any object renamed without mathematical need?
6. Is a vague claim hiding an exact condition, operation, or complexity?
7. Is the reader told the same thing more than once?
8. Does the final paragraph stop naturally after the last necessary point?

Revise until every retained sentence has a clear function. Naturalness review does not replace semantic, proof, Markdown-render, or code-correspondence review.
