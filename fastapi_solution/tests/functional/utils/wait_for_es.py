import time

from elasticsearch import Elasticsearch
from tests.functional.settings import test_settings


def wait_for_es():
    es_client = Elasticsearch(hosts=f'http://{test_settings.elastic_host}:{test_settings.elastic_port}')
    while True:
        if es_client.ping():
            break
        time.sleep(1)
