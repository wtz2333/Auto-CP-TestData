# Competitive Programming Template Catalog

Use this catalog to locate a reusable algorithm before writing a new standard or genuine partial solution. Load only the relevant source section and its required dependencies.

## Contents

- [Source policy](#source-policy)
- [Selection workflow](#selection-workflow)
- [Verified original assets](#verified-original-assets)
- [Data structures](#data-structures)
- [Trees and graphs](#trees-and-graphs)
- [Strings](#strings)
- [Mathematics](#mathematics)
- [Polynomials](#polynomials)
- [Computational geometry](#computational-geometry)
- [DP and miscellaneous techniques](#dp-and-miscellaneous-techniques)
- [External Jiangly-derived index](#external-jiangly-derived-index)
- [Adaptation checklist](#adaptation-checklist)

## Source policy

Use these sources as references:

1. Verified original assets in `assets/cpp-templates/`.
2. The user-designated local library at `D:\iCloudDrive\CompetitivePrograming\template`.
3. <https://github.com/lihaoze123/jiangly-s-code-style-for-xcpc> for style rules.
4. <https://github.com/allwellll/cf_code_jiangly> and <https://www.cnblogs.com/WIDA/p/17633758.html> for structure discovery and solution references.

The local library contains user-curated files and third-party notes with mixed or unstated provenance. The Jiangly submission indexes also do not license every linked solution for republication. Read them to recover interfaces, invariants, and algorithm choices, then write an original problem-specific implementation. Never copy a whole solution or publish the local library wholesale.

Prefer Markdown sources over duplicate PDFs. Read a PDF only when no equivalent text source exists and the missing detail is necessary.

## Selection workflow

1. Identify the exact required operation, algebra, graph model, alphabet, modulus, and offline or online constraints.
2. Check the verified assets below.
3. If an asset matches, inline only its needed methods and adapt its types and identities.
4. Otherwise open the routed local `.cpp` or the relevant heading in a routed `.md` file.
5. Reimplement it using `jiangly-cpp-style.md`; do not preserve legacy globals, macros, 1-based storage, fixed limits, or unmeasured recursion merely because the reference uses them. Keep recursive structure when its worst-case live stack is budgeted and verified under the configured limit.
6. Compile under the frozen standard and create a small deterministic behavior test. Differential-test against a direct model whenever practical.
7. If the implementation becomes generally reusable and passes review, add it as a verified asset and extend `scripts/test_cpp_templates.cpp`.

## Verified original assets

These assets are maintained by this skill and must compile under C++14 unless their header states a stricter requirement:

| Family | Asset | Contract |
|---|---|---|
| Point segment tree | `segment-tree.hpp` | `Info()` identity, associative `operator+`, `[l,r)` query |
| Lazy segment tree | `lazy-segment-tree.hpp` | `Info` action and old-then-new `Tag::apply`, `[l,r)` |
| Heavy-light decomposition | `hld.hpp` | iterative build; subtree intervals; unordered path cover |
| Fenwick tree | `fenwick.hpp` | 0-based updates and half-open prefix/range sums |
| Disjoint sets | `dsu.hpp` | path-compressed DSU and rollback DSU |
| Sparse table | `sparse-table.hpp` | static idempotent range query on `[l,r)` |
| Binary lifting | `binary-lifting.hpp` | iterative tree preprocessing, ancestor/LCA/distance |
| Maximum flow | `dinic.hpp` | directed residual network with generic capacity; recursive blocking-flow DFS requires a safe path-depth bound |
| Min-cost flow | `min-cost-flow.hpp` | capacity, signed cost, optional flow limit; no reachable negative-cost cycle |
| SCC and 2-SAT | `scc.hpp`, `two-sat.hpp` | iterative Kosaraju; implication graph |
| Basic strings | `string-algorithms.hpp` | prefix function, Z function, odd/even Manacher |
| Aho-Corasick | `aho-corasick.hpp` | configurable lowercase alphabet and failure automaton |
| Suffix automaton | `suffix-automaton.hpp` | lowercase SAM with clone states |
| Palindromic tree | `palindromic-tree.hpp` | lowercase eertree with occurrence propagation |
| Modular arithmetic | `modint.hpp` | compile-time modulus; prime-modulus inverse contract |
| XOR linear basis | `linear-basis.hpp` | insertion, representability, maximum xor |
| Exact 2D geometry | `point-2d.hpp` | vector operations, orientation, convex hull |
| NTT convolution | `ntt.hpp` | modulus `998244353`, primitive root `3` |

## Data structures

Primary overview: `D:\iCloudDrive\CompetitivePrograming\template\1-数据结构.md`.

- Static RMQ and sparse table: heading `ST表`, plus `ST.cpp`.
- Point and lazy segment trees: headings `线段树`, plus `SegmentTree.cpp`, `SegTree.cpp`, and `lazysegment.cpp`.
- Persistent segment tree or chairman tree: heading `主席树`, plus `Persistent_SegmentTree.cpp`.
- Dynamic tree diameter: heading `树上动态直径`, plus `DynamicDiameter.cpp`.
- Sweep line: heading `扫描线`.
- Segment tree beats: heading `Seg beats`.
- Fenwick tree: heading `树状数组`, plus `Fenwick.cpp`.
- Ordinary and rollback DSU: heading `DSU`, plus `DSU.cpp`.
- Splay and link-cut tree: headings `Splay` and `LCT`.
- Ordered-disjoint interval tree: heading `珂朵莉树`.
- Li Chao tree: heading `李超树`, plus `LCTree.cpp`.
- Dynamic convex hull or line container: heading `动态维护凸壳`, plus `DynamicConvexHull.cpp` and `DynamicConvexShell.cpp`.
- Segment-tree merge/split: heading `线段树合并`; advanced discussion in `book\线段树的高级用法 - qAlex_Weiq - 博客园.md`.
- Custom dynamic bitset and hash: `bitset.cpp`, `custom_hash.cpp`.

## Trees and graphs

Primary overview: `D:\iCloudDrive\CompetitivePrograming\template\2-图论.md`.

- HLD, LCA, tree hash, and virtual tree: `HLD.cpp`, `LCA.cpp`, `TreeHash.cpp`, `Virtual_tree.cpp`.
- Additional tree techniques: `book\简单树论 - qAlex_Weiq - 博客园.md` covers six LCA methods, Kruskal reconstruction trees, virtual trees, centroid decomposition, long-chain decomposition, DSU-on-tree, and Cartesian trees.
- Shortest paths, MST, biconnected components, SCC, and Euler circuits: `book\图论基础 - qAlex_Weiq - 博客园 (1).md`; see `EBCC.cpp` and `euler_circuit.cpp` for focused code.
- Difference constraints and minimum cycles: matching headings in `2-图论.md`.
- Maximum flow and min-cost max-flow: `Flow.cpp`, `MCF.cpp`, and `book\网络流，二分图与图的匹配 - qAlex_Weiq - 博客园.md`.
- Lower-bound flow, bipartite matching, KM, and general matching: matching headings in `2-图论.md`; general blossom code in `FlowerTree.cpp`.
- SCC, articulation points, bridges, EBCC, block-cut trees, generalized block-cut trees, and 2-SAT: matching headings, plus `EBCC.cpp` and `BlockCutTree.cpp`.
- Advanced topics: `book\高级图论 - qAlex_Weiq - 博客园.md` covers modular shortest paths, 2-SAT, generalized block-cut trees, dominator trees, and DAG chain decomposition.
- Euler/BEST and cycle counting: `euler_circuit.cpp` and the `BEST 定理` or `环计数` headings.

## Strings

Primary overview: `D:\iCloudDrive\CompetitivePrograming\template\3-字符串.md`.

- Manacher, suffix array, KMP, Z, border theory: `book\常见字符串算法 - qAlex_Weiq - 博客园.md`; focused files `manacher.cpp`, `KMP.cpp`, `Z_function.cpp`.
- Palindromic automaton/tree: heading `PAM`, file `PAM.cpp`.
- Suffix automaton: heading `SAM`, file `SAM.cpp`.
- Aho-Corasick automaton: heading `ACAM`, file `ACAM.cpp`.
- KMP automaton, LCP techniques, and rolling hash: matching headings; `Hash.cpp` for focused code.
- Automatic string structures: `book\常见字符串算法 II：自动机相关 - qAlex_Weiq - 博客园.md`.

## Mathematics

Primary overview: `D:\iCloudDrive\CompetitivePrograming\template\4-数学.md`.

- Congruences: extended gcd, inverses, CRT, Lucas, primitive roots, BSGS, Wilson, and Euclidean-like algorithms. Use `Exgcd.cpp`, `QuickPow.cpp`, and `book\初等数论学习笔记 I：同余相关 - qAlex_Weiq - 博客园 (1).md`.
- Prime and factorization algorithms: linear sieve, Miller-Rabin, Pollard-Rho, Euler functions, and multiplicative functions. Use the corresponding headings and `book\初等数论学习笔记 II：分解质因数 - qAlex_Weiq - 博客园.md`.
- Convolution and inversion: Dirichlet convolution, Möbius inversion, Euler inversion, divisor blocking, Du Jiao sieve, and Min_25. Use `Min25.cpp`, `dusum.cpp`, `book\初等数论学习笔记 III：数论函数与筛法 - qAlex_Weiq - 博客园.md`, and `book\反演与狄利克雷卷积 - qAlex_Weiq - 博客园.md`.
- Combinatorics: inclusion-exclusion, binomial identities, multisets, circular permutations, derangements, Catalan, Stirling, partitions, transforms, and high-dimensional prefix sums. Use the `组合数学` section and `book\组合数学相关 - qAlex_Weiq - 博客园.md`.
- Linear algebra: Gaussian elimination, XOR basis, determinants, Matrix-Tree, Prüfer, LGV, and BEST. Use `Gauss.cpp`, `LinearBasis.cpp`, and `book\线性代数相关 - qAlex_Weiq - 博客园.md`.
- Modular number and fraction wrappers: `Z.cpp`, `Frac.cpp`.
- Game theory: heading `博弈`; derive the exact game model before selecting a theorem.

## Polynomials

Primary overview: `D:\iCloudDrive\CompetitivePrograming\template\5-多项式.md`.

- Lagrange interpolation, FFT/NTT, cyclic/difference/multiplicative convolutions, and divide-and-conquer FFT: matching headings, plus `FFT.cpp`.
- Formal power series operations: inverse, derivative, integral, logarithm, exponential, power, square root, shift, and transposed multiplication in `Poly.cpp`, `Poly_.cpp`, `Poly_easyt.cpp`, and `jiangly_poly.cpp`.
- FWT and subset power series: headings `FWT` and `集合幂级数`; deeper reference in `book\集合幂级数相关 - qAlex_Weiq - 博客园.md`.
- Theory and applications: `book\多项式 I：拉格朗日插值与快速傅里叶变换 - qAlex_Weiq - 博客园.md`.

## Computational geometry

Primary overview: `D:\iCloudDrive\CompetitivePrograming\template\6-计算几何.md`.

- Exact or floating 2D primitives, lines, segments, polygons, convex hulls, rotating calipers, circles, and half-plane operations: inspect only the relevant portion of `CG_.cpp`, `CG_cjj.cpp`, `CG_x.cpp`, `ComputationalGeometry.cpp`, or `dls_C.cpp`.
- Dynamic convex hull: heading `动态凸包`, plus `DynamicConvexHull.cpp` and `DynamicConvexShell.cpp`.
- Minimum enclosing circle: heading `最小圆覆盖`.
- Choose coordinate type and epsilon policy before importing any operation. Do not mix exact orientation with approximate equality without a written invariant.

## DP and miscellaneous techniques

- DP optimization overview: `dp优化.md`.
- Dynamic DP, matrix exponentiation, bitmask optimization, monotone queues, WQS binary search, divide-and-conquer optimization, slope optimization, binary queues/stacks, holistic DP, long-chain optimization, plug DP, and DP-of-DP: the two `book\DP 优化方法大杂烩 ...` Markdown files.
- Bit operations, `__int128` output, PBDS, custom hash tables, rope, stress testing, performance tuning, and language/tool snippets: `7-杂.md`.
- Team contest process and review discipline: `电竞指南.md`; use only for workflow, never as an algorithm source.
- Small implementation reminders: `Trick.md`, `Language.cpp`, `NumberSqrt.cpp`, and `cf_template.cpp`.

## External Jiangly-derived index

The external structure index includes `MInt`, `MLong`, `Info`, `Tag`, `SegmentTree`, `LazySegmentTree`, `Fenwick`, `DSU`, `HLD`, `TwoSat`, `Flow`, `Graph`, `Poly`, `Matrix`, `Comb`, `SAM`, `AC`, `Point`, `Line`, `Frac`, `Node`, and related problem-specific records. Use the index to compare naming and decomposition patterns, not as a copy source. Prefer a matching verified asset or rederive the implementation from its invariant.

## Adaptation checklist

Before accepting any reused algorithm, verify:

1. Index base and every public interval boundary.
2. Neutral elements, associativity, lazy composition order, and whether operations commute.
3. Graph direction, parallel-edge behavior, self-loops, capacity and cost signs, and disconnected inputs.
4. Tree root, edge-versus-vertex semantics, path direction, maximum depth, and the measured or derived stack budget of the chosen recursive or iterative traversal.
5. Alphabet mapping, sentinel choice, empty strings, and character range.
6. Modulus primality, primitive root, transform length divisibility, inverse preconditions, and overflow before reduction.
7. Floating versus exact geometry, epsilon scale, collinearity policy, and duplicate points.
8. Fixed array limits, stale global state, multi-test reset, and memory at maximum constraints.
9. Frozen C++ standard and non-standard library dependencies such as PBDS or compiler intrinsics.
10. A deterministic unit test plus brute or independent cross-check appropriate to the algorithm.
