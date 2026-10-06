# apps/api/src/core/concurrency.py
"""
ML Inference Concurrency and Thread Pool Isolation Manager.

Ensures:
1. CPU/GPU-heavy forward passes (PyTorch, TensorFlow, Whisper) never block the FastAPI event loop.
2. Concurrency ceiling via asyncio.Semaphore prevents GPU VRAM exhaustion and process OOM.
3. Dedicated ThreadPoolExecutor prevents starvation of standard asyncio.to_thread workers.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, TypeVar
from apps.api.src.config import settings
from rakshagrid.common.logging.logger import setup_logger

logger = setup_logger("rakshagrid.api.concurrency")

R = TypeVar("R")


class InferenceConcurrencyManager:
    """Manages isolated concurrency limits for heavy machine learning inference."""

    def __init__(self, max_concurrent: int = 4):
        self.max_concurrent = max_concurrent
        self._semaphore: asyncio.Semaphore | None = None
        self._executor: ThreadPoolExecutor | None = None

    def _get_semaphore(self) -> asyncio.Semaphore:
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent)
        return self._semaphore

    def _get_executor(self) -> ThreadPoolExecutor:
        if self._executor is None:
            self._executor = ThreadPoolExecutor(
                max_workers=self.max_concurrent,
                thread_name_prefix="rakshagrid_ml_worker",
            )
        return self._executor

    async def run(self, target_func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
        """
        Executes a CPU/GPU-bound inference function inside the dedicated ML thread pool
        while respecting the concurrency semaphore.
        """
        sem = self._get_semaphore()
        executor = self._get_executor()
        loop = asyncio.get_running_loop()

        async with sem:
            if kwargs:
                # functools.partial for kwargs compatibility
                import functools
                call_obj = functools.partial(target_func, *args, **kwargs)
                return await loop.run_in_executor(executor, call_obj)
            return await loop.run_in_executor(executor, target_func, *args)

    def shutdown(self, wait: bool = True):
        """Cleanly releases worker threads during application shutdown."""
        if self._executor:
            logger.info("Shutting down ML worker thread pool...")
            self._executor.shutdown(wait=wait)
            self._executor = None


# Authoritative singleton concurrency manager
inference_concurrency = InferenceConcurrencyManager(
    max_concurrent=settings.INFERENCE_MAX_CONCURRENCY
)
