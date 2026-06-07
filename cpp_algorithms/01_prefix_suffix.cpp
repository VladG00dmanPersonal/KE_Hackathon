#include <algorithm>
#include <iostream>
#include <vector>

using namespace std;

int main() {
    vector<int> a = {5, 2, 7, 1, 3};
    int n = static_cast<int>(a.size());

    vector<int> prefixSum(n + 1, 0);
    vector<int> prefixMin(n);
    vector<int> prefixMax(n);
    vector<int> prefixCount(n + 1, 0);

    for (int i = 0; i < n; ++i) {
        prefixSum[i + 1] = prefixSum[i] + a[i];
        prefixCount[i + 1] = prefixCount[i] + 1;
        prefixMin[i] = (i == 0 ? a[i] : min(prefixMin[i - 1], a[i]));
        prefixMax[i] = (i == 0 ? a[i] : max(prefixMax[i - 1], a[i]));
    }

    vector<int> suffixSum(n + 1, 0);
    vector<int> suffixMin(n);
    vector<int> suffixMax(n);
    vector<int> suffixCount(n + 1, 0);

    for (int i = n - 1; i >= 0; --i) {
        suffixSum[i] = suffixSum[i + 1] + a[i];
        suffixCount[i] = suffixCount[i + 1] + 1;
        suffixMin[i] = (i == n - 1 ? a[i] : min(suffixMin[i + 1], a[i]));
        suffixMax[i] = (i == n - 1 ? a[i] : max(suffixMax[i + 1], a[i]));
    }

    cout << "Array: ";
    for (int x : a) {
        cout << x << ' ';
    }
    cout << "\n\n";

    cout << "Prefix sum on [0..3] = " << prefixSum[4] - prefixSum[0] << '\n';
    cout << "Prefix count on [0..3] = " << prefixCount[4] - prefixCount[0] << '\n';
    cout << "Min on prefix [0..3] = " << prefixMin[3] << '\n';
    cout << "Max on prefix [0..3] = " << prefixMax[3] << '\n';

    cout << '\n';
    cout << "Suffix sum on [2..4] = " << suffixSum[2] << '\n';
    cout << "Suffix count on [2..4] = " << suffixCount[2] << '\n';
    cout << "Min on suffix [2..4] = " << suffixMin[2] << '\n';
    cout << "Max on suffix [2..4] = " << suffixMax[2] << '\n';

    return 0;
}
