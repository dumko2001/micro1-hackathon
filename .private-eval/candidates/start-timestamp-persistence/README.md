# Histogram start-timestamp persistence calibration candidates

## Alternate valid: equivalent chunk dispatch

Apply the reference feature patch and then `alternate-valid/fix.patch`. The candidate selects the same registered encodings through a table-backed legacy fallback rather than the reference switch body.

Expected reward: `1`.

This proves that grading is not a source-diff comparison. The final verifier does not require the landed concrete Go type names or source organization. It does require the reviewed wire format: a root-only reader built from the exact landed patch must decode the same sealed blocks as the candidate reader. The checks cover each lifecycle receipt and clean-parent legacy blocks.

## Named mutant: coupled feature flags

Apply the reference patch and then `mutant-1/fix.patch`. Enabling `xor2-encoding` silently enables the histogram format too.

Expected reward: `0`.

## Named mutant: OOO histogram downgrade

Apply the reference patch and then `mutant-2/fix.patch`. Normal ingestion uses the new format, but OOO chunk conversion selects the legacy integer and float histogram encodings even when histogram start-timestamp storage is enabled.

Expected reward: `0`.

## Named mutant: integer histogram recode corruption

Apply the reference patch and then `mutant-3/fix.patch`. Basic start-timestamp persistence remains intact, but layout expansion in an integer histogram incorrectly treats delta-encoded bucket values as absolute values while recoding earlier samples.

Expected reward: `0`.

Static and host discrimination evidence is recorded in `mutant-3/REPORT.md`.

## Named mutant: always-on histogram ST encoding

Apply the reference patch and then `mutant-4/fix.patch`. Histogram chunks use the ST-capable encodings even when the independent histogram encoding option is disabled.

Expected reward: `0`.

## Named mutant: block-reader ST loss

Apply the reference patch and then `mutant-5/fix.patch`. Head, WAL/WBL, and block bytes remain intact, but the durable block reader drops start timestamps while rebuilding multi-sample histogram iterators.

Expected reward: `0`.

## Named mutant: stale-to-live ST loss

Apply the reference patch and then `mutant-6/fix.patch`. The AppenderV2 batch path drops the start timestamp when a live histogram follows a stale histogram.

Expected reward: `0`.

## Named mutant: iterator Seek off by one

Apply the reference patch and then `mutant-7/fix.patch`. Iteration remains correct, but exact-timestamp `Seek` advances to the following histogram sample.

Expected reward: `0`.
