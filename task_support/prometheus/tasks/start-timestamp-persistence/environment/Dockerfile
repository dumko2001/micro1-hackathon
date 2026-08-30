ARG GO_BUILDER=golang:1.26-bookworm@sha256:e8c859f5632dcfde7b32d2012b4351728f6437930887c2f6a91ea242459e5514
FROM ${GO_BUILDER}

LABEL org.opencontainers.image.source="https://github.com/prometheus/prometheus" \
      io.micro1.environment.family="prometheus"

ENV DEBIAN_FRONTEND=noninteractive \
    GOTOOLCHAIN=local \
    GOPROXY=https://proxy.golang.org,direct \
    GOSUMDB=sum.golang.org \
    GOCACHE=/opt/micro1-go-build-cache \
    PROMETHEUS_ROOT=/app/prometheus

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git patch \
    && rm -rf /var/lib/apt/lists/*

# Keep reviewer-only provenance out of the actor image.
COPY source/SOURCE.SHA256SUMS source/PREWARM_PACKAGES source/prometheus-*.tar.gz /opt/prometheus-input/
COPY build/verify-source.sh /usr/local/bin/verify-prometheus-source

RUN chmod 0555 /usr/local/bin/verify-prometheus-source \
    && /usr/local/bin/verify-prometheus-source \
      /opt/prometheus-input \
      /app/prometheus

WORKDIR /app/prometheus

# This task prewarms promtool through the repository workspace. Go generates a
# go.work.sum while doing so; it is a build byproduct, not part of the pinned
# first-parent tree, and must not leak into no-op candidate evidence.
RUN mkdir -p "$GOCACHE" \
    && go mod download \
    && xargs go test -run '^$' < /opt/prometheus-input/PREWARM_PACKAGES \
    && rm -f /app/prometheus/go.work.sum

COPY build/build-candidate.sh /usr/local/bin/build-candidate
COPY build/diagnose.sh /usr/local/bin/diagnose-environment
RUN chmod 0555 /usr/local/bin/build-candidate /usr/local/bin/diagnose-environment

RUN useradd --create-home --uid 1000 --shell /bin/bash agent \
    && chown -R agent:agent /app/prometheus \
    && chown -R agent:agent /opt/micro1-go-build-cache \
    && mkdir -p /app/verifier-artifacts /app/bin \
    && chown -R agent:agent /app/verifier-artifacts /app/bin

USER root
CMD ["sleep", "infinity"]
