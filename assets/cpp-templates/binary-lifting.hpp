#pragma once

#include <bits/stdc++.h>

struct BinaryLifting {
    int n;
    int levels;
    std::vector<int> dep;
    std::vector<std::vector<int>> up;
    std::vector<std::vector<int>> adj;

    BinaryLifting() : n(0), levels(0) {}

    explicit BinaryLifting(int n_) {
        init(n_);
    }

    void init(int n_) {
        n = n_;
        levels = 1;
        while ((1LL << levels) <= std::max(1, n)) {
            levels++;
        }
        dep.assign(n, 0);
        up.assign(levels, std::vector<int>(n, -1));
        adj.assign(n, {});
    }

    void add_edge(int u, int v) {
        assert(0 <= u && u < n);
        assert(0 <= v && v < n);
        adj[u].push_back(v);
        adj[v].push_back(u);
    }

    void work(int root = 0) {
        assert(0 <= root && root < n);
        std::vector<int> parent(n, -2);
        std::vector<int> stack(1, root);
        parent[root] = root;
        dep[root] = 0;
        int visited = 0;
        while (!stack.empty()) {
            int u = stack.back();
            stack.pop_back();
            visited++;
            up[0][u] = parent[u];
            for (int v : adj[u]) {
                if (parent[v] != -2) {
                    continue;
                }
                parent[v] = u;
                dep[v] = dep[u] + 1;
                stack.push_back(v);
            }
        }
        assert(visited == n);
        for (int k = 1; k < levels; k++) {
            for (int u = 0; u < n; u++) {
                up[k][u] = up[k - 1][up[k - 1][u]];
            }
        }
    }

    int kth_ancestor(int u, int k) const {
        assert(0 <= u && u < n);
        if (k < 0 || k > dep[u]) {
            return -1;
        }
        for (int bit = 0; bit < levels; bit++) {
            if (k >> bit & 1) {
                u = up[bit][u];
            }
        }
        return u;
    }

    int lca(int u, int v) const {
        if (dep[u] < dep[v]) {
            std::swap(u, v);
        }
        u = kth_ancestor(u, dep[u] - dep[v]);
        if (u == v) {
            return u;
        }
        for (int k = levels - 1; k >= 0; k--) {
            if (up[k][u] != up[k][v]) {
                u = up[k][u];
                v = up[k][v];
            }
        }
        return up[0][u];
    }

    int dist(int u, int v) const {
        int w = lca(u, v);
        return dep[u] + dep[v] - 2 * dep[w];
    }
};
