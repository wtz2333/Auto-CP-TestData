#pragma once

#include <bits/stdc++.h>

template<class T, class Merge>
struct SparseTable {
    int n;
    Merge merge;
    std::vector<int> log;
    std::vector<std::vector<T>> table;

    SparseTable() : n(0), merge(Merge()) {}

    explicit SparseTable(const std::vector<T>& init_, Merge merge_ = Merge()) {
        init(init_, merge_);
    }

    void init(const std::vector<T>& init_, Merge merge_ = Merge()) {
        n = static_cast<int>(init_.size());
        merge = merge_;
        log.assign(n + 1, 0);
        for (int i = 2; i <= n; i++) {
            log[i] = log[i / 2] + 1;
        }
        int levels = n == 0 ? 0 : log[n] + 1;
        table.assign(levels, std::vector<T>(n));
        if (n == 0) {
            return;
        }
        table[0] = init_;
        for (int k = 1; k < levels; k++) {
            int len = 1 << k;
            for (int i = 0; i + len <= n; i++) {
                table[k][i] = merge(table[k - 1][i], table[k - 1][i + len / 2]);
            }
        }
    }

    T query(int l, int r) const {
        assert(0 <= l && l < r && r <= n);
        int k = log[r - l];
        return merge(table[k][l], table[k][r - (1 << k)]);
    }
};
