# Adversarial agent strength review

Apply this review after the statement, scoring units, oracle, and an initial formal data set are frozen. Its purpose is to discover score leakage: plausible solutions that are not valid full solutions but receive more points than their proved domain should allow.

## Table of contents

1. Red-team role and isolation
2. Minimum three-round protocol
3. Candidate portfolio
4. Close-complexity frontier
5. Multi-test heterogeneity
6. Repair loop
7. Required evidence and exit rule
8. External survivor regression
9. Proof-obligation coverage
10. Harness-valid verdicts
11. Complexity-survivor postmortem

## Red-team role and isolation

Dispatch an adversarial contestant agent independently from the statement, oracle, and data designers. Give it only the frozen contestant-facing statement, public constraints and subtasks, language and judge mode, and time, memory, and stack limits. Do not expose `std.cpp`, `brute.cpp`, generator or validator source, formal inputs or answers, manifests, intended kills, or another agent's code before it submits its own candidates.

Tell the agent to maximize awarded score without using a correct full solution. It must produce plausible contestant programs based on a stated false assumption, restricted domain, weaker algorithm, or excessive complexity. Randomly corrupting correct code, inserting undefined behavior, or submitting code known to fail immediately does not test data strength.

For every candidate, require:

- algorithm and actual time and space complexity;
- claimed supported domain and the reason it is not a valid full solution;
- one isolated defect or resource boundary;
- the public scoring units it attempts to obtain;
- compilable source and an expected score range.
- a peak-resource budget and confirmation that no unrelated host/system failure is required for rejection.

If analysis, proof, or exhaustive testing shows that a candidate is a correct alternative full solution, reclassify it as accepted. It does not count as a wrong attack for that round, and the agent must still submit a genuinely non-full candidate.

## Minimum three-round protocol

Complete at least three distinct adversarial rounds:

1. **Broad attack:** target common false observations, missing cases, greedy or DP mistakes, and boundary assumptions derived only from the statement.
2. **Score-farming attack:** target every public subtask boundary, partial algorithm, and plausible close-complexity solution; deliberately optimize for the largest score below full correctness.
3. **Adaptive attack:** reveal only the previous candidates' aggregate verdicts and per-public-unit scores, not case contents or generator details. Ask for new candidates or mutations that exploit the observed leakage.

A round counts only when it introduces at least one new proved-wrong defect or complexity class, compiles it, runs it on the complete formal set, and records its per-unit score. Reusing the same assumption with cosmetic code changes, rerunning an old binary, or producing only invalid/undefined programs does not count.

Three rounds are a minimum, not a stopping rule. Continue when a candidate exceeds its allowed score, a new plausible weakness is identified, or the latest repair has not yet survived a clean adaptive round. If independent-agent capability is unavailable, mark the data-acceptance gate blocked rather than replacing the adversary with the data designer's own guesses.

## Candidate portfolio

Across the rounds, cover every problem-relevant layer:

- conceptual mistakes and overstrong structural assumptions;
- genuine partial algorithms tied to public subtask constraints;
- close but out-of-budget time or memory complexities;
- implementation defects such as overflow, reset, ties, indexing, recursion, or parsing;
- algorithms that are correct on random or average-shaped inputs but fail on directed structures.

Do not satisfy coverage with many variants of one bug. Maintain a ledger keyed by defect and complexity class, and require the adversarial agent to target gaps in that ledger.

Do not infer completeness from the number of rounds or candidates. Derive a second ledger from the full-solution proof and sufficient state. For every state component, record what future decision depends on it and construct plausible programs that:

- erase that component;
- merge per-object components into one global total or slack pool;
- retain only the current, previous, minimum, maximum, or next-deadline object;
- replace a reachable-state distribution with aggregate counts;
- use an interval delta where the proof requires history since the object's last event.

These are quotient-state attacks: they deliberately identify distinct legal histories that the correct algorithm must distinguish. Require at least one executable candidate for every high-risk quotient and a brute-searched witness pair of histories with the same candidate state but different correct continuation values when feasible. Random-data success is expected for many such candidates and does not lower their priority.

## Close-complexity frontier

Build a problem-specific complexity frontier around the accepted algorithm. When plausible, include candidates whose bounds differ by only one logarithmic factor, one data-structure factor, a larger state dimension, or a close polynomial exponent—for example `O(F(n) log n)` against `O(F(n))`, or `O(n^2)` against `O(n^2 / w)`.

For every close candidate:

1. Establish semantic status first. State the candidate invariant, attempt a proof or counterexample, and run tiny differential tests. Reclassify a correct-but-slow program as a genuine complexity partial rather than inventing a conceptual defect from unusual code shape.
2. Derive the actual controlling operations, memory, and crossover scale instead of relying only on Big-O labels.
3. Name the index space and progress variable of every repeated scan: objects, events, states, edges, values, or test cases. Two candidates with the same asymptotic label do not share a stress test when one rescans objects and another rescans event positions or zero aliases.
4. Complete a loop-path table with loop header, reset point, index range, early-stop predicate, per-iteration useful/zero work, tight iteration sum, and the input relations needed to realize it.
5. Derive a legal witness that maximizes each loop's actual iteration count. Track why the loop cannot terminate early—for example, all scanned entries are already zero while usable resource is stored outside the scanned suffix—and estimate the iteration sum explicitly.
6. Identify input shapes that realize its costly path and prevent pruning, early termination, favorable ordering, or accidental amortization. Merely setting dimensions to their maxima is insufficient when random values make the loop stop at its first positive entry.
7. Create at least two structurally distinct maximum or near-maximum compositions when legal, so one accidental optimization or data-shape shortcut cannot erase the boundary.
8. Compile with the release toolchain and benchmark on the same host and resource policy as the oracle, at least three times per marked case.
9. Record raw timings, including the candidate's fastest, median, and slowest runs, the oracle's slowest run, oracle-to-candidate ratios, and the safety margin relative to the time limit. Treat a one-off or near-limit TLE as unstable evidence.

Do not label a theoretically slower program as wrong solely because its asymptotic bound is worse. If it remains comfortably within the frozen limit on every valid worst case, treat it as an accepted alternative or revise constraints and limits fairly. Never use timing noise, illegal input, or an artificially hostile compiler to force rejection.

## Multi-test heterogeneity

When one input file contains multiple test instances, do not fill the entire file with one structural family under different random seeds. If the scoring unit admits at least two legal families, every multi-test formal input must mix at least two, and preferably three, distinct families. Mix dimensions such as:

- small, transition, near-maximum, and maximum scales;
- random, monotone, periodic, block, degenerate, and directed adversarial structures;
- low and high values, duplicate and distinct values, ties and unique optima;
- state-reset traps, cheap cases, and cases that exercise the expensive path.

Use a deterministic order or fixed-seed shuffle, and place reset-sensitive families in different relative positions across files. Across the formal set, vary the family-count vector and order; changing only the seed while retaining the same composition is not sufficient heterogeneity.

For each multi-test input, record family names, counts, size bands, order policy, aggregate-limit accounting, and attacked defects. If a frozen subtask predicate makes a second structural family mathematically impossible, document that impossibility and diversify size, values, labels, or ordering within the remaining family.

## Repair loop

Run every adversarial candidate under the frozen scoring rules. An unexpected score means a candidate receives points outside its proved supported domain or above its approved `score_max`.

For each unexpected score:

1. Prove the candidate wrong or reclassify it as correct.
2. Minimize a counterexample with the brute oracle when possible.
3. Map the defect to a missing semantic family, scale, composition, or complexity pressure.
4. Update the manifest and generator profile; never hand-edit a formal input.
5. Regenerate or selectively replace affected cases, then rerun validation, answers, hashes, all candidates from all rounds, scoring, and timing.

After a repair, keep the earlier adversarial programs in the regression suite. The final formal data hashes must be tested against the complete accumulated portfolio.

Do not replace an earlier killing family merely because a newer counterexample is stronger against one program. First run every accumulated candidate on the proposed replacement. If any old candidate regains points, retain both families or construct and brute-verify a combined instance that kills both for the same mathematical reasons. With fixed case count, combine multiple small test instances inside the same formal file or replace weak random material; never exceed aggregate constraints.

## External survivor regression

When a user, contestant, reviewer, or later audit supplies a wrong solution that scores above its proved domain:

1. Save the submitted source unchanged and reproduce its exact per-unit score on the delivered hashes.
2. Differential-test it against the oracle and brute force; minimize a counterexample by total tokens and controlling dimensions.
3. State the missing invariant precisely. Prefer an explanation such as “merges per-object slack into a transferable global pool” over a surface description of the wrong branch.
4. Derive multiple counterexample families that vary repeated versus alternating objects, equality boundaries, interval starting states, and reachability or prefix conditions as applicable.
5. Put the families in named deterministic generator profiles. Do not hand-edit formal inputs and do not copy one identical micro-case into every file.
6. Compile a plausible patched mutation that fixes one surface symptom while retaining the underlying false abstraction. Run it as the clean adaptive round after the repair.
7. Rerun every earlier candidate. A repair that kills the new survivor but revives an old one is incomplete.
8. Replace the published package only after a clean full pipeline in a non-synchronized temporary directory and a destination hash audit.

This external-survivor round is mandatory even after a prior `go`. The old release report becomes stale at the moment the excess score is reproduced.

## Proof-obligation coverage

Before the first release, write an invariant attack table with these columns:

| Proof/state obligation | Plausible information loss | Executable candidate | Brute witness | Named killing families | Final score |
|---|---|---|---|---|---:|

The table must cover every nontrivial distinction used in the correctness proof, not only mistakes an agent happened to volunteer. Treat a blank executable-candidate or brute-witness cell for a high-risk aggregation as a blocking gap. In particular, whenever operations name one object but the objective or resource limit is global, always test the false abstraction that replaces per-object state with one transferable global pool.

After any repair, mutate the survivor in both error directions where possible. A patch that removes an over-count can introduce an under-count; test both, rather than assuming that fixing the observed branch yields a weaker version of the same failure family.

## Harness-valid verdicts

Before full scoring, run every candidate on public samples and at least one tiny oracle-checked case through the same judge harness. Preserve user source unchanged and record any evaluation adapter, such as removal of `freopen`, separately.

Classify a result as data-strength evidence only when its cause matches the candidate model:

- use WA for a proved semantic counterexample;
- use TLE/MLE only after the program passes smoke tests and the legal input realizes the claimed resource path;
- treat missing files, wrong working directories, empty output, wrapper timeouts, and harness-induced RE as infrastructure failures requiring repair and rerun.
- treat oversized `vector`/matrix allocation, stack or recursion exhaustion, output floods, process/thread leaks, disk/handle exhaustion, launch failures, and cleanup failures as invalid evidence unless a safely enforced resource boundary is the explicit isolated target.

A score of zero is not evidence of strong data by itself. The verdict cause must be audited, and conceptual candidates expected to test semantics must not be accepted as killed solely by I/O failure.

Before formal scoring, require the candidate resource preflight in [runtime-resource-policy.md](runtime-resource-policy.md). A memory-heavy partial solution may be analyzed by formula without executing a host-dangerous allocation. An observed MLE counts only when a hard per-process cap was effective and the host remained healthy; otherwise record the environment limitation and use a safer representative.

## Complexity-survivor postmortem

When a semantically correct out-of-budget solution receives more points than its supported complexity domain, invalidate the strength gate and answer these questions before changing data:

1. Why was the program classified incorrectly or omitted from the complexity frontier?
2. Which concrete loop, index space, reset point, and early-stop condition control its work?
3. Why did each existing named stress family fail to maximize that work expression?
4. Which input relation keeps the loop alive, and what exact or tight iteration sum results?
5. Which second independent family realizes the same complexity by a different structure?
6. Do direct three-run preflight timings show a stable candidate failure and a safe oracle margin?
7. Did the repair preserve every earlier semantic and complexity kill under the final hashes?

Do not close this postmortem with “the old data was not large enough” unless size alone is proved to control the work. Distinguish input size from executed work, and distinguish asymptotic class from scan dimension. Add the survivor permanently to the matrix with its genuine partial score rather than forcing it into a wrong-answer role.

## Required evidence and exit rule

Adapt [the adversarial review template](../assets/adversarial-review-template.md). Preserve:

- agent isolation prompt and input allowlist for each round;
- proof-obligation/invariant attack table and quotient-state witness pairs;
- round number, candidate source, defect class, complexity, supported domain, and expected score;
- full per-unit verdict and awarded-score matrix;
- I/O smoke-test result, any evaluation adapter, and audited verdict cause;
- candidate peak-resource budget, scale-ladder measurements, enforced caps, and cleanup result;
- minimized counterexamples and repair decisions;
- multi-test family-composition manifest;
- close-complexity operation estimates and raw benchmark runs;
- loop-path tables, two-family worst-case witnesses, and any complexity-survivor postmortem;
- final input, answer, generator, validator, and candidate hashes.

Pass the strength gate only when at least three qualifying rounds have completed, the proof-obligation ledger has no untested high-risk quotient state, every verdict used as strength evidence has a harness-valid cause, the final data hashes have been rerun against every accumulated candidate, every partial scoring unit has a concrete tested solution, every required multi-test file passes the heterogeneity review, and the last adaptive round introduces no unresolved excess score. Majority opinion or a high candidate count cannot replace this evidence.
