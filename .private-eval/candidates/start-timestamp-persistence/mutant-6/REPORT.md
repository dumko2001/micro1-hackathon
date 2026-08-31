# Mutant 6: stale-to-live ST loss

## Defect

The fixture applies the exact landed Oracle, then drops the start timestamp in the AppenderV2 batch record when a live integer or float histogram immediately follows a stale histogram. Ordinary samples, consecutive stale samples, recoding, and reset handling are unchanged.

## Pinned inputs

- Final task checksum prefix: `faba462b`
- Oracle patch: `38ef116cef20d074d89110f544974c4733478043a50a4dec3feade7c4f6f744c`
- Mutant patch: `28aa2ab0e35df4e3dcba3927f145804a27cd378544ae34a77d2e168b3e3baf77`
- Fixture solver: `3a6100e672ed4bb9f67951b32faec20caf2049de5addabd9d415fbebe61159cd`
- Candidate writer source: `166a12c9e2473de8c4787ce303747b576f7f2f0b40cb5696bb4531820dc67ad0`
- Candidate reader source: `39e7a0b7a5c40c275b2757b5e9090a4b8e19755831e5ce7ebd0a3a53c5513c2d`
- External controller: `310f975ec38327783e8679339b9eba151e158faa13f606040ae29c333791830b`

## Static and host discrimination

- Clean-parent Oracle apply: passed.
- Mutant apply after Oracle: passed.
- Candidate writer and reader compilation: passed.
- Final neutral controller: option discovery, integer reset, and integer recode passed. The integer stale-recovery assertion rejected the candidate at controller line 792 with `candidate reader did not recover the complete expected histogram sample`.

Two earlier variants were discarded because the final controller reached the legacy phase, proving they were inert after the V2/WAL lifecycle. They are not retained as fixtures or claimed as evidence. The host controller differed only by replacing Linux UID ownership changes with no-ops. No Daytona or local container run was used for this host calibration.
