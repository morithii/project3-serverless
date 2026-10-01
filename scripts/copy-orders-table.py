#!/usr/bin/env python3
"""One-off migration: copy every item from the old single-region "Orders" table
into the new "project3-orders" Global Table, using the AWS CLI.

Usage:  python3 scripts/copy-orders-table.py
"""
import json
import subprocess

PROFILE = "project3"
REGION = "eu-west-2"
SOURCE = "Orders"
TARGET = "project3-orders"


def aws(*args, stdin=None):
    cmd = ["aws", *args, "--profile", PROFILE, "--region", REGION, "--output", "json"]
    result = subprocess.run(cmd, input=stdin, capture_output=True, text=True, check=True)
    return json.loads(result.stdout) if result.stdout.strip() else {}


# The CLI follows pagination automatically, so this returns every item
items = aws("dynamodb", "scan", "--table-name", SOURCE)["Items"]
print(f"Read {len(items)} items from {SOURCE}")

# BatchWriteItem accepts at most 25 items per call
for start in range(0, len(items), 25):
    batch = {TARGET: [{"PutRequest": {"Item": item}} for item in items[start:start + 25]]}
    pending = batch
    while pending:
        response = aws("dynamodb", "batch-write-item", "--request-items", json.dumps(pending))
        pending = response.get("UnprocessedItems") or None
    print(f"Copied {min(start + 25, len(items))}/{len(items)}")

count = aws("dynamodb", "scan", "--table-name", TARGET, "--select", "COUNT")["Count"]
print(f"{TARGET} now holds {count} items")
