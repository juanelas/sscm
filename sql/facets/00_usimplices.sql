CREATE INDEX IF NOT EXISTS simplices_q_idx ON "{0}".simplices (q);

ALTER TABLE "{0}".simplices
    ADD COLUMN sorted_node_ids int[];
ALTER TABLE "{0}".simplices
    ADD COLUMN unique_id uuid; -- md5(array_to_string(sorted_node_ids, ','))::uuid
UPDATE "{0}".simplices
SET (sorted_node_ids, unique_id) = (SELECT sorted_node_ids, id FROM sorted_simplex(node_ids));

CREATE INDEX simplices_unique_id_idx ON "{0}".simplices (unique_id);


CREATE TABLE "{0}".usimplices AS -- Unique simplices. 1,4,3 = 3,1,4 = 1,3,4
SELECT unique_id                        AS unique_id,
       sorted_node_ids                  AS node_ids,
       count(id)::int                   AS weight, -- number of simplices in this usimplex
       icount(sorted_node_ids)::int - 1 AS q
FROM "{0}".simplices
GROUP BY unique_id, sorted_node_ids;

ALTER TABLE "{0}".usimplices
    ADD COLUMN id int GENERATED ALWAYS AS IDENTITY;

CREATE INDEX usimplices_unique_id_idx ON "{0}".usimplices (id);