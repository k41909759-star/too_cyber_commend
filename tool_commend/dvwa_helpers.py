#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import requests
from requests.exceptions import RequestException
from html_helpers import extract_user_token

def require(ok, msg):
    if not ok:
        print(f"[-] {msg}")
        sys.exit(1)

def norm_join(base, path):
    base = base.rstrip('/')
    if not path.startswith('/'):
        path = '/' + path
    return base + path

def dvwa_login(sess, base_url, username, password):
    login_url = norm_join(base_url, '/login.php')
    try:
        r = sess.get(login_url, timeout=15)
        token = extract_user_token(r.text)
    except RequestException:
        token = None

    data = {"username": username, "password": password, "Login": "Login"}
    if token:
        data["user_token"] = token

    r2 = sess.post(login_url, data=data, timeout=15, allow_redirects=True)
    logged_in = ("Logout" in r2.text) or ("logout" in r2.text)

    if not logged_in:
        try:
            r3 = sess.get(norm_join(base_url, '/index.php'), timeout=15)
            logged_in = ("Logout" in r3.text) or ("logout" in r3.text)
        except RequestException:
            logged_in = False

    require(logged_in, "Login failed.")

def dvwa_set_security(sess, base_url, level="low"):
    sec_url = norm_join(base_url, '/security.php')
    try:
        r = sess.get(sec_url, timeout=15)
        token = extract_user_token(r.text)
        data = {"security": level, "seclev_submit": "Submit"}
        if token:
            data["user_token"] = token
        sess.post(sec_url, data=data, timeout=15)
    except RequestException:
        pass

def parse_extra(s):
    extra = {}
    if not s:
        return extra
    for item in s.split('&'):
        if '=' not in item:
            raise ValueError(f"Invalid POST pair: {item}")
        k, v = item.split('=', 1)
        extra[k] = v
    return extra

def post_exec(sess, url, param, value, extra):
    body = extra.copy()
    body[param] = value
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": url,
        "User-Agent": "Mozilla/5.0"
    }
    r = sess.post(url, data=body, headers=headers, timeout=15)
    return r.text