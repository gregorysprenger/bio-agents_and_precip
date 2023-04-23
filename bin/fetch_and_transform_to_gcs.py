#!/usr/bin/env python3

"""
This script parses data obtained via esearch/efetch,
obtains weather data, and exports a dataframe.
"""

import os
import re
import sys
import json
import pandas as pd
import concurrent.futures

from tqdm import tqdm
from pathlib import Path
from datetime import datetime
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from meteostat import Monthly, Point, Stations
from scrape_agents_webpage import scrape_agents_webpage
from fetch_data import fetch_data


__author__ = "Gregory Sprenger"
__license__ = "Apache 2.0"
__version__ = "1.0.0"


def transform_biosample(filename, biosample, data_list, regions, countries):
    """
    Parses each biosample from input file. Grabs collection date,
    geographic location (country and hopefully region), and accession
    number. Finds precipitation by using location and collection date.
    Then adds all of this information to the dataframe parameter.

    :param filename: Basename of input file
    :param biosample: Parsed biosample from input file
    :param df: Dataframe that data will be added to
    :param regions: Dictionary of regions and their alpha-2 abbreviation
    :param countries: Dictionary of countries and their alpha-2 abbreviation
    :return: None
    """
    collection_date = re.search(r"collection date=\"(.+)\"", biosample)
    geographic_location = re.search(r'geographic location=\"(.+)"', biosample)
    accession = re.search(r"Accession:\s(.+)[\s\t]ID:.+", biosample)

    missing_collection_date = ["missing", "unknown", "not applicable"]
    if (
        collection_date is not None
        and geographic_location is not None
        and accession is not None
    ):
        if collection_date.group(
            1
        ) not in missing_collection_date and "-" in collection_date.group(1):
            # Get country abbreviation
            if ":" in geographic_location.group(1):
                country = geographic_location.group(1).split(":")[0]
                region = (
                    geographic_location.group(1).split(":")[1].split(",")[0].strip()
                )
            else:
                country = geographic_location.group(1)
                region = ""

            if country == "USA":
                country_abbrev = "US"
            else:
                country_abbrev = countries.get(country.upper(), "")

            # Get region abbreviation
            if region:
                region_abbrev = regions.get(region.upper(), "")
            else:
                region_abbrev = ""

            # Get weather data
            stations = Stations()
            if country_abbrev and region_abbrev:
                stations = stations.region(country_abbrev, region_abbrev)
            elif country_abbrev:
                stations = stations.region(country_abbrev)
            else:
                return

            stations = stations.fetch(1)
            try:
                area = Point(stations.latitude[0], stations.longitude[0], 1)
            except IndexError:
                area = "Error"

            if area != "Error":
                split_date = collection_date.group(1).split("-")
                if len(split_date) == 3:
                    reformatted_date = datetime(
                        int(split_date[0]), int(split_date[1]), int(split_date[2])
                    )

                    data = Monthly(area, reformatted_date, reformatted_date)
                    data = data.fetch()

                    # Incase data['prcp'] returns an index error = no data avail for that date
                    try:
                        precip = data["prcp"][0]
                    except IndexError:
                        precip = "Error"

                    if precip != "Error":
                        new_row = [
                            accession.group(1),
                            filename,
                            collection_date.group(1),
                            country_abbrev,
                            region_abbrev,
                            precip,
                        ]
                        data_list.append(new_row)


def transform_biosample_wrapper(args):
    """
    Wrapper function that multiprocesses the parsing of the input file.

    :param args: filename, biosample, dataframe, regions, and countries from main function
    :return: Returns parse_lines function with parameters
    """
    return transform_biosample(*args)


@task(log_prints=True)
def write_local(df, filename, local_outpath):
    """
    Write dataframe to local path as parquet.
    """
    df.to_parquet(f"{local_outpath}/{filename}.parquet", index=False)
    print(f"INFO: Writing {filename} to local path.")


@task(log_prints=True)
def write_gcs(filename, local_outpath, gcs_path):
    """
    Upload parquet files to GCS.
    """
    gcs_bucket = GcsBucket.load("gcs-agents-precip")
    gcs_bucket.upload_from_path(
        from_path=f"{local_outpath}/{filename}.parquet",
        to_path=f"{gcs_path}/{filename}.parquet",
    )
    print(f"INFO: Writing {filename} to GCS.")


@flow(log_prints=True)
def fetch_and_transform(api_key='', start=0, end=66):
    """
    Entry point of script that does the processing of input file.
    """
    # Set params
    infile = "agents_list.txt"
    local_inpath = "raw_data"
    local_outpath = "clean_data"
    gcs_path = "data"

    # Scrape webpage
    scrape_agents_webpage(start, end)

    # Grab data with esearch/efetch
    print("INFO: Fetching data..")
    fetch_data(api_key)
    print("INFO: Done fetching data.")

    # Check if input/output directory exists
    if not os.path.exists(infile):
        sys.stderr.write("ERROR: Input file does not exist.")
        sys.exit(1)

    # Make directories if they don't exist
    if not os.path.exists(local_outpath):
        os.makedirs(local_outpath)
    if not os.path.exists(local_inpath):
        os.makedirs(local_inpath)

    # Load countries from
    # https://www.iban.com/country-codes
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "countries.json"), "r"
    ) as f:
        countries = json.load(f)

    # Load regions from
    # https://www.in.gov/dor/files/reference/foreign-state-province-codes-2018.pdf
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "regions.json"), "r"
    ) as f:
        regions = json.load(f)

    filenames = []

    # Read input file
    with open(infile) as f:
        for line in f.readlines():
            line = line.strip().replace(" ", "_")
            filenames.append(line + ".tsv")

    for i in filenames:
        data_list = []

        file = os.path.join(local_inpath, i)
        if os.path.isfile(file):
            with open(file) as f:
                lines = f.read()

            data = lines.split("\n\n")
            filename = os.path.basename(i).split(".")[0]

            print(f"INFO: Cleaning {filename}")

            # Multiprocess the parsing of data with process bar
            for biosample in tqdm(data):
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    executor.submit(
                        transform_biosample_wrapper,
                        args=(filename, biosample, data_list, regions, countries),
                    )

        # Create dataframe from data_list
        df = pd.DataFrame(
            data_list,
            columns=[
                "Biosample",
                "Agent",
                "Date",
                "Country",
                "region",
                "Precipitation",
            ],
        )

        print(f"INFO: Length of df = {len(df)}")

        # Write df to local area
        write_local(df, filename, local_outpath)

        # Write files in outpath to Google Cloud Storage (GCS)
        write_gcs(filename, local_outpath, gcs_path)


if __name__ == "__main__":
    api_key = ''
    start = 1
    end = 60
    fetch_and_transform(api_key, start, end)
