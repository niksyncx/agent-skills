---
name: "explain-change"
description: "Explain a code change, diff, branch or PR as plain text a reader can follow. Use when the user asks what a change does, to walk through a diff or PR, to write a PR body or review note, or to hand a change to someone who did not write it. Text only, no HTML, no files."
---

# Explain change

Teach the change, do not narrate the diff. Output is text in the reply. No
HTML file, no artifact, no `/tmp` deliverable.

## Investigate before writing

1. **Find the change.** Working tree, `git diff`, a branch, a PR, or files the
   user pasted. Ambiguous? Pick the most likely one and say which in the first
   line. Do not stop to ask.
2. **Read around it.** Callers, tests, config, data models, docs. Trace the old
   path and the new path far enough to describe behaviour, not edits.
3. **Only claim what the source shows.** Anything inferred gets marked as
   inferred. A confident wrong mechanism is the expensive failure here, same as
   in `support-reply`.

## Output shape

Four sections, this order, markdown headings:

**Background** - the parts of the system the change touches, and how they
behaved before. Nothing else about the system.

**Intuition** - the idea, before any code. One small concrete example, real
values. Show before and after when the contrast is the point.

**Code** - the changes grouped by what they do, ordered by execution flow, not
by filename. Reference `path/to/file.py:42`. Quote only the lines that carry
the change. Never paste the whole diff.

**Consequences** - edge cases, trade-offs, what a reader will observe at
runtime, what is now easy or hard that was not before.

## Length

Match the change. A one-function fix is a short page. A migration is longer.
If a section has nothing real in it, cut the heading. Padding a section to look
complete is worse than a missing one.

## Rules

- Plain prose. Explain jargon the first time it appears.
- No ASCII diagrams, no box drawing. If structure matters, use a short list or
  a small table.
- Code in fenced blocks, unchanged, exact.
- Distinguish observed from interpreted. "The retry loop now caps at 3" is
  observed. "This probably fixes the timeout reports" is interpreted, and say so.

## De-slop before handing it over

Run the `human` skill on the prose before showing the explanation. That is the
last step, after the content is right.

Prose only. Code blocks, file paths, exact error strings and identifiers go
through untouched - `humanize.py` rewrites plain words wherever it finds them
and does not know it is inside a fence. Split the prose out, clean it, put it
back.

Mask customer data and secrets before any text lands on disk. Pipe stdin:

```bash
pbpaste | python3 humanize.py - --report
```
