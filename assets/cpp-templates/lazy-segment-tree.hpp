#pragma once

#include <bits/stdc++.h>

template<class Info, class Tag>
struct LazySegmentTree {
    int n;
    std::vector<Info> info;
    std::vector<Tag> tag;

    LazySegmentTree() : n(0) {}

    explicit LazySegmentTree(const std::vector<Info>& init_) {
        init(init_);
    }

    void init(const std::vector<Info>& init_) {
        n = static_cast<int>(init_.size());
        info.assign(4 * std::max(1, n), Info());
        tag.assign(4 * std::max(1, n), Tag());
        if (n > 0) {
            build(1, 0, n, init_);
        }
    }

    void build(int p, int l, int r, const std::vector<Info>& init_) {
        if (r - l == 1) {
            info[p] = init_[l];
            return;
        }
        int m = (l + r) / 2;
        build(2 * p, l, m, init_);
        build(2 * p + 1, m, r, init_);
        pull(p);
    }

    void pull(int p) {
        info[p] = info[2 * p] + info[2 * p + 1];
    }

    void apply(int p, const Tag& value) {
        info[p].apply(value);
        tag[p].apply(value);
    }

    void push(int p) {
        apply(2 * p, tag[p]);
        apply(2 * p + 1, tag[p]);
        tag[p] = Tag();
    }

    void modify(int p, int l, int r, int x, const Info& value) {
        if (r - l == 1) {
            info[p] = value;
            tag[p] = Tag();
            return;
        }
        push(p);
        int m = (l + r) / 2;
        if (x < m) {
            modify(2 * p, l, m, x, value);
        } else {
            modify(2 * p + 1, m, r, x, value);
        }
        pull(p);
    }

    void modify(int x, const Info& value) {
        assert(0 <= x && x < n);
        modify(1, 0, n, x, value);
    }

    void range_apply(int p, int l, int r, int x, int y, const Tag& value) {
        if (y <= l || r <= x) {
            return;
        }
        if (x <= l && r <= y) {
            apply(p, value);
            return;
        }
        push(p);
        int m = (l + r) / 2;
        range_apply(2 * p, l, m, x, y, value);
        range_apply(2 * p + 1, m, r, x, y, value);
        pull(p);
    }

    void range_apply(int l, int r, const Tag& value) {
        assert(0 <= l && l <= r && r <= n);
        if (l < r) {
            range_apply(1, 0, n, l, r, value);
        }
    }

    Info query(int p, int l, int r, int x, int y) {
        if (y <= l || r <= x) {
            return Info();
        }
        if (x <= l && r <= y) {
            return info[p];
        }
        push(p);
        int m = (l + r) / 2;
        return query(2 * p, l, m, x, y) + query(2 * p + 1, m, r, x, y);
    }

    Info query(int l, int r) {
        assert(0 <= l && l <= r && r <= n);
        if (l == r) {
            return Info();
        }
        return query(1, 0, n, l, r);
    }

    Info all() const {
        if (n == 0) {
            return Info();
        }
        return info[1];
    }
};
