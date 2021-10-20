CREATE OR REPLACE FUNCTION "{0}".q0_faces_degrees(face_node_ids int[],
                                                  OUT maximal_degree_u int,
                                                  OUT maximal_degree int,
                                                  OUT weighted_maximal_degree int,
                                                  OUT classical_degree int)
AS
$$
DECLARE
    facets_arr      RECORD;
    nodes_arr       RECORD;
    no_nodes        int;
    adjacent_facets int[] := '{{}}'::int[];
    neighbour_nodes int[] := '{{}}'::int[];
    upper_facets    int[];
    first_item      bool  := true;
BEGIN
    no_nodes := icount(face_node_ids);
    weighted_maximal_degree := 0;
    FOR facets_arr in (SELECT facet_ids, icount(facet_ids) AS no_facets FROM "{0}".nodes WHERE id = ANY (face_node_ids))
        LOOP
            weighted_maximal_degree := weighted_maximal_degree + facets_arr.no_facets;
            adjacent_facets := adjacent_facets + facets_arr.facet_ids;
            IF first_item THEN
                upper_facets := facets_arr.facet_ids;
                first_item := false;
            ELSE
                upper_facets := upper_facets & facets_arr.facet_ids;
            END IF;
        END LOOP;

    maximal_degree := icount(uniq(adjacent_facets));
    maximal_degree_u := icount(upper_facets);
    classical_degree := null;

    IF no_nodes = 1 THEN
        FOR nodes_arr IN (SELECT node_ids FROM "{0}".facets WHERE id = ANY (upper_facets))
            LOOP
                neighbour_nodes = neighbour_nodes | nodes_arr.node_ids;
            END LOOP;
        classical_degree := icount(neighbour_nodes) - 1;
    END IF;
END;
$$
    LANGUAGE plpgsql
    PARALLEL SAFE
    IMMUTABLE
    COST 1;

CREATE OR REPLACE FUNCTION "{0}".simplicial_degrees(face_node_ids int[],
                                                    no_face_nodes int,
                                                    OUT maximal_degree_u int,
                                                    OUT maximal_degree int,
                                                    OUT weighted_maximal_degree int)
AS
$$
WITH facets AS (
    SELECT unnest(facet_ids) AS facet_id
    FROM "{0}".nodes
    WHERE id = ANY (face_node_ids)
),
adjacency AS (
    SELECT facet_id, count(facet_id) AS no_nodes FROM facets GROUP BY facet_id
)
SELECT count(facet_id) FILTER (WHERE no_nodes = no_face_nodes)::int AS maximal_degree_u,
       count(no_nodes)::int                                         AS maximal_degree,
       sum(no_nodes)::int                                           AS weighted_maximal_degree
FROM adjacency
$$ LANGUAGE SQL
    PARALLEL SAFE
    IMMUTABLE
    COST 1;

CREATE OR REPLACE FUNCTION "{0}".classical_degree(face_node_ids int[],
                                                  OUT classical_degree int)
AS
$$
DECLARE
    nodes_facets    int[];
    nodes_arr       RECORD;
    neighbour_nodes int[] := '{{}}'::int[];
BEGIN
    nodes_facets := (SELECT facet_ids FROM "{0}".nodes WHERE id = face_node_ids[1]);
    classical_degree := null;

    FOR nodes_arr IN (SELECT node_ids FROM "{0}".facets WHERE id = ANY (nodes_facets))
        LOOP
            neighbour_nodes = neighbour_nodes | nodes_arr.node_ids;
        END LOOP;
    classical_degree := icount(neighbour_nodes) - 1;
END;
$$
    LANGUAGE plpgsql
    PARALLEL SAFE
    IMMUTABLE
    COST 1;