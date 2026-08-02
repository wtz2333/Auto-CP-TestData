#include <bits/stdc++.h>

#include "../assets/cpp-templates/aho-corasick.hpp"
#include "../assets/cpp-templates/binary-lifting.hpp"
#include "../assets/cpp-templates/dinic.hpp"
#include "../assets/cpp-templates/dsu.hpp"
#include "../assets/cpp-templates/fenwick.hpp"
#include "../assets/cpp-templates/hld.hpp"
#include "../assets/cpp-templates/lazy-segment-tree.hpp"
#include "../assets/cpp-templates/linear-basis.hpp"
#include "../assets/cpp-templates/min-cost-flow.hpp"
#include "../assets/cpp-templates/modint.hpp"
#include "../assets/cpp-templates/ntt.hpp"
#include "../assets/cpp-templates/palindromic-tree.hpp"
#include "../assets/cpp-templates/point-2d.hpp"
#include "../assets/cpp-templates/scc.hpp"
#include "../assets/cpp-templates/segment-tree.hpp"
#include "../assets/cpp-templates/sparse-table.hpp"
#include "../assets/cpp-templates/string-algorithms.hpp"
#include "../assets/cpp-templates/suffix-automaton.hpp"
#include "../assets/cpp-templates/two-sat.hpp"

using i64 = long long;

struct SumInfo {
    i64 sum;
    int len;

    SumInfo(i64 sum_ = 0, int len_ = 0) : sum(sum_), len(len_) {}

    void apply(const struct AffineTag& value);
};

struct AffineTag {
    i64 mul;
    i64 add;

    AffineTag(i64 mul_ = 1, i64 add_ = 0) : mul(mul_), add(add_) {}

    void apply(const AffineTag& value) {
        add = add * value.mul + value.add;
        mul *= value.mul;
    }
};

void SumInfo::apply(const AffineTag& value) {
    sum = sum * value.mul + value.add * len;
}

SumInfo operator+(const SumInfo& lhs, const SumInfo& rhs) {
    return SumInfo(lhs.sum + rhs.sum, lhs.len + rhs.len);
}

void test_segment_tree() {
    std::vector<SumInfo> init;
    for (int x : {1, 2, 3, 4, 5}) {
        init.emplace_back(x, 1);
    }

    SegmentTree<SumInfo> seg(init);
    assert(seg.query(0, 5).sum == 15);
    assert(seg.query(1, 4).sum == 9);
    assert(seg.query(2, 2).sum == 0);
    seg.modify(2, SumInfo(10, 1));
    assert(seg.all().sum == 22);
    assert(seg.query(2, 3).sum == 10);

    SegmentTree<SumInfo> empty(std::vector<SumInfo>{});
    assert(empty.query(0, 0).sum == 0);
    assert(empty.all().sum == 0);
}

void test_lazy_segment_tree() {
    std::vector<SumInfo> init;
    for (int x = 0; x < 6; x++) {
        init.emplace_back(x, 1);
    }
    LazySegmentTree<SumInfo, AffineTag> seg(init);
    seg.range_apply(0, 4, AffineTag(2, 0));
    seg.range_apply(0, 4, AffineTag(1, 3));
    assert(seg.query(0, 6).sum == 33);
    assert(seg.query(1, 2).sum == 5);
    seg.range_apply(2, 5, AffineTag(1, 2));
    assert(seg.query(2, 4).sum == 20);
    seg.modify(3, SumInfo(7, 1));
    assert(seg.query(1, 5).sum == 27);
}

void test_hld() {
    HLD hld(7);
    hld.add_edge(0, 1);
    hld.add_edge(0, 2);
    hld.add_edge(1, 3);
    hld.add_edge(1, 4);
    hld.add_edge(2, 5);
    hld.add_edge(5, 6);
    hld.work();

    assert(hld.lca(3, 4) == 1);
    assert(hld.lca(3, 6) == 0);
    assert(hld.dist(3, 6) == 5);
    assert(hld.is_ancestor(0, 6));
    assert(!hld.is_ancestor(1, 6));
    assert(hld.subtree(1).second - hld.subtree(1).first == 3);

    std::vector<int> on_path(7, 0);
    hld.for_path(3, 6, [&](int l, int r) {
        for (int i = l; i < r; i++) {
            on_path[hld.seq[i]]++;
        }
    });
    for (int u = 0; u < 7; u++) {
        int expected = (u != 4);
        assert(on_path[u] == expected);
    }

    constexpr int chain_n = 200000;
    HLD chain(chain_n);
    for (int i = 1; i < chain_n; i++) {
        chain.add_edge(i - 1, i);
    }
    chain.work();
    assert(chain.lca(chain_n / 2, chain_n - 1) == chain_n / 2);
    assert(chain.dist(0, chain_n - 1) == chain_n - 1);
}

void test_random_hld() {
    std::mt19937 rng(20260801);
    for (int test = 0; test < 100; test++) {
        int n = 2 + static_cast<int>(rng() % 79);
        HLD hld(n);
        for (int v = 1; v < n; v++) {
            int p = static_cast<int>(rng() % static_cast<unsigned>(v));
            hld.add_edge(p, v);
        }
        hld.work();

        for (int u = 0; u < n; u++) {
            int subtree_size = 0;
            for (int v = 0; v < n; v++) {
                int x = v;
                while (x != -1 && x != u) {
                    x = hld.parent[x];
                }
                if (x == u) {
                    subtree_size++;
                    assert(hld.in[u] <= hld.in[v] && hld.in[v] < hld.out[u]);
                }
            }
            assert(hld.out[u] - hld.in[u] == subtree_size);
        }

        for (int query = 0; query < 200; query++) {
            int u = static_cast<int>(rng() % static_cast<unsigned>(n));
            int v = static_cast<int>(rng() % static_cast<unsigned>(n));
            int a = u;
            int b = v;
            while (hld.dep[a] > hld.dep[b]) {
                a = hld.parent[a];
            }
            while (hld.dep[b] > hld.dep[a]) {
                b = hld.parent[b];
            }
            while (a != b) {
                a = hld.parent[a];
                b = hld.parent[b];
            }
            assert(hld.lca(u, v) == a);

            std::vector<int> expected(n, 0);
            for (int x = u; x != a; x = hld.parent[x]) {
                expected[x] = 1;
            }
            for (int x = v; x != a; x = hld.parent[x]) {
                expected[x] = 1;
            }
            expected[a] = 1;

            std::vector<int> actual(n, 0);
            hld.for_path(u, v, [&](int l, int r) {
                for (int i = l; i < r; i++) {
                    actual[hld.seq[i]]++;
                }
            });
            assert(actual == expected);
        }
    }
}

void test_basic_data_structures() {
    Fenwick<i64> fenwick(5);
    for (int i = 0; i < 5; i++) {
        fenwick.add(i, i + 1);
    }
    assert(fenwick.prefix_sum(5) == 15);
    assert(fenwick.range_sum(1, 4) == 9);
    assert(fenwick.lower_bound(1) == 0);
    assert(fenwick.lower_bound(7) == 3);
    assert(fenwick.lower_bound(16) == 5);

    DSU dsu(5);
    assert(dsu.merge(0, 1));
    assert(dsu.merge(1, 2));
    assert(!dsu.merge(0, 2));
    assert(dsu.same(0, 2));
    assert(dsu.size(1) == 3);

    RollbackDSU rollback(4);
    rollback.merge(0, 1);
    std::size_t state = rollback.snapshot();
    rollback.merge(1, 2);
    assert(rollback.same(0, 2));
    rollback.rollback(state);
    assert(!rollback.same(0, 2));
    assert(rollback.same(0, 1));

    struct Minimum {
        int operator()(int lhs, int rhs) const {
            return std::min(lhs, rhs);
        }
    };
    SparseTable<int, Minimum> sparse({5, 2, 4, 1, 3});
    assert(sparse.query(0, 5) == 1);
    assert(sparse.query(1, 3) == 2);
}

void test_graph_templates() {
    BinaryLifting tree(7);
    for (std::pair<int, int> edge : {
        std::pair<int, int>{0, 1}, {0, 2}, {1, 3}, {1, 4}, {2, 5}, {5, 6}
    }) {
        tree.add_edge(edge.first, edge.second);
    }
    tree.work();
    assert(tree.kth_ancestor(6, 2) == 2);
    assert(tree.kth_ancestor(6, 4) == -1);
    assert(tree.lca(3, 6) == 0);
    assert(tree.dist(3, 6) == 5);

    Dinic<i64> dinic(4);
    dinic.add_edge(0, 1, 3);
    dinic.add_edge(0, 2, 2);
    dinic.add_edge(1, 2, 1);
    dinic.add_edge(1, 3, 2);
    dinic.add_edge(2, 3, 3);
    assert(dinic.max_flow(0, 3) == 5);

    MinCostFlow<int, i64> min_cost(4);
    min_cost.add_edge(0, 1, 2, -1);
    min_cost.add_edge(1, 3, 2, 2);
    min_cost.add_edge(0, 2, 1, 0);
    min_cost.add_edge(2, 3, 1, 5);
    assert(min_cost.flow(0, 3, 3) == std::make_pair(3, i64(7)));

    SCC scc(4);
    scc.add_edge(0, 1);
    scc.add_edge(1, 0);
    scc.add_edge(1, 2);
    scc.add_edge(2, 3);
    scc.add_edge(3, 2);
    assert(scc.work() == 2);
    assert(scc.comp[0] == scc.comp[1]);
    assert(scc.comp[2] == scc.comp[3]);
    assert(scc.comp[0] != scc.comp[2]);

    TwoSat sat(2);
    sat.add_or(0, true, 1, true);
    sat.add_or(0, false, 1, true);
    sat.add_or(0, true, 1, false);
    assert(sat.solve());
    assert(sat.assignment[0] && sat.assignment[1]);

    TwoSat unsat(1);
    unsat.set_value(0, true);
    unsat.set_value(0, false);
    assert(!unsat.solve());
}

void test_string_templates() {
    assert(prefix_function("ababa") == std::vector<int>({0, 0, 1, 2, 3}));
    assert(z_function("aaaaa") == std::vector<int>({5, 4, 3, 2, 1}));
    assert(manacher_odd("abacaba")[3] == 4);
    assert(manacher_even("abba")[2] == 2);

    AhoCorasick<> aho;
    int he = aho.insert("he");
    int she = aho.insert("she");
    aho.insert("hers");
    aho.build();
    int state = 0;
    for (char c : std::string("she")) {
        state = aho.advance(state, c);
    }
    assert(state == she);
    assert(aho.node[state].terminal == 1);
    assert(aho.node[aho.node[state].link].terminal == aho.node[he].terminal);

    SuffixAutomaton<> sam;
    sam.build("ababa");
    long long distinct = 0;
    for (int u = 1; u < static_cast<int>(sam.state.size()); u++) {
        distinct += sam.state[u].len - sam.state[sam.state[u].link].len;
    }
    assert(distinct == 9);
    sam.propagate_occurrences();
    state = 0;
    for (char c : std::string("aba")) {
        state = sam.state[state].next[c - 'a'];
    }
    assert(sam.state[state].occurrences == 2);

    PalindromicTree<> pam;
    pam.build("ababa");
    assert(pam.distinct_palindromes() == 5);
    pam.propagate_occurrences();
}

void test_math_and_geometry_templates() {
    using Mint = ModInt<998244353>;
    assert((Mint(3) / Mint(2) * Mint(2)).val() == 3);
    assert(Mint(2).power(10).val() == 1024);

    LinearBasis<8> basis;
    assert(basis.insert(1));
    assert(basis.insert(2));
    assert(!basis.insert(3));
    assert(basis.representable(3));
    assert(!basis.representable(4));
    assert(basis.max_xor() == 3);

    using Point = Point2D<i64>;
    std::vector<Point> hull = convex_hull<i64>({
        {0, 0}, {2, 0}, {2, 2}, {0, 2}, {1, 1}, {0, 0}
    });
    assert(hull.size() == 4);
    i64 twice_area = 0;
    for (int i = 0; i < 4; i++) {
        twice_area += cross(hull[i], hull[(i + 1) % 4]);
    }
    assert(twice_area == 8);

    std::vector<int> convolution = NTT998244353::convolution({1, 2, 3}, {4, 5});
    assert(convolution == std::vector<int>({4, 13, 22, 15}));
}

void test_random_data_structures() {
    std::mt19937 rng(712367);
    for (int test = 0; test < 100; test++) {
        int n = 1 + static_cast<int>(rng() % 50);
        Fenwick<i64> fenwick(n);
        std::vector<i64> value(n, 0);
        for (int operation = 0; operation < 500; operation++) {
            int x = static_cast<int>(rng() % static_cast<unsigned>(n));
            i64 add = static_cast<int>(rng() % 8);
            fenwick.add(x, add);
            value[x] += add;

            int l = static_cast<int>(rng() % static_cast<unsigned>(n + 1));
            int r = static_cast<int>(rng() % static_cast<unsigned>(n + 1));
            if (l > r) {
                std::swap(l, r);
            }
            i64 expected = std::accumulate(value.begin() + l, value.begin() + r, i64(0));
            assert(fenwick.range_sum(l, r) == expected);

            i64 total = std::accumulate(value.begin(), value.end(), i64(0));
            i64 target = static_cast<i64>(rng() % static_cast<unsigned long long>(total + 2));
            int position = 0;
            i64 prefix = 0;
            while (position < n && prefix < target) {
                prefix += value[position];
                position++;
            }
            int expected_index = target <= 0 ? 0 : position - 1;
            if (prefix < target) {
                expected_index = n;
            }
            assert(fenwick.lower_bound(target) == expected_index);
        }

        std::vector<int> array(n);
        for (int& x : array) {
            x = static_cast<int>(rng() % 1000);
        }
        struct Minimum {
            int operator()(int lhs, int rhs) const {
                return std::min(lhs, rhs);
            }
        };
        SparseTable<int, Minimum> sparse(array);
        for (int l = 0; l < n; l++) {
            int expected = array[l];
            for (int r = l + 1; r <= n; r++) {
                expected = std::min(expected, array[r - 1]);
                assert(sparse.query(l, r) == expected);
            }
        }
    }
}

void test_random_graph_templates() {
    std::mt19937 rng(918273);
    for (int test = 0; test < 150; test++) {
        int n = 2 + static_cast<int>(rng() % 6);
        struct FlowEdge {
            int u;
            int v;
            int cap;
        };
        std::vector<FlowEdge> edge;
        Dinic<int> dinic(n);
        for (int u = 0; u < n; u++) {
            for (int v = 0; v < n; v++) {
                if (u != v && rng() % 3 == 0) {
                    int cap = static_cast<int>(rng() % 4);
                    if (cap > 0) {
                        edge.push_back({u, v, cap});
                        dinic.add_edge(u, v, cap);
                    }
                }
            }
        }
        int expected_flow = std::numeric_limits<int>::max();
        for (int mask = 0; mask < (1 << n); mask++) {
            if (!(mask & 1) || (mask >> (n - 1) & 1)) {
                continue;
            }
            int cut = 0;
            for (const FlowEdge& item : edge) {
                if ((mask >> item.u & 1) && !(mask >> item.v & 1)) {
                    cut += item.cap;
                }
            }
            expected_flow = std::min(expected_flow, cut);
        }
        assert(dinic.max_flow(0, n - 1) == expected_flow);

        SCC scc(n);
        std::vector<std::vector<char>> reach(n, std::vector<char>(n, false));
        for (int u = 0; u < n; u++) {
            reach[u][u] = true;
            for (int v = 0; v < n; v++) {
                if (rng() % 4 == 0) {
                    scc.add_edge(u, v);
                    reach[u][v] = true;
                }
            }
        }
        for (int k = 0; k < n; k++) {
            for (int u = 0; u < n; u++) {
                for (int v = 0; v < n; v++) {
                    reach[u][v] = reach[u][v] || (reach[u][k] && reach[k][v]);
                }
            }
        }
        scc.work();
        for (int u = 0; u < n; u++) {
            for (int v = 0; v < n; v++) {
                assert((scc.comp[u] == scc.comp[v]) == (reach[u][v] && reach[v][u]));
            }
        }
    }

    for (int test = 0; test < 300; test++) {
        int n = 1 + static_cast<int>(rng() % 5);
        struct Clause {
            int x;
            bool x_value;
            int y;
            bool y_value;
        };
        std::vector<Clause> clause;
        TwoSat sat(n);
        int clauses = static_cast<int>(rng() % 16);
        for (int i = 0; i < clauses; i++) {
            Clause item{
                static_cast<int>(rng() % static_cast<unsigned>(n)),
                static_cast<bool>(rng() & 1),
                static_cast<int>(rng() % static_cast<unsigned>(n)),
                static_cast<bool>(rng() & 1)
            };
            clause.push_back(item);
            sat.add_or(item.x, item.x_value, item.y, item.y_value);
        }
        bool expected = false;
        for (int mask = 0; mask < (1 << n); mask++) {
            bool valid = true;
            for (const Clause& item : clause) {
                bool lhs = static_cast<bool>(mask >> item.x & 1) == item.x_value;
                bool rhs = static_cast<bool>(mask >> item.y & 1) == item.y_value;
                valid = valid && (lhs || rhs);
            }
            expected = expected || valid;
        }
        bool actual = sat.solve();
        assert(actual == expected);
        if (actual) {
            for (const Clause& item : clause) {
                bool lhs = static_cast<bool>(sat.assignment[item.x]) == item.x_value;
                bool rhs = static_cast<bool>(sat.assignment[item.y]) == item.y_value;
                assert(lhs || rhs);
            }
        }
    }
}

void test_random_string_and_polynomial_templates() {
    std::mt19937 rng(192837);
    for (int test = 0; test < 300; test++) {
        int n = static_cast<int>(rng() % 20);
        std::string s(n, 'a');
        for (char& c : s) {
            c = static_cast<char>('a' + rng() % 3);
        }

        std::vector<int> pi = prefix_function(s);
        std::vector<int> z = z_function(s);
        std::vector<int> odd = manacher_odd(s);
        std::vector<int> even = manacher_even(s);
        for (int i = 0; i < n; i++) {
            int expected_pi = 0;
            for (int len = 1; len <= i; len++) {
                if (s.substr(0, len) == s.substr(i - len + 1, len)) {
                    expected_pi = len;
                }
            }
            assert(pi[i] == expected_pi);

            int expected_z = 0;
            while (i + expected_z < n && s[expected_z] == s[i + expected_z]) {
                expected_z++;
            }
            assert(z[i] == expected_z);

            int expected_odd = 1;
            while (i - expected_odd >= 0 && i + expected_odd < n &&
                   s[i - expected_odd] == s[i + expected_odd]) {
                expected_odd++;
            }
            assert(odd[i] == expected_odd);

            int expected_even = 0;
            while (i - expected_even - 1 >= 0 && i + expected_even < n &&
                   s[i - expected_even - 1] == s[i + expected_even]) {
                expected_even++;
            }
            assert(even[i] == expected_even);
        }

        SuffixAutomaton<> sam;
        sam.build(s);
        long long sam_distinct = 0;
        for (int u = 1; u < static_cast<int>(sam.state.size()); u++) {
            sam_distinct += sam.state[u].len - sam.state[sam.state[u].link].len;
        }
        std::set<std::string> substring;
        std::set<std::string> palindrome;
        for (int l = 0; l < n; l++) {
            for (int r = l + 1; r <= n; r++) {
                std::string part = s.substr(l, r - l);
                substring.insert(part);
                std::string reversed = part;
                std::reverse(reversed.begin(), reversed.end());
                if (part == reversed) {
                    palindrome.insert(part);
                }
            }
        }
        assert(sam_distinct == static_cast<long long>(substring.size()));

        PalindromicTree<> pam;
        pam.build(s);
        assert(pam.distinct_palindromes() == static_cast<int>(palindrome.size()));

        int a_size = static_cast<int>(rng() % 16);
        int b_size = static_cast<int>(rng() % 16);
        std::vector<int> a(a_size);
        std::vector<int> b(b_size);
        for (int& x : a) {
            x = static_cast<int>(rng() % 1000);
        }
        for (int& x : b) {
            x = static_cast<int>(rng() % 1000);
        }
        std::vector<int> expected_convolution;
        if (!a.empty() && !b.empty()) {
            expected_convolution.assign(a.size() + b.size() - 1, 0);
            for (int i = 0; i < a_size; i++) {
                for (int j = 0; j < b_size; j++) {
                    expected_convolution[i + j] = static_cast<int>(
                        (expected_convolution[i + j] + 1LL * a[i] * b[j]) % NTT998244353::mod
                    );
                }
            }
        }
        assert(NTT998244353::convolution(a, b) == expected_convolution);
    }
}

int main() {
    test_segment_tree();
    test_lazy_segment_tree();
    test_hld();
    test_random_hld();
    test_basic_data_structures();
    test_graph_templates();
    test_string_templates();
    test_math_and_geometry_templates();
    test_random_data_structures();
    test_random_graph_templates();
    test_random_string_and_polynomial_templates();
    std::cout << "cpp template tests passed\n";
    return 0;
}
