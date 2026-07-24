#include <bits/stdc++.h>
using namespace std;

// CUSTOMIZE: Replace the sample array format, limits, and profiles for the task.
// Keep the deterministic CLI contract: --case, --seed, --profile.

struct Options {
    int case_index = -1;
    uint64_t seed = 0;
    string profile;
};

[[noreturn]] static void die(const string &message) {
    cerr << "gen: " << message << '\n';
    exit(2);
}

static Options parse_args(int argc, char **argv) {
    Options opt;
    for (int i = 1; i < argc; ++i) {
        string key = argv[i];
        if (i + 1 >= argc) die("missing value after " + key);
        string value = argv[++i];
        if (key == "--case") opt.case_index = stoi(value);
        else if (key == "--seed") opt.seed = stoull(value);
        else if (key == "--profile") opt.profile = value;
        else die("unknown option " + key);
    }
    if (opt.case_index < 1) die("--case must be positive");
    if (opt.profile.empty()) die("--profile is required");
    return opt;
}

static long long randint(mt19937_64 &rng, long long low, long long high) {
    if (low > high) die("invalid random interval");
    uniform_int_distribution<long long> distribution(low, high);
    return distribution(rng);
}

static uint32_t stable_profile_hash(const string &text) {
    uint32_t hash = 2166136261u;
    for (unsigned char byte : text) {
        hash ^= byte;
        hash *= 16777619u;
    }
    return hash;
}

int main(int argc, char **argv) {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    Options opt = parse_args(argc, argv);
    seed_seq sequence{
        uint32_t(opt.seed), uint32_t(opt.seed >> 32),
        uint32_t(opt.case_index), stable_profile_hash(opt.profile)
    };
    mt19937_64 rng(sequence);

    // CUSTOMIZE: This sample emits n followed by n integers in [0, 100].
    int n;
    vector<int> a;
    if (opt.profile == "minimum") {
        n = 1;
        a = {0};
    } else if (opt.profile == "maximum") {
        n = 100;
        a.assign(n, 100);
    } else if (opt.profile == "random") {
        n = int(randint(rng, 1, 100));
        a.resize(n);
        for (int &value : a) value = int(randint(rng, 0, 100));
    } else {
        die("unknown profile " + opt.profile);
    }

    cout << n << '\n';
    for (int i = 0; i < n; ++i) {
        if (i) cout << ' ';
        cout << a[i];
    }
    cout << '\n';
}
