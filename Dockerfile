# Install Prefect from their image
FROM prefecthq/prefect:2.10.4-python3.9 as build1

COPY docker-requirements.txt .

# Install python dependencies
RUN pip install -r docker-requirements.txt \
    --trusted-host pypi.python.org \
    --no-cache-dir

COPY bin /opt/prefect/flows/bin

# Make all scripts executable
RUN chmod +x /opt/prefect/flows/bin/*.py && \
    chmod +x /opt/prefect/flows/bin/*.sh

RUN mkdir -p /opt/prefect/data

# Use ubuntu:focal as main image to build edirect
FROM ubuntu:focal as build2
LABEL base.image="ubuntu:focal"
LABEL dockerfile.version="1.0.0"
LABEL description="Prefect and NCBI's edirect tool."
LABEL maintainer="Gregory Sprenger"

# Install dependencies for edirect
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y \
    libtime-hires-perl \
    curl \
    wget \
    tzdata \
    parallel

# Install edirect
RUN sh -c "$(curl -fsSL https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh)"

# Final docker image
FROM ubuntu:focal as app

COPY --from=build1 /usr/ /usr/
COPY --from=build1 /opt/prefect/ /opt/prefect/
COPY --from=build2 /usr/ /usr/
COPY --from=build2 /root/edirect/ /root/edirect/

ENV PATH="${PATH}:/root/edirect"
ENV PATH="${PATH}:/opt/prefect/flows/bin"
ENV PATH="${PATH}:/opt/prefect/flows/credentials"
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV TZ UTC

RUN mkdir /data
WORKDIR /data

# ENTRYPOINT ["main_flow.py"]

# Test versions of dependencies
FROM app as test

RUN apt-get update && apt-get install -y python3

COPY docker_tests/ ../tests
RUN python3 -m unittest discover -v -s ../tests