import time

from src.domain.statistics import ExecutionMeasure
def measure(func, *args, **kwargs):
    start: float = time.perf_counter()
    datasets: list[str] = []

    try:
        result, datasets_list = func(*args, **kwargs)
        datasets = [dataset.filename for dataset in datasets_list]

        return result, ExecutionMeasure(
            success=True,
            elapsed=time.perf_counter() - start,
            function=func.__name__,
            accessed=datasets
        ).out()

    except Exception:
        return None, ExecutionMeasure(
            success=False,
            elapsed=time.perf_counter() - start,
            function=func.__name__,
            accessed=datasets
        ).out()
