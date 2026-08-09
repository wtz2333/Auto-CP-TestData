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

## Red-team role and isolation

Dispatch an adversarial contestant agent independently from the statement, oracle, and data designers. Give it only the frozen contestant-facing statement, public constraints and subtasks, language and judge mode, and time, memory, and stack limits. Do not expose `std.cpp`, `brute.cpp`, generator or validator source, formal inputs or answers, manifests, intended kills, or another agent's code before it submits its own candidates.

Tell the agent to maximize awarded score without using a correct full solution. It must produce plausible contestant programs based on a stated false assumption, restricted domain, weaker algorithm, or excessive complexity. Randomly corrupting correct code, inserting undefined behavior, or submitting code known to fail immediately does not test data strength.

For every candidate, require:

- algorithm and actual time and space complexity;
- claimed supported domain and the reason it is not a valid full solution;
- one isolated defect or resource boundary;
- the public scoring units it attempts to obtain;
- compilable source and an expected score range.

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

## Close-complexity frontier

Build a problem-specific complexity frontier around the accepted algorithm. When plausible, include candidates whose bounds differ by only one logarithmic factor, one data-structure factor, a larger state dimension, or a close polynomial exponent—for example `O(F(n) log n)` against `O(F(n))`, or `O(n^2)` against `O(n^2 / w)`.

For every close candidate:

1. Derive the actual controlling operations, memory, and crossover scale instead of relying only on Big-O labels.
2. Identify input shapes that realize its costly path and prevent pruning, early termination, favorable ordering, or accidental amortization.
3. Create more than one maximum or near-maximum composition when a single shape does not pressure every close algorithm.
4. Compile with the release toolchain and benchmark on the same host and resource policy as the oracle, at least three times per marked case.
5. Record raw timings, the slowest run, oracle-to-candidate ratios, and the safety margin relative to the time limit.

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

## Required evidence and exit rule

Adapt [the adversarial review template](../assets/adversarial-review-template.md). Preserve:

- agent isolation prompt and input allowlist for each round;
- round number, candidate source, defect class, complexity, supported domain, and expected score;
- full per-unit verdict and awarded-score matrix;
- minimized counterexamples and repair decisions;
- multi-test family-composition manifest;
- close-complexity operation estimates and raw benchmark runs;
- final input, answer, generator, validator, and candidate hashes.

Pass the strength gate only when at least three qualifying rounds have completed, the final data hashes have been rerun against every accumulated candidate, every partial scoring unit has a concrete tested solution, every required multi-test file passes the heterogeneity review, and the last adaptive round introduces no unresolved excess score. Majority opinion or a high candidate count cannot replace this evidence.
