"""
cpu_scheduling.py

A small CPU scheduling simulator implementing three classic scheduling
algorithms over a fixed set of sample processes:

    1. FCFS (First-Come, First-Served)
    2. SJF  (Shortest Job First, non-preemptive)
    3. Round Robin (preemptive, fixed time quantum)

For each algorithm the script computes, per process:
    - completion time
    - turnaround time  = completion_time - arrival_time
    - waiting time      = turnaround_time - burst_time

...and prints a results table plus the average waiting time and average
turnaround time for that algorithm.

This file has no third-party dependencies; it only uses the Python
standard library.

Run it directly:

    python cpu_scheduling.py
"""

from copy import deepcopy
from collections import deque


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------
# Each process is a dict with: pid, arrival_time, burst_time.
# This exact list is referenced in documentation/README.md's worked example,
# so keep the two in sync if you ever change these values.
SAMPLE_PROCESSES = [
    {"pid": "P1", "arrival_time": 0, "burst_time": 5},
    {"pid": "P2", "arrival_time": 1, "burst_time": 3},
    {"pid": "P3", "arrival_time": 2, "burst_time": 8},
    {"pid": "P4", "arrival_time": 3, "burst_time": 6},
]

ROUND_ROBIN_QUANTUM = 4


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _finalize(results):
    """Given a list of dicts that already contain completion_time,
    arrival_time and burst_time, fill in turnaround_time and waiting_time,
    and return (results_sorted_by_pid, avg_waiting_time, avg_turnaround_time).
    """
    for r in results:
        r["turnaround_time"] = r["completion_time"] - r["arrival_time"]
        r["waiting_time"] = r["turnaround_time"] - r["burst_time"]

    results_sorted = sorted(results, key=lambda r: r["pid"])
    n = len(results_sorted)
    avg_wt = sum(r["waiting_time"] for r in results_sorted) / n
    avg_tat = sum(r["turnaround_time"] for r in results_sorted) / n
    return results_sorted, avg_wt, avg_tat


def print_results(algorithm_name, results, avg_wt, avg_tat):
    print(f"\n=== {algorithm_name} ===")
    header = f"{'PID':<6}{'Arrival':<10}{'Burst':<8}{'Completion':<12}{'Turnaround':<12}{'Waiting':<8}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(
            f"{r['pid']:<6}"
            f"{r['arrival_time']:<10}"
            f"{r['burst_time']:<8}"
            f"{r['completion_time']:<12}"
            f"{r['turnaround_time']:<12}"
            f"{r['waiting_time']:<8}"
        )
    print(f"\nAverage Waiting Time    : {avg_wt:.2f}")
    print(f"Average Turnaround Time : {avg_tat:.2f}")


# ---------------------------------------------------------------------------
# FCFS - First Come, First Served
# ---------------------------------------------------------------------------
def fcfs(processes):
    """Non-preemptive: processes run strictly in arrival order (ties broken
    by pid). A process starts as soon as the CPU is free and it has
    arrived."""
    procs = sorted(deepcopy(processes), key=lambda p: (p["arrival_time"], p["pid"]))

    results = []
    clock = 0
    for p in procs:
        start_time = max(clock, p["arrival_time"])
        completion_time = start_time + p["burst_time"]
        clock = completion_time
        results.append(
            {
                "pid": p["pid"],
                "arrival_time": p["arrival_time"],
                "burst_time": p["burst_time"],
                "completion_time": completion_time,
            }
        )

    return _finalize(results)


# ---------------------------------------------------------------------------
# SJF - Shortest Job First (non-preemptive)
# ---------------------------------------------------------------------------
def sjf_non_preemptive(processes):
    """Non-preemptive: whenever the CPU becomes idle, pick the arrived,
    not-yet-run process with the smallest burst time (ties broken by
    arrival time, then pid)."""
    procs = deepcopy(processes)
    remaining = {p["pid"]: p for p in procs}
    results = []
    clock = 0

    while remaining:
        arrived = [p for p in remaining.values() if p["arrival_time"] <= clock]
        if not arrived:
            # CPU sits idle until the next process arrives.
            clock = min(p["arrival_time"] for p in remaining.values())
            arrived = [p for p in remaining.values() if p["arrival_time"] <= clock]

        chosen = min(arrived, key=lambda p: (p["burst_time"], p["arrival_time"], p["pid"]))
        start_time = max(clock, chosen["arrival_time"])
        completion_time = start_time + chosen["burst_time"]
        clock = completion_time

        results.append(
            {
                "pid": chosen["pid"],
                "arrival_time": chosen["arrival_time"],
                "burst_time": chosen["burst_time"],
                "completion_time": completion_time,
            }
        )
        del remaining[chosen["pid"]]

    return _finalize(results)


# ---------------------------------------------------------------------------
# Round Robin (preemptive, fixed quantum)
# ---------------------------------------------------------------------------
def round_robin(processes, quantum):
    """Preemptive: each process gets at most `quantum` time units per turn
    in the ready queue. Newly arrived processes are added to the back of
    the queue before the just-run process is re-queued (if it still has
    remaining burst time), which is the standard textbook convention."""
    procs = sorted(deepcopy(processes), key=lambda p: (p["arrival_time"], p["pid"]))
    remaining_burst = {p["pid"]: p["burst_time"] for p in procs}
    arrival_of = {p["pid"]: p["arrival_time"] for p in procs}
    burst_of = {p["pid"]: p["burst_time"] for p in procs}

    completion_time = {}
    queue = deque()
    clock = 0
    in_queue = set()
    not_arrived = deque(procs)  # still sorted by arrival time

    # Seed the queue with anything arriving at time 0 (or earlier, in theory).
    while not_arrived and not_arrived[0]["arrival_time"] <= clock:
        p = not_arrived.popleft()
        queue.append(p["pid"])
        in_queue.add(p["pid"])

    while queue:
        pid = queue.popleft()
        in_queue.discard(pid)

        run_time = min(quantum, remaining_burst[pid])
        clock += run_time
        remaining_burst[pid] -= run_time

        # Bring in anyone who arrived during this time slice, in arrival order.
        while not_arrived and not_arrived[0]["arrival_time"] <= clock:
            p = not_arrived.popleft()
            queue.append(p["pid"])
            in_queue.add(p["pid"])

        if remaining_burst[pid] > 0:
            queue.append(pid)
            in_queue.add(pid)
        else:
            completion_time[pid] = clock

        # If the ready queue is empty but processes haven't arrived yet,
        # jump the clock forward to the next arrival.
        if not queue and not_arrived:
            clock = max(clock, not_arrived[0]["arrival_time"])
            while not_arrived and not_arrived[0]["arrival_time"] <= clock:
                p = not_arrived.popleft()
                queue.append(p["pid"])
                in_queue.add(p["pid"])

    results = [
        {
            "pid": pid,
            "arrival_time": arrival_of[pid],
            "burst_time": burst_of[pid],
            "completion_time": completion_time[pid],
        }
        for pid in arrival_of
    ]
    return _finalize(results)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Sample processes (pid, arrival_time, burst_time):")
    for p in SAMPLE_PROCESSES:
        print(f"  {p['pid']}: arrival={p['arrival_time']}, burst={p['burst_time']}")

    results, avg_wt, avg_tat = fcfs(SAMPLE_PROCESSES)
    print_results("FCFS (First-Come, First-Served)", results, avg_wt, avg_tat)

    results, avg_wt, avg_tat = sjf_non_preemptive(SAMPLE_PROCESSES)
    print_results("SJF (Shortest Job First, non-preemptive)", results, avg_wt, avg_tat)

    results, avg_wt, avg_tat = round_robin(SAMPLE_PROCESSES, ROUND_ROBIN_QUANTUM)
    print_results(f"Round Robin (quantum={ROUND_ROBIN_QUANTUM})", results, avg_wt, avg_tat)


if __name__ == "__main__":
    main()
