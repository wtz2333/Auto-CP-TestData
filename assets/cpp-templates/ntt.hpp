#pragma once

#include <bits/stdc++.h>

struct NTT998244353 {
    static constexpr int mod = 998244353;
    static constexpr int primitive_root = 3;

    static int power(int base, int exponent) {
        int result = 1;
        while (exponent > 0) {
            if (exponent & 1) {
                result = static_cast<int>(1LL * result * base % mod);
            }
            base = static_cast<int>(1LL * base * base % mod);
            exponent >>= 1;
        }
        return result;
    }

    static void transform(std::vector<int>& a, bool inverse) {
        int n = static_cast<int>(a.size());
        assert(n > 0 && (n & (n - 1)) == 0);
        assert((mod - 1) % n == 0);
        for (int i = 1, j = 0; i < n; i++) {
            int bit = n >> 1;
            while (j & bit) {
                j ^= bit;
                bit >>= 1;
            }
            j ^= bit;
            if (i < j) {
                std::swap(a[i], a[j]);
            }
        }
        for (int len = 2; len <= n; len <<= 1) {
            int root = power(primitive_root, (mod - 1) / len);
            if (inverse) {
                root = power(root, mod - 2);
            }
            for (int l = 0; l < n; l += len) {
                int value = 1;
                for (int i = 0; i < len / 2; i++) {
                    int even = a[l + i];
                    int odd = static_cast<int>(1LL * a[l + i + len / 2] * value % mod);
                    a[l + i] = even + odd;
                    if (a[l + i] >= mod) {
                        a[l + i] -= mod;
                    }
                    a[l + i + len / 2] = even - odd;
                    if (a[l + i + len / 2] < 0) {
                        a[l + i + len / 2] += mod;
                    }
                    value = static_cast<int>(1LL * value * root % mod);
                }
            }
        }
        if (inverse) {
            int inverse_n = power(n, mod - 2);
            for (int& value : a) {
                value = static_cast<int>(1LL * value * inverse_n % mod);
            }
        }
    }

    static std::vector<int> convolution(std::vector<int> a, std::vector<int> b) {
        if (a.empty() || b.empty()) {
            return {};
        }
        int result_size = static_cast<int>(a.size() + b.size()) - 1;
        int n = 1;
        while (n < result_size) {
            n <<= 1;
        }
        a.resize(n, 0);
        b.resize(n, 0);
        transform(a, false);
        transform(b, false);
        for (int i = 0; i < n; i++) {
            a[i] = static_cast<int>(1LL * a[i] * b[i] % mod);
        }
        transform(a, true);
        a.resize(result_size);
        return a;
    }
};
