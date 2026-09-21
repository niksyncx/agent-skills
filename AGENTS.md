# AGENTS.md

Syncx writing tooling. Three skills, one shared CLI. This file is a pointer,
not a copy: each skill's real instructions live in its own `SKILL.md`, and that
file is the source of truth. Read the relevant one before you use it.

## The skills

| Skill | Read this | Use it when |
|---|---|---|
| `human` | `skills/human/SKILL.md` | Text is about to be read by a customer, a teammate or the public, and it must not read as generated. |
| `support-reply` | `skills/support-reply/SKILL.md` | Answering a customer about a feed, profile, or import/export failure. |
| `explain-change` | `skills/explain-change/SKILL.md` | Explaining a diff, branch or PR to whoever did not write it. |
| `internal-note` | `skills/internal-note/SKILL.md` | Writing up an investigation for the team: handoff, escalation, shift handover. |

Order matters. `support-reply`, `explain-change` and `internal-note` decide
what to say. `human`
decides how it reads, and runs last, after the content is correct. A reply that
sounds human but names the wrong profile is still a bad reply.

## The CLI

Python 3, stdlib only. No dependencies, no network, no API key. Runs anywhere,
with or without an agent.

```bash
python3 skills/human/humanize.py draft.txt --report   # clean it, show changes
python3 skills/human/detect.py draft.txt              # score it, five checks
python3 skills/human/detect.py before.txt after.txt   # prove the delta
pbpaste | python3 skills/human/humanize.py - --report # nothing touches disk
```

`detect.py` exits 0 on PASS, 1 otherwise, so it works as a CI gate or a
pre-commit hook.

`slop.json` is the lexicon and is meant to be edited. If it strips a word the
team actually uses, delete that entry and commit it.

## Rules that bite

**Prose only.** The lexical pass rewrites plain words wherever it finds them
and does not know it is inside a fence. Never run it on code, config, SQL,
logs, stack traces, or exact error strings. For markdown with inline code
spans, split the prose out, clean that, put it back.

**Customer data goes through stdin.** A finished support reply holds store
names, SKUs, profile IDs and run IDs. A draft file on disk gets copied, synced
and backed up. Pipe it. If you need a before/after score, mask the identifiers
before a file exists, not after.

**Read the diff, do not trust the output.** Check that every identifier, error
string and field name survived byte-for-byte before anything is sent.

**Short text scores badly and that is expected.** Under four sentences, three
of the five checks return `too short to judge` and flatten to 50, so a two-line
answer can never reach PASS. Read the FINGERPRINT line and ignore the verdict.

## Editing this repo

Skills are prose. Keep the instructions in `SKILL.md` and keep this file a
pointer, so the two cannot drift. If you add a skill, add a row to the table
above and to `README.md`.
