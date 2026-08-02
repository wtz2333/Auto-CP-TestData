#pragma once

#include <bits/stdc++.h>

std::vector<int> prefix_function(const std::string& s) {
    int n = static_cast<int>(s.size());
    std::vector<int> pi(n, 0);
    for (int i = 1; i < n; i++) {
        int j = pi[i - 1];
        while (j > 0 && s[i] != s[j]) {
            j = pi[j - 1];
        }
        if (s[i] == s[j]) {
            j++;
        }
        pi[i] = j;
    }
    return pi;
}

std::vector<int> z_function(const std::string& s) {
    int n = static_cast<int>(s.size());
    std::vector<int> z(n, 0);
    for (int i = 1, l = 0, r = 0; i < n; i++) {
        if (i < r) {
            z[i] = std::min(r - i, z[i - l]);
        }
        while (i + z[i] < n && s[z[i]] == s[i + z[i]]) {
            z[i]++;
        }
        if (i + z[i] > r) {
            l = i;
            r = i + z[i];
        }
    }
    if (n > 0) {
        z[0] = n;
    }
    return z;
}

std::vector<int> manacher_odd(const std::string& s) {
    int n = static_cast<int>(s.size());
    std::vector<int> radius(n, 0);
    for (int i = 0, l = 0, r = -1; i < n; i++) {
        int k = i > r ? 1 : std::min(radius[l + r - i], r - i + 1);
        while (i - k >= 0 && i + k < n && s[i - k] == s[i + k]) {
            k++;
        }
        radius[i] = k;
        if (i + k - 1 > r) {
            l = i - k + 1;
            r = i + k - 1;
        }
    }
    return radius;
}

std::vector<int> manacher_even(const std::string& s) {
    int n = static_cast<int>(s.size());
    std::vector<int> radius(n, 0);
    for (int i = 0, l = 0, r = -1; i < n; i++) {
        int k = i > r ? 0 : std::min(radius[l + r - i + 1], r - i + 1);
        while (i - k - 1 >= 0 && i + k < n && s[i - k - 1] == s[i + k]) {
            k++;
        }
        radius[i] = k;
        if (i + k - 1 > r) {
            l = i - k;
            r = i + k - 1;
        }
    }
    return radius;
}
