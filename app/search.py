from flask import current_app

def add_to_index(index: str, model: 'SQLAlchemy model'):
	"""
	 Builds the document that is inserted into the index.

	 __searchable__ is used as a list of fields that should be find

	"""
	if not current_app.elasticsearch:
		return
	payload = {}
	for field in model.__searchable__:
		payload[field] = getattr(model, field)
	current_app.elasticsearch.index(index=index, id=model.id, body=payload)

def remove_from_index(index: str, model: 'SQLAlchemy model'):
	"""
	Deletes the document stored under the given id.
	id for deleting is unique id of the document in SQL_DB

	"""
	if not current_app.elasticsearch:
		return
	current_app.elasticsearch.delete(index=index, id=model.id)

def query_index(index: str, query: str, page: int, per_page: int) ->'list of ids' \
																'total number of results':
	"""
	Takes the index name and a text to search for, 
	along with pagination controls
	"""
	if not current_app.elasticsearch:
		return [], 0
	search = current_app.elasticsearch.search(
		index=index, body={'query': {'multi_match': {'query': query, # 'multi_match' can search across multiple fields
							'fields': ['*']}},
							'from': (page-1) * per_page, 'size': per_page})
	ids = [int(hit['_id']) for hit in search['hits']['hits']] #extracts the id values from 
	return ids, search['hits']['total']['value']                       #the list of results provided by Elasticsearch