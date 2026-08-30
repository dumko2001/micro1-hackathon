Experimental extended-range queries work for floats but reject native histograms. A bare `mixed_types smoothed` instant query can also terminate the query even though wrapping the same selector in `sort(...)` returns a normal warning.

Add native-histogram support for anchored and smoothed rate, increase, delta, and smoothed selectors.

Do not look for or use online solutions.
