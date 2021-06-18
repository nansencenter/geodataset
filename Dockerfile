FROM pynextsim
LABEL maintainer="Arash Azamifard <arash.azamifard@nersc.no>"
LABEL purpose="Python libs for regridding"
ENV PYTHONUNBUFFERED=1
RUN pip install satpy==0.29.0
RUN  mkdir /opt/notebooks
WORKDIR /opt/notebooks
ENTRYPOINT ["sh", "-c", "/opt/conda/bin/jupyter notebook  --allow-root --no-browser --ip=0.0.0.0 --notebook-dir=/opt/notebooks"]
