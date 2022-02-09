CREATE TABLE "{0}".dnodes AS
SELECT node_ids[1] as id,
       node_ids,
       facet_ids
FROM (
         SELECT array_agg(id) AS node_ids,
                facet_ids
         FROM "{0}".nodes
         GROUP BY facet_ids
     ) n;
CREATE INDEX dnodes_id_idx ON "{0}".dnodes (id);

CREATE TABLE "{0}".dnodes_nodes AS
SELECT  id as dnode_id,
        unnest(node_ids) as node_id
FROM "{0}".dnodes;
-- ALTER TABLE "{0}".dnodes_nodes ADD CONSTRAINT dnodes_nodes_pkey PRIMARY KEY (dnode_id, node_id);
-- CREATE INDEX IF NOT EXISTS nodes_dnodes_dnode_id_idx ON "{0}".nodes_dnodes (dnode_id);
CREATE INDEX IF NOT EXISTS dnodes_nodes_node_id_idx ON "{0}".dnodes_nodes (node_id);

ALTER TABLE "{0}".facets
    ADD COLUMN dnode_ids int[];
UPDATE "{0}".facets
SET dnode_ids = (WITH dnode_ids AS (SELECT DISTINCT ON (dnode_id) dnode_id
                                    FROM "{0}".dnodes_nodes
                                    WHERE node_id = ANY (node_ids))
                 SELECT array_agg(dnode_id)
                 FROM dnode_ids);
ALTER TABLE "{0}".facets
    ADD COLUMN dq int GENERATED ALWAYS AS ( icount(dnode_ids) - 1 ) STORED;

UPDATE "{0}".dnodes
SET facet_ids = fn.facet_ids
FROM (
         SELECT node_id, array_agg(facet_id) AS facet_ids
         FROM "{0}".facets_nodes
         GROUP BY node_id
     ) fn
WHERE node_id = id;
