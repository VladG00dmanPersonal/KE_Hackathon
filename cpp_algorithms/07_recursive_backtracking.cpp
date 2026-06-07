#include <iostream>
#include <vector>

using namespace std;

void generate(int n, vector<int>& current) {
    if (static_cast<int>(current.size()) == n) {
        for (int x : current) {
            cout << x;
        }
        cout << '\n';
        return;
    }

    for (int digit = 0; digit <= 1; ++digit) {
        current.push_back(digit);
        generate(n, current);
        current.pop_back();
    }
}

int main() {
    int n = 3;
    vector<int> current;

    cout << "All binary strings of length " << n << ":\n";
    generate(n, current);

    return 0;
}
