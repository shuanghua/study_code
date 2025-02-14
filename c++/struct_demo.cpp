#include <iostream>
using namespace std;

struct Point {
    int x;
    int y;
};

int main() {
    Point p = {10, 20};
    cout << "x: " << p.x << ", y: " << p.y << endl;
    return 0;
}
