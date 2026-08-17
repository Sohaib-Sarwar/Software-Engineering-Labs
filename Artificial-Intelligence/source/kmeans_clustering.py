"""
kmeans_clustering.py

A from-scratch implementation of the K-Means clustering algorithm using
only the Python standard library (no scikit-learn, no numpy).

K-Means is an unsupervised algorithm: unlike KNN, the data points here
have no labels at all. The algorithm groups points into `k` clusters
purely from their positions in feature space:

    1. Pick k initial centroids at random from the data points.
    2. Assign step: assign every point to its nearest centroid
       (by Euclidean distance).
    3. Update step: recompute each centroid as the mean of the points
       assigned to it.
    4. Repeat steps 2-3 until the assignments stop changing (convergence)
       or a maximum number of iterations is reached.

This file defines a small synthetic 2D dataset with three visually
separable blobs, runs k-means with k=3, and prints the final centroids
and the cluster assignment for every point.
"""

import math
import random


# ---------------------------------------------------------------------------
# Synthetic 2D dataset: three roughly separable blobs.
# ---------------------------------------------------------------------------
DATASET = [
    # Blob 1 - near (2, 2)
    (1.0, 2.0), (2.0, 1.5), (1.5, 1.0), (2.5, 2.5), (1.0, 1.0),
    (2.0, 2.5), (1.5, 2.5), (2.5, 1.0),

    # Blob 2 - near (8, 3)
    (8.0, 3.0), (7.5, 2.5), (8.5, 3.5), (7.0, 3.0), (8.0, 2.0),
    (8.5, 2.5), (7.5, 3.5), (8.0, 4.0),

    # Blob 3 - near (4, 8)
    (4.0, 8.0), (3.5, 7.5), (4.5, 8.5), (3.0, 8.0), (4.0, 7.0),
    (4.5, 7.5), (3.5, 8.5), (4.0, 9.0),
]


# ---------------------------------------------------------------------------
# Core K-Means implementation
# ---------------------------------------------------------------------------
def euclidean_distance(point_a, point_b):
    """Euclidean distance between two equal-length numeric tuples."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(point_a, point_b)))


def _mean_point(points):
    """Component-wise mean of a non-empty list of equal-length tuples."""
    dims = len(points[0])
    n = len(points)
    return tuple(sum(p[d] for p in points) / n for d in range(dims))


def _nearest_centroid_index(point, centroids):
    """Index of the centroid closest to `point`."""
    distances = [euclidean_distance(point, c) for c in centroids]
    return distances.index(min(distances))


def initialize_centroids(data, k, seed=None):
    """
    Choose k distinct initial centroids by sampling without replacement
    from the data points themselves (a common, simple K-Means++-free
    initialization strategy).
    """
    if k > len(data):
        raise ValueError("k cannot exceed the number of data points.")
    rng = random.Random(seed)
    return [tuple(p) for p in rng.sample(data, k)]


def kmeans(data, k, max_iterations=100, seed=None):
    """
    Run the K-Means clustering algorithm.

    Args:
        data: list of numeric tuples (points).
        k: number of clusters to form.
        max_iterations: safety cap on the number of assign/update rounds.
        seed: random seed for reproducible centroid initialization.

    Returns:
        A tuple (centroids, assignments, n_iterations) where:
            centroids   -- list of k final centroid tuples.
            assignments -- list, same length as `data`, giving the
                           cluster index (0..k-1) assigned to each point.
            n_iterations -- number of assign/update rounds actually run.
    """
    if k < 1:
        raise ValueError("k must be a positive integer.")
    if not data:
        raise ValueError("data must be non-empty.")

    centroids = initialize_centroids(data, k, seed=seed)
    assignments = [None] * len(data)

    for iteration in range(1, max_iterations + 1):
        # --- Assign step ---
        new_assignments = [_nearest_centroid_index(p, centroids) for p in data]

        # --- Update step ---
        new_centroids = []
        for cluster_idx in range(k):
            members = [p for p, a in zip(data, new_assignments) if a == cluster_idx]
            if members:
                new_centroids.append(_mean_point(members))
            else:
                # Empty cluster: keep its previous centroid unchanged so
                # k-means doesn't lose a centroid entirely.
                new_centroids.append(centroids[cluster_idx])

        converged = (new_assignments == assignments)
        assignments = new_assignments
        centroids = new_centroids

        if converged:
            return centroids, assignments, iteration

    return centroids, assignments, max_iterations


def inertia(data, centroids, assignments):
    """
    Sum of squared distances of each point to its assigned centroid
    (a common measure of cluster compactness -- lower is tighter).
    """
    total = 0.0
    for point, cluster_idx in zip(data, assignments):
        total += euclidean_distance(point, centroids[cluster_idx]) ** 2
    return total


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    k = 3
    seed = 7

    print("=" * 60)
    print("K-MEANS CLUSTERING DEMO (pure Python, no numpy)")
    print("=" * 60)
    print(f"Number of points : {len(DATASET)}")
    print(f"k (clusters)     : {k}")

    centroids, assignments, n_iterations = kmeans(
        DATASET, k=k, max_iterations=100, seed=seed
    )

    print(f"Converged after  : {n_iterations} iteration(s)")

    print("\nFinal centroids:")
    for idx, c in enumerate(centroids):
        print(f"  Cluster {idx}: ({c[0]:.3f}, {c[1]:.3f})")

    print("\nCluster assignments:")
    print(f"{'point':>16} | {'cluster':>8}")
    print("-" * 30)
    for point, cluster_idx in zip(DATASET, assignments):
        point_str = f"({point[0]:.1f}, {point[1]:.1f})"
        print(f"{point_str:>16} | {cluster_idx:>8}")

    print("\nCluster sizes:")
    for idx in range(k):
        size = assignments.count(idx)
        print(f"  Cluster {idx}: {size} point(s)")

    print(f"\nFinal inertia (sum of squared distances to assigned centroid): "
          f"{inertia(DATASET, centroids, assignments):.3f}")
