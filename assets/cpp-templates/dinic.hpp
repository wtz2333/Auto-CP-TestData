#pragma once

#include <bits/stdc++.h>

template<class Cap>
struct Dinic {
    struct Edge {
        int to;
        int reverse;
        Cap cap;
    };

    int n;
    std::vector<int> level;
    std::vector<int> current;
    std::vector<std::vector<Edge>> graph;

    Dinic() : n(0) {}

    explicit Dinic(int n_) {
        init(n_);
    }

    void init(int n_) {
        n = n_;
        level.assign(n, -1);
        current.assign(n, 0);
        graph.assign(n, {});
    }

    void add_edge(int u, int v, Cap cap) {
        assert(cap >= Cap());
        Edge forward{v, static_cast<int>(graph[v].size()), cap};
        Edge backward{u, static_cast<int>(graph[u].size()), Cap()};
        graph[u].push_back(forward);
        graph[v].push_back(backward);
    }

    bool bfs(int source, int sink) {
        std::fill(level.begin(), level.end(), -1);
        std::queue<int> queue;
        level[source] = 0;
        queue.push(source);
        while (!queue.empty()) {
            int u = queue.front();
            queue.pop();
            for (const Edge& edge : graph[u]) {
                if (edge.cap > Cap() && level[edge.to] == -1) {
                    level[edge.to] = level[u] + 1;
                    queue.push(edge.to);
                }
            }
        }
        return level[sink] != -1;
    }

    Cap dfs(int u, int sink, Cap pushed) {
        if (u == sink || pushed == Cap()) {
            return pushed;
        }
        for (int& i = current[u]; i < static_cast<int>(graph[u].size()); i++) {
            Edge& edge = graph[u][i];
            if (edge.cap <= Cap() || level[edge.to] != level[u] + 1) {
                continue;
            }
            Cap flow = dfs(edge.to, sink, std::min(pushed, edge.cap));
            if (flow == Cap()) {
                continue;
            }
            edge.cap -= flow;
            graph[edge.to][edge.reverse].cap += flow;
            return flow;
        }
        return Cap();
    }

    Cap max_flow(int source, int sink, Cap limit = std::numeric_limits<Cap>::max()) {
        Cap flow = Cap();
        while (flow < limit && bfs(source, sink)) {
            std::fill(current.begin(), current.end(), 0);
            while (flow < limit) {
                Cap pushed = dfs(source, sink, limit - flow);
                if (pushed == Cap()) {
                    break;
                }
                flow += pushed;
            }
        }
        return flow;
    }
};
