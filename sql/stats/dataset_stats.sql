SELECT '{0}'                               AS "dataset",
       no_simplices                        AS "simplices",
       no_usimplices_with_order            AS "unique simplices with order ({{1,2,3}} != {{2,3,1}})",
       no_usimplices                       AS "unique simplices (usimplices)",
       no_facets                           AS "facets",
       no_facets::float / no_simplices     AS "facets / simplices",
       no_facets::float / no_usimplices    AS "facets / usimplices",
       no_nodes                            AS "nodes",
       no_dnodes                           AS "distinct nodes (dnodes)",
       no_dnodes::float / no_nodes         AS "dnodes / nodes",
       simplices_qmostfrequent + 1         AS "nodes per simplex: most frequent value",
       simplices_qstd                      AS "nodes per simplex: std",
       simplices_qavg + 1                  AS "nodes per simplex: avg",
       simplices_qmin + 1                  AS "nodes per simplex: min",
       simplices_qpercentiles[1]::int + 1  AS "nodes per simplex: median",
       simplices_qpercentiles[2]::int + 1  AS "nodes per simplex: percentile 95",
       simplices_qpercentiles[3]::int + 1  AS "nodes per simplex: percentile 99",
       simplices_qmax + 1                  AS "nodes per simplex: max",

       facets_qmostfrequent + 1            AS "nodes per facet: most frequent value",
       dfacets_qmostfrequent + 1           AS "dnodes per facet: most frequent value",
       facets_qstd                         AS "nodes per facet: std",
       dfacets_qstd                        AS "dkranodes per facet: std",
       facets_qavg + 1                     AS "nodes per facet: avg",
       dfacets_qavg + 1                    AS "dnodes per facet: avg",
       facets_qmin + 1                     AS "nodes per facet: min",
       dfacets_qmin + 1                    AS "dnodes per facet: min",
       facets_qpercentiles[1]::int + 1     AS "nodes per facet: median",
       dfacets_qpercentiles[1]::int + 1    AS "dnodes per facet: median",
       facets_qpercentiles[2]::int + 1     AS "nodes per facet: percentile 95",
       dfacets_qpercentiles[2]::int + 1    AS "dnodes per facet: percentile 95",
       facets_qpercentiles[3]::int + 1     AS "nodes per facet: percentile 99",
       dfacets_qpercentiles[3]::int + 1    AS "dnodes per facet: percentile 99",
       facets_qmax + 1                     AS "nodes per facet: max",
       dfacets_qmax + 1                    AS "dnodes per facet: max",

       nodes_simplices_avg                 AS "simplices per node: avg",
       nodes_facets_avg                    AS "facets per node: avg",
       nodes_simplices_min                 AS "simplices per node: min",
       nodes_facets_min                    AS "facets per node: min",
       nodes_simplices_percentiles[1]::int AS "simplices per node: median",
       nodes_facets_percentiles[1]::int    AS "facets per node: median",
       nodes_simplices_percentiles[2]::int AS "simplices per node: percentile 95",
       nodes_facets_percentiles[2]::int    AS "facets per node: percentile 95",
       nodes_simplices_percentiles[3]::int AS "simplices per node: percentile 99",
       nodes_facets_percentiles[3]::int    AS "facets per node: percentile 99",
       nodes_simplices_max                 AS "simplices per node: max",
       nodes_facets_max                    AS "facets per node: max"
FROM (
         SELECT count(id)::int                                                         AS no_simplices,
                min(q)::int                                                            AS simplices_qmin,
                max(q)::int                                                            AS simplices_qmax,
                avg(q)::float                                                          AS simplices_qavg,
                mode() WITHIN GROUP (ORDER BY q)                                       AS simplices_qmostfrequent,
                stddev(q)::float                                                       AS simplices_qstd,
                percentile_disc('{{.5, .95, .99}}'::float[]) WITHIN GROUP (ORDER BY q) AS simplices_qpercentiles
         FROM "{0}".simplices
     ) s,
     (
         SELECT COUNT(*)::int AS no_usimplices_with_order
         FROM (SELECT DISTINCT md5(array_to_string(node_ids, ','))::uuid
               FROM "{0}".simplices) foo
     ) uo,
     (
         SELECT count(id)::int AS no_usimplices
         FROM "{0}".usimplices
     ) u,
     (
         SELECT count(id)::int                                                          AS no_facets,
                min(q)::int                                                             AS facets_qmin,
                min(dq)::int                                                            AS dfacets_qmin,
                max(q)::int                                                             AS facets_qmax,
                max(dq)::int                                                            AS dfacets_qmax,
                avg(q)::float                                                           AS facets_qavg,
                avg(dq)::float                                                          AS dfacets_qavg,
                mode() WITHIN GROUP (ORDER BY q)                                        AS facets_qmostfrequent,
                mode() WITHIN GROUP (ORDER BY dq)                                       AS dfacets_qmostfrequent,
                stddev(q)::float                                                        AS facets_qstd,
                stddev(dq)::float                                                       AS dfacets_qstd,
                percentile_disc('{{.5, .95, .99}}'::float[]) WITHIN GROUP (ORDER BY q)  AS facets_qpercentiles,
                percentile_disc('{{.5, .95, .99}}'::float[]) WITHIN GROUP (ORDER BY dq) AS dfacets_qpercentiles
         FROM "{0}".facets
     ) f,
     (
         SELECT count(id)::int                                   AS no_nodes,
                min(icount(facet_ids))::int                      AS nodes_facets_min,
                min(weight)::int                                 AS nodes_simplices_min,
                max(icount(facet_ids))::int                      AS nodes_facets_max,
                max(weight)::int                                 AS nodes_simplices_max,
                avg(icount(facet_ids))::float                    AS nodes_facets_avg,
                avg(weight)::float                               AS nodes_simplices_avg,
                mode() WITHIN GROUP (ORDER BY icount(facet_ids)) AS nodes_facets_mostfrequent,
                mode() WITHIN GROUP (ORDER BY weight)            AS nodes_simplices_mostfrequent,
                stddev(icount(facet_ids))::float                 AS nodes_facets_std,
                stddev(weight)::float                            AS nodes_simplices_std,
                percentile_disc('{{.5, .95, .99}}'::float[])
                WITHIN GROUP (ORDER BY icount(facet_ids))        AS nodes_facets_percentiles,
                percentile_disc('{{.5, .95, .99}}'::float[])
                WITHIN GROUP (ORDER BY weight)                   AS nodes_simplices_percentiles
         FROM "{0}".nodes
     ) n,
     (
         SELECT count(id)::int AS no_dnodes
         FROM "{0}".dnodes
     ) dn