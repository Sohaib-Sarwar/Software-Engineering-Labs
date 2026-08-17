#!/usr/bin/env python3
"""
TCP Echo Client
===============

A minimal TCP client, built on Python's standard `socket` module, that
connects to simulations/tcp_echo_server.py, sends a handful of test
messages, and prints each server reply.

TCP requires an explicit connect() before any data can be exchanged
(the "three-way handshake" happens transparently inside this call).
The connection remains open for the whole conversation, and data is
delivered reliably and in order. Compare this with the connectionless
model shown in simulations/udp_ping_demo.py.

Usage
-----
    python tcp_echo_client.py [host] [port]

Defaults to host="127.0.0.1", port=5000.

Start simulations/tcp_echo_server.py first in one terminal, then run
this script in a second terminal.
"""

import socket
import sys

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000
BUFFER_SIZE = 1024

# A few sample messages to exercise the echo server.
TEST_MESSAGES = [
    "hello",
    "computer networks lab",
    "TCP is connection-oriented",
    "quit",
]


def run_client(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
        print(f"[CLIENT] Connecting to {host}:{port} ...")
        try:
            client_sock.connect((host, port))
        except ConnectionRefusedError:
            print(
                "[CLIENT] Connection refused. Is tcp_echo_server.py "
                "running first?"
            )
            return

        print("[CLIENT] Connected. Sending test messages.\n")

        for message in TEST_MESSAGES:
            payload = (message + "\n").encode("utf-8")
            client_sock.sendall(payload)
            print(f"[CLIENT] Sent: {message!r}")

            response = client_sock.recv(BUFFER_SIZE)
            if not response:
                print("[CLIENT] Server closed the connection.")
                break

            reply = response.decode("utf-8", errors="replace").strip()
            print(f"[CLIENT] Received: {reply!r}\n")

            if message.strip().lower() == "quit":
                break

        print("[CLIENT] Done.")


def main() -> None:
    host = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    run_client(host, port)


if __name__ == "__main__":
    main()
