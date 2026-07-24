#include <bits/stdc++.h>
using namespace std;

// CUSTOMIZE: Replace the sample array grammar and constraints for the task.

[[noreturn]] static void reject(const string &message) {
    cerr << "invalid input: " << message << '\n';
    exit(1);
}

template <class T>
static T read_value(const string &name) {
    T value;
    if (!(cin >> value)) reject("cannot read " + name);
    return value;
}

static void require(bool condition, const string &message) {
    if (!condition) reject(message);
}

int main(int argc, char **argv) {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string group = "full";
    for (int i = 1; i < argc; ++i) {
        string key = argv[i];
        if (key != "--group" || i + 1 >= argc) reject("expected --group <id>");
        group = argv[++i];
    }

    // CUSTOMIZE: Sample format: 1 <= n <= 100, then n values in [0, 100].
    long long n = read_value<long long>("n");
    require(1 <= n && n <= 100, "n is outside [1, 100]");
    if (group == "small") require(n <= 10, "small group requires n <= 10");
    else if (group != "full") reject("unknown group " + group);
    for (long long i = 0; i < n; ++i) {
        long long value = read_value<long long>("a[" + to_string(i) + "]");
        require(0 <= value && value <= 100, "array value is outside [0, 100]");
    }

    string extra;
    if (cin >> extra) reject("extra token after the expected input: " + extra);
    return 0;
}
