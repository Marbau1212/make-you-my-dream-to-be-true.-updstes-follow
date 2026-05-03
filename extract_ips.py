#!/usr/bin/env python3
"""
extract_ips.py – Extracts all IPv4 and IPv6 addresses from
/proc/<pid>/net/tcp (IPv4) and /proc/<pid>/net/tcp6 (IPv6).

Usage:
    python3 extract_ips.py <pid> [--include-unspecified]

Arguments:
    pid                    Process ID whose network connections to inspect.
    --include-unspecified  Also include unspecified addresses (0.0.0.0 and ::).

Examples:
    python3 extract_ips.py 1234
    python3 extract_ips.py 1234 --include-unspecified
"""

import argparse
import ipaddress
import os
import socket
import struct
import sys


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _parse_ipv4_hex(hex_str: str) -> str:
    """Convert a little-endian 8-char hex string to a dotted IPv4 string.

    In /proc/net/tcp each IPv4 address is stored as a 32-bit integer in
    host (little-endian on x86) byte order, printed as 8 uppercase hex
    digits.  We unpack it as a native unsigned 32-bit int and then convert
    to the standard dotted-decimal notation.

    Example:
        '0101007F' -> '127.0.0.1'
    """
    # struct.unpack '<I' reads 4 bytes as an unsigned 32-bit little-endian int
    raw = bytes.fromhex(hex_str)
    addr_int = struct.unpack("<I", raw)[0]
    return socket.inet_ntoa(struct.pack(">I", addr_int))


def _parse_ipv6_hex(hex_str: str) -> str:
    """Convert a 32-char hex string from /proc/net/tcp6 to an IPv6 string.

    The kernel writes four consecutive 32-bit little-endian words that
    together form the 128-bit IPv6 address.

    Example:
        '00000000000000000000000001000000' -> '::1'
    """
    raw = bytes.fromhex(hex_str)
    # Four little-endian 32-bit words → reassemble in network byte order
    words = struct.unpack("<IIII", raw)
    packed = struct.pack(">IIII", *words)
    return str(ipaddress.IPv6Address(packed))


# ---------------------------------------------------------------------------
# File readers
# ---------------------------------------------------------------------------

def _read_tcp_addresses(path: str) -> list:
    """Read IPv4 addresses from a /proc/…/net/tcp style file."""
    addresses = []
    try:
        with open(path, encoding="ascii") as fh:
            for line in fh:
                parts = line.split()
                if len(parts) < 3 or not parts[1].replace(":", "").isalnum():
                    continue
                # Column 2 (index 1) is the local address, column 3 is remote
                for col in (parts[1], parts[2]):
                    hex_addr, _port = col.split(":")
                    if len(hex_addr) == 8:
                        addresses.append(_parse_ipv4_hex(hex_addr))
    except FileNotFoundError:
        pass  # File may not exist (IPv4 stack not available or pid gone)
    return addresses


def _read_tcp6_addresses(path: str) -> list:
    """Read IPv6 addresses from a /proc/…/net/tcp6 style file."""
    addresses = []
    try:
        with open(path, encoding="ascii") as fh:
            for line in fh:
                parts = line.split()
                if len(parts) < 3 or not parts[1].replace(":", "").isalnum():
                    continue
                for col in (parts[1], parts[2]):
                    hex_addr, _port = col.split(":")
                    if len(hex_addr) == 32:
                        addresses.append(_parse_ipv6_hex(hex_addr))
    except FileNotFoundError:
        pass
    return addresses


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

_UNSPECIFIED = {
    str(ipaddress.IPv4Address(0)),   # '0.0.0.0'
    str(ipaddress.IPv6Address(0)),   # '::'
}


def extract_ips(pid: int, include_unspecified: bool = False) -> list:
    """Return a sorted, deduplicated list of IP addresses for *pid*."""
    base = "/proc/{}/net".format(pid)
    tcp_path = os.path.join(base, "tcp")
    tcp6_path = os.path.join(base, "tcp6")

    ipv4_raw = _read_tcp_addresses(tcp_path)
    ipv6_raw = _read_tcp6_addresses(tcp6_path)

    # Deduplicate while preserving type for sorting
    seen = set()
    ipv4_unique = []
    for addr in ipv4_raw:
        if addr not in seen:
            seen.add(addr)
            ipv4_unique.append(addr)

    ipv6_unique = []
    for addr in ipv6_raw:
        if addr not in seen:
            seen.add(addr)
            ipv6_unique.append(addr)

    if not include_unspecified:
        ipv4_unique = [a for a in ipv4_unique if a not in _UNSPECIFIED]
        ipv6_unique = [a for a in ipv6_unique if a not in _UNSPECIFIED]

    # Sort each group individually (IPv4 first, then IPv6)
    ipv4_sorted = sorted(ipv4_unique, key=lambda a: ipaddress.IPv4Address(a))
    ipv6_sorted = sorted(ipv6_unique, key=lambda a: ipaddress.IPv6Address(a))

    return ipv4_sorted + ipv6_sorted


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="extract_ips.py",
        description=(
            "Extract all IPv4 and IPv6 addresses from "
            "/proc/<pid>/net/tcp and /proc/<pid>/net/tcp6."
        ),
    )
    parser.add_argument(
        "pid",
        type=int,
        help="Process ID whose network connections to inspect.",
    )
    parser.add_argument(
        "--include-unspecified",
        action="store_true",
        default=False,
        help="Also output unspecified addresses (0.0.0.0 and ::).",
    )
    return parser


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    ips = extract_ips(args.pid, include_unspecified=args.include_unspecified)

    if not ips:
        print("No addresses found for PID {}.".format(args.pid), file=sys.stderr)
        return 1

    for ip in ips:
        print(ip)

    return 0


if __name__ == "__main__":
    sys.exit(main())
