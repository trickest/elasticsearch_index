FROM python:3.9-slim-buster
LABEL licenses.elasticsearch-index.name="" \
      licenses.elasticsearch-index.url="" \
      licenses.python.name="PSF" \
      licenses.python.url="https://docs.python.org/3/license.html#psf-license"

COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt

RUN mkdir -p /hive/in /hive/out

ENTRYPOINT ["python", "elasticsearch_index.py"]
