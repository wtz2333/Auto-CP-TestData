#pragma once

#include <bits/stdc++.h>

template<int Sigma = 26, char Base = 'a'>
struct AhoCorasick {
    struct Node {
        std::array<int, Sigma> next;
        int link;
        int terminal;

        Node() : link(0), terminal(0) {
            next.fill(-1);
        }
    };

    std::vector<Node> node;
    std::vector<int> bfs_order;

    AhoCorasick() {
        init();
    }

    void init() {
        node.assign(1, Node());
        bfs_order.clear();
    }

    int insert(const std::string& s) {
        int u = 0;
        for (char c : s) {
            int x = c - Base;
            assert(0 <= x && x < Sigma);
            if (node[u].next[x] == -1) {
                node[u].next[x] = static_cast<int>(node.size());
                node.emplace_back();
            }
            u = node[u].next[x];
        }
        node[u].terminal++;
        return u;
    }

    void build() {
        std::queue<int> queue;
        bfs_order.clear();
        for (int x = 0; x < Sigma; x++) {
            int v = node[0].next[x];
            if (v == -1) {
                node[0].next[x] = 0;
            } else {
                node[v].link = 0;
                queue.push(v);
            }
        }
        while (!queue.empty()) {
            int u = queue.front();
            queue.pop();
            bfs_order.push_back(u);
            for (int x = 0; x < Sigma; x++) {
                int v = node[u].next[x];
                if (v == -1) {
                    node[u].next[x] = node[node[u].link].next[x];
                } else {
                    node[v].link = node[node[u].link].next[x];
                    queue.push(v);
                }
            }
        }
    }

    int advance(int state, char c) const {
        int x = c - Base;
        assert(0 <= x && x < Sigma);
        return node[state].next[x];
    }
};
