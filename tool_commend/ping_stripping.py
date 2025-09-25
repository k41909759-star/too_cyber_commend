#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

PING_PATTERNS = [
    r'^\s*ping\b',
    r'bytes from',
    r'icmp_seq=\d+',
    r'ttl=\d+',
    r'time[=<]\s*\d+(\.\d+)?\s*ms',
    r'^\s*\d+\s+bytes from',
    r'^\s*reply from',
    r'^\s*request timed out',
    r'^\s*destination (host|net) unreachable',
    r'^\s*packets:\s*sent',
    r'^\s*approximate round trip times',
    r'^\s*minimum\s*=\s*\d+ms',
    r'^\s*rtt min/avg/max/mdev',
    r'^\s*\d+\s+packets transmitted',
    r'^\s*\d+(\.\d+)?%\s*packet loss',
]

PING_REGEXES = [re.compile(p, re.I) for p in PING_PATTERNS]

def is_ping_line(line):
    s = line.strip()
    if not s:
        return False
    for rx in PING_REGEXES:
        if rx.search(s):
            return True
    return False

def strip_ping_lines(text):
    kept = []
    for ln in text.split('\n'):
        if is_ping_line(ln):
            continue
        if ln.strip():
            kept.append(ln.strip())
    return "\n".join(kept).strip()