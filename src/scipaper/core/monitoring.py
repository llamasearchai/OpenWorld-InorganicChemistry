"""Performance monitoring and optimization utilities."""
import time
from typing import Dict, Any, List
from contextlib import contextmanager

from loguru import logger


@contextmanager
def time_function(func_name: str):
    """Context manager to time function execution."""
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"{func_name} execution time: {duration:.2f}s")


def optimize_search_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Optimize search results by caching or filtering."""
    # Simple optimization: sort by relevance score if present
    if results and 'relevance_score' in results[0]:
        results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    return results


def monitor_system_resources() -> Dict[str, Any]:
    """Monitor system resources like memory usage."""
    import psutil
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }


def log_performance_metrics(func):
    """Decorator to log performance metrics for functions."""
    def wrapper(*args, **kwargs):
        with time_function(func.__name__):
            result = func(*args, **kwargs)
        logger.info(f"{func.__name__} completed successfully")
        return result
    return wrapper