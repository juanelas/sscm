CREATE UNLOGGED TABLE "{0}".papers_authors AS
SELECT paper_id,
       an.id AS author_id
FROM (SELECT id AS paper_id, unnest(authors) AS author_name FROM "{0}".papers pn) t
         INNER JOIN "{0}".authors AS an ON author_name = an.name;
CREATE INDEX papers_authors_paper_id_hash_idx ON "{0}".papers_authors (paper_id);
CREATE INDEX papers_authors_author_id_hash_idx ON "{0}".papers_authors (author_id);
