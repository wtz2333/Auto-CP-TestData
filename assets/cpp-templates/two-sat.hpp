#pragma once

#include <bits/stdc++.h>

#include "scc.hpp"

struct TwoSat {
    int n;
    SCC scc;
    std::vector<char> assignment;

    TwoSat() : n(0) {}

    explicit TwoSat(int n_) : n(n_), scc(2 * n_), assignment(n_, false) {}

    int literal(int variable, bool value) const {
        return 2 * variable + static_cast<int>(value);
    }

    void add_implication(int x, bool x_value, int y, bool y_value) {
        scc.add_edge(literal(x, x_value), literal(y, y_value));
    }

    void add_or(int x, bool x_value, int y, bool y_value) {
        add_implication(x, !x_value, y, y_value);
        add_implication(y, !y_value, x, x_value);
    }

    void set_value(int x, bool value) {
        add_implication(x, !value, x, value);
    }

    bool solve() {
        scc.work();
        for (int x = 0; x < n; x++) {
            int false_id = literal(x, false);
            int true_id = literal(x, true);
            if (scc.comp[false_id] == scc.comp[true_id]) {
                return false;
            }
            assignment[x] = scc.comp[true_id] > scc.comp[false_id];
        }
        return true;
    }
};
