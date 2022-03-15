CREATE OR REPLACE FUNCTION "{0}".q0_faces_degrees(face_node_ids int[],
                                                  OUT maximal_degree_u int,
                                                  OUT maximal_degree int,
                                                  OUT weighted_maximal_degree int,
                                                  OUT classical_degree int,
                                                  OUT upper_facets int[])
AS
$$
DECLARE
    no_nodes        int;
    nodes_arr       RECORD;
    neighbour_nodes int[] := '{{}}'::int[];
BEGIN
    no_nodes := icount(face_node_ids);
    IF no_nodes != 1 THEN
        RAISE EXCEPTION 'Not a vertex (q=0). Received a face with % nodes', no_nodes;
    END IF;

    SELECT facet_ids, icount(facet_ids)
    INTO upper_facets, maximal_degree_u
    FROM "{0}".nodes WHERE id = face_node_ids[1];

    maximal_degree := maximal_degree_u;
    weighted_maximal_degree := maximal_degree_u;

    -- node-to_1-faces, which is computed with q-faces degrees is already the classical degree
    -- classical_degree := null;

    -- FOR nodes_arr IN (SELECT node_ids FROM "{0}".facets WHERE id = ANY (upper_facets))
    --     LOOP
    --         neighbour_nodes = neighbour_nodes | nodes_arr.node_ids;
    --     END LOOP;
    -- classical_degree := icount(neighbour_nodes) - 1;
END;
$$
LANGUAGE plpgsql
PARALLEL SAFE
IMMUTABLE;

-- CREATE OR REPLACE FUNCTION "{0}".simplicial_degrees(face_node_ids int[],
--                                                     no_face_nodes int,
--                                                     OUT maximal_degree_u int,
--                                                     OUT maximal_degree int,
--                                                     OUT weighted_maximal_degree int,
--                                                     OUT facet_ids_u int[])
-- AS
-- $$
-- WITH facets AS (
--     SELECT unnest(facet_ids) AS facet_id
--     FROM "{0}".nodes
--     WHERE id = ANY (face_node_ids)
-- ),
-- adjacency AS (
--     SELECT facet_id, count(facet_id) AS no_nodes FROM facets GROUP BY facet_id
-- )
-- SELECT count(facet_id) FILTER (WHERE no_nodes = no_face_nodes)::int     AS maximal_degree_u,
--        count(no_nodes)::int                                             AS maximal_degree,
--        sum(no_nodes)::int                                               AS weighted_maximal_degree,
--        array_agg(facet_id) FILTER (WHERE no_nodes = no_face_nodes)::int AS facet_ids_u

-- FROM adjacency
-- $$ LANGUAGE SQL
--     PARALLEL SAFE
--     IMMUTABLE
--     COST 1;

-- CREATE OR REPLACE FUNCTION "{0}".classical_degree(face_node_ids int[],
--                                                   OUT classical_degree int)
-- AS
-- $$
-- DECLARE
--     nodes_facets    int[];
--     nodes_arr       RECORD;
--     neighbour_nodes int[] := '{{}}'::int[];
-- BEGIN
--     nodes_facets := (SELECT facet_ids FROM "{0}".nodes WHERE id = face_node_ids[1]);
--     classical_degree := null;

--     FOR nodes_arr IN (SELECT node_ids FROM "{0}".facets WHERE id = ANY (nodes_facets))
--         LOOP
--             neighbour_nodes = neighbour_nodes | nodes_arr.node_ids;
--         END LOOP;
--     classical_degree := icount(neighbour_nodes) - 1;
-- END;
-- $$
--     LANGUAGE plpgsql
--     PARALLEL SAFE
--     IMMUTABLE
--     COST 1;