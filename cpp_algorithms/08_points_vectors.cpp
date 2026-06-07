#include <iostream>
#include <cmath>

using namespace std;

struct Point {
    double x;
    double y;
};

struct Vector {
    double x;
    double y;
};

struct Line {
    double a, b, c;
};

Vector makeVector(const Point& a, const Point& b) {
    return {b.x - a.x, b.y - a.y};
}

double length(const Vector& v) {
    return sqrt(v.x * v.x + v.y * v.y);
}

double distance(const Point& a, const Point& b) {
    return length(makeVector(a, b));
}

double dot(const Vector& a, const Vector& b) {
    return a.x * b.x + a.y * b.y;
}

double cross(const Vector& a, const Vector& b) {
    return a.x * b.y - a.y * b.x;
}

// Проверка, лежит ли точка C на отрезке AB
bool isBetween(const Point& a, const Point& b, const Point& c) {
    Vector ac = makeVector(a, c);
    Vector bc = makeVector(b, c);
    // Коллинеарность (векторное произведение должно быть равно 0) 
    // и проверка направления (скалярное произведение <= 0)
    return abs(cross(ac, bc)) < 1e-9 && dot(ac, bc) <= 1e-9;
}

// Построение прямой Ax + By + C = 0 по двум точкам
Line getLine(const Point& p1, const Point& p2) {
    Line l;
    l.a = p2.y - p1.y;
    l.b = p1.x - p2.x;
    l.c = -l.a * p1.x - l.b * p1.y;
    return l;
}

// Пересечение прямых
bool intersect(const Line& l1, const Line& l2, Point& out) {
    double d = l1.a * l2.b - l1.b * l2.a;
    if (abs(d) < 1e-9) return false; // прямые параллельны или совпадают
    out.x = (l1.b * l2.c - l1.c * l2.b) / d;
    out.y = (l1.c * l2.a - l1.a * l2.c) / d;
    return true;
}

int main() {
    Point a = {1, 2};
    Point b = {4, 6};
    Point c = {6, 3};

    Vector ab = makeVector(a, b);
    Vector ac = makeVector(a, c);

    cout << "AB = (" << ab.x << ", " << ab.y << ")\n";
    cout << "AC = (" << ac.x << ", " << ac.y << ")\n";
    cout << "Dot product AB * AC = " << dot(ab, ac) << '\n';
    cout << "Cross product AB x AC = " << cross(ab, ac) << '\n';

    cout << "Distance A to B = " << distance(a, b) << '\n';

    Point mid = {2.5, 4.0}; // середина AB
    cout << "Is point (2.5, 4) between A & B? " << (isBetween(a, b, mid) ? "yes" : "no") << '\n';
    cout << "Is point C between A & B? " << (isBetween(a, b, c) ? "yes" : "no") << '\n';

    Line l1 = getLine(a, b);
    Point d = {1, 6};
    Point e = {6, 2};
    Line l2 = getLine(d, e);
    
    Point intersection;
    if (intersect(l1, l2, intersection)) {
        cout << "Line AB intersects Line DE at (" << intersection.x << ", " << intersection.y << ")\n";
    }

    return 0;
}
