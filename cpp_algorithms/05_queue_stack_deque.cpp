#include <deque>
#include <iostream>
#include <queue>
#include <stack>

using namespace std;

int main() {
    queue<int> q;
    q.push(10);
    q.push(20);
    q.push(30);

    stack<int> st;
    st.push(1);
    st.push(2);
    st.push(3);

    deque<int> dq;
    dq.push_back(5);
    dq.push_back(6);
    dq.push_front(4);

    cout << "Queue front: " << q.front() << '\n';
    q.pop();
    cout << "Queue front after pop: " << q.front() << '\n';

    cout << "Stack top: " << st.top() << '\n';
    st.pop();
    cout << "Stack top after pop: " << st.top() << '\n';

    cout << "Deque front: " << dq.front() << '\n';
    cout << "Deque back: " << dq.back() << '\n';
    dq.pop_front();
    dq.push_back(7);

    cout << "Deque now: ";
    while (!dq.empty()) {
        cout << dq.front() << ' ';
        dq.pop_front();
    }
    cout << '\n';

    return 0;
}
