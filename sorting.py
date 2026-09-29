"""Three hand-written sorts that mutate their input; comparisons use only <."""


def insertion_sort(a):
    """Stable insertion sort: O(n) best, O(n^2) worst, O(1) extra space."""
    for i in range(1, len(a)):
        value = a[i]
        j = i - 1
        while j >= 0 and value < a[j]:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = value


def merge_sort(a):
    """Stable top-down merge sort, one O(n) buffer; no ordered-run shortcut."""
    buf = [None] * len(a)

    def sort(lo, hi):
        if hi - lo < 2:
            return
        mid = (lo + hi) // 2
        sort(lo, mid)
        sort(mid, hi)
        i, j = lo, mid
        for k in range(lo, hi):
            # On equal keys, take the left item to preserve original order.
            if i < mid and (j >= hi or not a[j] < a[i]):
                buf[k] = a[i]
                i += 1
            else:
                buf[k] = a[j]
                j += 1
        for k in range(lo, hi):
            a[k] = buf[k]

    sort(0, len(a))


def heap_sort(a):
    """Iterative max-heapsort: O(n log n) worst, O(1) extra space, unstable."""
    def sift_down(root, end):
        # end is exclusive; larger child is selected at every level.
        while 2 * root + 1 < end:
            child = 2 * root + 1
            if child + 1 < end and a[child] < a[child + 1]:
                child += 1
            if not a[root] < a[child]:
                break
            a[root], a[child] = a[child], a[root]
            root = child

    for root in range(len(a) // 2 - 1, -1, -1):
        sift_down(root, len(a))
    for end in range(len(a) - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift_down(0, end)


ALGORITHMS = {"insertion": insertion_sort, "merge": merge_sort, "heap": heap_sort}
