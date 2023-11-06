from time import perf_counter

from vllm.metrics.constants import CpuOperationMetrics
from vllm.metrics.metrics_store import MetricsStore


class CpuTimer:

    def __init__(self, name: CpuOperationMetrics):
        self.name = name
        self.start_time = None
        self.metrics_store = MetricsStore(None)
        self.disabled = not self.metrics_store.is_op_enabled(self.name)

    def __enter__(self):
        if self.disabled:
            return

        self.start_time = perf_counter()
        return self

    def __exit__(self, *_):
        if self.disabled:
            return

        self.metrics_store.push_cpu_operation_metrics(
            self.name,
            (perf_counter() - self.start_time) * 1e3  # convert to ms
        )
