# syncx-agent-skill

Internal Syncx tooling. Four skills: `human`, `support-reply`, `explain-change`
and `internal-note`, packaged as a Claude Code plugin.

The Python in `skills/human/` is stdlib-only and has no Claude dependency. It
runs as a plain CLI, in a git hook, or as a CI gate, with or without an agent.

## What it does

`support-reply` decides what to say to a customer. `explain-change` explains a
code change to whoever did not write it. `human` decides how either one reads,
and runs last.

`human` strips the machine fingerprint out of a draft and scores what is left. Two
Python scripts, one editable lexicon, no dependencies, no network. Everything
runs locally and nothing is uploaded.

Use it on anything a customer, a teammate or the public reads: support replies,
investigation write-ups, release notes, help-centre articles, PR bodies and
marketing copy. Do not use it on code, logs or exact error strings.

## Install

Once this is pushed to the Syncx org, teammates use the remote instead:

```bash
/plugin marketplace add syncx-org/syncx-agent-skill
/plugin install syncx@syncx
```

Both commands need an interactive `claude` terminal.

### Claude Code desktop app

`/plugin` does nothing in the desktop app. Paste this into a session instead:

```
https://github.com/syncx-org/syncx-agent-skill
Install this skill, then confirm /human works.
```

## Use

```bash
python3 skills/human/humanize.py draft.txt --report   # clean it, show changes
python3 skills/human/detect.py draft.txt              # score it
python3 skills/human/detect.py before.txt after.txt   # prove the delta
pbpaste | python3 skills/human/humanize.py - --report # nothing touches disk
```

`detect.py` exits 0 on PASS and 1 otherwise, so it works as a CI gate on docs.

**Pipe customer-facing drafts through stdin.** A finished support reply holds
store names, SKUs, profile IDs and run IDs. A draft file on disk gets copied,
synced and backed up. Mask the identifiers before a file exists, not after.

## Layout

```
AGENTS.md              pointer file for non-Claude agents: what each skill
                       is for, the CLI, and the rules that bite
.claude-plugin/
  plugin.json          plugin manifest
  marketplace.json     single-plugin marketplace, so the repo installs directly
skills/human/
  SKILL.md             when to run it, what it cannot fix, the honest claim
  humanize.py          three passes: invisible chars, typography, lexicon
  detect.py            five checks, 0-100, higher is more human
  slop.json            the lexicon. Edit it. It is meant to be yours.
skills/support-reply/
  SKILL.md             turn a finished investigation into a reply the
                       customer can act on, then hand it to human
skills/explain-change/
  SKILL.md             explain a diff, branch or PR as plain text:
                       background, intuition, code, consequences
skills/internal-note/
  SKILL.md             write up an investigation for the team, proven
                       split from assumed, every action owned
```

## The lexicon is yours

`slop.json` holds 17 invisible codepoints, 11 typographic swaps, 81 words,
32 phrases and 11 structural regexes. If it strips a word the team actually
uses, delete that entry and commit it. That is the intended workflow.

## What it is not

Five local heuristics modelled on the signals public detectors key on. Not
GPTZero, Originality, Copyleaks, Winston or Turnitin. No API calls to any of
them, and no promise of their verdict. Fixing what these measure does tend to
move those numbers, because they measure the same underlying things. Do not
tell anyone their text is undetectable.
