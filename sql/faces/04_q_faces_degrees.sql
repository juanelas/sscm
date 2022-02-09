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
    SELECT f.face, f.weight, d.maximal_degree_u, d.maximal_degree, d.weighted_maximal_degree
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
            SELECT count(facet_id) FILTER (WHERE no_nodes = {1} + 1)::int       AS maximal_degree_u,
                   count(no_nodes)::int                                         AS maximal_degree,
                   sum(no_nodes)::int                                           AS weighted_maximal_degree
            FROM adjacency
        ) AS d
);

DROP TABLE "{0}".q{1}_faces CASCADE;

ALTER TABLE "{0}".q{1}_faces_tmp RENAME TO q{1}_faces;

ALTER TABLE "{0}".q{1}_faces ADD CONSTRAINT q{1}_faces_pkey PRIMARY KEY (face);