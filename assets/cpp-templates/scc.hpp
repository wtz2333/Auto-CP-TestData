#pragma once

#include <bits/stdc++.h>

struct SCC {
    int n;
    int components;
    std::vector<int> comp;
    std::vector<std::vector<int>> graph;
    std::vector<std::vector<int>> reverse_graph;

    SCC() : n(0), components(0) {}

    explicit SCC(int n_) {
        init(n_);
    }

    void init(int n_) {
        n = n_;
        components = 0;
        comp.assign(n, -1);
        graph.assign(n, {});
        reverse_graph.assign(n, {});
    }

    void add_edge(int u, int v) {
        graph[u].push_back(v);
        reverse_graph[v].push_back(u);
    }

    int work() {
        std::vector<char> seen(n, false);
        std::vector<int> order;
        order.reserve(n);

        for (int start = 0; start < n; start++) {
            if (seen[start]) {
                continue;
            }
            std::vector<std::pair<int, int>> stack;
            stack.emplace_back(start, 0);
            seen[start] = true;
            while (!stack.empty()) {
                int u = stack.back().first;
                int& edge_index = stack.back().second;
                if (edge_index < static_cast<int>(graph[u].size())) {
                    int v = graph[u][edge_index++];
                    if (!seen[v]) {
                        seen[v] = true;
                        stack.emplace_back(v, 0);
                    }
                } else {
                    order.push_back(u);
                    stack.pop_back();
                }
            }
        }

        std::fill(comp.begin(), comp.end(), -1);
        components = 0;
        for (int i = n - 1; i >= 0; i--) {
            int start = order[i];
            if (comp[start] != -1) {
                continue;
            }
            std::vector<int> stack(1, start);
            comp[start] = components;
            while (!stack.empty()) {
                int u = stack.back();
                stack.pop_back();
                for (int v : reverse_graph[u]) {
                    if (comp[v] == -1) {
                        comp[v] = components;
                        stack.push_back(v);
                    }
                }
            }
            components++;
        }
        return components;
    }
};
