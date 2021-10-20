CREATE TABLE "{0}".usimplices_nodes AS
SELECT id               AS usimplex_id,
       unnest(node_ids) AS node_id,
       weight           AS usimplex_weight
FROM "{0}".usimplices;
-- ALTER TABLE "{0}".usimplices_nodes ADD CONSTRAINT usimplices_nodes_pkey PRIMARY KEY (usimplex_id, node_id);
CREATE INDEX usimplices_nodes_usimplex_id_idx ON "{0}".usimplices_nodes (usimplex_id);
CREATE INDEX usimplices_nodes_node_id_idx ON "{0}".usimplices_nodes (node_id);

CREATE TABLE "{0}".nodes AS
SELECT node_id                   AS id,
       array_agg(usimplex_id)    AS usimplex_ids,
       sum(usimplex_weight)::int AS weight
FROM "{0}".usimplices_nodes
GROUP BY node_id;
ALTER TABLE "{0}".nodes ADD CONSTRAINT nodes_pkey PRIMARY KEY (id);
