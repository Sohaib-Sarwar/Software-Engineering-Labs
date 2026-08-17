"""
producer_consumer.py

A classic Producer-Consumer synchronization demo using Python's
`threading` module, a bounded (fixed-size) buffer, one `Lock` for mutual
exclusion, and two `Semaphore`s that count empty and full slots.

Synchronization primitives used
--------------------------------
- `empty_slots` (Semaphore, initial value = BUFFER_SIZE): counts how many
  free slots the buffer currently has. The producer must acquire this
  before inserting an item (it blocks if the buffer is full).
- `full_slots` (Semaphore, initial value = 0): counts how many filled
  slots the buffer currently has. The consumer must acquire this before
  removing an item (it blocks if the buffer is empty).
- `buffer_lock` (Lock): guards the actual list operations (append/pop) so
  that the producer and consumer never mutate the shared buffer at the
  same time.

This is the standard "two counting semaphores + one mutex" solution to
the bounded-buffer problem, and it prevents both race conditions on the
buffer and busy-waiting (threads block on the semaphores instead of
spinning).

The demo produces a fixed, small number of items (see NUM_ITEMS) with
short random delays, so the whole run finishes in well under a couple of
seconds. It prints every item as it is produced and consumed, plus a
final summary.

Run it directly:

    python producer_consumer.py
"""

import random
import threading
import time


BUFFER_SIZE = 5   # Maximum number of items the buffer can hold at once.
NUM_ITEMS = 12     # Total number of items the producer will create.

buffer = []                                   # The shared bounded buffer.
buffer_lock = threading.Lock()                # Protects `buffer` itself.
empty_slots = threading.Semaphore(BUFFER_SIZE)  # Counts free slots.
full_slots = threading.Semaphore(0)           # Counts filled slots.

print_lock = threading.Lock()  # Keeps console output from interleaving mid-line.


def log(message):
    with print_lock:
        print(message, flush=True)


def producer():
    for item in range(1, NUM_ITEMS + 1):
        time.sleep(random.uniform(0.01, 0.05))  # Simulate time spent producing.

        empty_slots.acquire()      # Wait for a free slot (blocks if buffer full).
        with buffer_lock:          # Exclusive access to the shared buffer.
            buffer.append(item)
            log(f"[Producer] produced item {item:>2}  (buffer size now {len(buffer)})")
        full_slots.release()       # Signal that a new filled slot is available.

    log("[Producer] done producing.")


def consumer():
    for _ in range(NUM_ITEMS):
        full_slots.acquire()       # Wait for an available item (blocks if buffer empty).
        with buffer_lock:          # Exclusive access to the shared buffer.
            item = buffer.pop(0)
            log(f"[Consumer] consumed item {item:>2}  (buffer size now {len(buffer)})")
        empty_slots.release()      # Signal that a slot has been freed.

        time.sleep(random.uniform(0.01, 0.05))  # Simulate time spent consuming.

    log("[Consumer] done consuming.")


def main():
    print(f"Starting producer-consumer demo: buffer_size={BUFFER_SIZE}, items={NUM_ITEMS}\n")

    start = time.time()

    producer_thread = threading.Thread(target=producer, name="Producer")
    consumer_thread = threading.Thread(target=consumer, name="Consumer")

    producer_thread.start()
    consumer_thread.start()

    # Fixed short duration: both threads are bounded by NUM_ITEMS and small
    # sleeps, so a generous timeout is only a safety net, not the normal
    # termination path.
    producer_thread.join(timeout=10)
    consumer_thread.join(timeout=10)

    elapsed = time.time() - start

    print(f"\nFinished in {elapsed:.2f} seconds.")
    print(f"Final buffer contents (should be empty if producer/consumer finished cleanly): {buffer}")

    if producer_thread.is_alive() or consumer_thread.is_alive():
        print("WARNING: one or more threads did not finish within the timeout.")
    else:
        print("Both threads completed successfully -- no deadlock, no race condition.")


if __name__ == "__main__":
    main()
