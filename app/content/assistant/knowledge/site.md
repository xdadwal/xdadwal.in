# This website and its assistant

- xdadwal.in is Akshay's personal website: a home page with his experience, a projects page and a
  blog at /blog.
- The site is built with FastAPI and Jinja2 templates on the server, Alpine.js for interactivity
  and Tailwind CSS for styling. Blog posts are Markdown files. It is self-hosted on a Linux
  server. The source is public at https://github.com/xdadwal/xdadwal.in.
- The assistant is an AI chat assistant. It runs on logpose, Akshay's own agent library, with an
  OpenAI language model behind it.
- It answers only from Akshay's resume and the notes he maintains for it. It cannot browse the
  web, look anything up or take actions, and it can be wrong; for anything important, confirm
  with Akshay.
- Conversations are stored for up to 30 days so Akshay can review and improve the assistant.
