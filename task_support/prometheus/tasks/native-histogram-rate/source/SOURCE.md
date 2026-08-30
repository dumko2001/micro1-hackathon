# Source provenance

- Clean landed parent: `cb085a6281e242e4694306901b7931e5801e5387`
- Feature anchor: Prometheus PR #18564, merge `06b569ae2a6e43d08490370e10f0df8c7ba0fb68`
- Direct panic correction: PR #18943, merge `2626a65a8282703f1378e341565922756a4a0f9a`
- Archive SHA-256: `9683e773587c96fa1e396cd83e53985fcd408789b964b7aab03f30e47d7be951`

The reference includes only the direct mixed-window panic correction. Guarantees introduced by PRs #18906, #18928, and #19431 are outside this task and must not appear in its verifier.
