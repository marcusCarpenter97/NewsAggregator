import json
import urllib3
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

        url = urllib3.util.parse_url(target_url)
        response = requests.get(url, headers = {"Authorization": self.api_key}, timeout=5)

        if response.status_code == 200:
            return json.loads(response.text).get("articles")[:n]
        return response.status_code

    def get_sources(self):
        endpoint = "top-headlines/sources"

        target_url = f"{BASE_URL}{endpoint}"

        url = urllib3.util.parse_url(target_url)
        response = requests.get(url, headers = {"Authorization": self.api_key}, timeout=5)

        if response.status_code == 200:
            return json.loads(response.text).get("sources", [])
        return response.status_code

    def search(self, search_params, sortby='relevancy', max_len=500):

        params = {'page': search_params.page_number}

        results = []

        target_url = f"{BASE_URL}everything"

        if len(search_params.key_words) > max_len:
            return "Key words parameter is too long, it must be shorter than 500 characters."

        target_url = f"{target_url}?q={search_params.key_words}"

        if search_params.sources and len(search_params.sources.split(',')) <= 20:
            target_url = f"{target_url}&sources={search_params.sources}"

        if search_params.domains:
            target_url = f"{target_url}&domains={search_params.domains}"

        if search_params.nodomains:
            target_url = f"{target_url}&excludeDomains={search_params.nodomains}"

        if search_params.oldest:
            target_url = f"{target_url}&from={search_params.oldest}"

        if search_params.newest:
            target_url = f"{target_url}&to={search_params.newest}"

        if search_params.language:
            target_url = f"{target_url}&language={search_params.language}"

        target_url = f"{target_url}&sortBy={sortby}&pageSize={search_params.page_size}"

        while True:
            url = urllib3.util.parse_url(target_url)
            response = requests.get(url, params = params, headers = {"Authorization": self.api_key}, timeout=5)

            if response.status_code == 200:
                results.extend(response.json().get("articles", []))
                params['page'] += 1
            else:
                logging.warning("Error fetching data from endpoint: %s - %s", response.status_code, response.reason)
            return results
