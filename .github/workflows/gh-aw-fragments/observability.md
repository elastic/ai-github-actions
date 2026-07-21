---
# Shared OpenTelemetry / OTLP observability — no `on:` field (shared component, not a runnable workflow)
# Sends workflow spans to an external OTLP backend when GH_AW_OTEL_ENDPOINT and
# GH_AW_OTEL_AUTHORIZATION secrets are present in the repository.
observability:
  otlp:
    endpoint:
      - url: ${{ secrets.GH_AW_OTEL_ENDPOINT }}
        headers:
          Authorization: ${{ secrets.GH_AW_OTEL_AUTHORIZATION }}
---
