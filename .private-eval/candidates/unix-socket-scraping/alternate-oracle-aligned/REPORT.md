# Oracle-aligned Unix-socket alternate

Base: Prometheus `92aa2e73df04594bd941dd9b6f073cf27e320820`.

This candidate uses a private `unixClientRegistry` value object rather than the landed `unixSocketClients` field and `clientForTarget`/`newUnixSocketScrapeClient` organization. The registry owns acquisition, retention, and cleanup. Scrape-pool code only asks it for the client associated with a socket path.

The implementation preserves the reviewed invariants:

- the literal `__unix_socket__` label selects Unix dialing;
- an empty advertised address becomes `localhost`, retaining an HTTP/TLS authority;
- one reusable HTTP client and connection pool is shared by targets on the same socket;
- different sockets and ordinary TCP targets never share that pool;
- standard keep-alives remain enabled;
- sync discards pools for unused sockets;
- reload replaces and closes the complete old registry;
- client-construction errors return a fixed failing transport instead of falling back to TCP.

Validation on the checksum-pinned clean parent:

- source archive SHA-256: `3f014fbedbdecbd18207b01e9deabba6a393bdb01e32765f64cab65fdfc2aff0`;
- `git apply --check`: pass;
- `go test ./scrape -run '^$'` with `GOWORK=off`, `GOPROXY=off`: pass;
- verifier-equivalent pool-identity test, including reload: pass;
- patch SHA-256: `7c8c83b6dae10fc437f90b252f64a48e3ff0c8aa5890db2002cf909847d791d8`;
- patched `scrape/scrape.go` SHA-256: `634593ed5b07a2822e8420dad15097f072889f0896ac6a73aae256fb865fd682`;
- patched `scrape/target.go` SHA-256: `5abff7ed4e2ba8b6cd4520ad2779fe8966b360c57974dc8c8f80ef356dc75543`.
