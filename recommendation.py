import numpy as np
from operator import itemgetter

from bot_data import data, movie_titles, tracks, data_music


class KNN:
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
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def fit(self):
        self.distances.extend(
            [(self.dist(self.test_point, point), i) for point, i in zip(self.data, range(len(self.data)))])

        sorted_distances = sorted(self.distances, key=itemgetter(0))

        self.indices.extend([index for (val, index) in sorted_distances[:self.k]])

        for i in self.indices:
            self.categories.append(self.target[i])

        self.counts.extend([(i, self.categories.count(i)) for i in set(self.categories)])

        self.category_assigned = sorted(self.counts, key=itemgetter(1), reverse=True)[0][0]


def recommender(test_point, k, data, target_items, model_class, get_item_info):
    target = [0 for _ in range(len(target_items))]

    model = model_class(data, target, test_point, k=k)
    model.fit()

    table = []
    for i in model.indices:
        table.append(get_item_info(target_items[i], data[i]))

    return table


def movie_recommender(test_point, k):
    return recommender(test_point, k, data, movie_titles, KNN,
                       lambda movie, data_point: [movie[0], movie[2], data_point[-1]])


def music_recommendation(test_point, k):
    return recommender(test_point, k, data_music, tracks, KNN, lambda track, _: track)
