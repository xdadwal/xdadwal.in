# xdadwal.in
This is my personal website, currently under construction.

## Assistant

A chat panel on every page answers visitors' questions about me. It runs on
[logpose](https://github.com/xdadwal/logpose) with an OpenAI model, and is switched off unless
its `LOGPOSE_*` variables are set (see Settings).

### Content

Everything the assistant knows and says lives in `app/content/assistant/`. Edit the files and
restart the site; no code changes are needed.

| File | What it controls |
| --- | --- |
| `context.md` | Which sources the model is given, and in what order |
| `instructions.md` | Voice, scope, topics it declines |
| `resume.md`, `knowledge/*.md` | The facts it answers from |
| `guardrails.md` | Message length cap, topic check wording and thresholds, replies to blocked messages |
| `panel.md` | Greeting, placeholder, starter questions, contact button and credit line for the ask bar and chat panel |

`python -m scripts.show_context` prints the size of each source the model receives
(`--full` prints the whole prompt).

The topic check judges each message against the paragraph in `guardrails.md` alone; it never
sees the resume. When you add a project, employer or notable tool to the resume, name it in that
paragraph too, or short questions about it may be blocked.

### Settings

Copy `env.example` to `.env` (never committed) and fill in the blank keys; it lists every setting
with its default. The app loads `.env` into the
process environment at startup; variables already exported in the shell or set by systemd win.

Model access is configured through logpose's own variables. logpose reads them itself; the app
only checks that they are present.

| Variable | Purpose |
| --- | --- |
| `LOGPOSE_BASE_URL` | Model endpoint, e.g. `https://api.openai.com/v1` (required) |
| `LOGPOSE_API_KEY` | Key for the model (required) |
| `LOGPOSE_GUARD_API_KEY` | Key for the topic and safety check; for OpenAI, the same key (required) |
| `LOGPOSE_DB_PATH` | Chat database; default `logpose.db`, the systemd unit sets `/var/lib/portfolio/logpose.db` |
| `LOGPOSE_TRACE` | `1` keeps a review log of each conversation turn |
| `LOGPOSE_TRACE_CONTENT` | `1` includes the questions and answers in that log |

The assistant is on only when all three required variables are set. If only some are, it stays
off and the server log names the missing ones.

logpose has no variable for these, so the app reads them:

| Variable | Default | Purpose |
| --- | --- | --- |
| `ASSISTANT_MODEL` | `gpt-6-luna` | Model |
| `ASSISTANT_REASONING_EFFORT` | `low` | Leave empty for models without reasoning |
| `ASSISTANT_MAX_OUTPUT_TOKENS` | `2000` | Output ceiling per reply, reasoning included |
| `ASSISTANT_CONTEXT_WINDOW` | `1050000` | The model's context window; change it with the model |
| `ASSISTANT_CONTEXT_BUDGET` | `16000` | Input tokens per request before older turns are summarized |
| `ASSISTANT_RUN_TIMEOUT_SECONDS` | `60` | Time allowed for a whole reply |
| `ASSISTANT_TURN_TIMEOUT_SECONDS` | `45` | Time allowed for one model call |
| `ASSISTANT_RETENTION_DAYS` | `30` | How long chats, ratings and the visitor cookie are kept |
| `ASSISTANT_FEEDBACK_DB_PATH` | `feedback.db` | Ratings database; the systemd unit sets `/var/lib/portfolio/feedback.db` |
| `ASSISTANT_RATE_LIMIT_PER_IP` | `20` | Messages per visitor per 10 minutes; `0` = no limit |
| `ASSISTANT_RATE_LIMIT_PER_DAY` | `1000` | Messages per day across all visitors; `0` = no limit |

Set a monthly budget on the OpenAI project as a second ceiling on spend.

### Reviewing chats

`python -m scripts.export_chats chats.jsonl` writes stored conversations as OTLP/JSON, one turn
per line.

Visitors can rate an answer with a thumbs up or down. `python -m scripts.show_feedback` lists the
ratings with the question and answer each one is about.

### Deploying

`deploy/portfolio.service` sets `StateDirectory=portfolio`, which gives the locked-down service a
writable `/var/lib/portfolio`, and points `LOGPOSE_DB_PATH` and `ASSISTANT_FEEDBACK_DB_PATH` at it. After pulling, reinstall the
unit, run `sudo systemctl daemon-reload`, add the three required `LOGPOSE_*` variables to the
server's `.env`, and restart.

