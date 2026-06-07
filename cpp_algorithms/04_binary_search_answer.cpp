#include <algorithm>
#include <iostream>
#include <vector>

using namespace std;

bool canSplit(const vector<int>& a, int maxSum, int k) {
    int parts = 1;
    int currentSum = 0;

    for (int x : a) {
        if (x > maxSum) {
            return false;
        }
        if (currentSum + x <= maxSum) {
            currentSum += x;
        } else {
            ++parts;
            currentSum = x;
        }
    }

    return parts <= k;
}

int main() {
    vector<int> a = {7, 2, 5, 10, 8};
    int k = 2;

    int left = 0;
    int right = 0;
    for (int x : a) {
        left = max(left, x);
        right += x;
    }

    while (left < right) {
        int mid = left + (right - left) / 2;
        if (canSplit(a, mid, k)) {
            right = mid;
        } else {
            left = mid + 1;
        }
    }

    cout << "Array: ";
    for (int x : a) {
        cout << x << ' ';
    }
    cout << '\n';
    cout << "Minimum possible maximum segment sum for k = " << k << " is " << left << '\n';

    return 0;
}
