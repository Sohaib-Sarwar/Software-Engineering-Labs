"""
knn_classifier.py

A K-Nearest-Neighbors (KNN) classifier implemented entirely from scratch
using the Python standard library (no scikit-learn, no numpy).

KNN is a supervised, instance-based classification algorithm:
    - Training is "lazy": it just stores the labeled examples.
    - To classify a new point, it computes the distance from that point
      to every stored training example, finds the K closest ones, and
      predicts the majority class label among those K neighbors.

This file defines a small synthetic 2D labeled dataset (two visually
separable classes plus a bit of overlap), splits it into a training set
and a held-out test set, trains the classifier, and prints its accuracy
on the held-out split.
"""

import math
import random
from collections import Counter


# ---------------------------------------------------------------------------
# Synthetic 2D labeled dataset
# ---------------------------------------------------------------------------
# Each entry is (x, y, label). Two classes: "A" clustered around (2, 2) and
# "B" clustered around (8, 8), with a handful of points that overlap the
# boundary to make the problem non-trivial.
DATASET = [
    # Class A - clustered near (2, 2)
    (1.0, 1.5, "A"), (1.5, 2.0, "A"), (2.0, 1.0, "A"), (2.5, 2.5, "A"),
    (1.0, 3.0, "A"), (3.0, 1.5, "A"), (2.0, 2.5, "A"), (1.5, 1.0, "A"),
    (2.5, 1.5, "A"), (0.5, 2.0, "A"), (3.0, 3.0, "A"), (2.0, 0.5, "A"),

    # Class B - clustered near (8, 8)
    (8.0, 8.5, "B"), (8.5, 7.5, "B"), (7.5, 8.0, "B"), (9.0, 9.0, "B"),
    (8.0, 7.0, "B"), (7.0, 8.5, "B"), (9.0, 8.0, "B"), (8.5, 9.0, "B"),
    (7.5, 7.0, "B"), (9.5, 8.5, "B"), (8.0, 9.5, "B"), (7.0, 7.5, "B"),

    # A few boundary/overlap points to make the task a bit harder.
    (4.5, 4.5, "A"), (5.0, 5.5, "B"), (4.0, 5.0, "A"), (5.5, 4.5, "B"),
]


# ---------------------------------------------------------------------------
# Core KNN implementation
# ---------------------------------------------------------------------------
def euclidean_distance(point_a, point_b):
    """Euclidean distance between two equal-length numeric tuples."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(point_a, point_b)))


class KNNClassifier:
    """
    A from-scratch K-Nearest-Neighbors classifier.

    Args:
        k: number of neighbors to consult when predicting a label.
    """

    def __init__(self, k=3):
        if k < 1:
            raise ValueError("k must be a positive integer.")
        self.k = k
        self._features = []
        self._labels = []

    def fit(self, features, labels):
        """
        Store the training data. `features` is a list of numeric tuples
        (e.g. (x, y)) and `labels` is a parallel list of class labels.
        """
        if len(features) != len(labels):
            raise ValueError("features and labels must be the same length.")
        if len(features) < self.k:
            raise ValueError(
                f"Need at least k={self.k} training examples, got {len(features)}."
            )
        self._features = list(features)
        self._labels = list(labels)

    def _predict_one(self, point):
        distances = [
            (euclidean_distance(point, train_point), label)
            for train_point, label in zip(self._features, self._labels)
        ]
        distances.sort(key=lambda pair: pair[0])
        k_nearest_labels = [label for _, label in distances[:self.k]]
        vote_counts = Counter(k_nearest_labels)
        top_count = max(vote_counts.values())
        # Deterministic tie-break: prefer the label that appears first
        # among the k nearest neighbors (i.e. the closest tied class).
        for label in k_nearest_labels:
            if vote_counts[label] == top_count:
                return label
        return k_nearest_labels[0]

    def predict(self, points):
        """Predict class labels for a list of query points."""
        return [self._predict_one(point) for point in points]


def accuracy_score(true_labels, predicted_labels):
    """Fraction of predictions that exactly match the true labels."""
    if not true_labels:
        return 0.0
    correct = sum(1 for t, p in zip(true_labels, predicted_labels) if t == p)
    return correct / len(true_labels)


def train_test_split(features, labels, test_ratio=0.3, seed=42):
    """
    Shuffle (features, labels) together with a fixed seed and split them
    into a training set and a held-out test set.
    """
    combined = list(zip(features, labels))
    rng = random.Random(seed)
    rng.shuffle(combined)

    n_test = max(1, int(round(len(combined) * test_ratio)))
    test_part = combined[:n_test]
    train_part = combined[n_test:]

    train_features, train_labels = zip(*train_part)
    test_features, test_labels = zip(*test_part)
    return (list(train_features), list(train_labels),
            list(test_features), list(test_labels))


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    features = [(x, y) for x, y, _ in DATASET]
    labels = [label for _, _, label in DATASET]

    train_x, train_y, test_x, test_y = train_test_split(
        features, labels, test_ratio=0.3, seed=42
    )

    print("=" * 60)
    print("K-NEAREST-NEIGHBORS (KNN) CLASSIFIER DEMO (pure Python)")
    print("=" * 60)
    print(f"Total examples : {len(features)}")
    print(f"Training set   : {len(train_x)} examples")
    print(f"Held-out set   : {len(test_x)} examples")

    k = 3
    model = KNNClassifier(k=k)
    model.fit(train_x, train_y)
    predictions = model.predict(test_x)

    print(f"\nUsing k = {k}")
    print("-" * 60)
    print(f"{'point':>16} | {'true label':>10} | {'predicted':>10}")
    print("-" * 60)
    for point, true_label, predicted_label in zip(test_x, test_y, predictions):
        point_str = f"({point[0]:.1f}, {point[1]:.1f})"
        print(f"{point_str:>16} | {true_label:>10} | {predicted_label:>10}")

    acc = accuracy_score(test_y, predictions)
    print("-" * 60)
    print(f"Accuracy on held-out test set: {acc * 100:.1f}% "
          f"({sum(1 for t, p in zip(test_y, predictions) if t == p)}/{len(test_y)} correct)")
