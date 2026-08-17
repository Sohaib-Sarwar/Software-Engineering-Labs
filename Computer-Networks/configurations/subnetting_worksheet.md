# Subnetting Worksheet

Worked examples of IPv4 subnetting, including CIDR notation, subnet
masks, network/broadcast addresses, and usable host ranges.

## 1. CIDR Notation — Quick Reference

CIDR (Classless Inter-Domain Routing) notation writes an IP address
together with a slash and a number, e.g. `192.168.1.0/24`. The number
after the slash is the **prefix length**: how many of the address's 32
bits are fixed as the *network* portion. The remaining bits belong to
the *host* portion and identify individual devices within that network.

| Concept              | Meaning                                                              |
|----------------------|-----------------------------------------------------------------------|
| `/24`                | First 24 bits = network, last 8 bits = host                          |
| Subnet mask          | The same idea written as four octets, e.g. `/24` = `255.255.255.0`  |
| Network address      | Host bits all set to `0` — identifies the subnet itself, not a host |
| Broadcast address    | Host bits all set to `1` — reaches every host on that subnet        |
| Usable host range    | Every address between network and broadcast (both excluded)         |
| Total addresses      | `2^(host bits)`                                                      |
| Usable hosts         | `2^(host bits) − 2` (network and broadcast are reserved)             |

Borrowing bits from the host portion to create more, smaller subnets
increases the prefix length (e.g. `/24` → `/26`) and shrinks the number
of usable hosts per subnet, but increases the number of subnets you can
carve out of the original block. This trade-off is the core of
subnetting: **more subnets, fewer hosts each** (for a fixed-size
starting block), and vice versa.

Common prefix lengths and their masks:

| Prefix | Subnet Mask         | Host bits | Total addresses | Usable hosts |
|--------|---------------------|-----------|------------------|--------------|
| /24    | 255.255.255.0       | 8         | 256              | 254          |
| /25    | 255.255.255.128     | 7         | 128              | 126          |
| /26    | 255.255.255.192     | 6         | 64               | 62           |
| /27    | 255.255.255.224     | 5         | 32               | 30           |
| /28    | 255.255.255.240     | 4         | 16               | 14           |
| /30    | 255.255.255.252     | 2         | 4                | 2            |

## 2. Worked Example — Dividing 192.168.1.0/24 into 4 Subnets

**Starting block:** `192.168.1.0/24` (256 total addresses, 254 usable
hosts, subnet mask `255.255.255.0`).

**Goal:** split it into exactly 4 equal-sized subnets.

**Step 1 — how many bits to borrow?**
To create 4 subnets we need `2^n >= 4`, so `n = 2` bits borrowed from
the host portion.

**Step 2 — new prefix length.**
`/24 + 2 borrowed bits = /26`.
New subnet mask: `255.255.255.192` (binary octet `11000000`).

**Step 3 — size of each subnet.**
Remaining host bits = `8 − 2 = 6`, so each subnet has `2^6 = 64` total
addresses (`62` usable, after removing the network and broadcast
addresses).

**Step 4 — the block size (increment) between subnets.**
`256 / 4 = 64`, so each subnet's network address increases by 64 in
the fourth octet: `.0`, `.64`, `.128`, `.192`.

### Resulting subnets

| Subnet | Network Address    | Subnet Mask       | Broadcast Address   | Usable Host Range              | Usable Hosts |
|--------|---------------------|-------------------|-----------------------|----------------------------------|--------------|
| 1      | 192.168.1.0/26      | 255.255.255.192   | 192.168.1.63          | 192.168.1.1 – 192.168.1.62      | 62           |
| 2      | 192.168.1.64/26     | 255.255.255.192   | 192.168.1.127         | 192.168.1.65 – 192.168.1.126    | 62           |
| 3      | 192.168.1.128/26    | 255.255.255.192   | 192.168.1.191         | 192.168.1.129 – 192.168.1.190   | 62           |
| 4      | 192.168.1.192/26    | 255.255.255.192   | 192.168.1.255         | 192.168.1.193 – 192.168.1.254   | 62           |

**How each row is derived (using Subnet 2 as an example):**
1. Network address: `192.168.1.64` (the boundary where this block starts;
   in binary, the last octet is `01000000`, i.e. all six host bits are 0).
2. Broadcast address: set all 6 host bits to 1 → `01111111` = `127`,
   giving `192.168.1.127`.
3. Usable host range: every address strictly between the network and
   broadcast addresses → `192.168.1.65` through `192.168.1.126`.
4. Subnet mask stays the same (`255.255.255.192`) for every subnet
   carved from the same `/26` split.

## 3. Worked Example — Dividing 192.168.1.0/24 into 8 Subnets

For comparison, here is the same starting block split more finely.

**Bits needed:** `2^n >= 8` → `n = 3` bits borrowed → new prefix `/27`.
**Subnet mask:** `255.255.255.224`.
**Size per subnet:** `2^(8-3) = 32` total addresses (`30` usable).
**Increment:** `256 / 8 = 32`.

| Subnet | Network Address    | Broadcast Address   | Usable Host Range              |
|--------|---------------------|-----------------------|----------------------------------|
| 1      | 192.168.1.0/27      | 192.168.1.31          | 192.168.1.1 – 192.168.1.30      |
| 2      | 192.168.1.32/27     | 192.168.1.63          | 192.168.1.33 – 192.168.1.62     |
| 3      | 192.168.1.64/27     | 192.168.1.95          | 192.168.1.65 – 192.168.1.94     |
| 4      | 192.168.1.96/27     | 192.168.1.127         | 192.168.1.97 – 192.168.1.126    |
| 5      | 192.168.1.128/27    | 192.168.1.159         | 192.168.1.129 – 192.168.1.158   |
| 6      | 192.168.1.160/27    | 192.168.1.191         | 192.168.1.161 – 192.168.1.190   |
| 7      | 192.168.1.192/27    | 192.168.1.223         | 192.168.1.193 – 192.168.1.222   |
| 8      | 192.168.1.224/27    | 192.168.1.255         | 192.168.1.225 – 192.168.1.254   |

## 4. General Method (Recipe)

Given a starting network `A.B.C.D/P` and a required number of subnets `N`:

1. Find the smallest `n` such that `2^n >= N` (bits to borrow).
2. New prefix length = `P + n`.
3. New subnet mask = 32-bit mask with the top `(P + n)` bits set to 1.
4. Block size (address increment between subnets) = `2^(32 - P) / 2^n`,
   equivalently `2^(host bits remaining)`.
5. List network addresses by starting at the original network address
   and adding the block size repeatedly.
6. For each network address: broadcast address = network address +
   (block size − 1); usable range = everything strictly in between.

This same recipe works at any prefix length and for subnetting based on
a required number of **hosts per subnet** instead of a required number
of subnets — in that case, pick `n` so that the remaining host bits
satisfy `2^(host bits) − 2 >= hosts needed`, then proceed identically.
