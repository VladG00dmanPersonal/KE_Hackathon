#include <algorithm>
#include <deque>
#include <iostream>
#include <stack>
#include <utility>
#include <vector>

using namespace std;

class MinStack {
public:
    void push(int x) {
        if (data.empty()) {
            data.push({x, x});
        } else {
            data.push({x, min(x, data.top().second)});
        }
    }

    void pop() {
        data.pop();
    }

    int top() const {
        return data.top().first;
    }

    int getMin() const {
        return data.top().second;
    }

    bool empty() const {
        return data.empty();
    }

private:
    stack<pair<int, int>> data;
};

vector<int> minInEveryWindow(const vector<int>& a, int k) {
    deque<int> dq;
    vector<int> result;

    for (int i = 0; i < static_cast<int>(a.size()); ++i) {
        while (!dq.empty() && dq.front() <= i - k) {
            dq.pop_front();
        }
        while (!dq.empty() && a[dq.back()] >= a[i]) {
            dq.pop_back();
        }

        dq.push_back(i);

        if (i + 1 >= k) {
            result.push_back(a[dq.front()]);
        }
    }

    return result;
}

int main() {
    MinStack st;
    st.push(5);
    st.push(2);
    st.push(7);

    cout << "MinStack current min: " << st.getMin() << '\n';
    st.pop();
    cout << "MinStack current min after pop: " << st.getMin() << '\n';
    cout << '\n';

    vector<int> a = {4, 2, 12, 3, 5, 1, 6};
    int k = 3;

    vector<int> mins = minInEveryWindow(a, k);

    cout << "Array: ";
    for (int x : a) {
        cout << x << ' ';
    }
    cout << '\n';

    cout << "Minimum in every window of size " << k << ": ";
    for (int x : mins) {
        cout << x << ' ';
    }
    cout << '\n';

    return 0;
}
