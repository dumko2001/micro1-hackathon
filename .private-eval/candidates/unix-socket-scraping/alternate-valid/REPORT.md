# Unix-socket alternate-valid candidate

Base: Prometheus `92aa2e73df04594bd941dd9b6f073cf27e320820`.

This candidate does not use the Oracle's shared transport plus request-context socket routing. It constructs a dedicated HTTP client for each Unix-socket target, installs a fixed Unix dialer in that target's transport, retains the advertised URL for Host and TLS identity, and closes owned idle connections with the scrape loop. TCP targets continue to use the scrape pool's shared client. Per-target transports make Unix/Unix and Unix/TCP connection reuse impossible by construction.

Validation on the clean parent:

- `git apply --check`: pass
- hidden behavioral Unix-socket and TCP controls: pass
- complete `./scrape/...` package tests: pass

The implementation changes only `scrape/scrape.go`; it does not copy the Oracle's exported constant, request context key, context-propagated socket lookup, or transport-pool organization.

