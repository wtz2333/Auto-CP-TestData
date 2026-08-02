# Jiangly-Inspired C++ Contest Style

Apply this reference to newly written `std.cpp` and genuine partial-score solutions. Use it as a project convention inspired by the user-designated sources, not as a claim that every rule is an exact habit of one programmer.

## Source and reuse policy

The style baseline comes from:

- <https://github.com/lihaoze123/jiangly-s-code-style-for-xcpc>
- <https://github.com/allwellll/cf_code_jiangly>
- <https://www.cnblogs.com/WIDA/p/17633758.html>

The first source publishes an MIT-licensed reconstructed style guide. The other two sources catalog or archive solution-derived structures and do not establish a reusable license for every listed program. Extract stable interfaces and conventions, but do not copy solution bodies or long source fragments. Use the original project templates in `assets/cpp-templates/` as the reusable implementation baseline.

## Precedence

Apply requirements in this order:

1. Frozen problem semantics and I/O contract.
2. Frozen C++ language standard and judge environment.
3. Correctness, overflow safety, stack safety, time, and memory limits.
4. This style reference.

Use a C++17 or C++20 feature only when the frozen standard permits it. Replace recursive DFS with an iterative traversal when a legal chain can exceed safe stack depth, even if a recursive lambda would otherwise fit the style.

## Default file skeleton

- Include only `#include <bits/stdc++.h>` unless the judge forbids it.
- Do not write `using namespace std;`; qualify standard-library names with `std::`.
- Use explicit aliases such as `using i64 = long long;`. Never use `#define int long long`.
- Put constants in `constexpr` variables with types that safely hold their values.
- Put problem logic in `solve()`. Read a test count only when the statement defines one.
- Start `main()` with fast iostream setup and print line breaks with `"\n"`, not `std::endl`.
- Keep problem-sized containers local to `solve()` or owned by a small structure. Avoid fixed global arrays.

## Layout and naming

- Use four spaces, K&R braces, spaces around binary operators, and one statement per line.
- Use concise mathematical names when their meaning is standard: `n`, `m`, `u`, `v`, `ans`, `siz`, `dep`, `adj`, `dp`, `ndp`.
- Otherwise use `snake_case` for variables and functions, and `PascalCase` for structures such as `Info`, `Tag`, `SegmentTree`, and `HLD`.
- Prefer 0-based indexing and half-open intervals `[l, r)` internally. Convert a 1-based input immediately when doing so preserves clarity.
- Use comments only for a non-obvious invariant, composition order, boundary convention, or deliberate deviation. Do not narrate routine statements.

## Structure patterns

- Give reusable structures a default constructor, a size or data constructor, and an `init` method when reinitialization is useful.
- Keep owned state inside the structure. Expose short public wrappers and keep recursion or traversal details in overloads or private helpers when that improves clarity.
- For segment trees, let `Info()` be the query identity and define `operator+` as the associative merge. Verify both properties for the problem-specific `Info` before reuse.
- For lazy trees, let `Tag()` be the no-op tag. Define and document whether `Tag::apply(new_tag)` means “old operation, then new operation”; ensure `Info::apply` uses the same order.
- Use method names consistently: `init`, `pull`, `push`, `modify`, `query`, `range_apply`, `add_edge`, `work`, `lca`, `for_path`.
- Inline only the methods the solution actually needs. Delivered contest solutions must be self-contained and must not include a skill asset by path.

## Template catalog

Read [cpp-template-catalog.md](cpp-template-catalog.md) before selecting an implementation. It indexes the full local library and the Jiangly-derived collections, distinguishes verified original assets from reference-only material, and records the adaptation checks for every algorithm family.

Treat every asset as a starting point. Rename fields only when the new names clarify the problem, remove unused operations, and adapt identities, merge rules, tag composition, numeric types, alphabet, modulus, graph model, and path-order requirements before use.

## Solution-role policy

- Write the standard solution and every genuine partial algorithm in this style.
- Keep `brute.cpp` deliberately direct so it remains an independent oracle; use the formatting and type rules, but do not force a generic template into it.
- In an intended wrong solution, preserve a single reviewable defect. Style it consistently only when doing so does not hide or accidentally repair that defect.
- Do not refactor frozen user-supplied code solely for style. Make the smallest necessary change unless the user explicitly requests a rewrite.

## Mandatory review

Before accepting newly written code, check:

1. The file compiles under the frozen standard with strict warnings.
2. All internal indices and interval endpoints follow their stated convention.
3. `Info()` is a true identity and `operator+` is associative on reachable states.
4. Lazy composition order is tested when a tag exists.
5. Tree traversal is stack-safe for the maximum legal depth.
6. Size products, distances, costs, and sentinels use safe types.
7. The template was trimmed and the final program remains self-contained.
8. The std and partial solutions still pass their required differential and score-boundary tests.
