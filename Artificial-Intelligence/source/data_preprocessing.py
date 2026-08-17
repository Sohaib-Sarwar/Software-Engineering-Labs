"""
data_preprocessing.py

Pure-Python data preprocessing utilities for a small tabular dataset
represented as a list of dictionaries (one dict per row/record).

No third-party libraries (no pandas, no numpy) are required -- everything
here is built on the Python standard library so it can be run with a
plain `python3` interpreter.

Techniques demonstrated:
    1. Missing-value imputation
         - Numeric columns  -> mean imputation
         - Categorical (string) columns -> mode imputation
    2. Min-max normalization  (rescales numeric values to the [0, 1] range)
    3. Z-score standardization (rescales numeric values to mean 0, std 1)

A record is missing a value for a field when that field is either absent
from the dict or explicitly set to `None`.
"""

from collections import Counter
import copy
import math


# ---------------------------------------------------------------------------
# Sample dataset
# ---------------------------------------------------------------------------
# A small, intentionally messy dataset of "student" records with a couple of
# missing numeric values (None) and one missing categorical value (None).
SAMPLE_DATASET = [
    {"name": "Alice",   "age": 23, "study_hours": 5.0, "grade": "A"},
    {"name": "Bob",      "age": 25, "study_hours": None, "grade": "B"},
    {"name": "Charlie",  "age": None, "study_hours": 2.0, "grade": "B"},
    {"name": "Diana",    "age": 30, "study_hours": 8.0, "grade": "A"},
    {"name": "Ethan",    "age": 22, "study_hours": 1.5, "grade": None},
    {"name": "Fatima",   "age": 28, "study_hours": 6.5, "grade": "A"},
    {"name": "George",   "age": 35, "study_hours": None, "grade": "C"},
    {"name": "Hana",     "age": 19, "study_hours": 3.0, "grade": "B"},
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def _is_missing(value):
    """Return True if a value should be treated as missing."""
    return value is None


def _numeric_values(dataset, field):
    """Collect all non-missing numeric values for a field."""
    return [row[field] for row in dataset
            if field in row and not _is_missing(row[field])]


def _categorical_values(dataset, field):
    """Collect all non-missing categorical (string) values for a field."""
    return [row[field] for row in dataset
            if field in row and not _is_missing(row[field])]


def mean(values):
    """Arithmetic mean of a non-empty list of numbers."""
    if not values:
        raise ValueError("Cannot compute mean of an empty list.")
    return sum(values) / len(values)


def stdev(values):
    """Population standard deviation of a non-empty list of numbers."""
    if not values:
        raise ValueError("Cannot compute standard deviation of an empty list.")
    m = mean(values)
    variance = sum((v - m) ** 2 for v in values) / len(values)
    return math.sqrt(variance)


def mode(values):
    """Most frequently occurring value in a non-empty list."""
    if not values:
        raise ValueError("Cannot compute mode of an empty list.")
    counts = Counter(values)
    top_count = max(counts.values())
    # Ties broken by first-seen order for determinism.
    for v in values:
        if counts[v] == top_count:
            return v
    return values[0]


# ---------------------------------------------------------------------------
# 1. Missing-value imputation
# ---------------------------------------------------------------------------
def impute_missing_values(dataset, numeric_fields, categorical_fields):
    """
    Return a deep copy of `dataset` with missing values filled in.

    Numeric fields are imputed with the column mean (computed over the
    non-missing values). Categorical fields are imputed with the column
    mode (the most common non-missing value).

    Args:
        dataset: list of dict records.
        numeric_fields: list of field names to treat as numeric.
        categorical_fields: list of field names to treat as categorical.

    Returns:
        A new list of dict records with no missing values in the given
        fields.
    """
    result = copy.deepcopy(dataset)

    # Pre-compute fill values once per field.
    numeric_fill = {}
    for field in numeric_fields:
        values = _numeric_values(dataset, field)
        numeric_fill[field] = mean(values) if values else 0.0

    categorical_fill = {}
    for field in categorical_fields:
        values = _categorical_values(dataset, field)
        categorical_fill[field] = mode(values) if values else ""

    for row in result:
        for field in numeric_fields:
            if field not in row or _is_missing(row[field]):
                row[field] = numeric_fill[field]
        for field in categorical_fields:
            if field not in row or _is_missing(row[field]):
                row[field] = categorical_fill[field]

    return result


# ---------------------------------------------------------------------------
# 2. Min-max normalization
# ---------------------------------------------------------------------------
def min_max_normalize(dataset, numeric_fields):
    """
    Return a deep copy of `dataset` where each numeric field is rescaled
    to the [0, 1] range using min-max normalization:

        x' = (x - min) / (max - min)

    If a field has zero variance (max == min), every value is mapped to
    0.0 to avoid division by zero.

    Assumes the dataset has already been imputed (no missing values in
    `numeric_fields`); raises ValueError otherwise.
    """
    result = copy.deepcopy(dataset)

    stats = {}
    for field in numeric_fields:
        values = [row[field] for row in dataset]
        if any(_is_missing(v) for v in values):
            raise ValueError(
                f"Field '{field}' contains missing values; "
                "impute before normalizing."
            )
        stats[field] = (min(values), max(values))

    for row in result:
        for field in numeric_fields:
            lo, hi = stats[field]
            if hi == lo:
                row[field] = 0.0
            else:
                row[field] = (row[field] - lo) / (hi - lo)

    return result


# ---------------------------------------------------------------------------
# 3. Z-score standardization
# ---------------------------------------------------------------------------
def z_score_standardize(dataset, numeric_fields):
    """
    Return a deep copy of `dataset` where each numeric field is rescaled
    to have mean 0 and standard deviation 1:

        x' = (x - mean) / std

    If a field has zero standard deviation, every value is mapped to 0.0
    to avoid division by zero.

    Assumes the dataset has already been imputed (no missing values in
    `numeric_fields`); raises ValueError otherwise.
    """
    result = copy.deepcopy(dataset)

    stats = {}
    for field in numeric_fields:
        values = [row[field] for row in dataset]
        if any(_is_missing(v) for v in values):
            raise ValueError(
                f"Field '{field}' contains missing values; "
                "impute before standardizing."
            )
        stats[field] = (mean(values), stdev(values))

    for row in result:
        for field in numeric_fields:
            m, s = stats[field]
            if s == 0:
                row[field] = 0.0
            else:
                row[field] = (row[field] - m) / s

    return result


# ---------------------------------------------------------------------------
# Pretty-printing helper (used only by the demo below)
# ---------------------------------------------------------------------------
def _print_table(dataset, fields, title):
    print(f"\n{title}")
    print("-" * len(title))
    header = " | ".join(f"{f:>12}" for f in fields)
    print(header)
    print("-" * len(header))
    for row in dataset:
        cells = []
        for f in fields:
            value = row.get(f)
            if isinstance(value, float):
                cells.append(f"{value:12.3f}")
            else:
                cells.append(f"{str(value):>12}")
        print(" | ".join(cells))


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    numeric_fields = ["age", "study_hours"]
    categorical_fields = ["grade"]
    display_fields = ["name", "age", "study_hours", "grade"]

    print("=" * 60)
    print("DATA PREPROCESSING DEMO (pure Python, no pandas/numpy)")
    print("=" * 60)

    _print_table(SAMPLE_DATASET, display_fields, "BEFORE: raw dataset (with missing values)")

    # Step 1: impute missing values.
    imputed = impute_missing_values(SAMPLE_DATASET, numeric_fields, categorical_fields)
    _print_table(imputed, display_fields, "AFTER: mean/mode imputation")

    # Step 2: min-max normalize the numeric fields (on the imputed data).
    normalized = min_max_normalize(imputed, numeric_fields)
    _print_table(normalized, display_fields, "AFTER: min-max normalization ([0, 1] range)")

    # Step 3: z-score standardize the numeric fields (on the imputed data).
    standardized = z_score_standardize(imputed, numeric_fields)
    _print_table(standardized, display_fields, "AFTER: z-score standardization (mean 0, std 1)")

    print("\nSummary of column statistics used for scaling (from imputed data):")
    for field in numeric_fields:
        values = [row[field] for row in imputed]
        print(f"  {field}: min={min(values):.3f} max={max(values):.3f} "
              f"mean={mean(values):.3f} std={stdev(values):.3f}")
