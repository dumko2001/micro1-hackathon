# Source provenance

- Clean landed parent: `92aa2e73df04594bd941dd9b6f073cf27e320820`
- Feature anchor: Prometheus PR #18091, merge `c5fa89db085c9b3855d7916f2ade047066a7a318`
- Correctness follow-up: PR #19399, merge `05f9eb8b3b8e10b48c8f4153b0714dbe9bc9a630`
- Archive SHA-256: `3f014fbedbdecbd18207b01e9deabba6a393bdb01e32765f64cab65fdfc2aff0`

The reference combines two changes. PR #18091 alone can pool transports across socket targets that share an advertised address; PR #19399 supplies the same-surface isolation correction. No later UDS correction was found through 2026-08-29.
