# Native-histogram alternate-valid candidate

Base: Prometheus `cb085a6281e242e4694306901b7931e5801e5387`.

This candidate uses a different computation model from the Oracle. It interpolates only the requested range boundaries, normalizes those boundaries and the interior samples into a histogram window, adjusts the reset hint when the left boundary has already crossed a reset, and delegates the final subtraction, schema reduction, reset accumulation, and annotations to Prometheus's pre-existing `histogramRate` implementation. The Oracle instead adds a parallel extended-rate implementation with bespoke reset-correction and annotated arithmetic helpers.

The normalized window is checked for mixed exponential and custom bucket families before delegation. This is required because the existing `histogramRate` path may intentionally discard an incompatible first sample when it infers a counter reset. Without the preflight, a two-point exponential/custom window was retained instead of being omitted with the expected warning.

For bare smoothed selectors, this candidate independently adds histogram point selection and interpolation to the existing evaluator and drops empty mixed-type series with warnings.

Validation on the clean parent:

- `git apply --check`: pass
- hidden extended-rate matrix, including single-sample windows, double resets, both-boundary reset interpolation, schema compatibility, custom buckets, and mixed types: pass
- exact two-point exponential/custom window used by the external controller: omitted with the expected warning
- upstream `TestEvaluations` regression set: pass

The implementation changes `promql/engine.go` and `promql/functions.go`; it does not copy the Oracle's `extendedHistogramRate`, boundary-picker helpers, reset-correction helper, or internal tests.
