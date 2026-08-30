# Stale-series WAL-expiry calibration candidates

## Alternate valid: established expiry helper

Apply `alternate-valid.patch` to the clean parent. It uses the pre-existing `updateWALExpiry` helper rather than the reference patch's direct map update and explicit lock. Both place the eviction horizon in the timestamp domain used by checkpoint truncation; the helper also preserves a later existing horizon.

Expected reward: `1`.

## Named mutant: exclusive boundary

Apply `mutant-1.patch` to the clean parent. It expires labels one millisecond early. The exact-boundary checkpoint case must reject it.

Expected reward: `0`.

## Named mutant: unbounded retention

Apply `mutant-2.patch` to the clean parent. Replay remains clean, but evicted metadata never leaves later checkpoints.

Expected reward: `0`.
