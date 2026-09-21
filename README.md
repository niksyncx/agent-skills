# The Syncx agent skill

Four Claude skills that write the things Syncx people write all day. No signup,
no API key, nothing to connect.

One turns a finished investigation into a reply the customer can act on. One
writes the internal note on that same investigation, where what is proven stays
separate from what is still a guess. One explains a diff to whoever did not
write it.

And one is the humanizer, which is the reason the other three are usable. It
strips the em dashes, the stock vocabulary and the invisible watermark
characters out of a draft, then scores what is left against a five-check panel
before anyone sees it.

Nothing gets sent until you say so. These skills draft. You send.

## Install

Paste this into Claude:

```
https://github.com/niksyncx/agent-skills
Install this skill, then confirm /human works.
```

Or as a plugin, in an interactive `claude` terminal:

```bash
/plugin marketplace add niksyncx/agent-skills
/plugin install syncx@syncx-agent-skills
```

Claude Code only, for now. The skills are written against its plugin and skill
loading, and nothing else has been tested.

## The four

| command | what it does |
|---|---|
| `/support-reply` | A finished investigation into a customer reply. 200 words, cause in sentence one, split by who fixes it. |
| `/internal-note` | The same investigation, written for the team. Status, found, proven, assumed, next. Proven and assumed never share a bullet. |
| `/explain-change` | A diff, branch or PR explained as plain text. Background, intuition, code, consequences. |
| `/human` | The humanizer. Two scripts that actually run. See below. |

They compose. `support-reply` and `explain-change` and `internal-note` decide
what to say, `human` decides how it reads and runs last. A reply that sounds
human but names the wrong profile is still a bad reply.

## The humanizer

`/human` ships two Python scripts with no dependencies. Stdlib only, no network,
no API key. They run on your machine, on your text, and nothing is uploaded.

```bash
python3 humanize.py draft.txt --report      # clean it, show every change
python3 detect.py draft.txt                  # score it, five checks
python3 detect.py before.txt after.txt       # prove the delta
pbpaste | python3 humanize.py - --report     # nothing touches disk
```

`detect.py` exits 0 on PASS and 1 otherwise, so it works as a CI gate on docs or
a pre-commit hook.

What comes out automatically:

- **Invisible characters.** 17 classes: zero-width spaces and joiners, word
  joiners, soft hyphens, byte-order marks, Unicode tag characters, non-breaking
  and narrow spaces. A keyboard does not produce these. They survive copy-paste
  and they are invisible in every editor you own.
- **Typography.** 11 substitutions. Em dash to comma, en dash to hyphen, curly
  quotes to straight, ellipsis to three dots.
- **The lexicon.** 174 words and 79 phrases with plain-English replacements,
  capitalisation preserved and URLs untouched. It lives in `slop.json`.

What gets flagged instead of fixed: 15 structural tells, including "It's not
just X, it's Y", rule-of-three triads, one-word rhetorical questions and uniform
sentence length. Changing the shape of a sentence needs judgement, so those come
back for a rewrite rather than getting mangled by a regex.

The five checks, scored 0-100, higher is more human:

| check | what it measures |
|---|---|
| BURSTINESS | sentence-length variation. Models write even. |
| SPECIFICITY | numbers, names and concrete markers per 100 words |
| SLOP DENSITY | lexicon hits per 100 words |
| FINGERPRINT | invisible characters, em dashes, curly quotes |
| VOICE | contractions, person, structural tells |

Run against a deliberately terrible draft:

```
  BURSTINESS    ################........  67.2
  SPECIFICITY   ........................   0.0    0 concrete markers
  SLOP DENSITY  ........................   0.0    12 stock terms, 24.5 per 100 words
  FINGERPRINT   ##########..............  43.1    1 em dash
  VOICE         ####################....  84.0    1 structural tell [not-just]
  --------------------------------------------------------------
  HUMAN SCORE   ######..................  23.3   FLAGGED
```

After `humanize.py`, with the flagged structure still unrewritten:

```
  23.3 FLAGGED  ->  40.8 FLAGGED   (+17.5)
```

The rest of the distance is the part the script deliberately leaves to you. It
cannot invent the number that would fix SPECIFICITY, and it will not pretend to.

## The fine print, which is the honest part

**The five checks are local heuristics, not detector APIs.** They are modelled
on the signals public detectors key on and they run entirely on your machine.
They are not GPTZero, Originality, Copyleaks or Turnitin, they do not call those
services, and they cannot promise those verdicts. Fixing what they measure tends
to move those numbers, because they measure the same underlying things. That is
the whole claim.

**Short text scores badly and that is expected.** Under four sentences, three of
the five checks return `too short to judge` and flatten to 50, which sits below
the floor. A two-line answer can never reach PASS no matter how good it is. Read
the FINGERPRINT line and ignore the verdict.

**Do not run it on code.** The lexical pass rewrites plain words wherever it
finds them and does not know it is inside a fence. Not on config, SQL, logs,
stack traces or exact error strings. For markdown with inline code spans, split
the prose out, clean that, put it back.

**Customer data goes through stdin.** A finished support reply holds store
names, SKUs, profile IDs and run IDs. A draft file on disk gets copied, synced
and backed up. Pipe it. Mask the identifying values before a file exists, not
after.

**Read the diff, do not trust the output.** The lexical pass cannot tell a field
name from a word. Check that every identifier, error string and column name
survived byte-for-byte before anything is sent.

## Files

```
skills/human/humanize.py         the three cleaning passes
skills/human/detect.py           the five-check panel
skills/human/slop.json           the lexicon: 174 words, 79 phrases, 17 invisible
                                 classes, 11 typographic swaps, 11 structures
skills/support-reply/SKILL.md    investigation into a customer reply
skills/internal-note/SKILL.md    investigation into a note for the team
skills/explain-change/SKILL.md   diff, branch or PR into plain text
.claude-plugin/                  plugin and single-plugin marketplace manifests
```

## Scope

Internal Syncx tooling. No licence file, so no licence is granted.

The skills target Claude Code and are tested nowhere else. The two Python
scripts are a separate matter: stdlib-only, no Claude dependency, so they run
as a plain CLI, in a git hook, or in CI on their own.
