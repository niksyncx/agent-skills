---
name: human
description: >-
  Strip the machine fingerprint out of any draft - em dashes, AI slop words,
  invisible watermark characters - and score it against a six-check detection
  panel before it goes out. Use whenever text needs to sound human, when the
  user says humanize, "does this sound like AI", "remove the em dashes",
  "de-slop this", "will this get flagged", and before any Syncx customer reply,
  investigation write-up, release note, help-centre article, PR description or
  marketing post is shown to the user.
---

# human

Two tools live in this folder and they both actually run. Use them. Do not
eyeball this. Paths below are relative to this skill's base directory, which
is given to you when the skill is invoked.

**Never guess where the scripts live.** `~/.claude/skills/human` is only there
on a symlinked install, and a plugin install keeps them under a versioned cache
directory that changes on every update. If you do not have a base directory,
invoke this skill to get one rather than searching the filesystem for it.

```bash
python3 humanize.py draft.txt --report        # clean it, show what changed
python3 detect.py draft.txt                    # score it, six checks
python3 detect.py before.txt after.txt         # prove the delta
pbpaste | python3 humanize.py - --report       # nothing touches disk
```

Both read `slop.json`, which is the lexicon: 228 stock words and phrases with
plain-English replacements, 17 invisible character classes, 11 typographic
substitutions, and 11 structural tells.

## What this is for at Syncx

Anything a customer, a teammate or the public reads: support replies about a
feed or profile failure, investigation write-ups, release notes, help-centre
articles, PR and commit bodies, and marketing copy. Run it last, after the
content is correct. A reply that sounds human but names the wrong profile is
still a bad reply.

Pair it with `support-reply` for customer answers: that skill decides what to
say, this one decides how it reads.

## Protecting text: `@@like this@@`

Anything between `@@` markers is skipped by every pass and excluded from every
check. The markers are dropped from the output, so the cleaned text is ready to
send.

```
@@Shopify said "delve into the robust tapestry"@@ but the feed is ever-evolving
└─ survives byte-for-byte ──────────────────────┘                └─ replaced ─┘
```

Use it for quoted error strings, vendor field names, a customer's own words in
an internal note, and markdown inline code. Several spans can sit in one
sentence, and unprotected slop between them is still caught.

Three things to know:

- **Single line only.** A span cannot cross a newline, so a forgotten closing
  marker cannot swallow the rest of the draft.
- **No nesting.** Markers pair first-to-second, third-to-fourth. In
  `@@a@@b@@c@@` the `b` is exposed.
- **Check the report.** It prints `2 protected span(s) left untouched`. A
  mistyped marker shows up as a missing count rather than as damage.

The marker lives in `slop.json` under `protect`, so it can be changed without
touching the Python.

## Do not run it on these

- **Code, config, SQL, logs, stack traces.** The lexical pass rewrites plain
  words wherever it finds them, and it does not know it is inside a fence.
  Wrapping a whole file in `@@` is not the answer, just do not run it.
- **Anything carrying customer data.** No API keys, tokens, store domains,
  account IDs or merchant names in a draft file. Pipe stdin instead, so
  nothing lands on disk. If you must write a file, mask the identifiers
  before it exists, not after.

Error strings, vendor field names and markdown code spans used to be on this
list. Wrap them in `@@` instead.

## What gets fixed automatically

**1. Invisible characters.** Zero-width spaces and joiners, word joiners,
soft hyphens, byte-order marks, Unicode tag characters, non-breaking and
narrow spaces. A keyboard does not produce these. They survive copy-paste,
they are invisible in every editor, and they are the single most mechanical
thing in generated text. `humanize.py` deletes every one, including any
remaining Unicode format character it does not have a name for.

**2. Typography.** Em dash to comma, en dash to hyphen, curly quotes to
straight, ellipsis to three dots, bullet character to hyphen. The em dash pass
is the one that matters: it collapses the spaced em dash to a comma and then
cleans up the double punctuation that leaves behind.

**3. The slop lexicon.** delve, leverage, robust, seamless, crucial, tapestry,
testament to, moreover, "in today's fast-paced world", "let that sink in" and
the rest, each swapped for a plain word, with capitalisation preserved and
URLs left untouched.

## What does NOT get fixed automatically

Structural tells get **flagged, not rewritten**, because changing the shape of
a sentence needs judgement:

- The set-up-then-correct family: "It's not just X, it's Y", "not only X but
  also Y", "It isn't about X. It's about Y.", "Not because X. But because Y.",
  "Not by doing X, but by doing Y.", "No X. No Y. Just Z."
- Rule-of-three triads
- Rhetorical lines standing in for a claim: "The result?", "And the fix? Y."
- Model self-reference: "As an AI", "as a language model"
- Essay closers: a paragraph opening with "In summary" or "In conclusion"
- Three or more bullets of near-identical length

That list is your job. Rewrite each flagged line by hand, keeping the meaning,
then re-run `detect.py`. This is the part that moves the score from REVIEW to
PASS, and it is the part a script cannot do.

## The six checks

`detect.py` scores six signals 0-100, higher is more human:

| check | what it measures | machine looks like |
| --- | --- | --- |
| BURSTINESS | sentence-length variation | every sentence the same length |
| SPECIFICITY | numbers, names, concrete markers per 100 words | abstract nouns, no figures |
| SLOP DENSITY | lexicon hits per 100 words | stock vocabulary |
| FINGERPRINT | invisible chars, em dashes, curly quotes per 1k chars | typographically perfect |
| VOICE | contractions and person per 100 words | no contractions, third person |
| STRUCTURE | structural tells, bullets of equal length | staged reveals, templated shapes |

The verdict weights the mean at 60% and the **weakest single check** at 40%,
because a detector only needs one signal to fire. PASS needs an overall of 70+
with no check below 55.

VOICE and STRUCTURE were one check until they were split apart. VOICE now reads
prose only, and STRUCTURE reads shape, which works on any text type. A document
of tables and command blocks can score 100 on STRUCTURE and near zero on VOICE,
and both numbers are telling the truth about different things.

Technical writing fails VOICE first, almost every time. Profile numbers and
vendor names carry SPECIFICITY for free, so the score you will be fixing is
the one measuring contractions and second person. Write "you'll see" instead
of "the user will observe" and most of the gap closes.

**Short drafts cannot pass.** Under four sentences, BURSTINESS, SPECIFICITY
and VOICE all return `too short to judge` and score a flat 50, which sits
below the 55 floor. STRUCTURE has no length guard and will usually read 100 on
a short draft, which lifts the mean but cannot lift the floor. A short reply
cannot reach PASS no matter how well written it is. On anything short, read
FINGERPRINT and STRUCTURE, and ignore the verdict.

## Say this honestly

These are six local heuristics modelled on the signals public detectors key
on. They run entirely on the user's machine and nothing is uploaded. They are
**not** GPTZero, Originality, Copyleaks, Winston or Turnitin, they do not call
those APIs, and they cannot promise those verdicts. Fixing what they measure
does tend to move those numbers, because they are measuring the same
underlying things. That is the claim. Do not make a bigger one on the user's
behalf, and do not tell a user their text is undetectable.

## Order of operations

1. `humanize.py draft.txt -o clean.txt --report`
2. Read the structural flags. Rewrite those lines yourself.
3. `detect.py draft.txt clean.txt` to show the before and after.
4. If the verdict is not PASS, fix the weakest check named in the output and
   go again. Two rounds is normal. Five means the draft was written by
   formula, and the fix is a different draft, not more passes.
5. Show the user the cleaned text and the score. Never the score alone.
