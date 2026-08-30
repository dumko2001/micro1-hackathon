# Mutant 7: iterator Seek off by one

## Defect

The fixture applies the exact landed Oracle, then advances histogram ST iterators while the requested timestamp is equal to the current sample. Full iteration remains correct, but exact-timestamp `Seek` returns the following sample.

## Pinned inputs

- Final task checksum prefix: `faba462b`
- Oracle patch: `38ef116cef20d074d89110f544974c4733478043a50a4dec3feade7c4f6f744c`
- Mutant patch: `8b6e8fca52e146f4a3da411e1481a6d67a76ae24b83aac62eee8866b7dcb6ad2`
- Fixture solver: `3a6100e672ed4bb9f67951b32faec20caf2049de5addabd9d415fbebe61159cd`
- Candidate writer source: `166a12c9e2473de8c4787ce303747b576f7f2f0b40cb5696bb4531820dc67ad0`
- Candidate reader source: `39e7a0b7a5c40c275b2757b5e9090a4b8e19755831e5ce7ebd0a3a53c5513c2d`
- External controller: `310f975ec38327783e8679339b9eba151e158faa13f606040ae29c333791830b`

## Static and host discrimination

- Clean-parent Oracle apply: passed.
- Mutant apply after Oracle: passed.
- Candidate writer and reader compilation: passed.
- Basic integer and float ST append/iteration tests: passed.
- The focused upstream integer and float `Seek` tests failed only at the intended boundary: expected timestamp `2000`, received `3000`.
- Final neutral controller completed option discovery and complete reset iteration, then rejected the fresh iterator at controller line 788 with `candidate iterator Seek returned the wrong complete histogram sample`.

The host controller differed only by replacing Linux UID ownership changes with no-ops. No Daytona or local container run was used for this host calibration.
