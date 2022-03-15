-- {{0}} is the dataset,
-- {{1}} is a float array passed        as a string in postgresql format; e.g. '{{.5,.6,.9,.99}}'
SELECT '{0}'                                                                           AS dataset,
       {1}                                                                             AS q,

       -- sum(weight)::int                                                                AS "no_qfaces",

       min(classical_degree)::int                                                      AS "classical: min",
       max(classical_degree)::int                                                      AS "classical: max",
       avg(classical_degree)::float                                                    AS "classical: avg",
       mode() WITHIN GROUP (ORDER BY classical_degree)                                 AS "classical: most frequent value",
       stddev(classical_degree)::float                                                 AS "classical: stddev",
       percentile_disc('{2}'::float[]) WITHIN GROUP (ORDER BY classical_degree)        AS "classical: percentiles {2}",

       min(maximal_degree)::int                                                        AS "maximal: min",
       max(maximal_degree)::int                                                        AS "maximal: max",
       avg(maximal_degree)::float                                                      AS "maximal: avg",
       mode() WITHIN GROUP (ORDER BY maximal_degree)                                   AS "maximal: most frequent value",
       stddev(maximal_degree)::float                                                   AS "maximal: stddev",
       percentile_disc('{2}'::float[]) WITHIN GROUP (ORDER BY maximal_degree)          AS "maximal: percentiles {2}",

       min(maximal_degree_u)::int                                                      AS "maximal upper: min",
       max(maximal_degree_u)::int                                                      AS "maximal upper: max",
       avg(maximal_degree_u)::float                                                    AS "maximal upper: avg",
       mode() WITHIN GROUP (ORDER BY maximal_degree_u)                                 AS "maximal upper: most frequent value",
       stddev(maximal_degree_u)::float                                                 AS "maximal upper: stddev",
       percentile_disc('{2}'::float[]) WITHIN GROUP (ORDER BY maximal_degree_u)        AS "maximal upper: percentiles {2}",

       min(weighted_maximal_degree)::int                                               AS "weighted maximal: min",
       max(weighted_maximal_degree)::int                                               AS "weighted maximal: max",
       avg(weighted_maximal_degree)::float                                             AS "weighted maximal: avg",
       mode() WITHIN GROUP (ORDER BY weighted_maximal_degree)                          AS "weighted maximal: most frequent value",
       stddev(weighted_maximal_degree)::float                                          AS "weighted maximal: stddev",
       percentile_disc('{2}'::float[]) WITHIN GROUP (ORDER BY weighted_maximal_degree) AS "weighted maximal percentiles {2}"
FROM "{0}".q0_faces