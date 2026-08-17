"""
deadlock_detection.py

A simple deadlock detector based on a Resource-Allocation Graph (RAG),
simplified to single-instance resources (each resource is held by at
most one process at a time).

Model
-----
- `allocation`: dict mapping process id -> list of resource ids it
  currently HOLDS.
- `request`:    dict mapping process id -> list of resource ids it is
  currently WAITING to acquire.

From this we build a "wait-for graph": a directed edge  Pi -> Pj  means
"process Pi is waiting for a resource that process Pj currently holds".
A deadlock exists (under the single-instance assumption) if and only if
this wait-for graph contains a cycle. This matches the standard OS
theorem: for single-instance resource types, a cycle in the resource
allocation graph is both necessary and sufficient for deadlock.

The cycle is found with a depth-first search that colors each node
WHITE (unvisited), GRAY (on the current DFS path / "in progress"), or
BLACK (fully explored). Finding an edge into a GRAY node means we have
looped back onto our own current path, i.e. a cycle -- exactly the
processes on that cycle are reported as deadlocked.

Run it directly:

    python deadlock_detection.py
"""

from typing import Dict, List, Optional


WHITE, GRAY, BLACK = 0, 1, 2


def build_wait_for_graph(
    allocation: Dict[str, List[str]], request: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    """Build a wait-for graph: graph[p] is the list of processes that p is
    waiting on, derived from who currently holds the resource(s) p wants.
    """
    # Figure out which process currently holds each resource.
    resource_holder: Dict[str, str] = {}
    for process, held_resources in allocation.items():
        for resource in held_resources:
            resource_holder[resource] = process

    # Every process that appears anywhere (holding or requesting) gets a
    # node in the graph, even if it has no outgoing edges.
    graph: Dict[str, List[str]] = {p: [] for p in allocation}
    for p in request:
        graph.setdefault(p, [])

    for process, requested_resources in request.items():
        for resource in requested_resources:
            holder = resource_holder.get(resource)
            if holder is not None and holder != process:
                graph[process].append(holder)

    return graph


def find_cycle(graph: Dict[str, List[str]]) -> Optional[List[str]]:
    """Depth-first search for a cycle in `graph`.

    Returns the list of process ids that make up a cycle (in order,
    e.g. [P1, P2, P3] meaning P1 -> P2 -> P3 -> P1), or None if the
    graph is acyclic (no deadlock).
    """
    color = {node: WHITE for node in graph}
    path: List[str] = []
    cycle_found: List[Optional[List[str]]] = [None]

    def dfs(node: str) -> None:
        if cycle_found[0] is not None:
            return

        color[node] = GRAY
        path.append(node)

        for neighbor in graph.get(node, []):
            if cycle_found[0] is not None:
                break
            if color.get(neighbor, WHITE) == WHITE:
                dfs(neighbor)
            elif color[neighbor] == GRAY:
                # `neighbor` is an ancestor on the current path -> cycle.
                start_index = path.index(neighbor)
                cycle_found[0] = path[start_index:]

        path.pop()
        if color[node] == GRAY:
            color[node] = BLACK

    for node in graph:
        if color[node] == WHITE and cycle_found[0] is None:
            dfs(node)

    return cycle_found[0]


def detect_deadlock(
    allocation: Dict[str, List[str]], request: Dict[str, List[str]]
):
    """Returns (is_deadlocked, cycle_processes, wait_for_graph)."""
    graph = build_wait_for_graph(allocation, request)
    cycle = find_cycle(graph)
    return cycle is not None, cycle, graph


def print_report(title: str, allocation: Dict[str, List[str]], request: Dict[str, List[str]]) -> None:
    print(f"\n=== {title} ===")
    print("Allocation (process -> resources held):")
    for p, resources in allocation.items():
        print(f"  {p}: {resources}")
    print("Request (process -> resources requested):")
    for p, resources in request.items():
        print(f"  {p}: {resources}")

    is_deadlocked, cycle, graph = detect_deadlock(allocation, request)

    print("Wait-for graph (process -> processes it waits on):")
    for p, waits_on in graph.items():
        print(f"  {p} -> {waits_on}")

    if is_deadlocked:
        cycle_display = " -> ".join(cycle + [cycle[0]])
        print(f"RESULT: Deadlock detected. Cycle: {cycle_display}")
        print(f"Processes involved: {sorted(cycle)}")
    else:
        print("RESULT: No deadlock detected (wait-for graph is acyclic).")


def main():
    # ------------------------------------------------------------------
    # Example 1: deadlocked. P1 holds R1 and wants R2 (held by P2); P2
    # holds R2 and wants R3 (held by P3); P3 holds R3 and wants R1 (held
    # by P1). This forms the cycle P1 -> P2 -> P3 -> P1.
    # ------------------------------------------------------------------
    allocation_deadlock = {
        "P1": ["R1"],
        "P2": ["R2"],
        "P3": ["R3"],
    }
    request_deadlock = {
        "P1": ["R2"],
        "P2": ["R3"],
        "P3": ["R1"],
    }
    print_report("Example 1: Deadlocked system", allocation_deadlock, request_deadlock)

    # ------------------------------------------------------------------
    # Example 2: not deadlocked. Same holdings, but P3 is not requesting
    # anything, so the chain P1 -> P2 -> P3 has nowhere to loop back to.
    # ------------------------------------------------------------------
    allocation_ok = {
        "P1": ["R1"],
        "P2": ["R2"],
        "P3": ["R3"],
    }
    request_ok = {
        "P1": ["R2"],
        "P2": ["R3"],
        "P3": [],
    }
    print_report("Example 2: Non-deadlocked system", allocation_ok, request_ok)


if __name__ == "__main__":
    main()
