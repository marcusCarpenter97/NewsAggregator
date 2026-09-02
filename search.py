import re
import pdb
import math
from collections import defaultdict
from unidecode import unidecode
from utils import tokenize_headline

def tokenize(query):
    delimiters = [re.escape(d) for d in ['"', '-', '+', '(', ')', 'AND', 'OR', 'NOT', ' ']]
    tokens = [result for result in re.split("|".join(delimiters), query) if result]
    return [unidecode(t).lower() for t in tokens]

def search_database_headlines(db, params):

    tokens = tokenize(params.key_words)

    article_ids = [i[0] for i in db.search_tokens(tokens)]

    articles = db.retreive_from_dates(params.oldest, params.newest, article_ids)

    selected_source_ids = db.filter_articles_by_sources(params.sources, params.domains, params.nodomains, params.language)

    if not selected_source_ids:
        return articles

    result = []
    for article in articles:
        if article[0] in selected_source_ids:
            result.append(article)
    return result

def rank_search_results(search_query, api_results, db_results, max_results, page, k1=1.5, b=0.75, t=0.001):

    query_tokens = tokenize(search_query)

    all_results = []
    all_results.extend(api_results)
    all_results.extend(db_results)

    if not all_results:
        return []

    return_count = (page - 1) * max_results

    headline_count = len(all_results)

    tokenized_documents = [tokenize_headline(headline) for headline in all_results]

    avg_doc_len = sum(len(document[1]) for document in tokenized_documents) / headline_count

    scores = defaultdict(float)

    for token in query_tokens:
        documents_containing_token = [document for document in tokenized_documents if token in document[1]]
        document_frequency_for_token = len(documents_containing_token)
        idf = math.log((headline_count - document_frequency_for_token + 0.5) / (document_frequency_for_token + 0.5)) + t

        for document in documents_containing_token:
            doc_len = len(document[1])
            denom = document_frequency_for_token + k1 * (1 - b + b * (doc_len / avg_doc_len))
            tf_weight = (document_frequency_for_token * (k1 + 1)) / denom

            scores[document[0]] += (idf * tf_weight)

    scored_results = list(dict(sorted(scores.items(), key=lambda item: item[1], reverse=True)).keys())

    selected_ids = scored_results[return_count:return_count+max_results]
    return sorted([headline for headline in all_results if headline[0] in selected_ids], key=lambda item: selected_ids.index(item[0]))
