#pragma once

#include <bits/stdc++.h>

template<int Mod>
struct ModInt {
    int value;

    ModInt() : value(0) {}

    template<class T>
    ModInt(T value_) {
        long long normalized = static_cast<long long>(value_ % Mod);
        if (normalized < 0) {
            normalized += Mod;
        }
        value = static_cast<int>(normalized);
    }

    static constexpr int mod() {
        return Mod;
    }

    int val() const {
        return value;
    }

    ModInt power(long long exponent) const {
        assert(exponent >= 0);
        ModInt result = 1;
        ModInt base = *this;
        while (exponent > 0) {
            if (exponent & 1) {
                result *= base;
            }
            base *= base;
            exponent >>= 1;
        }
        return result;
    }

    ModInt inv() const {
        assert(value != 0);
        return power(Mod - 2);
    }

    ModInt& operator+=(const ModInt& rhs) {
        value += rhs.value;
        if (value >= Mod) {
            value -= Mod;
        }
        return *this;
    }

    ModInt& operator-=(const ModInt& rhs) {
        value -= rhs.value;
        if (value < 0) {
            value += Mod;
        }
        return *this;
    }

    ModInt& operator*=(const ModInt& rhs) {
        value = static_cast<int>(1LL * value * rhs.value % Mod);
        return *this;
    }

    ModInt& operator/=(const ModInt& rhs) {
        return *this *= rhs.inv();
    }

    friend ModInt operator+(ModInt lhs, const ModInt& rhs) {
        return lhs += rhs;
    }

    friend ModInt operator-(ModInt lhs, const ModInt& rhs) {
        return lhs -= rhs;
    }

    friend ModInt operator*(ModInt lhs, const ModInt& rhs) {
        return lhs *= rhs;
    }

    friend ModInt operator/(ModInt lhs, const ModInt& rhs) {
        return lhs /= rhs;
    }

    friend bool operator==(const ModInt& lhs, const ModInt& rhs) {
        return lhs.value == rhs.value;
    }

    friend bool operator!=(const ModInt& lhs, const ModInt& rhs) {
        return !(lhs == rhs);
    }
};
