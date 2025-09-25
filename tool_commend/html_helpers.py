#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def extract_pre_text(html):
    m = re.search(r'<pre[^>]*>(.*?)</pre>', html, re.I | re.S)
    if not m:
        return ""
    text = re.sub(r'<[^>]+>', '', m.group(1))
    return text.replace('\r\n', '\n').replace('\r', '\n').strip()

def extract_user_token(html):
    m = re.search(r'name\s*=\s*["\']user_token["\']\s+value\s*=\s*["\']([^"\']+)["\']',
                  html, re.I)
    return m.group(1) if m else None