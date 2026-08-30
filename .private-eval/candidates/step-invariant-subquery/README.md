# Step-invariant subquery calibration candidates

## Alternate valid

`alternate-valid/solve.sh` prevents the generic wrapper constructor from wrapping subqueries. The Oracle instead changes the subquery branch's `shouldWrap` result.

Expected reward: `1`.

## Mutant 1: start/end wrapping

`mutant-1/solve.sh` applies the Oracle, then incorrectly wraps subqueries fixed with `@ start()` or `@ end()`.

Expected reward: `0`.

## Mutant 2: offset wrapping

`mutant-2/solve.sh` applies the Oracle, then incorrectly wraps fixed-time subqueries carrying an offset.

Expected reward: `0`.
