# logpose

logpose is Akshay's open-source Python library for building applications that use language
models as agents. Source: https://github.com/xdadwal/logpose (MIT licence).

- What it does: an application gives logpose a model and a set of Python functions ("tools").
  logpose runs the loop between them: the model's turn, the tool calls it asks for, the tool
  results, and the follow-up turns, until the model has an answer. It returns the full message
  history and token usage.
- Provider-neutral: it works with any server that speaks the OpenAI Chat Completions API, such as
  OpenAI, vLLM, Ollama, LM Studio, llama.cpp and OpenRouter. No vendor SDK is needed.
- Main features: typed Python tools with JSON Schema generated from type annotations and
  docstrings; streaming events for text and tool activity; concurrent execution of parallel tool
  calls; multi-turn conversations stored as sessions in a local SQLite database; input guardrails
  that screen a user's message before the agent acts; retries with backoff; credential redaction
  in errors.
- Built with Python 3.10+, async-first, with pydantic and httpx as its only runtime dependencies.
- Status: alpha. It is installed from GitHub and is not on PyPI yet.
- The assistant on this website runs on logpose, so it is a working example of the library.
