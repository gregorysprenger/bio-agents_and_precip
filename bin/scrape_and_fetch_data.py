#!/usr/bin/env python3

"""
This script is essentially a wrapper script
for run_flow.sh to import in deploy.py
"""

import subprocess
from prefect import flow


def fetch_data():
    script = "run_flow.sh"

    process = subprocess.Popen(
        ["run_flow.sh"],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()


if __name__ == "__main__":
    fetch_data()
