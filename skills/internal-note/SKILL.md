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

- **Use the real names.** `variant_group`, `check_existing?`, `product_title`,
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
note. The worst failure in this repo's history was a plausible sentence sent
as fact. Internally it is cheaper but the mechanism is identical: someone
downstream builds on your guess because you wrote it like a finding.

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

- **The score will be low.** Bullets are short, and three of the five checks
  return `too short to judge` on fragments. Read the FINGERPRINT line, ignore
  the verdict.
- **The lexical pass does not know a field name from a word.** Check that
  every identifier, error string and column name survived byte-for-byte.

## Before posting

- Status line present, and is it actually the status?
- Is every `Found` bullet sourced, or should it be in `Assumed`?
- Is `Assumed` present, even if it says nothing?
- Does every `Next` item have a name on it?
- Store domains and merchant names masked?
- Field names and error strings intact after the humanize pass?

## Worked example

> **Status:** cause found, fix not deployed. Blocked on confirming the second
> profile is unaffected.
>
> **Found:**
> - Feed 473116 groups on `handle`, `existing_product_identifier` is
>   `product_title`. The merge never matches, so every group trips the
>   group-level existing check.
> - The "1,049 already existing" counter reports products, not variants. Label
>   is wrong on our side.
>
> **Proven:**
> - Read the profile config directly, both values above.
> - Run 8841: 3 of 6,464 rows eligible. The rest excluded by the merchant's
>   own `BO-`/`LO-` filter or sitting at zero quantity.
> - Checked all 5,713 variants in store-A, none of the three are present.
>
> **Assumed:**
> - Feed 473103 uses the same grouping and is probably affected too. Not
>   opened yet. Reading its config confirms or kills this.
>
> **Next:**
> - Switch 473116 to group by `product_title`, then rerun. Nik, today.
> - Open 473103 and check `existing_product_identifier`. Nik, before the fix
>   ships.
> - Fix the counter label. Backlog, nobody yet.

Two causes, each with its source. The unopened profile sits in `Assumed` with
the exact thing that would settle it. Every action has a name except the one
that honestly does not, and that is said out loud rather than hidden.
