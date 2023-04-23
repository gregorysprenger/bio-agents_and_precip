#!/usr/bin/env python3

"""
This script scrapes the select agents webpage,
removes duplicates and extra characters, and
adds them to a text file.
"""

import os
import sys
import re
import certifi
import urllib.request

from prefect import task
from bs4 import BeautifulSoup
from itertools import chain

__author__ = "Gregory Sprenger"
__license__ = "Apache 2.0"
__version__ = "1.0.0"


@task(log_prints=True)
def scrape_agents_webpage(start, end):
    """
    Entry point of this script.
    """
    # Set website and parse it
    agents_page = "https://www.selectagents.gov/sat/list.htm"
    page = urllib.request.urlopen(agents_page, cafile=certifi.where())
    soup = BeautifulSoup(page, "html.parser")

    agent_list = []

    # Find all <ol> fields that var soup parsed
    for data in soup.find_all("ol"):
        agent_list.append(str(data.text).split("\n"))

    # Set agent_list to a 1D array instead of 2D
    agent_list = list(chain.from_iterable(agent_list))

    # Remove bracket/parentheses and information between them
    agent_list = [re.sub(" ?[\(\[].*?[\)\]]", "", line) for line in agent_list]

    # Remove html character
    agent_list = [re.sub("\xa0", " ", line) for line in agent_list]

    # Remove items from remove_list
    # Have to make them more broad to fetch data
    list_of_duplicates = ["SARS", "influenza virus", "Botulinum"]
    for i in range(len(agent_list)):
        if any([elem in agent_list[i] for elem in list_of_duplicates]):
            agent_list[i] = ""

    # Add simpler names to list after they've been removed
    agent_list.append("SARS-CoV")
    agent_list.append("influenza virus")
    agent_list.append("Botulinum neurotoxins")

    # Remove any remaining empty lines in list
    while "" in agent_list:
        agent_list.remove("")

    # Fix possible errors
    if start < 0:
        start = 0
    elif start > len(agent_list):
        start = len(agent_list) - 1
    if end > len(agent_list):
        end = len(agent_list)
    elif end < 0:
        end = 1

    outfile = "agents_list.txt"

    if start and end:
        with open(outfile, "w") as f:
            for i in range(start - 1, end):
                f.write(f"{agent_list[i]}\n")
    else:
        with open(outfile, "w") as f:
            for line in agent_list:
                f.write(f"{line}\n")

    print("INFO: Scraping agents webpage complete.")


if __name__ == "__main__":
    start = 1
    end = 60
    scrape_agents_webpage(start, end)
