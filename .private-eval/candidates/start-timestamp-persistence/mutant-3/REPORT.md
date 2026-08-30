# Mutant 3: integer histogram recode corruption

## Defect

The fixture applies the exact landed Oracle, then changes the ST integer-histogram recoder to treat delta-encoded bucket values as absolute values during positive and negative layout expansion. Ordinary ST persistence remains valid; only the historical buckets rebuilt into the expanded layout are corrupted.

## Pinned inputs

- Oracle patch: `38ef116cef20d074d89110f544974c4733478043a50a4dec3feade7c4f6f744c`
- Mutant patch: `2a45779537b62bef2cd6ea4f8150a33a3b6d86eac90a638a6b2c763db98f4d72`
- Fixture solver: `3a6100e672ed4bb9f67951b32faec20caf2049de5addabd9d415fbebe61159cd`
- Candidate writer: `e0f9ab3b033e9e85fc61478043ba140975a772fb16b09d161f7993727c375d7e`
- Candidate reader: `267009b1633393dfe030346182215b33dfc9b15f2c8f70e07ac3ab33a5558136`
- Trusted reader: `2cce6fc4d55b132cf6072ed54fba40bd9709470b7028db451c9f920cf8fc0487`
- External controller: `5189d47937d92cea13ed79855eb2f47d311a58c3e22cdab1603e95566d256215`

## Static and host discrimination

- Clean-parent Oracle apply: passed.
- Mutant apply after Oracle: passed.
- Focused upstream `TestHistogramSTChunkBasic`, `TestHistogramSTChunkAppendAndIterate`, and `TestHistogramSTChunkRecode`: passed. The mutant is not a build break or a basic-persistence failure.
- Current external writer/candidate-reader/trusted-reader/controller path: rejected twice with `trusted reader did not recover the complete expected histogram sample` at the controller's integer `recode` assertion. Option discovery and the preceding randomized reset lifecycle both passed, so the failure is the intended receipt mismatch rather than infrastructure.

The host controller differed from the verifier only by omitting its Linux UID `chown` calls. A non-runnable `/bin/false` Prometheus sentinel was supplied because the controller rejected the mutant during recode verification before reaching the later public feature-endpoint checks. No Daytona or local container run was used for this calibration.
