#!/usr/bin/env python3

import re
import sys
import argparse
import ipaddress


def iprange2cidr(start, end):
    try:
        startip = ipaddress.ip_address(start)
        endip = ipaddress.ip_address(end)
        yield from ipaddress.summarize_address_range(startip, endip)
    except ValueError:
        print(f"skipping invalid network: {start},{end}", file=sys.stderr)
        return []


splitter = re.compile(r"[,;\s\-_@\|]+")


def handle_file(filename):
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "/" in line:
                try:
                    yield ipaddress.ip_network(line)
                except ValueError:
                    print(f"skipping invalid network: {line}", file=sys.stderr)
                continue
            line = splitter.split(line)
            if len(line) != 2:
                continue
            yield from iprange2cidr(line[0], line[1])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs="+")
    parser.add_argument("-p", "--prefix")
    parser.add_argument("-s", "--suffix")
    args = parser.parse_args()

    ipv4 = []
    ipv6 = []
    for filename in args.filename:
        for i in handle_file(filename):
            if i.version == 4:
                ipv4.append(i)
            else:
                ipv6.append(i)
    if ipv4:
        for i in ipaddress.collapse_addresses(ipv4):
            content = f"{args.prefix if args.prefix else ''}{i}{args.suffix if args.suffix else ''}"
            print(content)
    if ipv6:
        for i in ipaddress.collapse_addresses(ipv6):
            content = f"{args.prefix if args.prefix else ''}{i}{args.suffix if args.suffix else ''}"
            print(content)


if __name__ == "__main__":
    main()
