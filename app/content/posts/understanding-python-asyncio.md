---
title: "Understanding Python's asyncio Event Loop"
date: 2026-03-18
description: "A ground-up explanation of how asyncio works — coroutines, tasks, the event loop, and where things go wrong."
tags: ["Python", "Async", "Systems"]
reading_time: 9
---

## The problem asyncio solves

A synchronous Python program blocks on I/O. When you call `requests.get(url)`, the thread sleeps until the network responds. For a server handling one request at a time, this is fine. For a server handling ten thousand concurrent connections, it is not.

Threading helps, but threads are expensive — each has a stack, a kernel object, and context-switch overhead. asyncio takes a different approach: a single thread, and cooperative multitasking.

## Coroutines and the event loop

A coroutine is a function that can pause itself:

```python
async def fetch(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    return response.text
```

When execution hits `await`, the coroutine suspends and returns control to the event loop. The loop checks what else is ready to run, executes it, and comes back when the I/O completes.

The event loop is just a `while True` loop that:
1. Polls I/O descriptors (via `select`/`epoll`/`kqueue`)
2. Fires callbacks for ready events
3. Runs scheduled coroutines

## Tasks vs. coroutines

Calling an `async def` function gives you a *coroutine object* — it does not run yet. To run it concurrently, wrap it in a `Task`:

```python
task = asyncio.create_task(fetch("https://example.com"))
```

Tasks are scheduled to run on the current event loop. Multiple tasks run concurrently on the same thread.

## Common mistake: blocking the event loop

The entire model breaks if you call blocking code inside `async def`:

```python
async def bad():
    time.sleep(5)  # blocks the event loop for 5 seconds
```

While `bad()` is sleeping, no other coroutine can run. For blocking I/O, use `asyncio.to_thread()`. For CPU-heavy work, use `ProcessPoolExecutor`.

## Practical rules

- Use `async def` for all I/O-bound work.
- Never call synchronous I/O inside a coroutine.
- Use `asyncio.gather()` to run multiple coroutines concurrently.
- Use `asyncio.create_task()` when you want background execution.
- Use `asyncio.to_thread()` when you must call synchronous code from async context.
