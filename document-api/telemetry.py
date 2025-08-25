import os, json, logging
from datetime import datetime
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.trace import get_current_span

class JSONFormatter(logging.Formatter):
    def format(self, record):
        span = get_current_span()
        trace_id = span.get_span_context().trace_id if span else 0
        span_id = span.get_span_context().span_id if span else 0
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "trace_id": f"{trace_id:032x}",
            "span_id": f"{span_id:016x}"
        }
        return json.dumps(payload)


def init_observability(app=None):
    service_name = os.environ.get("OTEL_SERVICE_NAME", "document-api")
    service_version = os.environ.get("OTEL_SERVICE_VERSION", "1.0.0")
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
    insecure = os.environ.get("OTEL_EXPORTER_OTLP_INSECURE", "false") == "true"

    resource = Resource.create({"service.name": service_name, "service.version": service_version})
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(
        OTLPSpanExporter(endpoint=endpoint, insecure=insecure)
    ))
    trace.set_tracer_provider(tracer_provider)

    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=endpoint, insecure=insecure),
        export_interval_millis=5000
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # instrument frameworks
    if app:
        FastAPIInstrumentor().instrument_app(app, tracer_provider=tracer_provider, meter_provider=meter_provider)
    HTTPXClientInstrumentor().instrument()

    # set JSON logging with trace correlation
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)

    print("OpenTelemetry observability initialised.")
