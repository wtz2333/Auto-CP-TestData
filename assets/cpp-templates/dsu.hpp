#pragma once

#include <bits/stdc++.h>

struct DSU {
    std::vector<int> parent;

    DSU() = default;

    explicit DSU(int n) {
        init(n);
    }

    void init(int n) {
        parent.assign(n, -1);
    }

    int leader(int x) {
        if (parent[x] < 0) {
            return x;
        }
        return parent[x] = leader(parent[x]);
    }

    bool same(int x, int y) {
        return leader(x) == leader(y);
    }

    bool merge(int x, int y) {
        x = leader(x);
        y = leader(y);
        if (x == y) {
            return false;
        }
        if (parent[x] > parent[y]) {
            std::swap(x, y);
        }
        parent[x] += parent[y];
        parent[y] = x;
        return true;
    }

    int size(int x) {
        return -parent[leader(x)];
    }
};

struct RollbackDSU {
    std::vector<int> parent;
    std::vector<std::pair<int, int>> history;

    RollbackDSU() = default;

    explicit RollbackDSU(int n) {
        init(n);
    }

    void init(int n) {
        parent.assign(n, -1);
        history.clear();
    }

    int leader(int x) const {
        while (parent[x] >= 0) {
            x = parent[x];
        }
        return x;
    }

    bool same(int x, int y) const {
        return leader(x) == leader(y);
    }

    bool merge(int x, int y) {
        x = leader(x);
        y = leader(y);
        if (x == y) {
            history.emplace_back(-1, 0);
            return false;
        }
        if (parent[x] > parent[y]) {
            std::swap(x, y);
        }
        history.emplace_back(x, parent[x]);
        history.emplace_back(y, parent[y]);
        parent[x] += parent[y];
        parent[y] = x;
        return true;
    }

    int size(int x) const {
        return -parent[leader(x)];
    }

    std::size_t snapshot() const {
        return history.size();
    }

    void rollback(std::size_t state) {
        assert(state <= history.size());
        while (history.size() > state) {
            int x = history.back().first;
            int value = history.back().second;
            history.pop_back();
            if (x != -1) {
                parent[x] = value;
            }
        }
    }
};
