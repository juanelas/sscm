-- DROP FUNCTION IF EXISTS "{0}".is_facet CASCADE;
-- CREATE FUNCTION "{0}".is_facet(int[]) RETURNS BOOLEAN
-- AS
-- $$
-- WITH a AS (
--     SELECT unnest(usimplex_ids) AS usimplex_id
--     FROM "{0}".dnodes
--     WHERE id = ANY ($1)
--     GROUP BY usimplex_id
--     HAVING count(id) = array_length($1, 1)
-- )
-- SELECT CASE WHEN count(usimplex_id) > 1 THEN FALSE ELSE TRUE END
-- FROM a;
-- $$
--     LANGUAGE SQL
--     PARALLEL SAFE
--     IMMUTABLE;

DROP FUNCTION IF EXISTS "{0}".is_facet CASCADE;
CREATE FUNCTION "{0}".is_facet(int[]) RETURNS bool AS
$$
DECLARE
    usimplex_arr RECORD;
    intersection int[];
    first        bool := true;
BEGIN
    FOR usimplex_arr in (SELECT usimplex_ids FROM "{0}".nodes WHERE id = ANY ($1))
        LOOP
            IF first THEN
                intersection := usimplex_arr.usimplex_ids;
                first := false;
            ELSE
                intersection := intersection & usimplex_arr.usimplex_ids;
            END IF;
        END LOOP;
    RETURN (SELECT CASE WHEN icount(intersection) > 1 THEN FALSE ELSE TRUE END);
END;
$$
    LANGUAGE plpgsql
    PARALLEL SAFE
    IMMUTABLE;

-- DROP FUNCTION IF EXISTS "{0}".is_facet CASCADE;
-- CREATE FUNCTION "{0}".is_facet(int[]) RETURNS BOOLEAN
-- AS
-- $$
-- WITH a AS (
--     SELECT usimplex_id
--     FROM "{0}".usimplices_dnodes
--     WHERE dnode_id = ANY ($1)
--     GROUP BY usimplex_id
--     HAVING count(dnode_id) = array_length($1, 1)
-- )
-- SELECT CASE WHEN count(usimplex_id) > 1 THEN FALSE ELSE TRUE END
-- FROM a;
-- $$
--     LANGUAGE SQL
--     PARALLEL SAFE
--     IMMUTABLE;

DROP TABLE IF EXISTS "{0}".facets;
CREATE TABLE "{0}".facets AS
SELECT id, node_ids, q
-- SELECT id, node_ids, dnode_ids, q, icount(dnode_ids) - 1 AS dq
FROM "{0}".usimplices
WHERE "{0}".is_facet(node_ids);
CREATE INDEX facets_id_idx ON "{0}".facets (id);
CREATE INDEX facets_q_idx ON "{0}".facets (q);

-- UPDATE "{0}".usimplices
-- SET is_facet = "{0}".is_facet(dnode_ids);
-- CREATE INDEX usimplices_is_facet_idx ON "{0}".usimplices (is_facet);
--
-- CREATE MATERIALIZED VIEW "{0}".facets AS
-- SELECT id, node_ids, dnode_ids, q, icount(dnode_ids) as dq
-- FROM "{0}".usimplices
-- WHERE is_facet;

DROP TABLE IF EXISTS "{0}".facets_nodes CASCADE;
CREATE TABLE "{0}".facets_nodes AS
SELECT id               AS facet_id,
       unnest(node_ids) AS node_id
FROM "{0}".facets;
CREATE INDEX facets_nodes_facet_id ON "{0}".facets_nodes (facet_id);
CREATE INDEX facets_nodes_node_id ON "{0}".facets_nodes (node_id);


ALTER TABLE "{0}".nodes
    ADD COLUMN IF NOT EXISTS facet_ids int[];
UPDATE "{0}".nodes
SET facet_ids = fn.facet_ids
FROM (
         SELECT node_id, array_agg(facet_id) AS facet_ids
         FROM "{0}".facets_nodes
         GROUP BY node_id
     ) fn
WHERE node_id = id;