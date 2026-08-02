#pragma once

#include <bits/stdc++.h>

struct HLD {
    int n;
    int cur;
    std::vector<int> siz;
    std::vector<int> top;
    std::vector<int> dep;
    std::vector<int> parent;
    std::vector<int> in;
    std::vector<int> out;
    std::vector<int> seq;
    std::vector<int> heavy;
    std::vector<std::vector<int>> adj;

    HLD() : n(0), cur(0) {}

    explicit HLD(int n_) {
        init(n_);
    }

    void init(int n_) {
        n = n_;
        cur = 0;
        siz.assign(n, 0);
        top.assign(n, -1);
        dep.assign(n, 0);
        parent.assign(n, -2);
        in.assign(n, -1);
        out.assign(n, -1);
        seq.assign(n, -1);
        heavy.assign(n, -1);
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
        std::fill(parent.begin(), parent.end(), -2);
        std::vector<int> order;
        order.reserve(n);
        std::vector<int> stack(1, root);
        parent[root] = -1;
        dep[root] = 0;

        while (!stack.empty()) {
            int u = stack.back();
            stack.pop_back();
            order.push_back(u);
            for (int v : adj[u]) {
                if (v == parent[u]) {
                    continue;
                }
                assert(parent[v] == -2);
                parent[v] = u;
                dep[v] = dep[u] + 1;
                stack.push_back(v);
            }
        }
        assert(static_cast<int>(order.size()) == n);

        std::fill(siz.begin(), siz.end(), 1);
        std::fill(heavy.begin(), heavy.end(), -1);
        for (int i = n - 1; i >= 0; i--) {
            int u = order[i];
            for (int v : adj[u]) {
                if (parent[v] != u) {
                    continue;
                }
                siz[u] += siz[v];
                if (heavy[u] == -1 || siz[v] > siz[heavy[u]]) {
                    heavy[u] = v;
                }
            }
        }

        cur = 0;
        std::vector<std::pair<int, int>> tasks;
        tasks.emplace_back(root, root);
        while (!tasks.empty()) {
            int u = tasks.back().first;
            int head = tasks.back().second;
            tasks.pop_back();
            for (int x = u; x != -1; x = heavy[x]) {
                top[x] = head;
                in[x] = cur;
                seq[cur] = x;
                cur++;
                for (int v : adj[x]) {
                    if (parent[v] == x && v != heavy[x]) {
                        tasks.emplace_back(v, v);
                    }
                }
            }
        }
        assert(cur == n);
        for (int u = 0; u < n; u++) {
            out[u] = in[u] + siz[u];
        }
    }

    bool is_ancestor(int u, int v) const {
        return in[u] <= in[v] && in[v] < out[u];
    }

    int lca(int u, int v) const {
        while (top[u] != top[v]) {
            if (dep[top[u]] < dep[top[v]]) {
                std::swap(u, v);
            }
            u = parent[top[u]];
        }
        if (dep[u] < dep[v]) {
            return u;
        }
        return v;
    }

    int dist(int u, int v) const {
        return dep[u] + dep[v] - 2 * dep[lca(u, v)];
    }

    std::pair<int, int> subtree(int u) const {
        return {in[u], out[u]};
    }

    template<class F>
    void for_path(int u, int v, F&& f, bool edge = false) const {
        // Intervals cover the path without preserving traversal order.
        while (top[u] != top[v]) {
            if (dep[top[u]] < dep[top[v]]) {
                std::swap(u, v);
            }
            f(in[top[u]], in[u] + 1);
            u = parent[top[u]];
        }
        if (dep[u] > dep[v]) {
            std::swap(u, v);
        }
        int l = in[u] + static_cast<int>(edge);
        int r = in[v] + 1;
        if (l < r) {
            f(l, r);
        }
    }
};
