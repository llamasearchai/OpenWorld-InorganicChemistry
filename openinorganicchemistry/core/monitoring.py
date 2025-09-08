from __future__ import annotations

import functools
import logging
import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, TypeVar
import os

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    execution_time: float = 0.0
    memory_peak_mb: float = 0.0
    memory_current_mb: float = 0.0
    cpu_percent: float = 0.0
    api_calls: int = 0
    api_tokens: int = 0
    additional_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return (
            f"Time: {self.execution_time:.2f}s, "
            f"Memory: {self.memory_current_mb:.1f}MB (peak: {self.memory_peak_mb:.1f}MB), "
            f"CPU: {self.cpu_percent:.1f}%, "
            f"API: {self.api_calls} calls/{self.api_tokens} tokens"
        )


class PerformanceTracker:
    """Tracks performance metrics for operations."""
    
    def __init__(self, name: str = "operation"):
        self.name = name
        self.metrics = PerformanceMetrics()
        self.start_time: Optional[float] = None
        self.start_memory: Optional[float] = None
        self.process = psutil.Process(os.getpid()) if psutil else None
    
    def start(self) -> None:
        """Start tracking performance."""
        tracemalloc.start()
        self.start_time = time.perf_counter()
        if self.process:
            self.start_memory = self.process.memory_info().rss / 1024 / 1024
        logger.debug(f"Started tracking performance for: {self.name}")
    
    def stop(self) -> PerformanceMetrics:
        """Stop tracking and return metrics."""
        if self.start_time is None:
            raise RuntimeError("Tracker not started")
        
        # Calculate execution time
        self.metrics.execution_time = time.perf_counter() - self.start_time
        
        # Calculate memory usage
        if self.process:
            current_memory = self.process.memory_info().rss / 1024 / 1024
            self.metrics.memory_current_mb = current_memory
        
        if tracemalloc.is_tracing():
            peak_memory = tracemalloc.get_traced_memory()[1] / 1024 / 1024
            self.metrics.memory_peak_mb = peak_memory
            tracemalloc.stop()
        
        # Calculate CPU usage (approximate)
        if self.process:
            try:
                self.metrics.cpu_percent = self.process.cpu_percent()
            except Exception:  # psutil.AccessDenied or AttributeError if psutil is None
                self.metrics.cpu_percent = 0.0
        
        logger.info(f"Performance metrics for {self.name}: {self.metrics}")
        return self.metrics
    
    def record_api_call(self, tokens: int = 0) -> None:
        """Record an API call."""
        self.metrics.api_calls += 1
        self.metrics.api_tokens += tokens
    
    def record_metric(self, key: str, value: Any) -> None:
        """Record a custom metric."""
        self.metrics.additional_metrics[key] = value


@contextmanager
def performance_monitor(name: str = "operation"):
    """Context manager for performance monitoring."""
    tracker = PerformanceTracker(name)
    tracker.start()
    try:
        yield tracker
    finally:
        metrics = tracker.stop()
        return metrics


def performance_timer(name: Optional[str] = None) -> Callable[[F], F]:
    """Decorator to time function execution."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracker_name = name or f"{func.__module__}.{func.__name__}"
            with performance_monitor(tracker_name) as tracker:
                result = func(*args, **kwargs)
                # If the function returns a dict with performance info, merge it
                if isinstance(result, dict) and "performance" in result:
                    for key, value in result["performance"].items():
                        tracker.record_metric(key, value)
            return result
        return wrapper
    return decorator


class ResourceMonitor:
    """System resource monitoring utility."""
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get current system information."""
        if not psutil:
            return {
                "cpu_count": 0,
                "cpu_percent": 0.0,
                "memory_total_gb": 0.0,
                "memory_available_gb": 0.0,
                "memory_percent": 0.0,
                "disk_total_gb": 0.0,
                "disk_free_gb": 0.0,
                "disk_percent": 0.0,
            }
        
        return {
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_total_gb": psutil.virtual_memory().total / 1024**3,
            "memory_available_gb": psutil.virtual_memory().available / 1024**3,
            "memory_percent": psutil.virtual_memory().percent,
            "disk_total_gb": psutil.disk_usage('/').total / 1024**3,
            "disk_free_gb": psutil.disk_usage('/').free / 1024**3,
            "disk_percent": psutil.disk_usage('/').percent,
        }
    
    @staticmethod
    def check_resource_limits(
        max_memory_gb: float = 8.0,
        max_cpu_percent: float = 80.0,
        min_disk_gb: float = 1.0
    ) -> Dict[str, bool]:
        """Check if system resources are within limits."""
        info = ResourceMonitor.get_system_info()
        
        return {
            "memory_ok": info["memory_available_gb"] > max_memory_gb * 0.1,  # 10% buffer
            "cpu_ok": info["cpu_percent"] < max_cpu_percent,
            "disk_ok": info["disk_free_gb"] > min_disk_gb,
        }
    
    @staticmethod
    def log_resource_usage() -> None:
        """Log current resource usage."""
        info = ResourceMonitor.get_system_info()
        logger.info(
            f"Resources - CPU: {info['cpu_percent']:.1f}%, "
            f"Memory: {info['memory_percent']:.1f}% "
            f"({info['memory_available_gb']:.1f}GB free), "
            f"Disk: {info['disk_percent']:.1f}% "
            f"({info['disk_free_gb']:.1f}GB free)"
        )


class APIUsageTracker:
    """Tracks API usage and costs."""
    
    def __init__(self):
        self.calls_by_model: Dict[str, int] = {}
        self.tokens_by_model: Dict[str, Dict[str, int]] = {}
        self.total_cost: float = 0.0
    
    def record_call(
        self,
        model: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: float = 0.0
    ) -> None:
        """Record an API call."""
        self.calls_by_model[model] = self.calls_by_model.get(model, 0) + 1
        
        if model not in self.tokens_by_model:
            self.tokens_by_model[model] = {"input": 0, "output": 0}
        
        self.tokens_by_model[model]["input"] += input_tokens
        self.tokens_by_model[model]["output"] += output_tokens
        self.total_cost += cost
    
    def get_summary(self) -> Dict[str, Any]:
        """Get usage summary."""
        total_calls = sum(self.calls_by_model.values())
        total_tokens = sum(
            tokens["input"] + tokens["output"]
            for tokens in self.tokens_by_model.values()
        )
        
        return {
            "total_calls": total_calls,
            "total_tokens": total_tokens,
            "total_cost": self.total_cost,
            "calls_by_model": self.calls_by_model.copy(),
            "tokens_by_model": {
                model: tokens.copy()
                for model, tokens in self.tokens_by_model.items()
            }
        }
    
    def log_summary(self) -> None:
        """Log usage summary."""
        summary = self.get_summary()
        logger.info(
            f"API Usage - {summary['total_calls']} calls, "
            f"{summary['total_tokens']} tokens, "
            f"${summary['total_cost']:.4f}"
        )