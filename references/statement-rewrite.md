# Statement rewriting and freeze

Read [luogu-text-format.md](luogu-text-format.md) and [human-readable-contest-text.md](human-readable-contest-text.md) before drafting or reviewing the statement. Apply only their contest-text, Markdown, and mathematical writing rules; do not import unrelated platform policy or casual/blog-style guidance.

## Table of contents

1. Source baseline
2. Equivalent rewrite
3. Natural object vocabulary
4. Interface and boundaries
5. Constraints and subtasks
6. New samples
7. Risk review
8. Render and freeze

## Source baseline

Read the complete original statement, constraints, solution, programs, and relevant archives. Record the mathematical definition, input/output grammar, full-score algorithm, complexity, edge conditions, and all source paths internally. If these cannot be recovered reliably, mark the problem unusable or request clarification; never invent missing semantics.

The source may be Chinese, English, or bilingual. Treat an English statement as a semantic source, not as deliverable text: translate and rewrite the complete contestant-facing statement into natural Chinese, including headings, constraints, notes, sample explanations, and special properties. Keep identifiers and literal output strings in their required original form.

Keep original titles, URLs, paths, and modification history out of the contestant statement.

## Equivalent rewrite

Choose a new Chinese display title. Under the supplied NOIP convention, choose an English name containing one lowercase ASCII word and keep it unique within the contest day.

Use the concrete statement style frozen in the task contract:

- `formal`: omit narrative and state the mathematical task directly.
- `light-context`: use a short neutral setup, then move promptly to formal wording.
- `themed`: apply the user-approved setting and terminology consistently. Do not add unapproved people, franchises, lore, or jokes.

If the user selected “adaptive”, resolve it to one of these concrete modes under `source: delegated` before drafting. For a themed statement, freeze the theme, required and forbidden elements, title preference, generic-name policy, and whether theme terms may replace mathematical object names.

Remove or fully replace the original background. Change names, exposition, field order, or equivalent representation only within the frozen rewrite scope and when clarity improves. Preserve the state space, feasibility conditions, objective, answer semantics, and indispensable full-score algorithm. Record every material change internally.

## Natural object vocabulary

Build the statement around one coherent model that a contestant can keep in mind from beginning to end. Technical precision does not mean defining every possible derived object. Use this information hierarchy:

1. Define the objects, legal relations or operations, and required result in the description.
2. Describe only the input serialization in the input section.
3. Describe only the requested output and judging semantics in the output section.
4. Put global bounds and short extra scoring predicates in the constraints section.

Introduce a named term only when it reduces repetition or is used throughout the task. Put its definition immediately before its first meaningful use. Do not create a term for ordinary counting, restate an everyday phrase as a formal convention, or place a block of auxiliary definitions between the global constraints and subtask table.

Write each subtask property in the vocabulary already established by the statement. Prefer a direct predicate such as “每个横坐标和纵坐标至多在两个点中出现” over a separate definition of what “出现” means. A scoring row must not force contestants to learn an auxiliary graph, transformed sequence, DP state, or full-solution modeling device that the main task never uses.

When a derived representation is genuinely the clearest way to state both the task and its special properties, and the rewrite scope permits equivalent representation, make it the native model of the whole statement: update the description, input interpretation, samples, constraints, validator contract, and reference programs consistently. Do not append the representation only for the table. If a full coherent rewrite would be disproportionate, redesign the special property instead.

After drafting, remove every sentence that only decodes another sentence. Read the statement once as a contestant: no paragraph should exist solely to explain one table cell, and no essential term should first appear in the data-range section.

## Interface and boundaries

Define objects before use. State indexing, inclusive bounds, ordering, duplicates, ties, empty cases, connectivity, total-over-tests limits, and other legality rules explicitly. Make the input grammar agree exactly with generator and validator behavior.

If contestant file I/O is required, state `<english-name>.in` and `<english-name>.out`; keep teacher programs on standard streams and redirect them. Adapt and revalidate every reference program after an interface change.

## Constraints and subtasks

Make each subtask row map internally to a nonempty, mutually exclusive set of formal cases. Assign every case exactly once and make row scores total the full score. Store case ids, expected methods, dependencies, generator profiles, and intended kills in the executable scoring contract and internal manifest, never in the public statement.

Follow the frozen scoring mode. For bundled rows, state publicly only that all tests in the subtask must pass. Show only the subtask number, score, contestant-visible additional constraints, and a dependency column when dependencies actually exist. Do not list formal case ids or case ranges in `statement.md`.

Normalize contestant-visible additional constraints before freezing the table. Rows with the same predicate—including multiple rows that all say “无”—must be merged into one public subtask and one executable scoring unit, with their cases and points combined. Different seeds, input sources, validator groups, stress profiles, difficulty impressions, or attacked mistakes do not make different problem scales and must not create separate subtasks. If a platform implementation needs several physical data batches, keep them inside the same scoring unit so the public subtask remains all-or-nothing.

Keep contestant-facing rows short and declarative. Internal manifests may use generator profiles, graph invariants, semantic tags, and intended kills; the public table should expose only the minimum property a contestant needs. Do not copy internal test-design language into the statement.

Under the supplied NOIP convention, use exactly 20 equal five-point formal cases or 25 equal four-point formal cases. Do not turn the formal-case count into a required public-row count; public rows are determined by distinct contestant-visible constraint predicates. Make T1 fully solvable by basic algorithms or simple ad-hoc reasoning. Give T2/T3/T4 at least 30 basic-algorithm or brute-force points; with 25 cases use at least eight cases, totaling 32. Treat these counts as project policy, not universal rules.

## New samples

Never reuse an original mathematical instance through renaming, reordering, whitespace, or equivalent encoding. Validate every new sample input and cross-check its answer with the frozen oracle and an independent calculation.

Under the supplied NOIP convention, provide at least three samples: simple, medium, and one whose principal size parameter reaches the formal maximum. Add a sample for each boundary that distinguishes two reasonable interpretations. Keep sample files in `examples/`. Display sample 1 fully; display another only when its nonempty input and answer lines total at most 20, otherwise reference the distributed filename.

Use a sample explanation only when it clarifies the input/output process or a likely interpretation boundary. Do not reveal the central lemma, optimization, recurrence, or standard algorithm merely to make the explanation look complete.

## Risk review

Treat title, background, names, and narrative-order-only changes as low risk. Give one independent reviewer both statements and require a clause-by-clause equivalence check.

Treat input representation/order, constraints, output, or potentially ambiguous mathematical wording as high risk. Give the new statement alone to two blind reviewers. Require each to restate the mathematical problem, interface, constraints, and edge semantics before revealing the baseline and change record. Resolve disagreement through source evidence, proof, or a counterexample, never by majority vote.

Run a separate natural-prose review even when semantic reviewers agree. Ask the reviewer to identify:

- definitions used only once or introduced far from first use;
- ordinary ideas replaced by needless conventions;
- solution-oriented models appearing only in subtask rows;
- background or theme text that does not help comprehension;
- repeated caveats, long sentences, and table cells that need a preceding glossary;
- canned openings, stock transitions, vague claims, unstable terminology, forced lists, and repeated conclusions;
- wording that is correct only after reading a sample.

Reject the draft until every such issue is removed or justified by a concrete ambiguity that cannot be resolved more simply. Record raw reviews, disposition reasons, fixes, and rechecks. Reopen this gate after any later change to definition, interface, constraints, subtasks, or samples; invalidate and regenerate affected data.

## Render and freeze

Write `statement.md` in the selected platform's Markdown dialect and follow every rule in Shared typography and Shared Markdown syntax in [luogu-text-format.md](luogu-text-format.md). For statements, use the supported `text` info string for sample input and output, and reserve backticks for filenames, literal output, and identifiers that contestants must copy exactly.

Apply the shared delimiter, fence, link, table, escaping, filename, and render checks without omission. If a PDF is produced, verify it opens and inspect every page for garbling, formula or table errors, bad page breaks, overflow, and wrong sample references.

Freeze only when the change record is complete, semantic and natural-prose reviews pass, samples validate and cross-check, and the statement, validator, and oracle share one interpretation.
