CREATE TABLE "{0}".simplices
(
    id       int PRIMARY KEY,
    node_ids int[],
    q int GENERATED ALWAYS AS ( array_length(node_ids, 1) - 1 ) STORED
);
