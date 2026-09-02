""" Module for the database class. """
import os
import logging
import psycopg
from psycopg_pool import ConnectionPool
from utils import tokenize_headline

class DB:

    def __init__(self):
        self.pool = ConnectionPool(conninfo=os.environ["DATABASE_URL"], min_size=1, max_size=10)

    def insert_headlines(self, headlines):
        """
            This method inserts one or more formatted headline objects into the databse and
            takes as input a list of tuples.
        """

        if not headlines or not (isinstance(headlines, (tuple, list)) and isinstance(headlines[0], (tuple, list))):
            return []

        num_params = 8

        query = """ INSERT INTO headlines ( source_id, source_name, author, article_title, subtitle, article_url, thumbnail_url, publication_date ) VALUES {} ON CONFLICT (article_url) DO NOTHING RETURNING id, article_url; """

        # Create placeholder group.
        values_template = "(" + ", ".join(["%s"] * num_params) + ")"
        values_clause = ", ".join([values_template] * len(headlines))

        params = [value for headline in headlines for value in headline]

        query = query.format(values_clause)

        with self.pool.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    result = cur.fetchall()

                conn.commit()
                return result

            except psycopg.Error as err:
                conn.rollback()
                logging.error("An SQL error occured while inserting headlines: %s", err)
                raise

    def tokenize_headlines(self, headlines):
        """
            Bulk inserts tokens for one or more news articles into
            the database.
            Takes as parameter a list of tuples and expects headlines to
            contain the database id.
            Returns a set of all tokens inserted into the database or
            an empty set in case no headlines could not be processed.
        """

        sql_query = """INSERT INTO tokens (headline_id, token)
                         VALUES (%s, %s) ON CONFLICT (token) DO NOTHING;"""

        all_tokens = set()

        #pdb.set_trace()
        for headline in headlines:
            headline_id, headline_tokens = tokenize_headline(headline)
            all_tokens.update(headline_tokens)

            data = list(zip([headline_id] * len(headline_tokens), headline_tokens))

            with self.pool.connection() as conn:
                try:
                    with conn.cursor() as cur:
                        cur.executemany(sql_query, params_seq=data)
                except psycopg.Error as err:
                    logging.error("An SQL error occured when tokenizing headlines: %s", err)
                    conn.rollback()
                    return set()
        return all_tokens

    def search_tokens(self, search_tokens):
        """
            Retreives the headline ids for tokens.
            Takes as parameter a tuple of strings.
            Return a list of tuples.
        """

        sql_query = """SELECT headline_id FROM tokens WHERE token = ANY(%s);"""

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query, (search_tokens,))
                return cur.fetchall()

    def retreive_from_dates(self, start_date, end_date, ids=None):
        """
            Selects headlines from between two dates with an optional parameter
            to restrict the results by id. Dates should be ISO formatted strings.
            ids must be a tuple if ints. Returns a list of tuples containing the headlines.
        """
        sql_query = """SELECT id, source_id, source_name, author, article_title, subtitle, article_url, thumbnail_url, publication_date FROM headlines
                        WHERE publication_date >= COALESCE(%s, (SELECT MIN(publication_date) FROM headlines))
                        AND publication_date <= COALESCE(%s, (SELECT MAX(publication_date) FROM headlines))"""

        if isinstance(ids, list) and len(ids) > 0 and isinstance(ids[0], int):
            sql_query += " AND id = ANY(%s);"
            params = [start_date, end_date, ids]
        else:
            sql_query += ";"
            params = [start_date, end_date]

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query, params)
                return cur.fetchall()

    def filter_articles_by_sources(self, sources, domains_to_include, domains_to_exclude, language):

        sql_query = """SELECT source_id FROM sources WHERE name = ANY(%s) AND url = ANY(%s) AND NOT (url = ANY(%s)) AND language = (%s);"""

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query, (sources, domains_to_include, domains_to_exclude, language))
                return cur.fetchall()

    def get_headline_id_from_url(self, url):
        """ Takes as parameter a list of tuples containing the urls. """
        sql_query = """SELECT id, article_url FROM headlines WHERE article_url = ANY(%s);"""

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query, (url,))
                return cur.fetchall()

    def insert_sources(self, sources):
        insert_query = """INSERT INTO sources (source_id, name, url, language, category, country, description)
                            VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (source_id) DO NOTHING;"""

        with self.pool.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.executemany(insert_query, params_seq=sources)
                conn.commit()
            except psycopg.Error as err:
                logging.error("The following SQL error occured when inserting sources: %s", err)
                conn.rollback()

    def get_sources(self):
        sql_query = """SELECT * FROM sources;"""

        with self.pool.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql_query)
                    return cur.fetchall()
            except psycopg.Error as err:
                logging.error("Error retreiving sources from database. %s", err)
        return None

    def clear_database(self):
        sql_query = """
                    TRUNCATE TABLE
                        headlines,
                        sources,
                        tokens
                    RESTART IDENTITY CASCADE;
                    """

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query)
        return True

    def get_headlines(self):
        sql_query = """SELECT * FROM headlines;"""

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query)
                return cur.fetchall()

    def get_headlines_by_id(self, ids):
        sql_query = """SELECT * FROM headlines WHERE id = ANY(%s);"""

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query, (ids,))
                return cur.fetchall()
