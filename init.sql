CREATE TABLE IF NOT EXISTS public.headlines (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id TEXT,
    source_name TEXT,
    author TEXT,
    article_title TEXT,
    subtitle TEXT,
    article_url TEXT NOT NULL UNIQUE,
    thumbnail_url TEXT,
    publication_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW());

CREATE TABLE IF NOT EXISTS public.sources (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id TEXT NOT NULL UNIQUE,
    name TEXT,
    url TEXT,
    language TEXT,
    category TEXT,
    country TEXT,
    description TEXT);

CREATE TABLE IF NOT EXISTS public.tokens (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    headline_id BIGINT REFERENCES headlines(id),
    token TEXT NOT NULL UNIQUE);
