Start timestamps survive float storage but disappear from native-histogram and float-histogram series as samples move through chunks and durable storage, blocking safe use of the experimental path for histogram-heavy ingestion.

Add a compact, opt-in persistent histogram representation behind the experimental `histograms-st-encoding` feature flag.

Do not look for or use online solutions.
