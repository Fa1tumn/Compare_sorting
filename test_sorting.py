import itertools
import random
import unittest
from dataclasses import dataclass

from sorting import ALGORITHMS


@dataclass
class Record:
    key: int
    original: int

    def __lt__(self, other):
        return self.key < other.key


class SortingTests(unittest.TestCase):
    def test_edge_cases(self):
        cases = [[], [1], [2, 1], [1, 2], [3] * 50, [-5, 0, -5, 8],
                 list(range(100)), list(range(100, -1, -1))]
        for name, sort in ALGORITHMS.items():
            for values in cases:
                with self.subTest(algorithm=name, values=values):
                    actual = values.copy()
                    sort(actual)
                    self.assertEqual(actual, sorted(values))

    def test_exhaustive_small_inputs(self):
        for n in range(7):
            for values in itertools.product((-1, 0, 1), repeat=n):
                for name, sort in ALGORITHMS.items():
                    actual = list(values)
                    sort(actual)
                    self.assertEqual(actual, sorted(values), name)

    def test_random_inputs(self):
        rng = random.Random(20260929)
        for _ in range(100):
            values = [rng.randint(-1000, 1000) for _ in range(rng.randrange(301))]
            for name, sort in ALGORITHMS.items():
                actual = values.copy()
                sort(actual)
                self.assertEqual(actual, sorted(values), name)

    def test_stability(self):
        values = [Record(i % 4, i) for i in range(60)]
        expected = sorted(values, key=lambda x: x.key)
        for name in ("insertion", "merge"):
            actual = values.copy()
            ALGORITHMS[name](actual)
            self.assertEqual(actual, expected)

    def test_heap_instability_witness(self):
        values = [Record(2, 0), Record(2, 1), Record(1, 2)]
        ALGORITHMS["heap"](values)
        self.assertEqual([x.key for x in values], [1, 2, 2])
        self.assertEqual([x.original for x in values if x.key == 2], [1, 0])


if __name__ == "__main__":
    unittest.main()
