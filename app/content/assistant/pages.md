---
# Tells the model which page the visitor is on when they send a message, so it can make sense of
# "this page", "these projects" or "this post". The note is placed in front of the visitor's
# message; they never see it, and their chat history shows only what they typed.
#
# {page} is replaced with one of the descriptions below. A page that is not listed gets no note.
# Delete this file to stop telling the model the page.
note: "[Website note, not written by the visitor: they are viewing {page}.]"
pages:
  "/": "the home page, which shows Akshay's introduction and work experience"
  "/projects": "the projects page, which lists Akshay's projects"
  "/blog": "the blog index, which lists Akshay's posts"
# Used for a published blog post. {title} and {path} are filled in from the post.
post: "the blog post \"{title}\" at {path}"
---
