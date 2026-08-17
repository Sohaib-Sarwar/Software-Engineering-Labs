# Operating Systems Lab Notes

This folder contains three small, runnable Python demos plus notes on the
underlying concepts:

```
Operating-Systems/
├── source/
│   ├── cpu_scheduling.py       # FCFS, SJF, Round Robin simulator
│   ├── producer_consumer.py    # threading-based bounded-buffer demo
│   └── deadlock_detection.py   # resource-allocation-graph cycle detector
└── documentation/
    └── README.md                # this file
```

All scripts use only the Python 3 standard library. Run any of them with:

```
python source/cpu_scheduling.py
python source/producer_consumer.py
python source/deadlock_detection.py
```

---

## 1. Process vs. Thread

| | Process | Thread |
|---|---|---|
| Definition | An independent, running instance of a program with its own memory space. | A unit of execution *within* a process; multiple threads share that process's memory. |
| Memory | Has its own address space (code, data, heap, stack). Isolated from other processes. | Shares code, data, and heap with sibling threads in the same process; each thread has its own stack and register/program-counter state. |
| Creation cost | Relatively expensive (OS allocates a new address space, page tables, etc.). | Cheaper -- no new address space needed, just a new stack and scheduling context. |
| Communication | Requires explicit IPC (pipes, sockets, shared memory, message queues) because memory is isolated. | Trivial -- threads read/write the same variables directly, but this means they need explicit synchronization (locks, semaphores) to avoid race conditions. |
| Crash isolation | One process crashing does not directly bring down another process. | One thread crashing (e.g., unhandled exception/segfault) can take down the whole process, including sibling threads. |
| Scheduling unit | The OS scheduler ultimately schedules threads (a single-threaded process has exactly one), but classic scheduling theory (and the algorithms below) is usually explained per-process/per-job. | The OS scheduler's actual dispatch unit on most modern systems. |

`producer_consumer.py` in this folder is a concrete example of the thread
side of this table: the producer and consumer are two threads inside the
*same* Python process, sharing one Python list (`buffer`) directly in
memory, which is exactly why they need a `Lock` and `Semaphore`s to stay
correct.

---

## 2. CPU Scheduling Algorithms

`source/cpu_scheduling.py` implements three algorithms and runs them all
against the same fixed sample workload:

```
PID   Arrival   Burst
P1    0         5
P2    1         3
P3    2         8
P4    3         6
```

For every algorithm we compute, per process:

- **Completion Time (CT)** -- when the process finishes running.
- **Turnaround Time (TAT)** = `CT - Arrival Time`. Total time from arrival
  until the process is done (waiting + running).
- **Waiting Time (WT)** = `TAT - Burst Time`. Time spent in the ready
  queue *not* running.

And then the *average* WT and TAT across all processes, which is the
usual metric used to compare scheduling policies.

### 2.1 FCFS -- First-Come, First-Served

**Idea:** Non-preemptive. Processes run strictly in arrival order (a
process that arrives earlier always runs before one that arrives later);
once a process starts, it runs to completion.

**Worked example** (matches `SAMPLE_PROCESSES` above):

| PID | Arrival | Burst | Start | Completion | Turnaround | Waiting |
|---|---|---|---|---|---|---|
| P1 | 0 | 5 | 0  | 5  | 5  | 0  |
| P2 | 1 | 3 | 5  | 8  | 7  | 4  |
| P3 | 2 | 8 | 8  | 16 | 14 | 6  |
| P4 | 3 | 6 | 16 | 22 | 19 | 13 |

- P1 arrives first and runs immediately: 0 -> 5.
- P2 arrived at t=1 but the CPU was busy with P1, so it waits until t=5,
  then runs 5 -> 8.
- P3 arrived at t=2 but waits until t=8, then runs 8 -> 16.
- P4 arrived at t=3 but waits until t=16, then runs 16 -> 22.

**Average Waiting Time = 5.75, Average Turnaround Time = 11.25**

**Trade-off:** Simple and fair in the "no starvation" sense (arrival
order is respected), but suffers from the *convoy effect* -- a long
process at the front (like P3's burst of 8, if it had arrived first)
makes every process behind it wait a long time, even short ones.

### 2.2 SJF -- Shortest Job First (non-preemptive)

**Idea:** Non-preemptive. Whenever the CPU goes idle, look at every
process that has *already arrived* and is still waiting, and run the one
with the smallest burst time next. Once started, a process still runs to
completion (no preemption if a shorter job arrives mid-execution -- that
variant is called SRTF, Shortest Remaining Time First).

**Worked example:**

| PID | Arrival | Burst | Start | Completion | Turnaround | Waiting |
|---|---|---|---|---|---|---|
| P1 | 0 | 5 | 0  | 5  | 5  | 0  |
| P2 | 1 | 3 | 5  | 8  | 7  | 4  |
| P4 | 3 | 6 | 8  | 14 | 11 | 5  |
| P3 | 2 | 8 | 14 | 22 | 20 | 12 |

- At t=0 only P1 has arrived, so it runs: 0 -> 5.
- At t=5, P2 (burst 3), P3 (burst 8), and P4 (burst 6) have all arrived.
  The shortest is P2, so it runs next: 5 -> 8.
- At t=8, P3 (burst 8) and P4 (burst 6) remain. P4 is shorter, so it
  runs: 8 -> 14.
- Only P3 is left, so it runs: 14 -> 22.

**Average Waiting Time = 5.25, Average Turnaround Time = 10.75**

**Trade-off:** SJF is *provably optimal* for minimizing average waiting
time among non-preemptive algorithms (notice its 5.25 beats FCFS's 5.75
on the same workload), but it requires knowing burst times in advance
(usually estimated, not known exactly, in real systems) and can starve
long jobs if short jobs keep arriving.

### 2.3 Round Robin (preemptive, fixed quantum)

**Idea:** Preemptive. Each process gets a fixed time slice ("quantum")
per turn. If it doesn't finish within that slice, it is preempted and
sent to the back of the ready queue, and the next process in the queue
runs. Newly-arrived processes join the back of the queue as soon as they
arrive. This code uses **quantum = 4**.

**Worked example** (ready-queue trace):

| Time | Running | Ready queue after this slice | Event |
|---|---|---|---|
| 0 -> 4  | P1 (rem. 5->1) | P2, P3, P4, P1 | P2/P3/P4 have all arrived by t=4, queued before re-queuing P1 |
| 4 -> 7  | P2 (rem. 3->0) | P3, P4, P1 | **P2 completes at t=7** |
| 7 -> 11 | P3 (rem. 8->4) | P4, P1, P3 | P3 still has 4 left, re-queued |
| 11 -> 15| P4 (rem. 6->2) | P1, P3, P4 | P4 still has 2 left, re-queued |
| 15 -> 16| P1 (rem. 1->0) | P3, P4 | **P1 completes at t=16** |
| 16 -> 20| P3 (rem. 4->0) | P4 | **P3 completes at t=20** |
| 20 -> 22| P4 (rem. 2->0) | (empty) | **P4 completes at t=22** |

| PID | Arrival | Burst | Completion | Turnaround | Waiting |
|---|---|---|---|---|---|
| P1 | 0 | 5 | 16 | 16 | 11 |
| P2 | 1 | 3 | 7  | 6  | 3  |
| P3 | 2 | 8 | 20 | 18 | 10 |
| P4 | 3 | 6 | 22 | 19 | 13 |

**Average Waiting Time = 9.25, Average Turnaround Time = 14.75**

**Trade-off:** Round Robin guarantees every process gets CPU time
regularly (good *response time*, no starvation), which is why it's the
basis of most real time-sharing OS schedulers -- but on this particular
workload its average waiting/turnaround time is worse than FCFS or SJF,
because of the extra context switches and because long jobs get chopped
up and interleaved rather than run straight through. The quantum size
matters a lot: too large and RR degenerates toward FCFS; too small and
context-switch overhead (not modeled in this simplified simulator)
dominates.

### 2.4 Summary comparison (same workload, quantum = 4)

| Algorithm | Avg. Waiting Time | Avg. Turnaround Time |
|---|---|---|
| FCFS | 5.75 | 11.25 |
| SJF (non-preemptive) | 5.25 | 10.75 |
| Round Robin (q=4) | 9.25 | 14.75 |

These numbers are exactly what `python source/cpu_scheduling.py` prints;
run it yourself to see the full per-process tables.

---

## 3. Necessary Conditions for Deadlock

A deadlock is a state where a set of processes are each waiting for a
resource that another process in the set holds, so none of them can ever
proceed. Coffman (1971) showed that **all four** of the following
conditions must hold simultaneously for a deadlock to occur:

1. **Mutual Exclusion** -- At least one resource is held in a
   non-shareable mode (only one process can use it at a time).
2. **Hold and Wait** -- A process holding at least one resource is
   waiting to acquire additional resources currently held by other
   processes.
3. **No Preemption** -- Resources cannot be forcibly taken away from a
   process; they can only be released voluntarily by the process holding
   them.
4. **Circular Wait** -- There exists a set of processes {P0, P1, ...,
   Pn} such that P0 is waiting for a resource held by P1, P1 is waiting
   for a resource held by P2, ..., and Pn is waiting for a resource held
   by P0.

Breaking *any one* of these four conditions is enough to prevent
deadlock, which is the basis for deadlock **prevention** strategies (e.g.
requiring processes to request all resources at once to remove
hold-and-wait, or imposing a strict global ordering on resource
acquisition to remove circular wait). Deadlock **avoidance** (e.g. the
Banker's algorithm) instead grants requests dynamically only when doing
so keeps the system in a "safe state." Deadlock **detection** (what this
lab implements) lets deadlocks happen and finds them after the fact so
the system can recover (e.g. by killing/rolling back a process in the
cycle).

### How `deadlock_detection.py` detects deadlock

Under the simplifying assumption that every resource type has exactly
**one instance**, condition 4 (circular wait) becomes easy to check:

1. Build a **wait-for graph**: for each process `P` that is requesting a
   resource `R`, find out which process `H` currently holds `R`
   (from the `allocation` mapping) and add a directed edge `P -> H`
   ("P is waiting on H").
2. Run a depth-first search over this graph, coloring nodes
   white (unvisited) / gray (currently on the DFS stack) / black (fully
   explored).
3. If the DFS ever follows an edge into a **gray** node, that node is an
   ancestor on the current path, so the path back to it forms a **cycle**
   -- and a cycle in the wait-for graph (single-instance case) means
   those processes are deadlocked.
4. If the DFS finishes exploring every node without finding a gray-to-gray
   edge, the graph is acyclic and the system is not deadlocked.

The script runs two examples:

- **Deadlocked**: P1 holds R1 and wants R2; P2 holds R2 and wants R3; P3
  holds R3 and wants R1. Wait-for graph: `P1 -> P2 -> P3 -> P1`, a
  3-cycle -- reported as a deadlock involving P1, P2, P3.
- **Non-deadlocked**: same holdings, but P3 requests nothing. Wait-for
  graph: `P1 -> P2 -> P3`, a chain with no way back to P1 -- reported as
  no deadlock.

(For resources with *multiple* instances, a cycle in the resource
allocation graph is necessary but not always sufficient for deadlock; a
full solution there needs a more general algorithm, such as the
Banker's-algorithm-style safety check.)

---

## 4. Virtual Memory and Paging (brief notes)

**Virtual memory** gives each process the illusion of a large, private,
contiguous address space, independent of how much physical RAM the
machine actually has and independent of where other processes' memory
lives. The OS (with help from the CPU's Memory Management Unit) maps
each process's *virtual addresses* to *physical addresses* transparently.

Benefits:
- **Isolation** -- one process cannot read or corrupt another process's
  memory, because each process only ever sees its own virtual address
  space.
- **Larger-than-RAM address spaces** -- programs can be written as if
  memory were effectively unlimited; the OS pages less-used data out to
  disk (or a swap file) as needed.
- **Simpler linking/loading** -- every process can assume the same
  virtual layout (e.g. code starting at a fixed base address) regardless
  of physical memory fragmentation.

**Paging** is the most common mechanism used to implement virtual
memory:

- Physical memory is divided into fixed-size **frames**; a process's
  virtual address space is divided into same-sized **pages**.
- A per-process **page table** maps virtual page numbers to physical
  frame numbers (or marks the page as "not present," meaning it currently
  lives only on disk / hasn't been allocated).
- A virtual address is split into a **page number** (looked up in the
  page table) and a **page offset** (kept as-is, since a whole page maps
  to a whole frame).
- The **TLB** (Translation Lookaside Buffer) is a small, fast hardware
  cache of recent virtual-to-physical translations, so most memory
  accesses don't need a full page-table walk.
- A **page fault** occurs when a process accesses a page that is marked
  not-present. The OS then finds a free frame (or evicts a page from an
  occupied one, using a policy like LRU or the clock algorithm), loads
  the needed page in from disk, updates the page table, and resumes the
  faulting instruction.
- Because paging divides memory into fixed-size chunks, it avoids
  **external fragmentation** (no need to find one large contiguous free
  region), though it can still waste some space via **internal
  fragmentation** (a process's last page is rarely used completely).

Paging is what allows the *isolation* property discussed above (process
vs. thread, Section 1) to actually be enforced by hardware: since each
process has its own page table, one process's virtual addresses simply
cannot resolve into another process's physical frames.

---

## How to run everything

```bash
python source/cpu_scheduling.py
python source/producer_consumer.py
python source/deadlock_detection.py
```

Each script is self-contained (standard library only, no `pip install`
needed) and prints its results directly to the console.
