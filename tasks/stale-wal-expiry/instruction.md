After stale-series compaction and a later checkpoint, restarting Prometheus reports unknown WAL series references even though the affected samples were safely compacted into a block. The replay warnings make a healthy database appear corrupt.

Restore clean checkpoint and replay behavior after stale-series compaction.

Do not look for or use online solutions.
