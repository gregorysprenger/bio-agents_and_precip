#!/usr/bin/env python3

"""
This script grabs data from Google Clooud Storage,
downloads, transforms, and uploads to BigQuery.
"""

import os
import sys
import pandas as pd
import pandas_gbq

from pathlib import Path
from prefect import flow, task
from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket
from scrape_agents_webpage import scrape_agents_webpage


__author__ = "Gregory Sprenger"
__license__ = "Apache 2.0"
__version__ = "1.0.0"


@task(retries=3, log_prints=True)
def extract_from_gcs(filename, local_path, gcs_path):
    """
    Download data from GCS.

    :return: Local path
    """
    print(f"INFO: Extracting {filename} from GCS.")

    file_gcs_path = f"{gcs_path}/{filename}"
    gcs_bucket = GcsBucket.load("gcs-agents-precip")
    gcs_bucket.get_directory(from_path=file_gcs_path, local_path=local_path)

    return Path(f"{local_path}/{file_gcs_path}")


@task(log_prints=True)
def transform_data(path, filename):
    """
    Read parquet data, clean, and return dataframe.

    :return: Pandas dataframe
    """
    if os.path.isfile(path) and os.path.getsize(path) > 0:
        print(f"INFO: Transforming {filename}")
        df = pd.read_parquet(path)

        print(f"INFO: PRE - Missing precipitation count: {df['Precipitation'].isna().sum()}")

        df["Precipitation"].fillna(0, inplace=True)

        print(f"INFO: POST - Missing precipitation count: {df['Precipitation'].isna().sum()}")
        return df
    else:
        print(f"INFO: {filename} is empty. Skipping..")


@task(log_prints=True)
def write_to_bq(df):
    """
    Write dataframe to BigQuery.
    """
    print("INFO: Writing file to BigQuery.")
    gcp_credentials = GcpCredentials.load("gcp-agents-creds")
    pandas_gbq.to_gbq(
        df,
        destination_table="agents.agents_and_precip",
        project_id="agents-and-precipitation",
        credentials=gcp_credentials.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="append",
    )


@flow(log_prints=True)
def gcs_to_bq(start, end):
    """
    Entry point on the script that extracts data
    from GCS and then uploads to BigQuery.
    """
    # Set params
    infile = "agents_list.txt"
    local_path = "gcs_data"
    gcs_path = "data"

    # Scrape agent's webpage again
    scrape_agents_webpage(start, end)

    if not os.path.exists(local_path):
        os.makedirs(local_path)

    # Create empty dataframe_list to append dataframes to
    dataframe_list = []

    # Loop over infile list
    with open(infile) as f:
        lines = f.readlines()

        for filename in lines:
            filename = filename.strip().replace(" ", "_")

            # Try to catch errors
            if "." in filename:
                if not filename.endswith(".parquet"):
                    sys.stderr.write("ERROR: Filename does not end with '.parquet'.")
                    sys.exit(1)
            elif not "." in filename:
                filename = filename + ".parquet"

            # ETL process
            path = extract_from_gcs(filename, local_path, gcs_path)
            df = transform_data(path, filename)
            dataframe_list.append(df)

    print(f"INFO: df list = {len(dataframe_list)}")

    merged_df = pd.concat(dataframe_list)

    print(f"INFO: Dataframe is of length {len(merged_df)}")
    write_to_bq(merged_df)


if __name__ == "__main__":
    start = 1
    end = 60
    gcs_to_bq(start, end)
