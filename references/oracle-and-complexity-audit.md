# Oracle and complexity audit

Audit the standard and brute solutions before using either as evidence. A plausible algorithm name or successful compilation is insufficient.

## Standard solution

Record the exact algorithm, maintained invariant, proof obligations, and implementation mapping. Derive time and space complexity from the loops, transitions, data-structure operations, recursion, and test-count aggregates that the code actually performs.

Turn asymptotic claims into a constraint worksheet:

- Maximum value of each controlling parameter and aggregate.
- Upper bound on states, transitions, operations, allocated elements, and recursion depth.
- Integer width required for inputs, intermediates, products, counts, and answers.
- The input shape that realizes the claimed worst case.
- Which formal profiles exercise correctness extremes and which exercise resource pressure.

If implementation constants or allocator behavior matter, measure them. Do not accept “should pass” as complexity evidence.

Run all resource and recursion tests under [runtime-resource-policy.md](runtime-resource-policy.md). The default runtime stack equals the frozen memory limit, but the audit must still prove that legal recursion cannot exceed that budget and that newly written accepted code does not depend on an unsafe depth. Distinguish a host-default stack failure from a failure under the configured release stack.

## Brute oracle

Design `brute.cpp` from the mathematical contract, not by simplifying `std.cpp`. It must directly enforce all mandatory choices, ordering rules, duplicate behavior, ties, and feasibility conditions. Reject a brute model that changes a required object into an optional choice merely because that is easier to enumerate.

Keep the implementation structurally independent from the standard solution. If both necessarily share a transformation, audit the shared assumption separately and add a third oracle or complete enumeration where possible.

State the brute's trustworthy domain. Within that domain it must never produce WA; outside it, TLE or MLE may be expected and is not evidence of incorrectness. Do not use outputs produced after timeout, crash, or truncation.

## Differential profiles

Use complete tiny enumeration, seeded uniform and biased random cases, directed definition boundaries, and reduced versions of every adversarial or worst-case formal family. Require every planned round to complete. Record profile, range, count, seeds, mismatch count, and stopping reason. On mismatch, minimize the counterexample and identify the faulty program or interpretation before continuing.

## Checker-aware comparison

For multiple-answer or tolerance-based tasks, compare through the accepted checker rather than raw text. Test valid alternative outputs, malformed and incomplete outputs, extra tokens, tolerance boundaries, and known wrong outputs. Require consumption of every relevant stream.

When comparing two independently produced answers, document which file is jury output and which is contestant output. If the acceptance relation is intended to be symmetric, test both directions; do not assume symmetry from one successful call.
