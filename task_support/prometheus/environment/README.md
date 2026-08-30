# Reusable Prometheus environment

This directory is the task-neutral runtime source for all five Prometheus episodes. It owns the pinned Go builder, safe source extraction, integrity checks, prewarmed module and build caches, generic candidate build command, and process controls.

It does not own task instructions, clean-parent commits, source archives, reference patches, verifier cases, rewards, or thresholds. Those belong to each overlay.

Materialization copies one Git-stripped source archive to `environment/source/`. The image verifies its digest, extracts it safely, and downloads checksum-pinned Go modules during construction. The actor can reach its model provider; the separate verifier uses `network_mode=no-network`.

Profiles may prepare reusable fixtures, but they must remain dormant unless the selected task enables them. Every rollout starts with fresh state.
