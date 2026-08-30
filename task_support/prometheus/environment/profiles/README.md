# Environment profiles

The five task overlays may select reusable setup for:

- PromQL engine evaluation;
- Unix-socket and TLS scrape transport;
- native-histogram query semantics;
- start-timestamp chunks, WAL/WBL, and blocks;
- stale-series checkpoint and replay.

A profile must be dormant unless its task selects it, and it must receive fresh state for every rollout. Task-specific cases and reward logic do not belong here.
