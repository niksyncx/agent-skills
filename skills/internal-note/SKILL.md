---
name: "internal-note"
description: "Write the internal note on an investigation: what was found, what is proven, what is still a guess, who holds it next. Use for handoffs, escalation notes, what-we-found summaries, shift handovers and Slack updates to the team. Not for anything the customer reads, that is support-reply."
---

# Internal note

Bullets, not paragraphs. A teammate picking this up cold should know in thirty
seconds what is true, what is not, and what they have to do.

## The opposite of support-reply on three points

`support-reply` bans internal vocabulary, keeps the mechanism to one sentence,
and never shows its working. An internal note does all three in reverse.

- **Use the real names.** `row_group`, `dedupe_check`, `product_title`,
  the exact column, the exact profile ID. Translating them for a teammate
  destroys the thing they need to grep for.
- **Show the mechanism.** That is the note's whole job.
- **Show the working.** Where you looked, what you read, what you ran.

## Structure

```
Status: [one line. blocked / waiting on X / fixed, unverified / done]

Found:
- [the cause, with the real field and value]
- [the second cause, if there is one]

Proven:
- [what you actually read, and where. run ID, log line, config value]

Assumed:
- [what you inferred but did not confirm, and what would confirm it]

Next:
- [action] [owner] [by when, if it matters]
```

Drop a section only when it is genuinely empty. **Never drop `Assumed`
silently.** If it is empty, write `Assumed: nothing, all of the above was
read directly.` An absent `Assumed` block reads as "everything is verified",
and that is the lie that costs days.

## Hard rules

**1. Status first, one line.** Whoever opens this is deciding whether to act.
Tell them before anything else.

**2. Split proven from assumed, always.** This is the entire point of the
note. A guess written like a finding is how a note does damage: someone
downstream builds on it, and nobody goes back to check whether the bullet
had a source.

**3. One line per fact.** If a bullet needs a second sentence, it is two
bullets or it is not a fact yet.

**4. Every claim carries its source.** A profile ID, run ID, log field, config
value, or file path. A bullet with no source belongs in `Assumed`.

**5. Name the owner in `Next`.** "Someone should check the mapping" is not an
action. Unowned work is how a note becomes a ticket nobody opens.

**6. Quote errors and field names byte-for-byte.** These are evidence. Do not
tidy them, do not correct the vendor's spelling, do not translate them.

**7. No hedging.** "Might possibly be related to" is either a finding with a
source or an `Assumed` bullet. Pick one.

**8. No narrative.** No "I started by looking at", no "after some digging".
Nobody reads an internal note for the journey.

## Customer data

An investigation note holds store domains, SKUs, merchant names, profile IDs
and run IDs. Mask the identifying ones before the note exists, not after.

- Store domains and merchant names: mask them. `store-A`, `merchant-B`.
- Profile IDs, feed IDs, run IDs: keep. They are ours and a teammate needs
  them to pull the run.
- SKUs and product titles: keep the pattern, mask the rest if the note leaves
  our own tools. `LO-03-****-00016-00` still shows the shape that matters.
- Never paste API keys, tokens or account credentials. Not even redacted, not
  even briefly. If one appears in a log line you are quoting, cut the line
  down to the field that matters.

## Run it through human

Same as everything else here, and for the same reason: a note full of stock
phrases reads as though nobody checked it.

```bash
pbpaste | python3 humanize.py - --report
```

Paths are relative to the `human` skill's base directory. Pipe it, never write
the draft to a file.

Two things that will happen and are fine:

- **The score will be low.** Bullets are short, and three of the checks
  return `too short to judge` on fragments. Read the FINGERPRINT line, ignore
  the verdict.
- **Wrap field names and error strings in `@@`.** `@@dedupe_check@@` and
  `@@Shopify said "handle already taken"@@` are skipped by the lexical pass and
  excluded from the score, and the markers are dropped from the output. Rule 6
  says these are evidence, so this is how you keep them byte-for-byte.
- **Read the diff for anything you did not mark.** The lexical pass cannot
  tell a column name from a word.

## Before posting

- Status line present, and is it actually the status?
- Is every `Found` bullet sourced, or should it be in `Assumed`?
- Is `Assumed` present, even if it says nothing?
- Does every `Next` item have a name on it?
- Store domains and merchant names masked?
- Field names and error strings intact after the humanize pass?
