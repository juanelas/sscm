-- UPDATE "{0}".q0_faces
-- SET (maximal_degree_u,
--      maximal_degree,
--      weighted_maximal_degree,
--      classical_degree) = (
--     SELECT sd.maximal_degree_u,
--            sd.maximal_degree,
--            sd.weighted_maximal_degree,
--            cd.classical_degree
--     FROM "{0}".simplicial_degrees(face, 1) AS sd,
--     "{0}".classical_degree(face) AS cd
--     );

-- DROP INDEX IF EXISTS q0_faces_face_idx CASCADE;
-- ALTER TABLE "{0}".q0_faces DROP CONSTRAINT q0_faces_pkey;
--
-- UPDATE "{0}".q0_faces
-- SET (maximal_degree_u,
--      maximal_degree,
--      weighted_maximal_degree,
--      classical_degree) = (
--     SELECT maximal_degree_u,
--            maximal_degree,
--            weighted_maximal_degree,
--            classical_degree
--     FROM "{0}".q0_faces_degrees(face));
--
-- ALTER TABLE "{0}".q0_faces ADD CONSTRAINT q0_faces_pkey PRIMARY KEY (face);

DROP TABLE IF EXISTS "{0}".q0_faces_tmp;

CREATE UNLOGGED TABLE "{0}".q0_faces_tmp AS (
    SELECT f.face, d.maximal_degree_u, d.maximal_degree, d.weighted_maximal_degree, d.classical_degree
    FROM "{0}".q0_faces AS f,
        LATERAL "{0}".q0_faces_degrees(f.face) AS d
);

-- UPTADE TABLE "{0}".q0_faces_tmp
-- SET classical_degree = (
--     SELECT count(DISTINCT fn1.node_id) - 1 AS classical_degree
--     FROM "{0}".facets_nodes fn1
--     INNER JOIN "{0}".facets_nodes fn2 ON (fn1.facet_id = fn2.facet_id)
--     WHERE fn2.node_id IN (SELECT face[1] FROM "{0}".q0_faces)
-- );


DROP TABLE "{0}".q0_faces CASCADE;

ALTER TABLE "{0}".q0_faces_tmp RENAME TO q0_faces;

ALTER TABLE "{0}".q0_faces ADD CONSTRAINT q0_faces_pkey PRIMARY KEY (face);