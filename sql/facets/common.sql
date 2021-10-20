CREATE EXTENSION IF NOT EXISTS intarray;

CREATE OR REPLACE FUNCTION sorted_simplex(
    node_ids int[],
    OUT id uuid,
    OUT sorted_node_ids int[]
    )
AS $$
BEGIN
    sorted_node_ids := uniq(sort(node_ids));
    id := md5(array_to_string(sorted_node_ids, ','))::uuid;
END;
$$
    LANGUAGE plpgsql
    PARALLEL SAFE
    IMMUTABLE;

CREATE OR REPLACE FUNCTION unique_simplices_before_trigger_fn() RETURNS trigger AS
$unique_simplices_trigger$
BEGIN
    SELECT id, sorted_node_ids
        INTO NEW.id, NEW.node_ids
    FROM sorted_simplex(NEW.node_ids);
    RETURN NEW;
END;
$unique_simplices_trigger$
    LANGUAGE plpgsql
    PARALLEL SAFE
    IMMUTABLE;