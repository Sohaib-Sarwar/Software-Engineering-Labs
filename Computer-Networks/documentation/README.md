# Computer Networks — Lab Notes

This folder contains reference notes and runnable demos covering core
computer networking concepts: the layered network models, the
TCP vs. UDP transport distinction, DNS and DHCP, and IPv4 subnetting.

## Folder Structure

```
Computer-Networks/
├── configurations/
│   └── subnetting_worksheet.md   # worked IPv4 subnetting examples + CIDR notes
├── simulations/
│   ├── tcp_echo_server.py        # TCP (connection-oriented) echo server
│   ├── tcp_echo_client.py        # TCP echo client
│   └── udp_ping_demo.py          # single-file UDP (connectionless) ping/pong demo
└── documentation/
    └── README.md                 # this file
```

## 1. The OSI Model (7 Layers)

The OSI (Open Systems Interconnection) model is a conceptual framework
that describes networking as seven stacked layers, each providing a
service to the layer above and consuming a service from the layer
below.

| Layer | Name         | Responsibility                                                        | Examples                          |
|-------|--------------|------------------------------------------------------------------------|------------------------------------|
| 7     | Application  | Provides network services directly to end-user applications           | HTTP, FTP, SMTP, DNS               |
| 6     | Presentation | Translates, encrypts, and compresses data between formats              | TLS/SSL, JPEG, ASCII/Unicode       |
| 5     | Session      | Establishes, manages, and tears down sessions between hosts            | Sockets, RPC session handling      |
| 4     | Transport    | End-to-end delivery, segmentation, flow control, reliability           | TCP, UDP                           |
| 3     | Network      | Logical addressing and routing between different networks              | IP, ICMP, routers                  |
| 2     | Data Link    | Framing, physical addressing (MAC), error detection on a single link   | Ethernet, Wi-Fi (802.11), switches |
| 1     | Physical     | Raw bit transmission over a physical medium                            | Cables, radio signals, connectors  |

A useful mnemonic (top to bottom): **A**ll **P**eople **S**eem **T**o
**N**eed **D**ata **P**rocessing.

Data moving down the stack is progressively wrapped ("encapsulated")
with each layer's own header (and, at Layer 2, a trailer); the
receiving host unwraps it layer by layer on the way back up
("decapsulation").

## 2. The TCP/IP Model (4 Layers)

The TCP/IP model is the practical model the modern Internet is actually
built on. It condenses OSI's seven layers into four, and maps roughly
as follows:

| TCP/IP Layer         | Roughly corresponds to OSI layers | Responsibility                                   | Examples             |
|-----------------------|------------------------------------|---------------------------------------------------|-----------------------|
| Application           | 5, 6, 7                            | End-user protocols and data formatting             | HTTP, DNS, DHCP, SMTP |
| Transport             | 4                                   | End-to-end communication, ports, reliability       | TCP, UDP              |
| Internet              | 3                                   | Logical addressing and routing across networks     | IP, ICMP, ARP         |
| Network Access (Link)  | 1, 2                                | Physical transmission and framing on a local link  | Ethernet, Wi-Fi       |

OSI is primarily a teaching/reference model; TCP/IP is the model
actually implemented in real operating systems' network stacks
(including the `socket` module used by the demos in this folder).

## 3. TCP vs. UDP

Both TCP and UDP live at the **Transport layer** and both use *ports*
to distinguish applications on the same host, but they make very
different trade-offs:

| Aspect              | TCP                                                | UDP                                             |
|---------------------|-----------------------------------------------------|---------------------------------------------------|
| Connection           | Connection-oriented (three-way handshake)           | Connectionless (no handshake, no session state)    |
| Reliability          | Guaranteed delivery, retransmits lost segments       | Best-effort; lost datagrams are simply lost        |
| Ordering             | Guarantees in-order delivery                         | No ordering guarantee                              |
| Overhead             | Higher (headers, acknowledgments, flow/congestion control) | Lower (minimal header, no acks)             |
| Typical use cases    | Web browsing, file transfer, email                   | DNS lookups, streaming, VoIP, online gaming        |
| Socket type in code  | `SOCK_STREAM`                                        | `SOCK_DGRAM`                                       |

### How this maps to the demos in `simulations/`

- **`tcp_echo_server.py` + `tcp_echo_client.py`** demonstrate TCP's
  connection-oriented model directly: the server calls
  `listen()`/`accept()` to establish a session, the client calls
  `connect()` before sending anything, and both sides exchange data
  over a persistent, ordered byte stream until one side closes it (or
  sends `"quit"`).

- **`udp_ping_demo.py`** demonstrates the opposite: there is no
  `connect()`/`accept()` step at all. The "server" just `bind()`s a
  socket and waits; the "client" immediately calls `sendto()` with the
  destination address attached to *each individual datagram*, and the
  server replies using `recvfrom()`, which reports the sender's
  address for every packet it receives. Nothing in the protocol
  guarantees the PING/PONG pairs arrive, or arrive in order — the demo
  works reliably on `localhost` in practice, but production UDP
  applications must handle loss and reordering themselves if they
  care about it.

## 4. DNS (Domain Name System)

DNS translates human-readable domain names (e.g. `example.com`) into
the IP addresses computers actually use to route traffic (e.g.
`93.184.216.34`). It operates at the Application layer and is itself
usually carried over UDP (for short queries/responses, port 53) with a
fallback to TCP for larger responses (e.g. zone transfers, DNSSEC, or
answers that don't fit in a single UDP datagram).

Key roles:
- **Resolution**: turning a name into an address (a "forward lookup"),
  or an address back into a name ("reverse lookup").
- **Hierarchy**: DNS is organized as a distributed, hierarchical
  database — root servers, then top-level domain (TLD) servers (e.g.
  `.com`, `.org`), then authoritative name servers for each specific
  domain.
- **Caching**: resolvers (often built into the OS or the local router)
  cache answers for a **TTL** (time-to-live) to reduce repeated
  lookups and load on upstream servers.
- **Records**: common record types include `A` (IPv4 address), `AAAA`
  (IPv6 address), `CNAME` (alias), `MX` (mail exchange), `NS` (name
  server), and `TXT` (arbitrary text, often used for verification).

Without DNS, every network application would need to work with raw IP
addresses instead of memorable names.

## 5. DHCP (Dynamic Host Configuration Protocol)

DHCP automatically assigns IP configuration to devices joining a
network, so administrators don't have to configure every host's
address by hand. It operates at the Application layer and runs over
UDP (server listens on port 67, client on port 68).

The typical exchange is remembered by the acronym **DORA**:

1. **Discover** — the client broadcasts a request looking for any DHCP
   server on the local network.
2. **Offer** — a DHCP server replies with a proposed IP address and
   configuration.
3. **Request** — the client broadcasts a message accepting one
   particular offer (in case multiple servers replied).
4. **Acknowledge** — the chosen server confirms the lease, finalizing
   the assignment.

DHCP typically hands out, in addition to an IP address:
- the subnet mask (see `configurations/subnetting_worksheet.md`),
- the default gateway (router) address,
- one or more DNS server addresses,
- a **lease duration**, after which the client must renew or release
  the address.

## 6. Running the Socket Demos

Both demos are pure standard-library Python 3 (only the `socket`,
`sys`, `threading`, and `time` modules are used) — no `pip install` is
required.

### TCP echo demo (two terminals required)

**Terminal 1 — start the server first:**
```
python simulations/tcp_echo_server.py
```
This binds to `127.0.0.1:5000` by default and waits for a connection.
You can override the host/port: `python tcp_echo_server.py 0.0.0.0 6000`.

**Terminal 2 — then run the client:**
```
python simulations/tcp_echo_client.py
```
The client connects, sends a few sample messages (including a final
`"quit"`), and prints the server's echoed reply for each one. The
server keeps running afterward, ready to accept another connection
(press Ctrl+C in the server's terminal to stop it).

> The server must already be listening before the client's `connect()`
> call runs, or the client will fail with a "connection refused"
> error — this is a direct consequence of TCP being connection-oriented.

### UDP ping demo (single terminal, single script)

```
python simulations/udp_ping_demo.py
```
This one script starts the "server" logic on a background thread and
the "client" logic on the main thread, so no second terminal is
needed. You'll see interleaved `[SERVER]` and `[CLIENT]` log lines as
five PING/PONG datagrams are exchanged over UDP, after which the
script exits on its own.

## 7. Suggested Exercises

- Modify `tcp_echo_client.py`'s `TEST_MESSAGES` list and observe how
  the server logs and echoes each new message.
- Run two `tcp_echo_client.py` instances against the same server (in
  two more terminals) one after another, and notice the server handles
  them sequentially, one connection at a time.
- In `udp_ping_demo.py`, try lowering the client's `settimeout()` value
  to see how the demo behaves if a reply doesn't arrive in time.
- Using `configurations/subnetting_worksheet.md` as a model, work out
  the subnets for a different network, such as `10.0.0.0/22` divided
  into 4 equal subnets.
