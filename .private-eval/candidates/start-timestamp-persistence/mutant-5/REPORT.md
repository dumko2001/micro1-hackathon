# Mutant 5: block-reader ST loss

## Defect

The fixture applies the exact landed Oracle, then makes the durable block reader rebuild multi-sample ST histogram chunks through an iterator that reports zero start timestamps. Head state, WAL/WBL state, and the block bytes remain intact; the defect is isolated to block-read reconstruction.

## Pinned inputs

- Final task checksum prefix: `faba462b`
- Oracle patch: `38ef116cef20d074d89110f544974c4733478043a50a4dec3feade7c4f6f744c`
- Mutant patch: `15623a24e72058c05ffc7047a43d68ffd9d3434740eed1ab43538eb99c4e841c`
- Fixture solver: `3a6100e672ed4bb9f67951b32faec20caf2049de5addabd9d415fbebe61159cd`
- Candidate writer source: `166a12c9e2473de8c4787ce303747b576f7f2f0b40cb5696bb4531820dc67ad0`
- Candidate reader source: `39e7a0b7a5c40c275b2757b5e9090a4b8e19755831e5ce7ebd0a3a53c5513c2d`
- External controller: `310f975ec38327783e8679339b9eba151e158faa13f606040ae29c333791830b`

## Static and host discrimination

- Clean-parent Oracle apply: passed.
- Mutant apply after Oracle: passed.
- Candidate writer and reader compilation: passed.
- Selected basic `tsdb/chunks` reader, ST sample, and write-queue tests: passed.
- Final neutral controller: option discovery, reset, recode, stale recovery, ordinary in-order persistence, and disabled-mode compatibility passed. The custom-profile durable block assertion rejected the candidate at controller line 798 with `candidate reader did not recover the complete expected histogram sample`.

The full `tsdb/chunks` package run was not usable as evidence because the host had less space than `TestWriterWithDefaultSegmentSize` preallocates; it failed with host `ENOSPC`, not a mutant assertion. The host controller differed only by replacing Linux UID ownership changes with no-ops. No Daytona or local container run was used for this host calibration.
