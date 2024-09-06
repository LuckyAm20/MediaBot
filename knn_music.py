import numpy as np
from operator import itemgetter
import json


class KNN_Class:
    def __init__(self, data, target, test_point, k):
        self.data = data
        self.target = target
        self.test_point = test_point
        self.k = k
        self.distances = list()
        self.categories = list()
        self.indices = list()
        self.counts = list()
        self.category_assigned = None

    @staticmethod
    def dist(p1, p2):
        """Calculate the Euclidean distance between two points."""
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def fit(self):
        """
        Perform the KNN classification.

        Algorithm Steps:
        1. Calculate distances from the test_point to each point in the data.
        2. Sort distances in ascending order.
        3. Fetch indices of the k nearest points from the data.
        4. Fetch categories from the target data corresponding to the nearest indices.
        5. Count occurrences of each category among the k nearest neighbors.
        6. Determine the most frequently occurring category among the k neighbors.
        """
        # Step 1: Calculate distances from test_point to each point in the data
        self.distances.extend([(self.dist(self.test_point, point), i) for point, i in
                               zip(self.data, range(len(self.data)))])
        # Step 2: Sort the distances in ascending order
        sorted_distances = sorted(self.distances, key=itemgetter(0))
        # Step 3: Fetch the indices of the k nearest points from the data
        self.indices.extend([index for (val, index) in sorted_distances[:self.k]])
        # Step 4: Fetch categories from the target data corresponding to the nearest indices
        for i in self.indices:
            self.categories.append(self.target[i])
        # Step 5: Count occurrences of each category among the k nearest neighbors
        self.counts.extend([(i, self.categories.count(i)) for i in set(self.categories)])
        # Step 6: Determine the most frequently occurring category among the k neighbors
        self.category_assigned = sorted(self.counts, key=itemgetter(1), reverse=True)[0][0]
