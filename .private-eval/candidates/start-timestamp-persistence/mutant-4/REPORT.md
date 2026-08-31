# Mutant 4: always-on histogram ST encoding

## Defect

The fixture applies the exact landed Oracle, then makes integer and float histograms select their ST-capable encodings even when the independent histogram encoding option is disabled. The public feature state remains disabled, but storage no longer honors it.

## Pinned inputs

- Final task checksum prefix: `faba462b`
- Oracle patch: `38ef116cef20d074d89110f544974c4733478043a50a4dec3feade7c4f6f744c`
- Mutant patch: `4cde6c8e90e67a8627db73c52b302dbeae6bbc4167381ae6eebb7022aa566397`
- Fixture solver: `3a6100e672ed4bb9f67951b32faec20caf2049de5addabd9d415fbebe61159cd`
- Candidate writer source: `166a12c9e2473de8c4787ce303747b576f7f2f0b40cb5696bb4531820dc67ad0`
- Candidate reader source: `39e7a0b7a5c40c275b2757b5e9090a4b8e19755831e5ce7ebd0a3a53c5513c2d`
- External controller: `310f975ec38327783e8679339b9eba151e158faa13f606040ae29c333791830b`

## Static and host discrimination

- Clean-parent Oracle apply: passed.
- Mutant apply after Oracle: passed.
- `go test ./tsdb/chunkenc`: passed.
- Final neutral controller: option discovery, reset, recode, stale recovery, and enabled in-order persistence passed. The disabled-mode assertion rejected the candidate at controller line 796 with `candidate reader did not recover the complete expected histogram sample`.

The host controller differed only by replacing Linux UID ownership changes with no-ops. No Daytona or local container run was used for this host calibration.
