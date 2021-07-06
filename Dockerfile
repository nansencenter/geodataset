FROM python:3.9-slim-buster as Builder
LABEL maintainer="Arash Azamifard <arash.azamifard@nersc.no>"
LABEL purpose="Python libs for regridding"
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN    apt-get update \
    && apt-get -y install gcc g++ libgeos++-dev libproj-dev \
    && apt clean \
    && rm -rf /var/lib/apt/lists/* \
    && python -m venv my_venv \
    && cat requirements.txt | xargs -L 1 /app/my_venv/bin/pip install --no-cache-dir \
    && find /app/my_venv \( -type d -a -name test -o -name tests \) -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) -exec rm -rf '{}' \;

FROM python:3.9-slim-buster
RUN    apt-get update \
    #cartopy needs these two to work properly
    && apt-get -y install libgeos++-dev libproj-dev \
    && apt clean \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir /opt/notebooks
COPY --from=Builder /app/my_venv /app/my_venv
ENV PYTHONPATH="${PYTHONPATH}:/app/my_venv/" \
    PATH="${PATH}:/app/my_venv/"
ENTRYPOINT ["sh", "-c", "/app/my_venv/bin/jupyter lab --allow-root --ip=0.0.0.0 --notebook-dir=/opt/notebooks"]
