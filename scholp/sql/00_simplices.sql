CREATE UNLOGGED TABLE"{0}".simplices
(
    id       int GENERATED ALWAYS AS IDENTITY,
    node_ids int[],
    q int GENERATED ALWAYS AS ( array_length(node_ids, 1) - 1 ) STORED
);
