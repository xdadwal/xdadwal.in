---
# Checks that run on every visitor message before the assistant answers.
max_chars: 2000        # longer messages get the too_long reply
# The topic check scores each message from 0 (off topic) to 1 (on topic) using only the text
# below this block; it never sees the resume. In the labelled tests genuine questions scored 0.15
# and up ("how can I get in touch", "is this a bot"), many plain yes/no ones 0.47 to 0.5, and
# clearly unrelated messages mostly 0.12 and below, so the threshold sits between. Scores shift whenever this
# text changes: after editing it, re-run the labelled messages. Keep the threshold low: a wrongly
# blocked visitor is worse than an off-topic message reaching the model, which instructions.md
# tells it to decline.
on_topic_min: 0.14    # below this "on topic" score, the off_topic reply is sent; 0 = never
unsafe_max: 0.5        # above this "unsafe" score, the unsafe reply is sent
block_patterns: []     # optional regexes; a match gets the blocked_pattern reply
replies:
  too_long: "That message is too long for me. Try a shorter question."
  blocked_pattern: "I can't help with that."
  off_topic: "I can only help with questions about Akshay and his work."
  unsafe: "I can't help with that."
---
a visitor asking about the person this website belongs to (Akshay Dadwal, a software engineer,
also referred to as "he"): his work, career, experience, skills, background, age, pay,
availability, resume, profiles (GitHub, LinkedIn, email) or contact details; his projects and
volunteering (logpose, dex-cli, ohara, his homelab, a Django boilerplate, mentoring on Exercism); his employers, their products and their
clients (Detect Technologies, Sherlock, Nova Scotia Power, Attentive.ai, Feathers, Renewbuy); or his
experience with a technology (such as Python, Django, FastAPI, PostgreSQL, Redis, Kafka, AWS,
GCP, Kubernetes or any other). Also within the domain: questions put to the chat assistant about
itself or this website, such as "are you an AI?", "what model are you?", "what can you do?" and
"how was this site built?". Short, vague or misspelled questions and bare words such as "skills",
"resume", "linkedin" or "django?" are within the domain unless they are clearly about something
else. Outside the domain: requests to explain, teach or compare technologies, to write, fix or
translate something, and questions about anything other than Akshay, this website or its assistant
