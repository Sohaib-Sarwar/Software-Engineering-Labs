"""
graph.py

A graph implemented as an adjacency list, supporting both directed and
undirected edges, with breadth-first (BFS) and depth-first (DFS) traversals.

Concepts demonstrated:
- Adjacency-list representation (a dict mapping each vertex to the set of
  its neighbors), which is memory-efficient for sparse graphs.
- BFS using an explicit queue (level-by-level exploration).
- DFS using both a recursive and an explicit-stack iterative form.
- Cycle-safety: both traversals track a `visited` set so that a graph
  containing cycles (or an undirected edge, which is a 2-cycle) will not
  loop forever or revisit a vertex.
"""

from collections import deque
from typing import Any, Dict, Iterable, List, Optional, Set


class Graph:
    """
    A graph stored as an adjacency list.

    By default edges are undirected (add_edge(a, b) connects both ways).
    Pass directed=True to the constructor to store one-way edges instead.
    """

    def __init__(self, directed: bool = False) -> None:
        self._directed = directed
        self._adjacency: Dict[Any, Set[Any]] = {}

    @property
    def directed(self) -> bool:
        return self._directed

    def add_vertex(self, vertex: Any) -> None:
        """Ensure `vertex` exists in the graph, even if it has no edges yet."""
        self._adjacency.setdefault(vertex, set())

    def add_edge(self, source: Any, destination: Any) -> None:
        """
        Add an edge between `source` and `destination`.

        For an undirected graph (the default) this connects both
        directions. For a directed graph, only source -> destination is
        added. Both endpoints are added as vertices if not already present.
        """
        self.add_vertex(source)
        self.add_vertex(destination)
        self._adjacency[source].add(destination)
        if not self._directed:
            self._adjacency[destination].add(source)

    def neighbors(self, vertex: Any) -> Set[Any]:
        """Return the set of vertices directly reachable from `vertex`."""
        if vertex not in self._adjacency:
            raise KeyError(f"vertex {vertex!r} is not in the graph")
        return set(self._adjacency[vertex])

    def vertices(self) -> List[Any]:
        return list(self._adjacency.keys())

    def __contains__(self, vertex: Any) -> bool:
        return vertex in self._adjacency

    def __len__(self) -> int:
        return len(self._adjacency)

    # ------------------------------------------------------------------
    # Traversals
    # ------------------------------------------------------------------
    def bfs(self, start: Any) -> List[Any]:
        """
        Breadth-first traversal starting at `start`.

        Returns the list of vertices in the order they were first visited.
        Safe on graphs containing cycles: a `visited` set ensures each
        vertex is enqueued at most once.
        """
        if start not in self._adjacency:
            raise KeyError(f"start vertex {start!r} is not in the graph")

        visited: Set[Any] = {start}
        order: List[Any] = []
        queue: deque = deque([start])

        while queue:
            current = queue.popleft()
            order.append(current)
            for neighbor in sorted(self._adjacency[current], key=repr):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return order

    def dfs(self, start: Any) -> List[Any]:
        """
        Depth-first traversal starting at `start`, implemented iteratively
        with an explicit stack (avoids Python recursion-limit issues on
        deep/large graphs).

        Returns the list of vertices in the order they were first visited.
        Safe on graphs containing cycles: a `visited` set ensures each
        vertex is pushed and processed at most once.
        """
        if start not in self._adjacency:
            raise KeyError(f"start vertex {start!r} is not in the graph")

        visited: Set[Any] = set()
        order: List[Any] = []
        stack: List[Any] = [start]

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            order.append(current)
            # Push neighbors in reverse sorted order so that, when popped,
            # they are visited in ascending order (purely cosmetic, makes
            # output deterministic and easy to test).
            for neighbor in sorted(self._adjacency[current], key=repr, reverse=True):
                if neighbor not in visited:
                    stack.append(neighbor)
        return order

    def dfs_recursive(self, start: Any) -> List[Any]:
        """
        Depth-first traversal starting at `start`, implemented recursively.
        Provided alongside the iterative dfs() to demonstrate the recursive
        formulation; also cycle-safe via a shared `visited` set.
        """
        if start not in self._adjacency:
            raise KeyError(f"start vertex {start!r} is not in the graph")

        visited: Set[Any] = set()
        order: List[Any] = []

        def _visit(vertex: Any) -> None:
            visited.add(vertex)
            order.append(vertex)
            for neighbor in sorted(self._adjacency[vertex], key=repr):
                if neighbor not in visited:
                    _visit(neighbor)

        _visit(start)
        return order

    def __repr__(self) -> str:
        kind = "Directed" if self._directed else "Undirected"
        return f"{kind}Graph({self._adjacency!r})"


if __name__ == "__main__":
    g = Graph()
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    g.add_edge("B", "D")
    g.add_edge("C", "D")
    g.add_edge("D", "A")  # creates a cycle: A-B-D-A and A-C-D-A
    print("BFS:", g.bfs("A"))
    print("DFS:", g.dfs("A"))
    print("DFS (recursive):", g.dfs_recursive("A"))
