#pragma once

#include <bits/stdc++.h>

template<class Cap, class Cost>
struct MinCostFlow {
    struct Edge {
        int to;
        int reverse;
        Cap cap;
        Cost cost;
    };

    int n;
    std::vector<std::vector<Edge>> graph;

    MinCostFlow() : n(0) {}

    explicit MinCostFlow(int n_) {
        init(n_);
    }

    void init(int n_) {
        n = n_;
        graph.assign(n, {});
    }

    void add_edge(int u, int v, Cap cap, Cost cost) {
        assert(cap >= Cap());
        Edge forward{v, static_cast<int>(graph[v].size()), cap, cost};
        Edge backward{u, static_cast<int>(graph[u].size()), Cap(), -cost};
        graph[u].push_back(forward);
        graph[v].push_back(backward);
    }

    std::vector<Cost> initial_potential(int source) const {
        const Cost inf = std::numeric_limits<Cost>::max() / 4;
        std::vector<Cost> dist(n, inf);
        std::vector<char> in_queue(n, false);
        std::queue<int> queue;
        dist[source] = Cost();
        queue.push(source);
        in_queue[source] = true;
        while (!queue.empty()) {
            int u = queue.front();
            queue.pop();
            in_queue[u] = false;
            for (const Edge& edge : graph[u]) {
                if (edge.cap > Cap() && dist[edge.to] > dist[u] + edge.cost) {
                    dist[edge.to] = dist[u] + edge.cost;
                    if (!in_queue[edge.to]) {
                        in_queue[edge.to] = true;
                        queue.push(edge.to);
                    }
                }
            }
        }
        for (Cost& value : dist) {
            if (value == inf) {
                value = Cost();
            }
        }
        return dist;
    }

    std::pair<Cap, Cost> flow(
        int source,
        int sink,
        Cap limit = std::numeric_limits<Cap>::max()
    ) {
        const Cost inf = std::numeric_limits<Cost>::max() / 4;
        std::vector<Cost> potential = initial_potential(source);
        Cap total_flow = Cap();
        Cost total_cost = Cost();

        while (total_flow < limit) {
            std::vector<Cost> dist(n, inf);
            std::vector<int> previous_vertex(n, -1);
            std::vector<int> previous_edge(n, -1);
            using State = std::pair<Cost, int>;
            std::priority_queue<State, std::vector<State>, std::greater<State>> queue;
            dist[source] = Cost();
            queue.emplace(Cost(), source);

            while (!queue.empty()) {
                Cost current_dist = queue.top().first;
                int u = queue.top().second;
                queue.pop();
                if (current_dist != dist[u]) {
                    continue;
                }
                for (int i = 0; i < static_cast<int>(graph[u].size()); i++) {
                    const Edge& edge = graph[u][i];
                    if (edge.cap == Cap()) {
                        continue;
                    }
                    Cost next_dist = current_dist + edge.cost + potential[u] - potential[edge.to];
                    if (next_dist < dist[edge.to]) {
                        dist[edge.to] = next_dist;
                        previous_vertex[edge.to] = u;
                        previous_edge[edge.to] = i;
                        queue.emplace(next_dist, edge.to);
                    }
                }
            }
            if (dist[sink] == inf) {
                break;
            }
            for (int u = 0; u < n; u++) {
                if (dist[u] != inf) {
                    potential[u] += dist[u];
                }
            }

            Cap pushed = limit - total_flow;
            for (int v = sink; v != source; v = previous_vertex[v]) {
                const Edge& edge = graph[previous_vertex[v]][previous_edge[v]];
                pushed = std::min(pushed, edge.cap);
            }
            for (int v = sink; v != source; v = previous_vertex[v]) {
                int u = previous_vertex[v];
                int edge_index = previous_edge[v];
                Edge& edge = graph[u][edge_index];
                edge.cap -= pushed;
                graph[v][edge.reverse].cap += pushed;
            }
            total_flow += pushed;
            total_cost += static_cast<Cost>(pushed) * potential[sink];
        }
        return {total_flow, total_cost};
    }
};
