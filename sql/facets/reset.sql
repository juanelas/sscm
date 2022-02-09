DROP INDEX IF EXISTS "{0}".simplices_unique_id_idx;
DROP INDEX IF EXISTS "{0}".simplices_sorted_node_ids_idx;
ALTER TABLE "{0}".simplices
    DROP COLUMN IF EXISTS sorted_node_ids;
ALTER TABLE "{0}".simplices
    DROP COLUMN IF EXISTS unique_id;
DROP TABLE IF EXISTS "{0}".usimplices CASCADE;
DROP TABLE IF EXISTS "{0}".usimplices_nodes CASCADE;
DROP TABLE IF EXISTS "{0}".usimplices_dnodes CASCADE;
DROP TABLE IF EXISTS "{0}".nodes CASCADE;
DROP TABLE IF EXISTS "{0}".facets CASCADE;
DROP TABLE IF EXISTS "{0}".facets_nodes CASCADE;
DROP TABLE IF EXISTS "{0}".dnodes CASCADE;
DROP TABLE IF EXISTS "{0}".dnodes_nodes CASCADE;
DROP TABLE IF EXISTS "{0}".dfacets CASCADE;
DROP TABLE IF EXISTS "{0}".facets_dnodes CASCADE;

DROP FUNCTION IF EXISTS "{0}".is_facet CASCADE;