FROM python:3.10-slim

VOLUME ["/network-availability-checker"]

WORKDIR "/"

RUN apt-get update --yes && \
    apt-get upgrade --yes && \
    apt-get install --yes --no-install-recommends \
    python3-dev \
    gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip
ADD ./requirements.txt /requirements.txt
RUN python3 -m pip install -r /requirements.txt

ENV PYTHONUNBUFFERED=1
CMD python3 -m network-availability-checker
