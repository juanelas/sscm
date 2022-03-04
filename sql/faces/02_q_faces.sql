DROP TABLE IF EXISTS "{0}".q{1}_faces CASCADE;
CREATE UNLOGGED TABLE "{0}".q{1}_faces
(
    face                    int[] PRIMARY KEY,
    weight                  int, -- if it is a distinct face, the weight is the number of represented faces
    upper_facets            int[], -- the facets that contain this face
    maximal_degree_u        int,
    maximal_degree          int,
    weighted_maximal_degree int
);