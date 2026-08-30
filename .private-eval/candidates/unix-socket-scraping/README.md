# Unix-socket scraping calibration candidates

## Alternate valid

`alternate-valid/solve.sh` applies a clean-parent implementation with one owned HTTP transport per Unix-socket target. It differs from the Oracle's socket-path client cache while preserving Host and TLS identity, reload behavior, TCP controls, isolation, and fail-closed behavior.

Expected reward: `1`.

## Mutant 1: shared transport

`mutant-1/solve.sh` applies only the first upstream feature patch and omits the isolation follow-up. Unix/Unix, Unix/TCP, and reload targets can reuse the wrong connection.

Expected reward: `0`.

## Mutant 2: TCP fallback

`mutant-2/solve.sh` applies the full Oracle, then falls back to the advertised TCP endpoint after a Unix-socket dial failure.

Expected reward: `0`.
