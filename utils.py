import re
import json
from unidecode import unidecode

def get_delimiters(delimiters):
    return "|".join([re.escape(d) for d in delimiters])

def format_headlines(raw_headlines):
    """ Takes in as parameter a list of JSON formatted dictionaries and returns a list of tuples. """
    formatted_data = []
    for headline in raw_headlines:
        source_id = headline.get("source", {}).get("id", "")
        source_name = headline.get("source", {}).get("name", "")
        author = headline.get("author", "")
        title = headline.get("title", "")
        description = headline.get("description", "")
        url = headline.get("url", "")
        thumbnail_url = headline.get("urlToImage", "")
        published_timestamp = headline.get("publishedAt", "")
        formatted_data.append((source_id, source_name, author, title, description, url, thumbnail_url, published_timestamp))
    return formatted_data

def load_test_data(source="top-stories.json"):
    with open(source, encoding='utf-8') as fp:
        return json.load(fp)["articles"]

def merge_ids_with_headlines(row_ids, headlines):
    return [(row_id[0], *row) for row_id, row in zip(row_ids, headlines)]

def tokenize_headline(headline):
    """ Tokenizes the headline using the source id, name, author, article
        description, title and URL as parameters. Returns a tuple containing the
        database id for the headline and a list of tokens found in the text. """
    tokens = []

    body_delimiters = get_delimiters([' ', "'", '(', ')', '-', ',', ':', ';', '.', '?', '!', '_'])
    url_delimiters = get_delimiters(['.', '-', '_', '/', ':'])

    for i in range(1, 7):
        if isinstance(headline[i], str):
            if i < 6:
                tokens.extend(re.split(body_delimiters, unidecode(headline[i]).lower()))
            else:
                tokens.extend(re.split(url_delimiters, headline[i]))
    return headline[0], list({t for t in tokens if t != ''})

def format_sources(raw_sources):
    formatted_data = []
    for source in raw_sources:
        source_id = source.get("id", "")
        name = source.get("name", "")
        url = source.get("url", "")
        language = source.get("language", "")
        category = source.get("category", "")
        country = source.get("country", "")
        description = source.get("description", "")
        formatted_data.append((source_id, name, url, language, category, country, description))
    return formatted_data
