import os
import json
from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket


def create_gcp_block():
    with open(os.path.abspath(os.path.expanduser("./credentials/creds.json"))) as f:
        credentials = f.read()

    credentials_block = GcpCredentials(service_account_info=credentials)
    credentials_block.save("gcp-agents-creds", overwrite=True)

    bucket_block = GcsBucket(
        gcp_credentials=GcpCredentials.load("gcp-agents-creds"),
        bucket="agents-precip",
    )

    bucket_block.save("gcs-agents-precip", overwrite=True)


if __name__ == "__main__":
    create_gcp_block()
