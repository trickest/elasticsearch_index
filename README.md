# Elasticsearch Index
This tool is designed to help you index your data in Elasticsearch. It supports several file types, including plain text files, JSON, and JSONLines. It also has the option to automatically determine the index name based on the file name, or you can specify the index name yourself.

## Installation
```
pip install -r requirements.txt
```

## Usage
```
usage: elasticsearch_index.py [-h] [--file FILE] [--file-type {list,json,jsonlines}] [--index INDEX] --config CONFIG
                              [--field FIELD] [--elastic-id] [--auto-index] [--dir DIR]

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           File to be indexed
  --file-type {list,json,jsonlines}
                        Type of the file to be indexed
  --index INDEX         Name of the Elasticsearch index
  --config CONFIG       Path to the config YAML file
  --field FIELD         Field name to use with "list" files
  --elastic-id          Use Elasticsearch's automatically-generated IDs
  --auto-index          Automatically determine the index name based on the file name (e.g. subdomains.txt -> subdomainsindex)
  --dir DIR             Directory with files to be indexed
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

## Examples
Import a single file `subdomains.txt` into the `subdomains` index as a `list` file:
```
python elasticsearch_index.py --config config.yaml --file subdomains.txt --file-type list --index subdomains
```

Import a JSONLines file `nuclei.json` while determining the index and file type automatically and using the `template-id` field as the document ID
```
python elasticsearch_index.py --config config.yaml --file nuclei.json --auto-index --field template-id
```

Import a JSONLines file `httpx.json` while setting random IDs (to import each run's output into separate documents and not overwrite old results with new ones)
```
python elasticsearch_index.py --config config.yaml --file httpx.json --elastic-id
```

Import multiple files in a directory
```
python elasticsearch_index.py --config config.yaml --dir /path/to/directory --auto-index

[*] Connected to Elasticsearch
[*] Importing /path/to/directory/nuclei.json into the nuclei index as a JSONLINES file
[*] Successfully imported /path/to/directory/nuclei.json into nuclei
[*] Importing /path/to/directory/httpx.json into the httpx index as a JSONLINES file
[*] Successfully imported /path/to/directory/httpx.json into httpx
```
