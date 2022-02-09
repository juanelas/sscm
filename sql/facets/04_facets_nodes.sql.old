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

UPDATE "{0}".dnodes
SET facet_ids = fn.facet_ids
FROM (
         SELECT node_id, array_agg(facet_id) AS facet_ids
         FROM "{0}".facets_nodes
         GROUP BY node_id
     ) fn
WHERE node_id = id;