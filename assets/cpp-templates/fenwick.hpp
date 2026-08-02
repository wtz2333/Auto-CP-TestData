#pragma once

#include <bits/stdc++.h>

template<class T>
struct Fenwick {
    int n;
    std::vector<T> bit;

    Fenwick() : n(0) {}

    explicit Fenwick(int n_) {
        init(n_);
    }

    void init(int n_) {
        n = n_;
        bit.assign(n + 1, T());
    }

    void add(int x, const T& value) {
        assert(0 <= x && x < n);
        for (int i = x + 1; i <= n; i += i & -i) {
            bit[i] += value;
        }
    }

    T prefix_sum(int r) const {
        assert(0 <= r && r <= n);
        T result = T();
        for (int i = r; i > 0; i -= i & -i) {
            result += bit[i];
        }
        return result;
    }

    T range_sum(int l, int r) const {
        assert(0 <= l && l <= r && r <= n);
        return prefix_sum(r) - prefix_sum(l);
    }

    int lower_bound(T target) const {
        if (!(T() < target)) {
            return 0;
        }
        int x = 0;
        T sum = T();
        int step = 1;
        while (step < n) {
            step <<= 1;
        }
        for (; step > 0; step >>= 1) {
            int next = x + step;
            if (next <= n && sum + bit[next] < target) {
                x = next;
                sum += bit[next];
            }
        }
        return x;
    }
};
