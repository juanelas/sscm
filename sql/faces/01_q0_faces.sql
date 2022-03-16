DROP TABLE IF EXISTS "{0}".q0_faces CASCADE;
CREATE UNLOGGED TABLE "{0}".q0_faces
(
    face                    int[] PRIMARY KEY,
    weight                  int, -- if it is a distinct face, the weight is the number of represented faces
    upper_facets            int[], -- the facets that contain this face
    maximal_degree_u        int,
    maximal_degree          int,
    weighted_maximal_degree int,
    node_to_qfaces_degree   int[] -- is an array where the index is q
);