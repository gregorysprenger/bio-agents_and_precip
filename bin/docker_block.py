import os
from prefect.infrastructure.docker import DockerContainer


def create_docker_block():
    docker_block = DockerContainer(
        image="gregorysprenger/prefect-and-edirect:v1.0.0",
        image_pull_policy="ALWAYS",
        auto_remove=True,
    )

    docker_block.save("prefect-and-edirect", overwrite=True)


if __name__ == "__main__":
    create_docker_block()
