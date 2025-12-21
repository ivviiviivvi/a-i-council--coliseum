## 2024-02-14 - Concurrent Event Processing
**Learning:** Python's `asyncio.gather` is powerful for batch processing, but unbounded concurrency can exhaust resources (connections, file descriptors).
**Action:** Always wrap concurrent batch operations with `asyncio.Semaphore` to limit the number of active tasks. For this project, a limit of 10 was chosen for the event pipeline.
