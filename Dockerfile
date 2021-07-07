FROM python:3.9-slim-buster
LABEL maintainer="Arash Azamifard <arash.azamifard@nersc.no>"
LABEL purpose="Python libs for regridding"
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN    apt-get update \
    && apt-get -y install gcc g++ libgeos++-dev libproj-dev \
    && cat requirements.txt | xargs -L 1 pip install \
    && mkdir /opt/notebooks
WORKDIR /opt/notebooks
ENTRYPOINT ["sh", "-c", "jupyter lab --allow-root --ip=0.0.0.0 --notebook-dir=/opt/notebooks"]
