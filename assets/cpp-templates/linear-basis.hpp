#pragma once

#include <bits/stdc++.h>

template<int Bits = 63>
struct LinearBasis {
    std::array<unsigned long long, Bits> basis;

    LinearBasis() {
        clear();
    }

    void clear() {
        basis.fill(0);
    }

    bool insert(unsigned long long value) {
        for (int bit = Bits - 1; bit >= 0; bit--) {
            if (!(value >> bit & 1ULL)) {
                continue;
            }
            if (basis[bit] == 0) {
                basis[bit] = value;
                return true;
            }
            value ^= basis[bit];
        }
        return false;
    }

    bool representable(unsigned long long value) const {
        for (int bit = Bits - 1; bit >= 0; bit--) {
            if (value >> bit & 1ULL) {
                if (basis[bit] == 0) {
                    return false;
                }
                value ^= basis[bit];
            }
        }
        return true;
    }

    unsigned long long max_xor(unsigned long long value = 0) const {
        for (int bit = Bits - 1; bit >= 0; bit--) {
            value = std::max(value, value ^ basis[bit]);
        }
        return value;
    }
};
