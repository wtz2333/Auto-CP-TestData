#pragma once

#include <bits/stdc++.h>

template<class T>
struct Point2D {
    T x;
    T y;

    Point2D() : x(T()), y(T()) {}

    Point2D(T x_, T y_) : x(x_), y(y_) {}

    Point2D& operator+=(const Point2D& rhs) {
        x += rhs.x;
        y += rhs.y;
        return *this;
    }

    Point2D& operator-=(const Point2D& rhs) {
        x -= rhs.x;
        y -= rhs.y;
        return *this;
    }

    friend Point2D operator+(Point2D lhs, const Point2D& rhs) {
        return lhs += rhs;
    }

    friend Point2D operator-(Point2D lhs, const Point2D& rhs) {
        return lhs -= rhs;
    }

    friend bool operator==(const Point2D& lhs, const Point2D& rhs) {
        return lhs.x == rhs.x && lhs.y == rhs.y;
    }

    friend bool operator<(const Point2D& lhs, const Point2D& rhs) {
        if (lhs.x != rhs.x) {
            return lhs.x < rhs.x;
        }
        return lhs.y < rhs.y;
    }
};

template<class T>
T dot(const Point2D<T>& lhs, const Point2D<T>& rhs) {
    return lhs.x * rhs.x + lhs.y * rhs.y;
}

template<class T>
T cross(const Point2D<T>& lhs, const Point2D<T>& rhs) {
    return lhs.x * rhs.y - lhs.y * rhs.x;
}

template<class T>
T cross(const Point2D<T>& origin, const Point2D<T>& a, const Point2D<T>& b) {
    return cross(a - origin, b - origin);
}

template<class T>
std::vector<Point2D<T>> convex_hull(std::vector<Point2D<T>> point) {
    std::sort(point.begin(), point.end());
    point.erase(std::unique(point.begin(), point.end()), point.end());
    if (point.size() <= 1) {
        return point;
    }
    std::vector<Point2D<T>> hull;
    for (const Point2D<T>& p : point) {
        while (hull.size() >= 2 && cross(hull[hull.size() - 2], hull.back(), p) <= T()) {
            hull.pop_back();
        }
        hull.push_back(p);
    }
    std::size_t lower_size = hull.size();
    for (int i = static_cast<int>(point.size()) - 2; i >= 0; i--) {
        const Point2D<T>& p = point[i];
        while (hull.size() > lower_size && cross(hull[hull.size() - 2], hull.back(), p) <= T()) {
            hull.pop_back();
        }
        hull.push_back(p);
    }
    hull.pop_back();
    return hull;
}
