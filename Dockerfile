FROM python:3.9-slim-buster
LABEL licenses.elasticsearch-index.name="MIT" \
      licenses.elasticsearch-index.url="https://github.com/trickest/elasticsearch_index/blob/d664944d1f253db1d9e145873dcd0d68ca227bf7/LICENSE"

COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt

RUN mkdir -p /hive/in /hive/out

ENTRYPOINT ["python", "elasticsearch_index.py"]
