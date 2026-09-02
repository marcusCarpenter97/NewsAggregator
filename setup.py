import logging
from utils import format_sources

def setup(news_endpoint, database):

    source_results = news_endpoint.get_sources()

    if not isinstance(source_results, list):
        error = f"Error retreiving sources from API: {source_results}"
        logging.critical(error)
        return

    formatted_sources = format_sources(source_results)
    database.insert_sources(formatted_sources)
