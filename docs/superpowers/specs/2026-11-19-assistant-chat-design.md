# Assistant chat panel — design

Date: 2026-11-19 · Revised: 2026-11-23 (rewritten around logpose sessions, guardrails and tracing)
Status: approved and built · Branch: `feat/assistant-chat`

## Intent

Visitors to xdadwal.in (recruiters, peers, blog readers) can ask an assistant questions about
Akshay — experience, projects, skills, writing — and get answers grounded **only** in material
Akshay controls: his instructions, a small knowledge base, his resume, and the site's own data.

The UI follows the "Assistant" side panel in the Chroma docs (reference screenshot from the
conversation): a right-hand drawer with a header (title, expand, new chat, close), right-aligned
user bubbles, assistant replies as plain text with a small action row, and an "Ask a question…"
composer pinned to the bottom. It is restyled to this site's design tokens (dark, sharp-cornered,
JetBrains Mono labels).

It also doubles as a showcase for **logpose**, Akshay's own agent loop: the site uses its
sessions, input guardrails, tracing, context compaction and per-run request fields.

## Goals

- Answer questions about Akshay accurately from the provided material, streamed token-by-token.
- Content is edited as plain files in the repo; no code change needed to update what it knows.
- Available on every page; a visitor's conversation survives navigation and return visits.
- Akshay can review what visitors asked and what was answered.
- Cheap and abuse-resistant on a public, unauthenticated endpoint.
- Built so tools (e.g. `search_blog`) can be added later without a rewrite.

## Non-goals (v1)

- File uploads / attachments (the paperclip in the reference is dropped).
- Accounts or login. Thumbs up/down feedback (logpose cannot annotate a run after it ends).
- "Regenerate this answer" (logpose sessions are append-only; no rewind).
- An admin UI for reading chats — review is by trace export (below).
- RAG / vector search. Tools of any kind in v1.

## Anti-goals (failure even if it "works")

- The assistant **invents** facts about Akshay (employers, dates, skills not in the material).
- A surprise OpenAI bill from scraping/abuse.
- The API key or the raw system prompt leaking to the client.
- One visitor reading another visitor's conversation.
- Storing visitor messages without telling visitors.
- Breaking the existing pages or the "no extra JS libraries" frontend rule.

## Constraints

- Stack: FastAPI, Jinja2, Alpine.js, Tailwind v4 tokens (see `.claude/CLAUDE.md`,
  `.claude/design-system.md`). Python 3.12. Dark mode only. No test suite; done = `ruff check .`,
  `ruff format --check .`, dev server serves pages, and the manual checks below.
- Provider: **OpenAI API**, configured through logpose's `LOGPOSE_*` variables (env / `.env` only,
  never committed).
- Model: **`gpt-6-luna`** ($0.10 in / $0.01 cached / $0.50 out per 1M), configurable.
- Runtime: **logpose**, pinned to `d921adfae4d6195021fa77f8d72554afd6b030dd` (master,
  2026-11-23). Not on PyPI (that name is an unrelated project), so:
  `logpose @ git+https://github.com/xdadwal/logpose.git@d921adfae4d6195021fa77f8d72554afd6b030dd`.
  It brings `aiosqlite`; `httpx` and `pydantic` are already present via FastAPI.
- Deployment: single uvicorn process under systemd behind nginx (`deploy/portfolio.service`),
  with `ProtectSystem=strict` and `ProtectHome=read-only` — the service cannot write inside its
  checkout.

## Approaches considered

| | Approach | Trade-off | Verdict |
|---|---|---|---|
| **A** | Put all material in the system prompt | Simplest, whole-picture answers, prompt-cached; must move blog to a tool once it grows | **Chosen** |
| B | RAG over a vector index | Scales to huge corpora; adds embeddings + index + reindexing, misses "summarize" questions | Overkill for one person's profile |
| C | Agent with lookup tools | Most "agentic", scales with blog; multiple round-trips = slower, more parts | Deferred — logpose makes it a later add-on |

Where the conversation lives was a second choice: **server-side logpose sessions** (chosen) versus
browser-held history re-sent on every request (the first draft). Sessions remove client-forged
history, give return visits, persist compaction summaries, and feed the trace log; the cost is a
SQLite file and the site's first cookie.

## Design

### Content (Akshay edits these)

**All content lives in `.md` files** *(Akshay's decision, 2026-11-23)* — what the assistant knows,
how it sounds, what the guardrails say and what the panel shows. Python holds no copy. Operational
numbers (model, limits, retention, paths) stay in `app/config.py` / `.env`.

```
app/content/assistant/
  instructions.md    # voice, scope, off-limits topics, refusal rules      → system prompt
  resume.md          # resume as markdown, converted once from the PDF     → system prompt
  knowledge/*.md     # extra facts: location, contact preference, FAQs     → system prompt
  context.md         # frontmatter `sources`: the ordered list of what the model is given —
                     # file paths/globs in this folder, or site:experience | site:projects | site:blog
  guardrails.md      # frontmatter: max_chars, thresholds, block replies, block_patterns;
                     # body: the topic description the decision guard judges against
  panel.md           # frontmatter: greeting, placeholder, starters
```

`guardrails.md` and `panel.md` are parsed with `python-frontmatter` (already a dependency) and
validated by Pydantic models at startup; a missing or invalid file is a startup error when the
assistant is enabled.

Akshay's answers (from the plan page, 2026-11-23): voice = an assistant talking about him, friendly
and direct; resume source `~/Documents/akshay/Akshay-Dadwal-SDE3.pdf`; facts "Based in Delhi,
India" and "Best way to reach me is Email"; off-limits = salary/compensation, employer internals,
personal life; one starter question, "Tell me about Akshay's work."; contact link LinkedIn;
retention 30 days; full-text review log; "New chat" keeps the old chat in the log.

The repo is **public on GitHub**, so everything in these files is public. When converting the
resume, leave out phone number, home address and personal email unless Akshay says otherwise.

### System prompt assembly — `app/services/assistant.py`

Built **once per process**, in the order `context.md` lists ("keep it flexible to manage context
 for the model" — Akshay, 2026-11-23), so OpenAI's automatic prompt caching hits. Removing, adding
or reordering a line in `context.md` changes the prompt with no code change;
`python -m scripts.show_context` prints each source's size. Default order:
`instructions.md` → `resume.md` → `knowledge/*.md` (sorted by filename) → `EXPERIENCE` and
`PROJECTS` from `app/data.py` rendered as compact markdown → published blog posts as
`title — description — /blog/<slug>` lines (from `get_all_posts()`). Each section gets a heading.
Missing `instructions.md` is a startup error; missing optional files are skipped. Editing content
requires a restart.

Guardrail rules in `instructions.md` (seeded by the builder): answer only from the provided
material, say "I don't know — ask Akshay directly" otherwise, stay on topic, plain text replies,
short by default.

### Config

**logpose handles the model-access environment variables itself** *(Akshay's decision,
2026-11-23)*. `app/config.py` loads `.env` into the process environment (`load_dotenv`; variables
already set win), and logpose reads its own names. The app never touches their values; it only
checks presence to decide whether the assistant is on.

| Read by logpose | Notes |
|---|---|
| `LOGPOSE_BASE_URL`, `LOGPOSE_API_KEY`, `LOGPOSE_GUARD_API_KEY` | All three required; assistant is **enabled iff all are set**. Partly set → disabled, with a startup warning naming the missing ones |
| `LOGPOSE_DB_PATH` | Default `logpose.db`; the systemd unit sets `/var/lib/portfolio/logpose.db` |
| `LOGPOSE_TRACE`, `LOGPOSE_TRACE_CONTENT` | Review log on/off and whether it includes message text |

logpose has no variable for the rest, so they are app settings (`ASSISTANT_*`):

| Setting | Default | Notes |
|---|---|---|
| `assistant_model` | `gpt-6-luna` | |
| `assistant_reasoning_effort: str \| None` | `"low"` | Empty → omitted (needed for a non-reasoning fallback like `gpt-4o-mini`) |
| `assistant_max_output_tokens` | `2000` | Total billed output per turn (reasoning + visible) |
| `assistant_context_window` / `assistant_context_budget` | `1_050_000` / `16_000` | Model window and per-request input budget; the window must change with the model |
| `assistant_run_timeout_seconds` / `assistant_turn_timeout_seconds` | `60` / `45` | Whole reply / one model call |
| `assistant_retention_days` | `30` | Session lifetime, cookie lifetime and trace retention — one number |
| rate-limit numbers | see below | |

### Agent — created in a FastAPI `lifespan`, closed on shutdown

```python
Agent(
    "openai-compat",                                   # endpoint + key: LOGPOSE_BASE_URL / LOGPOSE_API_KEY
    model=settings.assistant_model,
    system=<assembled prompt>,
    max_tokens=settings.assistant_max_output_tokens,   # sent as max_completion_tokens
    max_iterations=1,                                  # no tools in v1
    run_timeout=settings.assistant_run_timeout_seconds,
    provider_turn_timeout=settings.assistant_turn_timeout_seconds,
    extra={"reasoning_effort": ...} or {},
    session_ttl=timedelta(days=settings.assistant_retention_days),
    context_window=settings.assistant_context_window,
    context_budget=settings.assistant_context_budget,  # bound input cost of long chats
    input_guardrails=[pattern_guard(...), openai_decision_guard(...)],
    guardrail_mode="parallel",
)                                                      # db path + tracing: LOGPOSE_DB_PATH / LOGPOSE_TRACE*
```

- **Guardrails** *(Claude's calls; all text and thresholds read from `guardrails.md`)*:
  `pattern_guard(max_chars=…, block_patterns=…, reply=…)` then
  `openai_decision_guard(domain, replies={"off_topic": …, "unsafe": …},  # key: LOGPOSE_GUARD_API_KEY
  client=<shared httpx client from lifespan>, on_error="allow")`. Domain text covers questions
  about Akshay's work, projects, skills, writing and contact, **plus greetings and questions about
  the assistant itself** (so "hi" isn't blocked). `parallel` mode hides guard latency; a blocked
  message may cost a few main-model tokens. `on_error="allow"` so a guard outage doesn't take the
  chat down — instructions and rate limits still apply.
  *Tuned 2026-11-24:* the original domain text at `on_topic_min: 0.5` blocked 53 of 142 genuine
  test questions, because the judge cannot see the resume. The domain text was rewritten (it now
  names his projects, employers and the kinds of short question visitors type) and the threshold
  lowered to `0.2`: 0 of 142 genuine questions blocked, 62 of 67 off-topic and 16 of 16 unsafe
  messages blocked. `instructions.md` carries the same off-topic rule for whatever gets through.
  The domain text is collapsed to one line when loaded, since the judge's scores shift when its
  line breaks move.
- **Compaction** stays on (logpose default) with a 16k input budget; summaries persist with the
  session. The system prompt counts toward the budget — if the assembled prompt exceeds ~8k tokens,
  raise `context_budget`.
- **Cleanup**: a lifespan background task runs at startup and every 24 h:
  `purge_expired_sessions()` then `purge_traces(older_than=retention)`.

### Visitor identity — one cookie

- `chat_sid`: `secrets.token_urlsafe(32)`, `HttpOnly`, `SameSite=Lax`, `Secure` unless
  `settings.debug`, `Path=/api/chat`, `Max-Age` = retention. Set by the server on the first chat
  request; never accepted from the URL or body. A malformed value is treated as absent.
- It holds no personal data and is the site's only cookie. Ownership = possession of the cookie.

### Endpoints — `app/routes/assistant.py` (all 503 when the assistant is disabled)

- **`POST /api/chat`** — body `{"message": str}` (1–2000 chars, JSON only). Flow: rate-limit check
  → read or mint `chat_sid` → enter `agent.session(sid)` via `AsyncExitStack` **before** building
  the response (`SessionBusyError` → 409) → `StreamingResponse` over
  `aclosing(agent.stream(message, session=handle, extra={"safety_identifier": sha256(sid)},
  metadata={"page": <path>}))`, closing the stack in `finally` and as a `BackgroundTask` (the
  pattern in logpose's README "Sessions").
  - SSE events: `delta` `{"text"}` · `done` `{"blocked": bool}` · `error` `{"message"}`.
    Headers: `Cache-Control: no-cache`, `X-Accel-Buffering: no`.
  - A guardrail block arrives as a normal `TextDelta` (the placeholder) + `RunEnd` with
    `stop_reason="refusal"` → `done` with `blocked: true`. Blocked exchanges are not saved to the
    session, so they disappear on reload — acceptable.
  - `stop_reason == "max_tokens"` → send the partial text then `error` ("Answer was cut short…").
  - `ProviderError` / `RunTimeoutError` → `error` event with safe text; detail to the server log.
  - `error` events carry `"retry": true|false`. A turn that fails or is abandoned (stop button,
    closed tab) is **rolled back** before the session saves, so it is never stored as a question
    with no answer; the panel offers retry only for those turns.
  - `ThinkingDelta` and other events are ignored.
- **`GET /api/chat/history`** — `agent.load_session(sid)` → `[{"role", "text"}]` for messages with
  text. No cookie / bad cookie → `[]`. Takes no lease, so it works mid-stream in another tab.
- **`POST /api/chat/reset`** — issues a fresh `chat_sid`. *(Claude's call)* The old session is
  **not** deleted: it expires with retention, so the conversation stays in Akshay's review log.
  The button is therefore labelled "New chat", not a trash icon.

### Rate limiting (in-memory, no new dependency)

Per client IP: 20 chat requests / 10 min sliding window. Global: 1,000 chat requests / UTC day as
a spend ceiling. 429 with `Retry-After`. Client IP from `request.client.host` (the unit already
runs uvicorn with `--proxy-headers --forwarded-allow-ips 127.0.0.1`). Also recommended: a monthly
budget limit on the OpenAI project (manual).

### Reviewing chats

`python -m scripts.export_chats <out.jsonl>`: calls `export_traces(<out.jsonl>)` (OTLP/JSON,
one trace per line; includes prompts and answers when content capture is on). Run by hand on the
server. A readable viewer is out of scope.

### Deployment changes

- `deploy/portfolio.service`: add `StateDirectory=portfolio` (gives a writable
  `/var/lib/portfolio` under `ProtectSystem=strict`) and `StateDirectoryMode=0700`.
- Prod `.env`: the three required `LOGPOSE_*` variables. The unit sets
  `LOGPOSE_DB_PATH=/var/lib/portfolio/logpose.db` itself.
- `.gitignore`: `logpose.db*`. README: setup notes.

### Frontend — `templates/partials/assistant.html` (included from `base.html`)

*(Revised 2026-11-23 after Akshay's UI review: floating ask bar instead of a nav button; no
expand control; no storage notice or contact link in the panel.)*

- **Floating ask bar**: sticks to the bottom centre of the screen while the page scrolls, and
  rests just **above the footer** at the end of the page (`position: sticky`, placed before the
  footer in `base.html`); shown while the panel is closed
  (full width minus gutters on phones): sparkle icon, single-line input with the placeholder from
  `panel.md`, send button. Submitting opens the panel, loads the earlier
  conversation, then sends; submitting it empty just opens the panel. While the panel is open the
  bar is invisible but keeps its space, so the page does not jump. There is no assistant button
  in the nav.
- **Keys**: `Esc` closes the panel. No open shortcut (Akshay removed `⌘I` as Mac-specific).
  Focus moves to the composer on open.
- **Panel**: fixed right drawer, `w-assistant-panel` (400px) on desktop, full-screen on mobile;
  overlays the page. Header: `ASSISTANT` label, new chat (＋, calls `/api/chat/reset`), close (✕).
  Sharp corners, tokens only.
- **History**: fetched from `/api/chat/history` the first time the panel opens on a page (or at
  load if it was left open). Only the open state lives in `sessionStorage` (try/catch).
- **Messages**: user = right-aligned bubble `bg-surface-container-high`; assistant = plain text
  `text-on-surface-variant`, `whitespace-pre-wrap` (no markdown renderer). Copy on assistant
  messages.
- **Empty state**: greeting plus the clickable starter questions from `panel.md` (any number,
  including none).
- **Composer**: textarea (Enter sends, Shift+Enter newline), send disabled while streaming or
  empty; a stop button replaces send while streaming (aborts the fetch). Nothing below it.
- **States**: typing indicator before first delta; inline error with **retry for failed sends
  only**; 429 and 409 get their own short messages.
- **No storage notice**: Akshay removed it. Conversations are still stored (sessions always; full
  text in traces when `LOGPOSE_TRACE_CONTENT=1`), so the "tell visitors" anti-goal above is now
  his to cover elsewhere (e.g. a privacy note) or by turning content capture off.
- One Alpine component (`x-data="assistant()"`); its function lives in an inline `<script>` in the
  partial (stream parsing needs `fetch` + `ReadableStream`).

## Verification (done = all pass)

1. `ruff check .` and `ruff format --check .` clean; Tailwind build succeeds.
2. Dev server: `/`, `/projects`, `/blog` render with and without the `LOGPOSE_*` variables (panel hidden
   without it; chat endpoints → 503).
3. `curl -N` with a cookie jar: first request sets `chat_sid` and streams `delta`…`done`; second
   request remembers the first; `/api/chat/history` returns both turns; without the cookie → `[]`.
4. Live checks on `gpt-6-luna`: 5–10 real questions are grounded; "don't know" for off-material;
   `reasoning_effort` accepted via `extra`; the Decisions API guard works with the key; "hi" is
   allowed and an off-topic request is blocked; note first-token latency.
5. **Stopped reply**: abort mid-stream, then send another message and reload history — the session
   must still work and render sensibly. (A stopped run saves the user message without a reply;
   confirm logpose/OpenAI handle the follow-up.) If not, raise it before shipping.
6. Rate limit: 21st request in the window → 429. Concurrent request on one session → 409.
7. `scripts/export_chats.py` produces a file containing the test conversation.
8. Panel UX at desktop and mobile widths: open/close/Esc, stream, stop, copy, new chat, history
   restored after navigation and after reopening the browser.

## Left to the builder

- Exact copy of seeded `instructions.md`, greeting, starter questions, guard domain and replies.
- Exact Tailwind classes/spacing within the token rules; icon choices (Material Symbols).
- Internal structure of the rate limiter, SSE helper and cleanup task.
- How `EXPERIENCE`/`PROJECTS` are rendered to markdown.
