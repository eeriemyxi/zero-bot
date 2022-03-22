# syntax=docker/dockerfile:1
FROM ubuntu:bionic


RUN apt-get -y update
RUN apt-get -y upgrade

# ffmpeg install
RUN apt-get install -y ffmpeg

# python3.8 install
RUN : \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        software-properties-common \
    && add-apt-repository -y ppa:deadsnakes \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3.8-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && :

# Set python 3.8 env variable
RUN python3.8 -m venv /venv
ENV PATH=/venv/bin:$PATH

# update and upgrade
RUN apt-get -y update
RUN apt-get -y upgrade

# check if all core software have been installed
RUN python3 --version
RUN pip3 --version
RUN ffmpeg -version

WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:/app"

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "bot.py"]