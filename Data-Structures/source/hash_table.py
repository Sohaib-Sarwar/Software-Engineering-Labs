"""
hash_table.py

A hash table implemented from scratch using separate chaining for collision
resolution. Storage is a fixed-size Python list of "buckets", where each
bucket is a small linked list of (key, value) pairs implemented internally
(no reliance on dict for the actual storage/lookup logic).

Concepts demonstrated:
- Hashing a key to a bucket index via Python's built-in hash() modulo the
  table's capacity.
- Separate chaining: each bucket holds a chain of entries; collisions
  (different keys, same bucket index) are resolved by appending to that
  bucket's chain and scanning it on lookup.
- Dynamic resizing: the table doubles its capacity and rehashes all
  entries once the load factor exceeds a threshold, keeping average-case
  operations close to O(1).
"""

from typing import Any, Iterator, List, Optional, Tuple


class KeyNotFoundError(KeyError):
    """Raised when get() or delete() is called with a key that is not present."""


class _Entry:
    __slots__ = ("key", "value", "next")

    def __init__(self, key: Any, value: Any, next_entry: Optional["_Entry"] = None) -> None:
        self.key = key
        self.value = value
        self.next = next_entry


class HashTable:
    """
    A hash table using separate chaining.

    `initial_capacity` sets the starting number of buckets.
    `max_load_factor` is the size/capacity ratio above which the table
    resizes (doubles) and rehashes all existing entries.
    """

    def __init__(self, initial_capacity: int = 8, max_load_factor: float = 0.75) -> None:
        if initial_capacity < 1:
            raise ValueError("initial_capacity must be at least 1")
        if max_load_factor <= 0:
            raise ValueError("max_load_factor must be positive")
        self._capacity = initial_capacity
        self._max_load_factor = max_load_factor
        self._buckets: List[Optional[_Entry]] = [None] * self._capacity
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def _bucket_index(self, key: Any, capacity: Optional[int] = None) -> int:
        cap = self._capacity if capacity is None else capacity
        return hash(key) % cap

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------
    def set(self, key: Any, value: Any) -> None:
        """
        Insert `key` with `value`, or overwrite the value if `key` already
        exists (duplicate keys do not create duplicate entries).
        """
        index = self._bucket_index(key)
        entry = self._buckets[index]
        while entry is not None:
            if entry.key == key:
                entry.value = value  # overwrite existing key
                return
            entry = entry.next

        # Key not found in its bucket's chain: prepend a new entry.
        self._buckets[index] = _Entry(key, value, next_entry=self._buckets[index])
        self._size += 1

        if self._load_factor() > self._max_load_factor:
            self._resize(self._capacity * 2)

    def get(self, key: Any, default: Any = KeyNotFoundError) -> Any:
        """
        Return the value stored for `key`.

        If `key` is absent: return `default` if one was supplied, otherwise
        raise KeyNotFoundError.
        """
        index = self._bucket_index(key)
        entry = self._buckets[index]
        while entry is not None:
            if entry.key == key:
                return entry.value
            entry = entry.next
        if default is KeyNotFoundError:
            raise KeyNotFoundError(key)
        return default

    def delete(self, key: Any) -> None:
        """
        Remove `key` (and its value) from the table.

        Raises KeyNotFoundError if `key` is not present.
        """
        index = self._bucket_index(key)
        entry = self._buckets[index]
        previous: Optional[_Entry] = None
        while entry is not None:
            if entry.key == key:
                if previous is None:
                    self._buckets[index] = entry.next
                else:
                    previous.next = entry.next
                self._size -= 1
                return
            previous = entry
            entry = entry.next
        raise KeyNotFoundError(key)

    def __contains__(self, key: Any) -> bool:
        index = self._bucket_index(key)
        entry = self._buckets[index]
        while entry is not None:
            if entry.key == key:
                return True
            entry = entry.next
        return False

    def __setitem__(self, key: Any, value: Any) -> None:
        self.set(key, value)

    def __getitem__(self, key: Any) -> Any:
        return self.get(key)

    def __delitem__(self, key: Any) -> None:
        self.delete(key)

    # ------------------------------------------------------------------
    # Resizing
    # ------------------------------------------------------------------
    def _load_factor(self) -> float:
        return self._size / self._capacity

    def _resize(self, new_capacity: int) -> None:
        old_items = list(self.items())
        self._capacity = new_capacity
        self._buckets = [None] * self._capacity
        self._size = 0
        for key, value in old_items:
            self.set(key, value)

    # ------------------------------------------------------------------
    # Iteration helpers
    # ------------------------------------------------------------------
    def keys(self) -> Iterator[Any]:
        for bucket in self._buckets:
            entry = bucket
            while entry is not None:
                yield entry.key
                entry = entry.next

    def values(self) -> Iterator[Any]:
        for bucket in self._buckets:
            entry = bucket
            while entry is not None:
                yield entry.value
                entry = entry.next

    def items(self) -> Iterator[Tuple[Any, Any]]:
        for bucket in self._buckets:
            entry = bucket
            while entry is not None:
                yield (entry.key, entry.value)
                entry = entry.next

    def __iter__(self) -> Iterator[Any]:
        return self.keys()

    def __repr__(self) -> str:
        pairs = ", ".join(f"{k!r}: {v!r}" for k, v in self.items())
        return f"HashTable({{{pairs}}})"


if __name__ == "__main__":
    table = HashTable(initial_capacity=4)
    table.set("apple", 1)
    table.set("banana", 2)
    table.set("cherry", 3)
    table.set("apple", 100)  # overwrite duplicate key
    print(table.get("apple"))  # 100
    print("banana" in table)  # True
    table.delete("banana")
    print("banana" in table)  # False
    print(sorted(table.items()))  # [('apple', 100), ('cherry', 3)]
