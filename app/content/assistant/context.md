---
# What the model is given, in this order. Edit this list to manage the assistant's context:
# remove a line to drop a source, reorder lines to change priority, add a line to include more.
#
#   - a path or glob relative to this folder (matching files are added in filename order)
#   - site:experience   the EXPERIENCE list in app/data.py
#   - site:projects     the PROJECTS list in app/data.py
#   - site:blog         titles, descriptions and links of published blog posts
#
# Run `python -m scripts.show_context` to print exactly what the model receives and its size.
# Changes take effect after the site restarts.
sources:
  - instructions.md
  - resume.md
  - knowledge/*.md
  - site:experience
  - site:projects
  - site:blog
---
