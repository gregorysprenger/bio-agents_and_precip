#!/usr/bin/env python3

"""
This script is essentially a wrapper script
for run_flow.sh to import in deploy.py
"""

import subprocess


def fetch_data(api_key):
    process = subprocess.call(
        ["run_flow.sh", api_key],
        shell=True,
    )


if __name__ == "__main__":
    api_key = "NULL"
    fetch_data(api_key)
