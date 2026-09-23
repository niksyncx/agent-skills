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

- **No em dashes.** Comma or full stop. Write it right the first time rather
  than leaving it for the humanize pass: that pass runs last, it is easy to
  skip, and an explanation written straight into a reply never goes through it.
  It is the one mark that makes a correct explanation read as generated.
- Backtick every identifier: file paths, line references, function and field
  names, commands, config keys. Backticks are for the reader and stay in the
  output. `@@` is for the cleaner and gets stripped. They are different marks,
  and backticks alone do not protect a word from the lexicon.
- Plain prose. Explain jargon the first time it appears.
- No ASCII diagrams, no box drawing. If structure matters, use a short list or
  a small table.
- Code in fenced blocks, unchanged, exact.
- Distinguish observed from interpreted. "The retry loop now caps at 3" is
  observed. "This probably fixes the timeout reports" is interpreted, and say so.

## De-slop before handing it over

Run the `human` skill on the prose before showing the explanation,
`/syncx:human` when this is installed as the plugin. It knows where its own
scripts live, so there is no path to get wrong. That is the last step, after
the content is right.

Hand it the prose through stdin. Mask customer data and secrets before any text
lands on disk.

### Mark the exact bits with `@@` first

`humanize.py` rewrites plain words wherever it finds them and does not know it
is inside a fence. This page is dense with things that must not move: file
paths, line references, function and field names, commands, exact error text.
Wrap each one in `@@`:

```
The retry loop in @@src/sync/runner.py:88@@ now caps at 3, and
@@existing_product_identifier@@ is read before @@check_existing@@ runs.
It failed with @@Shopify said "handle already taken"@@ on every row.
```

Everything inside the markers survives byte-for-byte and is excluded from the
score. Everything outside is cleaned normally.

One span per line, and no nesting. Check the report's
`N protected span(s) left untouched` against what you marked.

**The markers never reach the reader.** `humanize.py` strips them, so the
cleaned text is the explanation. If you skip the humanize pass, delete the
markers yourself before showing the page: `@@` is a working mark for the
cleaning step, not part of the output.

Fenced code blocks are a different problem. Do not mark them and do not feed
them through at all, since a block can run to dozens of lines and a span cannot
cross a newline. Clean the prose around them and leave the blocks alone.
