FROM ubuntu:bionic
LABEL maintainer="Anton Korosov <anton.korosov@nersc.no>"
LABEL version="0.0.2"

RUN apt-get update  --fix-missing && \
    apt-get install -y --no-install-recommends \
        gcc \
        libc-dev \
        wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN wget --quiet --no-check-certificate https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    /bin/bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc

ENV PATH="/opt/conda/bin/:$PATH"
COPY environment.yml /tmp/environment.yml
RUN conda env update --file /tmp/environment.yml --name base && \
    /opt/conda/bin/conda clean -a && \
    rm -rf $HOME/.cache/yarn && \
    rm -rf /opt/conda/pkgs/*

COPY setup.py /tmp/
COPY README.md /tmp/
COPY geodataset /tmp/geodataset
WORKDIR /tmp/
RUN python setup.py install
WORKDIR /root