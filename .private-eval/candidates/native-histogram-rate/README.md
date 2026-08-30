# Native-histogram extended-rate calibration candidates

## Alternate valid

`alternate-valid/solve.sh` interpolates the requested boundaries, normalizes a histogram window, and delegates subtraction, schema reduction, and reset accumulation to the pre-existing `histogramRate` path. The Oracle adds a separate extended histogram-rate implementation.

Expected reward: `1`.

## Mutant 1: mixed-window panic

`mutant-1/solve.sh` applies the feature patch but omits the direct mixed-window panic correction.

Expected reward: `0`.

## Mutant 2: reset-blind interpolation

`mutant-2/solve.sh` applies the full Oracle, then linearly interpolates across counter resets.

Expected reward: `0`.
