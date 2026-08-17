#!/usr/bin/env python3
"""
UDP "Ping" Demo (single file, server + client)
===============================================

Demonstrates connectionless communication with Python's standard
`socket` module using UDP (SOCK_DGRAM), all inside one script by
running the server in a background thread and the client on the main
thread.

Key contrast with the TCP demo (tcp_echo_server.py / tcp_echo_client.py):
    - No connect()/accept() handshake: each UDP packet ("datagram") is
      sent independently with sendto() and received with recvfrom(),
      which also reports the sender's address for each packet.
    - No guarantee of delivery, ordering, or duplicate suppression --
      the application is responsible for that if it cares (this demo
      keeps it simple and assumes a healthy loopback connection).
    - Because there is no persistent connection, either side can just
      start sending; the "server" here simply binds a socket and waits
      for datagrams to arrive.

This script sends a small number of "PING n" datagrams from a client
socket to a server socket, and the server replies to each with "PONG n",
simulating a basic ping/pong exchange (similar in spirit to ICMP ping,
but implemented entirely at the UDP application level for teaching
purposes).

Usage
-----
    python udp_ping_demo.py

No arguments needed -- the server and client both run inside this one
process (server on a background thread, client on the main thread).
"""

import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 5001
BUFFER_SIZE = 1024
PING_COUNT = 5
SERVER_READY_TIMEOUT = 5.0  # seconds


def run_server(ready_event: threading.Event, stop_event: threading.Event) -> None:
    """Bind a UDP socket and reply PONG to every PING datagram received,
    until stop_event is set."""
    # SOCK_DGRAM -> UDP (connectionless, unordered, best-effort datagrams)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        # Non-blocking-ish polling via timeout so we can check stop_event
        # without needing a dedicated shutdown datagram.
        server_sock.settimeout(0.5)

        print(f"[SERVER] UDP server bound to {HOST}:{PORT}, waiting for datagrams.")
        ready_event.set()

        while not stop_event.is_set():
            try:
                data, client_addr = server_sock.recvfrom(BUFFER_SIZE)
            except socket.timeout:
                continue

            message = data.decode("utf-8", errors="replace")
            print(f"[SERVER] Received {message!r} from {client_addr}")

            if message.startswith("PING"):
                seq = message.split()[1] if len(message.split()) > 1 else "?"
                reply = f"PONG {seq}".encode("utf-8")
                server_sock.sendto(reply, client_addr)
                print(f"[SERVER] Sent {reply!r} to {client_addr}")

        print("[SERVER] Stopping.")


def run_client() -> None:
    """Send a handful of PING datagrams to the server and print each
    PONG reply, demonstrating connectionless request/response over UDP."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_sock:
        client_sock.settimeout(2.0)
        server_addr = (HOST, PORT)

        for seq in range(1, PING_COUNT + 1):
            message = f"PING {seq}".encode("utf-8")
            client_sock.sendto(message, server_addr)
            print(f"[CLIENT] Sent {message!r} to {server_addr}")

            try:
                data, _ = client_sock.recvfrom(BUFFER_SIZE)
                reply = data.decode("utf-8", errors="replace")
                print(f"[CLIENT] Received {reply!r}\n")
            except socket.timeout:
                print("[CLIENT] No reply received (datagram may have been lost).\n")

            time.sleep(0.2)  # small pacing delay between pings


def main() -> None:
    ready_event = threading.Event()
    stop_event = threading.Event()

    server_thread = threading.Thread(
        target=run_server, args=(ready_event, stop_event), daemon=True
    )
    server_thread.start()

    # Wait for the server to finish binding before the client sends
    # anything, so the very first datagram is not lost.
    if not ready_event.wait(timeout=SERVER_READY_TIMEOUT):
        print("[MAIN] Server did not become ready in time; aborting.")
        stop_event.set()
        server_thread.join()
        return

    try:
        run_client()
    finally:
        stop_event.set()
        server_thread.join()

    print("[MAIN] UDP ping demo complete.")


if __name__ == "__main__":
    main()
