
""" FastAPI endpoints for our application. """

import os
import pdb
import logging
from typing import Optional
import uvicorn
from datetime import datetime
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from setup import setup
from endpoints import NewsEndpoint
from search import search_database_headlines, rank_search_results
from utils import format_headlines, merge_ids_with_headlines, load_test_data
from database import DB

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: {%(filename)s:%(lineno)d} - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

USE_TEST_DATA = os.getenv("USE_TEST_DATA", "False") == "True"

NEWS_API_KEY = os.getenv("API_KEY")

class SearchParameters:

    def __init__(self, key_words: str, page_number: int, page_size: int,
                        sources: str = None, domains: str = None,
                        nodomains: str = None, oldest: str = None,
                        newest: str = None, language: str = None):

        self.key_words = key_words
        self.sources = sources
        self.domains = domains
        self.nodomains = nodomains
        self.oldest = oldest
        self.newest = newest
        self.language = language
        self.page_number = page_number
        self.page_size = page_size

app = FastAPI(title="News Aggregator")

news_endpoint = NewsEndpoint(NEWS_API_KEY)
database = DB()

# TODO for debugging only!
database.clear_database()

setup(news_endpoint, database)

@app.get("/top-stories")
def get_top_stories():

    if USE_TEST_DATA:
        endpoint_result = load_test_data("top-stories.json")
    else:
        endpoint_result = news_endpoint.get_top_stories()

    if not isinstance(endpoint_result, list):
        return {"status": endpoint_result}

    formatted_headlines = format_headlines(endpoint_result)

    url_ids = database.insert_headlines(formatted_headlines)

    if url_ids:
        url_set = {i[1] for i in url_ids}
        new_headlines = [h for h in formatted_headlines if h[5] in url_set]

    new_results = merge_ids_with_headlines(url_ids, new_headlines)
    database.tokenize_headlines(new_results)

    return formatted_headlines

@app.get("/")
def index():
    return FileResponse("index.html")

@app.get("/search")
def get_search_results(
                key_words: str = Query(...),
                sources: Optional[str] = Query(None),
                domains: Optional[str] = Query(None),
                nodomains: Optional[str] = Query(None),
                oldest: Optional[datetime] = Query(None),
                newest: Optional[datetime] = Query(None),
                language: Optional[str] = Query(None),
                page_number: int = Query(1, ge=1),
                page_size: int = Query(20, ge=1, le=100)):

    #pdb.set_trace()
    search_params = SearchParameters(key_words, page_number, page_size,
                                        sources, domains, nodomains,
                                        oldest, newest, language)

    if USE_TEST_DATA:
        api_results = load_test_data("sports-results.json")
    else:
        api_results = news_endpoint.search(search_params)

    if not isinstance(api_results, list):
        return {"status": api_results}

    database_results = search_database_headlines(database, search_params)

    formatted_headlines = format_headlines(api_results)

    row_ids = database.insert_headlines(formatted_headlines)

    if row_ids:
        results = merge_ids_with_headlines(row_ids, formatted_headlines)
        database.tokenize_headlines(results)

    search_results = rank_search_results(search_params.key_words,
                                            formatted_headlines,
                                            database_results,
                                            search_params.page_size,
                                            search_params.page_number)

    return search_results

@app.get("/sources")
def get_sources():
    return database.get_sources()

@app.get("/headlines")
def get_headlines():
    if USE_TEST_DATA:
        return load_test_data("sources.json")
    return database.get_headlines()

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000)
