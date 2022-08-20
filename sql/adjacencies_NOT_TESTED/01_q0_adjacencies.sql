DROP TABLE IF EXISTS "{0}".q0_adjacencies CASCADE;
-- CREATE UNLOGGED TABLE "{0}".q0_adjacencies
-- (
--     face           int[] PRIMARY KEY,
--     ufacets        int[], -- the facets that contain this face
-- );

CREATE UNLOGGED TABLE "{0}".q0_adjacencies AS (
  SELECT ARRAY[id] AS face, facet_ids AS ufacets
  FROM "{0}".nodes
  WHERE icount(facet_ids) > 1 -- only nodes in more than one facet generate adjacencies
)

ALTER TABLE "{0}".q0_adjacencies ADD CONSTRAINT q0_adjacencies_pkey PRIMARY KEY (face);
