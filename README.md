<h1 align="center">Elasticsearch Index<a href="https://twitter.com/intent/tweet?text=Elaticsearch%20Index%20-%20Manage%20attack%20surface%20data%20on%20Elasticsearch%0Ahttps://github.com/trickest/elasticsearch_index"> <img src="https://img.shields.io/badge/Tweet--lightgrey?logo=twitter&style=social" alt="Tweet" height="20"/></a></h1>

<h3 align="center">
Manage attack surface data on Elasticsearch
</h3>
<br>

Elasticsearch Index is a straightforward tool for indexing data into Elasticsearch. It supports several file types, including plain text files, JSON, and JSONLines. It also has the option to automatically determine the index name based on the file name, or you can specify the index name yourself. You can also query for matching records from your terminal or [Trickest workflows](https://trickest.io/auth/register).

## Installation
### Source
```
git clone https://github.com/trickest/elasticsearch_index
cd elasticsearch_index
pip install -r requirements.txt
```
### Docker
```
docker run quay.io/trickest/elasticsearch_index
```

## Usage
```
usage: elasticsearch_index.py [-h] [--file FILE] [--file-type {list,json,jsonlines}] [--index INDEX] --config CONFIG [--field FIELD] [--elastic-id] [--auto-index] [--dir DIR] [--query QUERY] [--log LOG] [--output OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           File to be indexed
  --file-type {list,json,jsonlines}
                        Type of the file to be indexed
  --index INDEX         Name of the Elasticsearch index
  --config CONFIG       Path to the config YAML file
  --field FIELD         Field name to use with "list" files
  --elastic-id          Use Elasticsearch's automatically-generated IDs
  --auto-index          Automatically determine the index name based on the file name (e.g. subdomains.txt -> subdomains index)
  --dir DIR             Directory with files to be indexed
  --query QUERY         Query to search for
  --log LOG             Log file
  --output OUTPUT       Output file
```

## Configuration
The tool requires a config file in YAML format. It should include the following information:
```yaml
elasticsearch:
    url: https://<ELASTICSEARCH_HOST>:443
    username: <USERNAME>
    password: <PASSWORD>
index: <INDEX>
```

The `elasticsearch` object is required for authentication. The URL must include a scheme and port.

The `index` key is optional. If it's not specified, you can either specify the index name using the `--index` argument or let the tool automatically determine the index name based on the file name by using the `--auto-index` argument.

[<img src="./banner.png" />](https://trickest.io/auth/register)

## Examples

### Import a plain text file
Import a single file `subdomains.txt` into the `subdomains` index as a `list` file:
```
python elasticsearch_index.py --config config.yaml --file subdomains.txt --file-type list --index subdomains
```

### Import a JSONLines file and assign a document ID field
Import a JSONLines file `nuclei.json` while determining the index and file type automatically and using the `template-id` field as the document ID
```
python elasticsearch_index.py --config config.yaml --file nuclei.json --auto-index --field template-id
```

### Import a file and assign random IDs
Import a JSONLines file `httpx.json` while setting random IDs (to import each run's output into separate documents and not overwrite old results with new ones)
```
python elasticsearch_index.py --config config.yaml --file httpx.json --elastic-id
```

### Import multiple files in a directory
Import multiple file to separate indices
```
python elasticsearch_index.py --config config.yaml --dir /path/to/directory --auto-index

[*] Connected to Elasticsearch
[*] Importing /path/to/directory/nuclei.json into the nuclei index as a JSONLINES file
[*] Successfully imported /path/to/directory/nuclei.json into nuclei
[*] Importing /path/to/directory/httpx.json into the httpx index as a JSONLINES file
[*] Successfully imported /path/to/directory/httpx.json into httpx
```

### Export records matching a query
Run an [Elasticsearch DSL query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-syntax) and return matching records
```
python elasticsearch_index.py --config config.yaml --query "status_code:200" --index webservers --output output.txt
```

[<img src="./banner.png" />](https://trickest.io/auth/register)
