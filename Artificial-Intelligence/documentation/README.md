# Artificial Intelligence Lab: Classical Machine Learning from Scratch

This lab contains three small, self-contained Python programs that
implement classical machine learning techniques **from scratch**, using
only the Python standard library (no `pandas`, no `numpy`, no
`scikit-learn`). The goal is to make the underlying mechanics of each
algorithm fully visible in the code, rather than hiding them behind a
library call.

```
Artificial-Intelligence/
├── source/
│   ├── data_preprocessing.py   # normalization, standardization, imputation
│   ├── knn_classifier.py       # K-Nearest-Neighbors classifier
│   └── kmeans_clustering.py    # K-Means clustering
└── documentation/
    └── README.md                # this file
```

---

## 1. The machine learning workflow

Every supervised learning script in this lab follows the same general
pipeline:

```
  Raw data  --->  Preprocessing  --->  Training  --->  Evaluation
 (messy,        (clean & scale       (fit model      (measure how
  incomplete)    the features)        on examples)     well it works)
```

1. **Preprocessing** (`data_preprocessing.py`)
   Real-world data is rarely ready to feed straight into a model. Before
   training, it is common to:
   - Fill in missing values (**imputation**), so the algorithm doesn't
     crash on `None` / empty fields.
   - Rescale numeric features (**normalization** / **standardization**),
     so that features on very different scales (e.g. "age" in years vs.
     "income" in dollars) don't unfairly dominate distance-based
     algorithms.

2. **Training**
   - `knn_classifier.py` performs *supervised* training: it is given
     labeled examples `(features, label)` and simply memorizes them
     (KNN has no explicit "learning" phase — see below).
   - `kmeans_clustering.py` performs *unsupervised* training: it is
     given only feature vectors (no labels) and discovers structure
     (groupings) in the data on its own.

3. **Evaluation**
   - For the supervised KNN classifier, the labeled data is split into
     a training set and a held-out test set. The model is trained on
     the training set only, then asked to predict labels for the test
     set, and its predictions are compared against the true labels
     using **accuracy**.
   - For the unsupervised K-Means algorithm there are no ground-truth
     labels to check against, so the script instead reports the final
     centroids, the cluster assigned to every point, and the
     **inertia** (sum of squared distances from each point to its
     assigned centroid) as a measure of how tight the clusters are.

---

## 2. `data_preprocessing.py` — cleaning and scaling data

This script works on a small dataset of "student" records, represented
as a plain Python `list` of `dict`s (no external library needed):

```python
{"name": "Bob", "age": 25, "study_hours": None, "grade": "B"}
```

It demonstrates three techniques:

- **Missing-value imputation** — `impute_missing_values(...)`
  - Numeric fields (e.g. `age`, `study_hours`) with a missing value
    (`None`) are filled in with the **mean** of that column, computed
    from the other rows.
  - Categorical fields (e.g. `grade`) with a missing value are filled
    in with the **mode** (most frequent value) of that column.

- **Min-max normalization** — `min_max_normalize(...)`
  Rescales every numeric value into the `[0, 1]` range:
  `x' = (x - min) / (max - min)`.
  Useful when you want all features bounded to the same fixed range.

- **Z-score standardization** — `z_score_standardize(...)`
  Rescales every numeric value to have mean `0` and standard deviation
  `1`: `x' = (x - mean) / std`.
  Useful when a feature's distribution matters more than its absolute
  range, and is generally more robust to outliers than min-max scaling.

Running the file prints the dataset **before** any processing, then
**after** imputation, then **after** min-max normalization, and finally
**after** z-score standardization, so you can see exactly what each
step changes.

### How to run

```bash
python3 source/data_preprocessing.py
```

(No installation step is required — everything used is part of the
Python standard library: `collections`, `copy`, `math`.)

---

## 3. `knn_classifier.py` — K-Nearest-Neighbors (classification)

**What KNN is used for:** *classification* — predicting a discrete
class label (e.g. "A" vs. "B") for a new, unseen data point, based on
labeled training examples.

**How it works:**
1. *"Training"* is trivial: the algorithm just stores every labeled
   training example. There is no weight-fitting step (this is why KNN
   is called a *lazy* / *instance-based* learner).
2. To classify a new point, it computes the **Euclidean distance**
   between that point and every stored training example.
3. It looks at the `k` closest training examples (the "nearest
   neighbors").
4. It predicts the **majority class** (most common label) among those
   `k` neighbors — this is the "majority vote".

The script defines a small synthetic 2D dataset with two roughly
separable classes ("A" clustered near `(2, 2)`, "B" clustered near
`(8, 8)`), plus a few overlapping boundary points to make the task
non-trivial. It:

1. Shuffles the data with a fixed random seed and splits it into a
   training set (~70%) and a held-out test set (~30%) via
   `train_test_split(...)`.
2. Fits a `KNNClassifier(k=3)` on the training set.
3. Predicts labels for the held-out test set.
4. Prints a per-point table of true vs. predicted labels, and the
   overall **accuracy** on the held-out set.

### How to run

```bash
python3 source/knn_classifier.py
```

(Standard library only: `math`, `random`, `collections`.)

---

## 4. `kmeans_clustering.py` — K-Means (clustering)

**What K-Means is used for:** *clustering* — grouping **unlabeled**
data points into `k` clusters based purely on how close they are to
each other in feature space. Unlike KNN, there are no "correct labels"
to learn from; the algorithm discovers structure on its own.

**How it works (assign/update loop):**
1. **Initialize:** pick `k` initial centroids by randomly sampling `k`
   points from the dataset itself.
2. **Assign step:** assign every data point to its nearest centroid
   (by Euclidean distance).
3. **Update step:** recompute each centroid as the mean position of all
   points currently assigned to it.
4. **Repeat** steps 2–3 until the assignments stop changing between
   iterations (**convergence**) or a maximum number of iterations is
   reached (a safety cap, in case of oscillation).

The script defines a small synthetic 2D dataset made of three visually
separable "blobs" of points, runs `kmeans(DATASET, k=3, ...)`, and
prints:
- the number of iterations it took to converge,
- the final centroid coordinates for each of the 3 clusters,
- the cluster assignment for every individual point,
- the cluster sizes, and
- the final **inertia** (sum of squared distances from each point to
  its assigned centroid — lower means tighter, more compact clusters).

### How to run

```bash
python3 source/kmeans_clustering.py
```

(Standard library only: `math`, `random`.)

---

## 5. The evaluation metric: accuracy, and its limitations

The KNN script reports **accuracy**:

```
accuracy = (number of correct predictions) / (total number of predictions)
```

Accuracy is simple, intuitive, and appropriate for this lab's balanced,
roughly-equal-sized two-class synthetic dataset. However, it has
well-known limitations that are important to understand when applying
it to real-world problems:

- **Misleading on imbalanced data.** If 95% of examples belong to one
  class, a model that *always* predicts that class scores 95% accuracy
  while being useless — it never correctly identifies the minority
  class.
- **No insight into *type* of error.** Accuracy treats all mistakes
  equally. It cannot distinguish a false positive from a false
  negative, which matters a great deal in domains like medical
  diagnosis or fraud detection where the two error types have very
  different costs.
- **No confidence information.** Accuracy is computed from hard
  class predictions only; it ignores how *confident* or *close* a
  prediction was.
- **Sensitive to the specific test split.** With a small dataset (as
  used here), accuracy can shift noticeably depending on which points
  happen to land in the test set — this is why real projects typically
  use cross-validation across many different splits rather than a
  single train/test split.

For imbalanced or high-stakes problems, complementary metrics such as
**precision**, **recall**, **F1-score**, or a full **confusion matrix**
give a much more complete picture than accuracy alone. K-Means, being
unsupervised, cannot use accuracy at all (there are no true labels to
compare against) — instead it is typically evaluated with metrics like
**inertia** (used here) or the **silhouette score**, which measure
cluster compactness and separation rather than correctness against
ground truth.

---

## 6. Running everything

No installation or virtual environment is required — every script uses
only the Python 3 standard library. From the `Artificial-Intelligence`
directory, simply run:

```bash
python3 source/data_preprocessing.py
python3 source/knn_classifier.py
python3 source/kmeans_clustering.py
```

Each script is fully self-contained (dataset included in the file) and
prints its results directly to the console.
