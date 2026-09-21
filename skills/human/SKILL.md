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

## Do not run it on these

- **Code, config, SQL, logs, stack traces.** The lexical pass rewrites plain
  words wherever it finds them, and it does not know it is inside a fence.
- **Markdown with inline code spans.** It protects URLs, nothing else. A
  documented character inside backticks gets substituted like prose and the
  meaning dies. Split the prose out, clean that, put it back.
- **Exact error strings and vendor field names.** Those are evidence. Keep
  them byte-for-byte.
- **Anything carrying customer data.** No API keys, tokens, store domains,
  account IDs or merchant names in a draft file. Pipe stdin instead, so
  nothing lands on disk. If you must write a file, mask the identifiers
  before it exists, not after.

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

- "It's not just X, it's Y" and "not only X but also Y"
- Rule-of-three triads
- Rhetorical one-word question lines: "The result?"
- Rocket, fire, bulb, sparkle and dart emoji
- Hashtag walls
- Reflex engagement bait: "Thoughts?", "Agree?", "Who else?"
- Uniform sentence length and uniform bullet length

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
a short draft, which lifts the mean but cannot lift the floor. A 22-word reply tops out at 62.0 REVIEW no matter how
well written it is. On anything short, read the FINGERPRINT line and ignore
the verdict.

## Say this honestly

These are five local heuristics modelled on the signals public detectors key
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
