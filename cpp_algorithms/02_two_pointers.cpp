#include <algorithm>
#include <iostream>
#include <vector>

using namespace std;

int main() {
    vector<int> a = {1, 2, 1, 3, 2, 1, 1};
    int target = 5;

    int left = 0;
    int currentSum = 0;
    int bestLength = static_cast<int>(a.size()) + 1;

    for (int right = 0; right < static_cast<int>(a.size()); ++right) {
        currentSum += a[right];

        while (currentSum >= target) {
            bestLength = min(bestLength, right - left + 1);
            currentSum -= a[left];
            ++left;
        }
    }

    cout << "Array: ";
    for (int x : a) {
        cout << x << ' ';
    }
    cout << '\n';

    if (bestLength == static_cast<int>(a.size()) + 1) {
        cout << "No segment with sum >= " << target << '\n';
    } else {
        cout << "Minimum length with sum >= " << target << " is " << bestLength << '\n';
    }

    return 0;
}
