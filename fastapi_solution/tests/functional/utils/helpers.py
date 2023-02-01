import json


def get_es_bulk_query(es_data, es_index, es_id_field):
    bulk_query = []
    for row in es_data:
        bulk_query.extend([
            json.dumps({'index': {'_index': es_index, '_id': es_id_field}}),
            json.dumps(row)
        ])
    return '\n'.join(bulk_query) + '\n'
