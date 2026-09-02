import json
import logging
import requests

BASE_URL = "https://newsapi.org/v2/"

class NewsEndpoint:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_top_stories(self, locale="us", n=5):
        """ Retunrs a list containing N results from the top stories API. """
        endpoint = "top-headlines"

        target_url = f"{BASE_URL}{endpoint}?country={locale}"

        response = requests.get(target_url, headers = {"Authorization": self.api_key}, timeout=5)

        if response.status_code == 200:
            return json.loads(response.text).get("articles")[:n]
        return response.status_code

    def get_sources(self):
        endpoint = "top-headlines/sources"

        target_url = f"{BASE_URL}{endpoint}"

        response = requests.get(target_url, headers = {"Authorization": self.api_key}, timeout=5)

        if response.status_code == 200:
            return json.loads(response.text).get("sources", [])
        return response.status_code

    def search(self, search_params, sortby='relevancy', max_len=500):

        params = {'page': search_params.page_number}

        results = []

        url = f"{BASE_URL}everything"

        if len(search_params.key_words) > max_len:
            return "Key words parameter is too long, it must be shorter than 500 characters."

        url = f"{url}?q={search_params.key_words}"

        if search_params.sources and len(search_params.sources.split(',')) <= 20:
            url = f"{url}&sources={search_params.sources}"

        if search_params.domains:
            url = f"{url}&domains={search_params.domains}"

        if search_params.nodomains:
            url = f"{url}&excludeDomains={search_params.nodomains}"

        if search_params.oldest:
            url = f"{url}&from={search_params.oldest}"

        if search_params.newest:
            url = f"{url}&to={search_params.newest}"

        if search_params.language:
            url = f"{url}&language={search_params.language}"

        url = f"{url}&sortBy={sortby}&pageSize={search_params.page_size}"

        while True:
            response = requests.get(url, params = params, headers = {"Authorization": self.api_key}, timeout=5)

            if response.status_code == 200:
                results.extend(response.json().get("articles", []))
                params['page'] += 1
            else:
                logging.warning("Error fetching data from endpoint: %s - %s", response.status_code, response.reason)
                return results
