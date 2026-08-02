#pragma once

#include <bits/stdc++.h>

template<int Sigma = 26, char Base = 'a'>
struct SuffixAutomaton {
    struct State {
        std::array<int, Sigma> next;
        int link;
        int len;
        long long occurrences;

        State() : link(-1), len(0), occurrences(0) {
            next.fill(-1);
        }
    };

    int last;
    std::vector<State> state;

    SuffixAutomaton() {
        init();
    }

    void init() {
        state.assign(1, State());
        last = 0;
    }

    int extend(char c) {
        int x = c - Base;
        assert(0 <= x && x < Sigma);
        int current = static_cast<int>(state.size());
        state.emplace_back();
        state[current].len = state[last].len + 1;
        state[current].occurrences = 1;

        int p = last;
        while (p != -1 && state[p].next[x] == -1) {
            state[p].next[x] = current;
            p = state[p].link;
        }
        if (p == -1) {
            state[current].link = 0;
        } else {
            int q = state[p].next[x];
            if (state[p].len + 1 == state[q].len) {
                state[current].link = q;
            } else {
                int clone = static_cast<int>(state.size());
                state.push_back(state[q]);
                state[clone].len = state[p].len + 1;
                state[clone].occurrences = 0;
                while (p != -1 && state[p].next[x] == q) {
                    state[p].next[x] = clone;
                    p = state[p].link;
                }
                state[q].link = clone;
                state[current].link = clone;
            }
        }
        last = current;
        return current;
    }

    void build(const std::string& s) {
        init();
        for (char c : s) {
            extend(c);
        }
    }

    void propagate_occurrences() {
        int max_len = 0;
        for (const State& item : state) {
            max_len = std::max(max_len, item.len);
        }
        std::vector<int> count(max_len + 1, 0);
        for (const State& item : state) {
            count[item.len]++;
        }
        for (int i = 1; i <= max_len; i++) {
            count[i] += count[i - 1];
        }
        std::vector<int> order(state.size());
        for (int i = static_cast<int>(state.size()) - 1; i >= 0; i--) {
            order[--count[state[i].len]] = i;
        }
        for (int i = static_cast<int>(order.size()) - 1; i > 0; i--) {
            int u = order[i];
            state[state[u].link].occurrences += state[u].occurrences;
        }
    }
};
