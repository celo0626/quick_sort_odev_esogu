import sys

def quick_sort(values):
    if len(values) <= 1:
        return values
    pivot = values[len(values) // 2]
    smaller = [x for x in values if x < pivot]
    equal = [x for x in values if x == pivot]
    larger = [x for x in values if x > pivot]
    return quick_sort(smaller) + equal + quick_sort(larger)

data = list(map(int, sys.stdin.buffer.read().split()))
result = quick_sort(data)
print(len(result), sum(result))
