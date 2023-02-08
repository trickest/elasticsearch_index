from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk
from urllib.parse import urlparse
import argparse
import json
import yaml
import os
import re

def create_client(url, username, password):
    """
    Creates a connection to Elasticsearch using basic authentication.
    TODO: Other authentication methods?
    """

    try:
        client = Elasticsearch(
            [url],
            basic_auth=(username, password)
        )
    except ConnectionError as e:
        raise ConnectionError(f"Error connecting to Elasticsearch: {e}")

    if not client.ping():
        raise ConnectionError("Error connecting to Elasticsearch: Make sure the URL and credentials are valid")
    return client

def index_list_file(client, index, filename, field_name, elastic_id=False):
    """
    Indexes lines from a file
    """

    def generator():
        with open(filename, 'r') as f:
            for line in f:
                obj = {
                    '_index': index,
                    field_name: line.strip()
                }
                if not elastic_id:
                    obj['_id'] = line.strip()
                yield obj

    for success, info in parallel_bulk(client, generator()):
        if not success:
            print(f"Error indexing line: {info}")

def index_jsonlines_file(client, index, filename, id_field_name=None):
    """
    Indexes JSONLines objects in a file
    """

    def generator():
        with open(filename, 'r') as file:
            for line in file:
                obj = json.loads(line)
                if id_field_name:
                    obj['_id'] = obj[id_field_name]
                obj['_index'] = index
                yield obj

    for success, info in parallel_bulk(client, generator()):
        if not success:
            print(f"Error indexing line: {info}")

def index_json_list(client, index, filename, id_field_name=None):
    """
    Indexes JSON objects from a list
    """

    try:
        with open(filename, 'r') as file:
            obj_list = json.load(file)
            if not isinstance(obj_list, list):
                raise ValueError("{filename} is not a JSON list")
            if id_field_name:
                for obj in obj_list:
                    obj['_id'] = obj[id_field_name]
                    obj['_index'] = index
            for success, info in parallel_bulk(client, obj_list):
                if not success:
                    print(f"Error indexing line: {info}")
    except Exception as e:
        print(f"Error processing file: {e}")

def read_config_yaml(yaml_file):
    """
    Reads a config yaml file containing the Elasticsearch URL, username, and password.
    The yaml file should have a root object named 'elasticsearch' containing 'url', 'username', and 'password' fields.
    Optionally, the file can contain an 'index' field to specify the Elasticsearch index (otherwise, it will be read from arguments)
    ---
    Example

    elasticsearch:
        url: https://example.us-central1.gcp.cloud.es.io:443
        username: elastic
        password: dolphin1
    index: subdomains
    """

    with open(yaml_file, 'r') as file:
        config = yaml.safe_load(file)
        if 'elasticsearch' not in config:
            raise ValueError("Missing 'elasticsearch' root object in the config YAML file")

        elasticsearch_config = config['elasticsearch']

        if 'url' not in elasticsearch_config:
            raise ValueError("Missing 'url' field in the 'elasticsearch' object of the config YAML file")
        parsed_url = urlparse(elasticsearch_config['url'])
        if not parsed_url.scheme or not parsed_url.port:
            raise ValueError("Elasticsearch URL must include a scheme and a port (e.g. https://example.us-central1.gcp.cloud.es.io:443)")

        if 'username' not in elasticsearch_config:
            raise ValueError("Missing 'username' field in the 'elasticsearch' object of the config YAML file")

        if 'password' not in elasticsearch_config:
            raise ValueError("Missing 'password' field in the 'elasticsearch' object of the config YAML file")

        return config

def get_files_in_directory(directory_path):
    """
    Lists files in a directory recursively
    """

    file_paths = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)
    return file_paths

def determine_file_type(filename):
    """
    Determines if the file is formatted as JSON, JSONLines, or a simple list
    """

    with open(filename, 'r') as file:
        first_line = file.readline()
        first_char = first_line[0]
        if first_char in '{[':
            # either JSON or JSONLines
            try:
                # If the first line alone is a valid JSON object, it's JSONLines
                json.loads(first_line)
                return 'jsonlines'
            except json.decoder.JSONDecodeError:
                return 'json'
        else:
            return 'list'

def find_last_index(search_list, search_item):
    return len(search_list) - 1 - search_list[::-1].index(search_item)

def determine_index(file_path):
    """
    Determines the index name automaitcally based on the file path
    """

    # Special handling for Trickest naming conventions
    # If the file path is `in/nuclei-1/output.txt`, the index is `nuclei` not `output`
    is_trickest_node_output_file = re.match(r"(.*)in\/([-a-z]+)-\d+\/(.*)", file_path)

    if is_trickest_node_output_file:
        path_chunks = file_path.split('/')
        in_index = find_last_index(path_chunks, 'in')
        node_id = path_chunks[in_index + 1]
        index = '-'.join(node_id.split('-')[:-1])
    else:
        base = os.path.basename(file_path)
        index = os.path.splitext(base)[0]

    return index

def exit_with_error(error):
    print(f'[X] {error}')
    exit(1)

def log_output(message, log_file):
    log_file.write(message + '\n')
    print(message)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help='File to be indexed')
    parser.add_argument('--file-type', choices=['list', 'json', 'jsonlines'], help='Type of the file to be indexed')
    parser.add_argument('--index', help='Name of the Elasticsearch index')
    parser.add_argument('--config', required=True, help='Path to the config YAML file')
    parser.add_argument('--field', help='Field name to use with "list" files')
    parser.add_argument('--elastic-id', action="store_true", help="Use Elasticsearch's automatically-generated IDs")
    parser.add_argument('--auto-index', action="store_true", help="Automatically determine the index name based on the file name (e.g. subdomains.txt -> subdomains index)")
    parser.add_argument('--dir', help='Directory with files to be indexed')
    parser.add_argument('--output', required=True, help='Output log')
    args = parser.parse_args()

    config = read_config_yaml(args.config)
    elasticsearch_config = config['elasticsearch']
    client = create_client(elasticsearch_config['url'], elasticsearch_config['username'], elasticsearch_config['password'])

    with open(args.output, 'a') as log_file:
        log_output('[*] Connected to Elasticsearch', log_file)

        if not ('index' in config or args.index or args.auto_index):
            exit_with_error("You need to either set an index of set the `--auto-index` flag")

        if not args.file and not args.dir:
            exit_with_error("No input provided. Use --file or --dir")

        files = []
        if args.dir:
            files = get_files_in_directory(args.dir)
        if args.file:
            files.append(args.file)

        index = config['index'] if 'index' in config else args.index

        file_type = args.file_type

        for file in files:
            if not file_type:
                file_type = determine_file_type(file)

            if args.dir or not index:
                index = determine_index(file)

            log_output(f'[*] Importing {file} into the {index} index as a {file_type.upper()} file', log_file)
            if file_type == 'jsonlines':
                index_jsonlines_file(client, index, file, args.field)
            elif file_type == 'json':
                index_json_list(client, index, file, args.field)
            else:
                index_list_file(client, index, file, args.field, args.elastic_id)

            log_output(f'[*] Successfully imported {file} into {index}', log_file)

if __name__ == '__main__':
    main()
