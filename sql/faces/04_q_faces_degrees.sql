-- UPDATE "{0}".q{1}_faces
-- SET (maximal_degree_u,
--      maximal_degree,
--      weighted_maximal_degree_u,
--      weighted_maximal_degree,
--      classical_degree) = (
--     SELECT maximal_degree_u,
--            maximal_degree,
--            weighted_maximal_degree_u,
--            weighted_maximal_degree,
--            classical_degree
--     FROM "{0}".face_degrees(face));

-- ALTER TABLE "{0}".q{1}_faces DROP CONSTRAINT q{1}_faces_pkey;
--
-- UPDATE "{0}".q{1}_faces
-- SET (maximal_degree_u,
--      maximal_degree,
--      weighted_maximal_degree) = (
--     SELECT maximal_degree_u,
--            maximal_degree,
--            weighted_maximal_degree
--     FROM "{0}".simplicial_degrees(face, q + 1));
--
-- ALTER TABLE "{0}".q{1}_faces ADD CONSTRAINT q{1}_faces_pkey PRIMARY KEY (face);

DROP TABLE IF EXISTS "{0}".q{1}_faces_tmp;

-- CREATE UNLOGGED TABLE "{0}".q{1}_faces_tmp AS (
--     SELECT f.face, d.maximal_degree_u, d.maximal_degree, d.weighted_maximal_degree
--     FROM "{0}".q{1}_faces AS f,
--         LATERAL "{0}".simplicial_degrees(f.face, {1} + 1) AS d
-- );

CREATE UNLOGGED TABLE "{0}".q{1}_faces_tmp AS (
    SELECT f.face, f.weight, d.upper_facets, d.maximal_degree_u, d.maximal_degree, d.weighted_maximal_degree
    FROM "{0}".q{1}_faces AS f,
        LATERAL (
            WITH facets AS (
                SELECT unnest(facet_ids) AS facet_id
                FROM "{0}".nodes
                WHERE id = ANY (f.face)
            ),
            adjacency AS (
                SELECT facet_id, count(facet_id) AS no_nodes FROM facets GROUP BY facet_id
            )
            SELECT count(facet_id) FILTER (WHERE no_nodes = {1} + 1)     AS maximal_degree_u,
                   count(no_nodes)                                       AS maximal_degree,
                   sum(no_nodes)                                         AS weighted_maximal_degree,
                   array_agg(facet_id) FILTER (WHERE no_nodes = {1} + 1) AS upper_facets
            FROM adjacency
        ) AS d
);

DROP TABLE "{0}".q{1}_faces CASCADE;

ALTER TABLE "{0}".q{1}_faces_tmp RENAME TO q{1}_faces;

ALTER TABLE "{0}".q{1}_faces ADD CONSTRAINT q{1}_faces_pkey PRIMARY KEY (face);


-- Let's initialize the degree to 0
UPDATE "{0}".q0_faces SET node_to_qfaces_degree[{1}] = 0;

-- we get a list of all the node_ids in the faces. node_ids in different faces will be repeated
WITH nodes AS (
    SELECT unnest(face) AS node_id FROM "{0}".q{1}_faces
),
-- grouping by node_id and counting how many times a node_id appears give us the amount of faces with the defined q every node is in.
d AS (
    SELECT ARRAY[nodes.node_id] as face, count(node_id) as deg FROM nodes GROUP BY node_id
)
--- and we just update the node_to_qfaces_degree for that q with the obtained values
UPDATE "{0}".q0_faces f SET node_to_qfaces_degree[{1}] = d.deg
FROM d 
WHERE f.face=d.face;
