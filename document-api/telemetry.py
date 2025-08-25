from opentelemetry import trace
from opentelemetry import metrics

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


def init_observability():
    """Initialize OpenTelemetry observability."""

    provider = TracerProvider()
    processor = BatchSpanProcessor(OTLPSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(), export_interval_millis=5000)
    provider = MeterProvider(metric_readers=[metric_reader])
    metrics.set_meter_provider(provider)

    print("OpenTelemetry observability initialised.")
