DROP TABLE IF EXISTS "{0}".q0_faces CASCADE;
CREATE UNLOGGED TABLE "{0}".q0_faces
(
    face                    int[] PRIMARY KEY,
    weight                  int, -- if it is a distinct face, the weight is the number of represented faces
    maximal_degree_u        int,
    maximal_degree          int,
    weighted_maximal_degree int,
    classical_degree        int
);