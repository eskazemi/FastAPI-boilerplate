import cProfile
import io
import pstats
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def profile(
    *,
    sort_by: pstats.SortKey = pstats.SortKey.CUMULATIVE,
    limit: int = 30,
    output_file: str | Path | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Profile a synchronous function."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            profiler = cProfile.Profile()
            profiler.enable()

            try:
                return func(*args, **kwargs)
            finally:
                profiler.disable()

                stream = io.StringIO()

                stats = pstats.Stats(
                    profiler,
                    stream=stream,
                )

                stats.strip_dirs()
                stats.sort_stats(sort_by)
                stats.print_stats(limit)

                print(
                    f"\nProfiling results for "
                    f"{func.__qualname__}:\n"
                )
                print(stream.getvalue())

                if output_file is not None:
                    destination = Path(output_file)
                    destination.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    profiler.dump_stats(str(destination))

                    print(
                        f"Profile saved to: {destination}"
                    )

        return wrapper

    return decorator


# import time


# @profile(
#     sort_by=pstats.SortKey.CUMULATIVE,
#     limit=20,
#     output_file="profiles/fast_function.prof",
# )
# def fast_function() -> None:
#     time.sleep(0.1)


# @profile(
#     sort_by=pstats.SortKey.TIME,
#     limit=10,
#     output_file="profiles/slow_function.prof",
# )
# def slow_function() -> None:
#     time.sleep(0.5)
