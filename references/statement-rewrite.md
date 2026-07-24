# Statement rewriting and freeze

Read [luogu-text-format.md](luogu-text-format.md) before drafting or reviewing the statement. Apply only its textual and mathematical writing rules; do not import unrelated platform policy.

## Table of contents

1. Source baseline
2. Equivalent rewrite
3. Interface and boundaries
4. Constraints and subtasks
5. New samples
6. Risk review
7. Render and freeze

## Source baseline

Read the complete original statement, constraints, solution, programs, and relevant archives. Record the mathematical definition, input/output grammar, full-score algorithm, complexity, edge conditions, and all source paths internally. If these cannot be recovered reliably, mark the problem unusable or request clarification; never invent missing semantics.

The source may be Chinese, English, or bilingual. Treat an English statement as a semantic source, not as deliverable text: translate and rewrite the complete contestant-facing statement into natural Chinese, including headings, constraints, notes, sample explanations, and special properties. Keep identifiers and literal output strings in their required original form.

Keep original titles, URLs, paths, and modification history out of the contestant statement.

## Equivalent rewrite

Choose a new Chinese display title. Under the supplied NOIP convention, choose an English name containing one lowercase ASCII word and keep it unique within the contest day.

Remove or fully replace the original background. Prefer a short neutral context or direct formal wording. Change names, exposition, field order, or equivalent representation only when clarity improves. Preserve the state space, feasibility conditions, objective, answer semantics, and indispensable full-score algorithm. Record every material change internally.

## Interface and boundaries

Define objects before use. State indexing, inclusive bounds, ordering, duplicates, ties, empty cases, connectivity, total-over-tests limits, and other legality rules explicitly. Make the input grammar agree exactly with generator and validator behavior.

If contestant file I/O is required, state `<english-name>.in` and `<english-name>.out`; keep teacher programs on standard streams and redirect them. Adapt and revalidate every reference program after an interface change.

## Constraints and subtasks

Make each subtask row map to a nonempty, mutually exclusive set of formal points. List point ids, extra constraints, score, and expected method. Assign every point exactly once and make row scores total the full score.

Under the supplied NOIP convention, use exactly 20 equal five-point cases or 25 equal four-point cases. Require at least five rows for T1/T2 and ten for T3/T4. Make T1 fully solvable by basic algorithms or simple ad-hoc reasoning. Give T2/T3/T4 at least 30 basic-algorithm or brute-force points; with 25 cases use at least eight points, totaling 32. Treat these counts as project policy, not universal rules.

## New samples

Never reuse an original mathematical instance through renaming, reordering, whitespace, or equivalent encoding. Validate every new sample input and cross-check its answer with the frozen oracle and an independent calculation.

Under the supplied NOIP convention, provide at least three samples: simple, medium, and one whose principal size parameter reaches the formal maximum. Add a sample for each boundary that distinguishes two reasonable interpretations. Keep sample files in `examples/`. Display sample 1 fully; display another only when its nonempty input and answer lines total at most 20, otherwise reference the distributed filename.

Use a sample explanation only when it clarifies the input/output process or a likely interpretation boundary. Do not reveal the central lemma, optimization, recurrence, or standard algorithm merely to make the explanation look complete.

## Risk review

Treat title, background, names, and narrative-order-only changes as low risk. Give one independent reviewer both statements and require a clause-by-clause equivalence check.

Treat input representation/order, constraints, output, or potentially ambiguous mathematical wording as high risk. Give the new statement alone to two blind reviewers. Require each to restate the mathematical problem, interface, constraints, and edge semantics before revealing the baseline and change record. Resolve disagreement through source evidence, proof, or a counterexample, never by majority vote.

Record raw reviews, disposition reasons, fixes, and rechecks. Reopen this gate after any later change to definition, interface, constraints, subtasks, or samples; invalidate and regenerate affected data.

## Render and freeze

Check Markdown tables, formulas, escaping, filenames, and renderer syntax. If a PDF is produced, verify it opens and inspect every page for garbling, formula/table errors, bad page breaks, overflow, and wrong sample references.

Freeze only when the change record is complete, reviews pass, samples validate and cross-check, and the statement, validator, and oracle share one interpretation.
