We’re seeing dashboard panels return empty or inconsistent series when a fixed-time PromQL subquery is passed to a function whose result changes at each step. One report reproduces it with `quantile_over_time(scalar(arg), metric[2m1s:30s] @ 2m)`: the subquery form returns empty even though the matching matrix selector and constant-argument form return data. Instant and range queries over the same data disagree, while ordinary subqueries remain healthy.

Restore correct instant and range query results.

Do not look for or use online solutions.
