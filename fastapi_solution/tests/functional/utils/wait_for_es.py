import time

from elasticsearch import Elasticsearch

from tests.functional.elastic_indexes import FILMS_INDEX, PERSONS_INDEX, GENRES_INDEX
from tests.functional.settings import test_settings


def wait_for_es():
    es_client = Elasticsearch(hosts=f'http://{test_settings.elastic_host}:{test_settings.elastic_port}')
    while True:
        if es_client.ping():
            indices_dict = {'movies': FILMS_INDEX, 'persons': PERSONS_INDEX, 'genres': GENRES_INDEX}
            for index_name, index_dict in indices_dict.items():
                if not es_client.indices.exists(index=index_name):
                    es_client.indices.create(index=index_name, ignore=400, body=index_dict)
            break
        time.sleep(1)

wait_for_es()
