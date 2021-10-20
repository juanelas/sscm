CREATE UNLOGGED TABLE "{0}".arxiv_papers
(
    title   text NOT NULL,
    authors varchar(128)[],
    dates   date[]
);
CREATE INDEX arxiv_papers_title_hash_idx ON "{0}".arxiv_papers USING HASH (title);

CREATE UNLOGGED TABLE "{0}".papers
(
    id    int UNIQUE GENERATED ALWAYS AS IDENTITY,
    title text PRIMARY KEY,
    authors varchar(128)[],
    dates date[]
);
CREATE INDEX papers_title_hash_idx ON "{0}".papers USING HASH (title);

CREATE UNLOGGED TABLE "{0}".discarded_papers
(
    title   text PRIMARY KEY,
    authors varchar(128)[],
    dates   date[],
    reason  varchar
);

CREATE UNLOGGED TABLE "{0}".authors
(
    id        int UNIQUE GENERATED ALWAYS AS IDENTITY,
    name      varchar(128) PRIMARY KEY,
    alt_names varchar(128)[] NOT NULL
);

CREATE UNLOGGED TABLE "{0}".discarded_authors
(
    name        varchar(128) NOT NULL,
    paper_title text         NOT NULL
);

