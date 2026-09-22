# The Syncx agent skill

Four Claude skills that write the things Syncx people write all day. No signup,
no API key, nothing to connect.

One turns a finished investigation into a reply the customer can act on. One
writes the internal note on that same investigation, where what is proven stays
separate from what is still a guess. One explains a diff to whoever did not
write it.

And one is the humanizer, which is the reason the other three are usable. It
strips the em dashes, the stock vocabulary and the invisible watermark
characters out of a draft, then scores what is left against a six-check panel
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

## Updating

Nothing updates on its own. An install pins one commit and stays there until
you move it:

```bash
claude plugin marketplace update syncx-agent-skills
claude plugin update syncx@syncx-agent-skills
```

Marketplace first, that refetches the catalogue. The second command moves the
pinned commit forward and re-caches. Restart Claude Code to apply.

**Maintainers: the version must change for an update to reach anyone.** The
updater compares versions, not commits. Leave the version alone and it reports
`already at the latest version`, fetches nothing, and everyone stays on an old
copy while being told they are current.

A tracked `pre-commit` hook bumps the patch digit for you. Enable it once per
clone, since git does not ship hooks:

```bash
git config core.hooksPath .githooks
```

Bump the minor or major by hand when a change deserves it. The hook only ever
touches the patch digit.

### Claude Code desktop app

These are CLI commands, not slash commands, so the missing `/plugin` dialogs do
not block them. Run them in the app's own Terminal panel, or paste this into a
session and let Claude run them:

```
Run these two commands and show me the output:

claude plugin marketplace update syncx-agent-skills
claude plugin update syncx@syncx-agent-skills

Then tell me which commit it moved to, and whether I need to restart.
```

Ask for the output. A pinned plugin fails quietly, and without seeing the
commands run you cannot tell an update from a no-op.

The paste-the-URL route has no update path, because it is not a defined install
path. Use it to try the skills, use the plugin route if you want to keep them
current.

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
python3 detect.py draft.txt                  # score it, six checks
python3 detect.py before.txt after.txt       # prove the delta
pbpaste | python3 humanize.py - --report     # nothing touches disk
```

`detect.py` exits 0 on PASS and 1 otherwise, so it works as a CI gate on docs or
a pre-commit hook.

## Protecting what must not change: `@@`

The cleaner rewrites plain words wherever it finds them. It has no idea whether
a word is your prose or somebody else's exact words, so left alone it will
happily edit an error message into something the vendor never said.

Wrap anything that must survive in `@@`:

```
@@Shopify said "delve into the robust tapestry"@@ but the feed is ever-evolving
└─ survives byte-for-byte ──────────────────────┘                └─ replaced ─┘
```

The markers are dropped from the output, so the cleaned text ships as it is.
`detect.py` ignores protected spans too, which stops a quoted vendor string
dragging your slop score down for text you are not allowed to touch.

### The three things worth marking

**A customer's own words.** Their sentence is evidence. Paraphrasing it into
better English is how a quote stops being a quote.

```
in:   The merchant wrote @@it's not just slow, it's completely broken@@ on Friday.
out:  The merchant wrote it's not just slow, it's completely broken on Friday.
```

That phrasing is a structural tell, so unmarked it would be flagged for rewrite.
Marked, it is not your sentence to fix.

**Error messages and field names.** One changed character makes an error string
ungreppable and a field name wrong.

```
in:   The run failed with @@Shopify said "handle already taken"@@ on every row.
in:   @@existing_product_identifier@@ was pointed at the wrong column.
```

**Code, paths and identifiers.** SKUs, profile IDs, file paths, commands.

```
in:   Set @@core.hooksPath@@ to @@.githooks@@ or the version stops bumping.
in:   @@LO-03-****-00016-00@@ was renamed in the store.
```

### Three rules

- **One line per span.** A span cannot cross a newline, so forgetting a closing
  marker costs you one line, not the rest of the document.
- **No nesting.** Markers pair first-to-second, third-to-fourth. In
  `@@a@@b@@c@@` the `b` is exposed.
- **Check the count.** The report prints `2 protected span(s) left untouched`.
  A mistyped marker shows up as a wrong count, before it shows up as damage.

Whole files of code, config, SQL or logs are not a case for `@@`. Do not run the
cleaner on them at all.

The marker is defined in `slop.json` under `protect`, so you can change it
without touching the Python.

What comes out automatically:

- **Invisible characters.** 17 classes: zero-width spaces and joiners, word
  joiners, soft hyphens, byte-order marks, Unicode tag characters, non-breaking
  and narrow spaces. A keyboard does not produce these. They survive copy-paste
  and they are invisible in every editor you own.
- **Typography.** 11 substitutions. Em dash to comma, en dash to hyphen, curly
  quotes to straight, ellipsis to three dots.
- **The lexicon.** 174 words and 54 phrases with plain-English replacements,
  capitalisation preserved and URLs untouched. It lives in `slop.json`.

What gets flagged instead of fixed: 11 structural tells, including "It's not
just X, it's Y", "Not because X. But because Y.", rule-of-three triads and
one-word rhetorical questions. Changing the shape of a sentence needs judgement, so those come
back for a rewrite rather than getting mangled by a regex.

The six checks, scored 0-100, higher is more human:

| check | what it measures |
|---|---|
| BURSTINESS | sentence-length variation. Models write even. |
| SPECIFICITY | numbers, names and concrete markers per 100 words |
| SLOP DENSITY | lexicon hits per 100 words |
| FINGERPRINT | invisible characters, em dashes, curly quotes |
| VOICE | contractions and person per 100 words |
| STRUCTURE | structural tells, bullets of equal length |

Run against a deliberately terrible draft:

```
  BURSTINESS    ################........  67.2
  SPECIFICITY   ........................   0.0    0 concrete markers
  SLOP DENSITY  ........................   0.0    12 stock terms, 24.5 per 100 words
  FINGERPRINT   ##########..............  43.1    1 em dash
  VOICE         #####################...  86.6    6.1 contractions per 100 words
  STRUCTURE     ###################.....  78.0    1 structural tell [not-just]
  --------------------------------------------------------------
  HUMAN SCORE   #######.................  27.5   FLAGGED
```

Note VOICE at 86.6 on a draft that is otherwise appalling. It is chatty, so it
scores well on the one thing VOICE measures. The mean cannot hide the two zeros
because the weakest check carries 40% of the verdict on its own.

After `humanize.py`, with the flagged structure still unrewritten:

```
  27.5 FLAGGED  ->  42.9 FLAGGED   (+15.4)
```

The rest of the distance is the part the script deliberately leaves to you. It
cannot invent the number that would fix SPECIFICITY, and it will not pretend to.

## The fine print, which is the honest part

**The six checks are local heuristics, not detector APIs.** They are modelled
on the signals public detectors key on and they run entirely on your machine.
They are not GPTZero, Originality, Copyleaks or Turnitin, they do not call those
services, and they cannot promise those verdicts. Fixing what they measure tends
to move those numbers, because they measure the same underlying things. That is
the whole claim.

**Short text scores badly and that is expected.** Under four sentences, three of
the checks return `too short to judge` and flatten to 50, which sits below
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
skills/human/detect.py           the six-check panel
skills/human/slop.json           the lexicon: 174 words, 54 phrases, 17 invisible
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
