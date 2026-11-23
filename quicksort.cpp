#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdint>
using namespace std;

void quickSort(vector<long long>& a, long long lo, long long hi) {
    while (lo < hi) {
        long long mid = lo + (hi - lo) / 2;
        long long pivot = a[mid];

        long long lt = lo, i = lo, gt = hi;
        while (i <= gt) {
            if (a[i] < pivot) {
                swap(a[lt], a[i]);
                ++lt; ++i;
            } else if (a[i] > pivot) {
                swap(a[i], a[gt]);
                --gt;
            } else {
                ++i;
            }
        }

        // Daha küçük parçayı önce özyinelemeli işle; yığın derinliğini sınırlar.
        if (lt - lo < hi - gt) {
            if (lo < lt - 1) quickSort(a, lo, lt - 1);
            lo = gt + 1;
        } else {
            if (gt + 1 < hi) quickSort(a, gt + 1, hi);
            hi = lt - 1;
        }
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    vector<long long> values;
    long long x;
    while (cin >> x) values.push_back(x);

    if (!values.empty()) quickSort(values, 0, (long long)values.size() - 1);

    long long checksum = 0;
    for (long long v : values) checksum += v;
    cout << values.size() << " " << checksum << "\n";
    return 0;
}
