#include <iostream>
#include <vector>

using namespace std;

int binarySearch(const vector<int>& a, int x) {
    int left = 0;
    int right = static_cast<int>(a.size()) - 1;

    while (left <= right) {
        int mid = left + (right - left) / 2;

        if (a[mid] == x) {
            return mid;
        }
        if (a[mid] < x) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    return -1;
}

int main() {
    vector<int> a = {1, 3, 4, 7, 9, 12, 15};
    int x = 9;

    int pos = binarySearch(a, x);

    cout << "Array: ";
    for (int value : a) {
        cout << value << ' ';
    }
    cout << '\n';

    if (pos == -1) {
        cout << x << " not found\n";
    } else {
        cout << x << " found at index " << pos << '\n';
    }

    return 0;
}
