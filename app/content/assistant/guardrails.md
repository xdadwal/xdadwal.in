---
# Checks that run on every visitor message before the assistant answers.
max_chars: 2000        # longer messages get the too_long reply
on_topic_min: 0.5      # below this "on topic" score, the off_topic reply is sent
unsafe_max: 0.5        # above this "unsafe" score, the unsafe reply is sent
block_patterns: []     # optional regexes; a match gets the blocked_pattern reply
replies:
  too_long: "That message is too long for me. Try a shorter question."
  blocked_pattern: "I can't help with that."
  off_topic: "I can only help with questions about Akshay and his work."
  unsafe: "I can't help with that."
---
Questions about Akshay Dadwal: his work experience, employers, roles, projects (including
logpose), skills and technologies, awards, education, writing and blog posts, location,
availability, and how to contact him. Also on topic: greetings, thanks, small talk that opens or
closes a conversation, follow-up questions about earlier answers, and questions about what this
assistant can do.
