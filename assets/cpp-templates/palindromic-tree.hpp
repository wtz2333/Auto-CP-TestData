#pragma once

#include <bits/stdc++.h>

template<int Sigma = 26, char Base = 'a'>
struct PalindromicTree {
    struct Node {
        std::array<int, Sigma> next;
        int link;
        int len;
        long long occurrences;

        Node() : link(0), len(0), occurrences(0) {
            next.fill(-1);
        }
    };

    int last;
    std::string text;
    std::vector<Node> node;

    PalindromicTree() {
        init();
    }

    void init() {
        node.assign(2, Node());
        node[0].len = 0;
        node[0].link = 1;
        node[1].len = -1;
        node[1].link = 1;
        last = 0;
        text.clear();
    }

    int get_link(int u, int position) const {
        while (position - node[u].len - 1 < 0 ||
               text[position - node[u].len - 1] != text[position]) {
            u = node[u].link;
        }
        return u;
    }

    int add(char c) {
        int x = c - Base;
        assert(0 <= x && x < Sigma);
        text.push_back(c);
        int position = static_cast<int>(text.size()) - 1;
        int parent = get_link(last, position);
        if (node[parent].next[x] == -1) {
            int current = static_cast<int>(node.size());
            node.emplace_back();
            node[current].len = node[parent].len + 2;
            if (node[current].len == 1) {
                node[current].link = 0;
            } else {
                int suffix_parent = get_link(node[parent].link, position);
                node[current].link = node[suffix_parent].next[x];
            }
            node[parent].next[x] = current;
        }
        last = node[parent].next[x];
        node[last].occurrences++;
        return last;
    }

    void build(const std::string& s) {
        init();
        for (char c : s) {
            add(c);
        }
    }

    void propagate_occurrences() {
        std::vector<int> order(node.size());
        std::iota(order.begin(), order.end(), 0);
        std::sort(order.begin(), order.end(), [&](int lhs, int rhs) {
            return node[lhs].len > node[rhs].len;
        });
        for (int u : order) {
            if (u >= 2) {
                node[node[u].link].occurrences += node[u].occurrences;
            }
        }
    }

    int distinct_palindromes() const {
        return static_cast<int>(node.size()) - 2;
    }
};
