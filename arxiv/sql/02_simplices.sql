CREATE UNLOGGED TABLE "{0}".simplices AS
SELECT paper_id             AS id,
       array_agg(author_id) AS node_ids,
       count(author_id) - 1 AS q
FROM "{0}".papers_authors
GROUP BY paper_id;
