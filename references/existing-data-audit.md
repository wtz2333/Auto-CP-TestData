# Existing data audit

Audit supplied formal data before deciding to generate replacements. Never assume that existing files are correct merely because they accompany an accepted standard solution.

## Inventory without mutation

List every supplied `.in` and `.ans` file, infer their pairing and numbering, and record missing mates, duplicate names, unexpected files, line endings, and hashes. Preserve the original files during the audit. If naming is ambiguous, resolve it from build scripts or package conventions and record the evidence.

## Legality and answer checks

Run the validator with the declared subtask or group for every input. Check complete token consumption, global limits, cross-field invariants, group-specific constraints, text encoding, and LF policy. Recompute every answer with the frozen `std.cpp`; compare without overwriting the supplied answer. Where feasible, also compare small cases with `brute.cpp` and formal cases with an independent standard solution.

## Coverage and strength checks

Map each existing case to its validator group and scoring unit. Verify the fixed count or bounded count policy, nonempty group/unit coverage, mutually exclusive scoring assignment, valid dependencies and point totals, input uniqueness, required boundaries, special structures, maximum-scale cases, and adversarial coverage. Run the partial and wrong solution suite on the complete data and compare observed verdicts and scores with the intended matrix under the frozen independent, bundled, or mixed rule.

For each existing input containing multiple test instances, recover and record its structural-family composition, scale distribution, and order. Reject single-family files when the scoring predicate permits heterogeneous instances, and reject a set whose files differ only by seed. Subject reused data to the same three-round adversarial-agent review and close-complexity benchmarks as generated data; existing provenance never waives the strength gate.

Assign semantic-role tags and a written purpose even when the supplied package lacks a manifest. Distinguish easy maximum-boundary cases from shapes that actually realize a weaker algorithm's worst-case complexity; one does not substitute for the other.

## Reuse decision

- If every legality, answer, coverage, strength, reproducibility, and timing gate passes, adopt the supplied data unchanged. Record hashes and mark provenance as `existing`; do not regenerate it merely for uniformity.
- If only some cases fail, preserve the passing cases when the delivery contract allows mixed provenance. Replace only the affected cases, then rerun all gates because scoring and solution outcomes may change.
- If the data cannot be paired, validated, reproduced where required, or shown strong enough, record the concrete failures and regenerate the necessary set from a fixed manifest.

For bounded strength-driven `bundled` scoring, retention is mandatory rather than optional: include every supplied formal input after legality checking, recompute or repair its answer, and add targeted cases until all strength goals pass, subject to the 20–40 limit. Never discard a weak but legal supplied input merely to free a slot. Escalate if the supplied set already exceeds the cap or contains an illegal input that cannot be retained faithfully.

Generated and reused data are subject to the same final acceptance criteria. Reuse is an evidence-based result, not a shortcut around validation.
