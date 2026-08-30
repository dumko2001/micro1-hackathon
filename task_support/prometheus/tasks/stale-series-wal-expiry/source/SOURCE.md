# Source provenance

- Clean landed parent: `05d9bd4a2789196c1361acfe06a2edf79440d8c0`
- Bug-fix anchor: Prometheus PR #18847, merge `5ddb7e49e3c89c406687cf020f85e04a3bac16fd`
- Archive SHA-256: `ed12931b2819c6159f50eb24960e78f505a4bdf32974a3717305c809d8019929`

The contract is limited to timestamp-based retention of evicted series metadata while WAL samples still reference it. Later PRs #19140 and #19183 address different replay/accounting incidents and are excluded.
