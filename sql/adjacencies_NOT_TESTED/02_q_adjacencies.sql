-- {0} is the dataset
-- {1} is q-1
-- {2} is q

DROP TABLE IF EXISTS "{0}".q{2}_adjacencies CASCADE;
-- CREATE UNLOGGED TABLE "{0}".q{2}_adjacencies
-- (
--     face           int[] PRIMARY KEY,
--     ufacets        int[], -- the facets that contain this face
-- );

CREATE UNLOGGED TABLE "{0}".q{2}_adjacencies AS (
    WITH qf AS (
        SELECT face, ufacets
        FROM "{0}".q{1}_adjacencies   -- use the current q-1
    )
    SELECT
        qf.face + ns.id as face,
        qf.ufacets & ns.facet_ids as ufacets
    FROM "{0}".facets_nodes fn
    JOIN "{0}".nodes ns ON fn.node_id = ns.id,
        qf
    WHERE
        fn.facet_id = ANY (qf.ufacets)
        AND #(ns.facet_ids & qf.ufacets) > 1 -- if the face and the neighbor share more than one ufacet, they generate and adjacency
        AND NOT (ns.id = ANY(qf.face))
)

ALTER TABLE "{0}".q{2}_adjacencies ADD CONSTRAINT q{2}_adjacencies_pkey PRIMARY KEY (face);
