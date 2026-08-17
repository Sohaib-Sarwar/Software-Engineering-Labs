#!/usr/bin/env python3
"""
TCP Echo Server
===============

A minimal, connection-oriented TCP server built on Python's standard
`socket` module. It accepts one client connection at a time and echoes
back every message it receives, until the client sends "quit" or closes
the connection.

TCP (Transmission Control Protocol) is connection-oriented: the server
must call listen()/accept() to establish a reliable, ordered byte-stream
session with a client before any application data can flow. Contrast
this with simulations/udp_ping_demo.py, which needs no such handshake.

Usage
-----
    python tcp_echo_server.py [host] [port]

Defaults to host="127.0.0.1", port=5000.

Run this script first, in its own terminal, then run
simulations/tcp_echo_client.py in a second terminal.
Press Ctrl+C to stop the server.
"""

import socket
import sys

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000
BUFFER_SIZE = 1024


def handle_client(conn: socket.socket, addr) -> None:
    """Read length-prefixed-free text messages from a single client and
    echo each one back, until the client disconnects or sends 'quit'."""
    print(f"[SERVER] Connection established with {addr}")
    with conn:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                # Client closed the connection (recv returns b"" on EOF).
                print(f"[SERVER] {addr} disconnected.")
                break

            message = data.decode("utf-8", errors="replace").rstrip("\n")
            print(f"[SERVER] Received from {addr}: {message!r}")

            if message.strip().lower() == "quit":
                conn.sendall(b"BYE\n")
                print(f"[SERVER] {addr} requested quit.")
                break

            reply = f"ECHO: {message}\n".encode("utf-8")
            conn.sendall(reply)


def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    # AF_INET  -> IPv4 addressing
    # SOCK_STREAM -> TCP (reliable, ordered, connection-oriented stream)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        # Allow quick restarts of the server without waiting for the OS
        # to release the port (TIME_WAIT state).
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((host, port))
        server_sock.listen(5)
        print(f"[SERVER] TCP echo server listening on {host}:{port}")
        print("[SERVER] Waiting for a client connection... (Ctrl+C to stop)")

        try:
            while True:
                conn, addr = server_sock.accept()
                handle_client(conn, addr)
                print("[SERVER] Ready for a new connection.\n")
        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down.")


def main() -> None:
    host = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    run_server(host, port)


if __name__ == "__main__":
    main()
