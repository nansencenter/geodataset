FROM continuumio/miniconda3
LABEL maintainer="Arash Azamifard <arash.azamifard@nersc.no>"
LABEL purpose="Python libs for regridding"
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt
RUN apt-get update \
&&  apt-get install -y --no-install-recommends \
&&  apt clean \
&&  rm -rf /var/lib/apt/lists/* \
&&  conda install setuptools \
&&  conda update conda \
&&  conda config --add channels conda-forge  \
&&  conda install -y \
    jupyter \
    cartopy=0.18.0 \
    ipython=7.17.0 \
    satpy=0.29.0 \
    netcdf4=1.5.4 \
    wget=1.20.1 \
&&  conda clean -a -y \
&&  rm /opt/conda/pkgs/* -rf \
&&  mkdir /opt/notebooks
WORKDIR /opt/notebooks
ENTRYPOINT ["sh", "-c", "/opt/conda/bin/jupyter notebook  --allow-root --no-browser --ip=0.0.0.0 --notebook-dir=/opt/notebooks"]
