#!/usr/bin/env python3

"""
This script deploys the docker container and
all other scripts needed to perform ETL.
"""

from docker_block import create_docker_block
from gcp_block import create_gcp_block
from fetch_and_transform_to_gcs import fetch_and_transform
from gcs_to_bq import gcs_to_bq

from prefect.deployments import Deployment
from prefect.infrastructure.docker import DockerContainer


__author__ = "Gregory Sprenger"
__license__ = "Apache 2.0"
__version__ = "1.0.0"


def main():
    # Add docker and gcp blocks
    create_docker_block()
    create_gcp_block()

    docker_block = DockerContainer.load("prefect-and-edirect")

    deployment1 = Deployment.build_from_flow(
        flow=fetch_and_transform,
        name="docker-flow1",
        infrastructure=docker_block,
    )

    deployment2 = Deployment.build_from_flow(
        flow=gcs_to_bq,
        name="docker-flow2",
        infrastructure=docker_block,
    )

    deployment1.apply()
    deployment2.apply()


if __name__ == "__main__":
    main()
