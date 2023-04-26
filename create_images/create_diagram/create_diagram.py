#!/usr/bin/env python3

"""
This script is to create a workflow diagram of tools used.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.programming.language import Python, Bash
from diagrams.gcp.analytics import BigQuery
from diagrams.gcp.storage import GCS
from diagrams.onprem.container import Docker
from diagrams.custom import Custom

main_cluster = {
    "splines": "spline",
    "pencolor": "black",
}

inner_cluster1 = {"fontsize": "15", "penwidth": "1"}

inner_cluster2 = {"fontsize": "20", "penwidth": "3", "pad": "20"}

with Diagram(direction="TB", graph_attr=main_cluster):
    prefect = Custom(
        "\n Workflow\norchestration\nwith Prefect",
        "./create_diagram/custom_images/prefect.png",
    )
    looker_studio = Custom(
        "\n\n\n\n\n\n\tLooker Studio",
        "./create_diagram/custom_images/looker_studio.svg",
    )

    with Cluster("fetch-and-transform/docker-flow1", graph_attr=inner_cluster1):
        docker = Docker("Docker\nImage")

        with Cluster(
            "Fetch, Transform, and load data\ninto Google Cloud Storage",
            graph_attr=inner_cluster2,
        ):
            transform = Python("Fetch and Transform\nto GCS")
            fetch_data = Bash("")
            scrape_webpage = Python("")
            scrape_webpage << Edge(label=" Scrape webpage", color="black") >> transform
            (
                fetch_data
                << Edge(label="Fetch data with\nNCBI edirect tool", color="black")
                >> transform
            )

            (
                transform
                >> Edge(
                    label=" Upload data to\nGoogle Cloud\nStorage",
                    color="black",
                    minlen="1",
                )
                >> GCS("Google Cloud Storage")
            )

    with Cluster("gcs-to-bq/docker-flow2", graph_attr=inner_cluster1):
        docker = Docker("Docker\nImage")

        with Cluster(
            "Transfer data from Google Cloud Storage to BigQuery",
            graph_attr=inner_cluster2,
        ):
            transfer = Python("Grab GCS data and\nTransfer to BigQuery")
            scrape_webpage = Python("")
            scrape_webpage << Edge(label=" Scrape webpage", color="black") >> transfer
            (
                GCS("Google Cloud Storage")
                << Edge(label="Grab Data from\nGoogle Cloud Storage", color="black")
                >> transfer
            )
            bq = BigQuery("BigQuery")
            transfer >> Edge(label=" Load data into\nBigQuery", color="black") >> bq

    (
        bq
        >> Edge(label="\n\nVisualize with\nLooker Studio", color="black", minlen="0")
        >> looker_studio
    )

    (
        prefect
        >> Edge(label="Run flow", color="black", minlen="1.5")
        >> [transform, transfer]
    )
