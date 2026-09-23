---
name: "support-reply"
description: "Turn a finished Stock-Sync investigation into a reply the customer can act on. Use when drafting any customer-facing answer about a feed, profile, or import/export failure: escalations, \"why didn't this sync\", angry follow-ups, or handing findings to the support team to send. Not for internal notes or commit messages."
---

# Support reply

Say what was wrong, what changed, what they must do. Stop.

## Length is the first rule

**200 words. Hard cap.** Over that, the customer skims and misses the action item. If it won't fit, you are explaining instead of answering.

What blows the budget, in order:

- **Walking through the mechanism.** One sentence for the cause. They want it fixed, not understood. Offer the detail: "Happy to explain the mechanism if useful."
- **Answering questions separately when they share a cause.** Group them. Nine questions with one root cause is one paragraph, not nine.
- **Proving you did the work.** One number proves it. A second is padding.
- **Restating their situation back to them.** They wrote it.
Long is not thorough. Long reads as evasive, which is what they are already angry about.

## Hard rules

**1. Cause in sentence one.** No "thanks for your patience", no "I've escalated this", no restating the question.

**2. Never explain a mechanism you have not verified.** A generic answer that sounds right is the expensive failure in this work. It ships mid-escalation, the customer acts on it, and the real cause keeps running for days. "Checking that now" always beats a plausible sentence.

**3a. No backticks.** A helpdesk or email client often shows them as literal
characters, so `SKU-001` arrives with the marks around it. Internal notes render
markdown, customer replies frequently do not. Quote identifiers plainly. `@@`
still applies, it is stripped before the reply is sent.

**3. No internal vocabulary.** `row_group` becomes "the setting that groups rows into one product". `dedupe_check` becomes "the step that checks whether the product is already in your store". Names the customer can see in the app are fine, quote those exactly.

**4. Split by who fixes it.** We fixed / you change / your supplier changes. Conflating these is what makes people feel stonewalled. Name exact records in the last two.

**5. Every question answered, but grouped.** Never leave one out, an omission reads as evasion. Never give each its own paragraph either. Share a cause, share a line.

**6. One proving number.** "3 of your 4,812 rows were eligible" ends the argument. Pull it from the run.

**7. Never claim a verification you did not run.** If the test import hasn't been read, leave a marked placeholder and do not send.

**8. Never blame them.** "The grouping was pointed at the wrong column", not "you misconfigured it."

**9. No em dashes.** Comma or full stop. This is rule 9 because it is the one tell that makes a correct answer read as generated, and a customer who thinks you sent a bot stops reading at line one. `human` enforces it, see below.

## Shape

```
[One sentence: the cause.]

Fixed: [change, profile ID, when it takes effect.] [What you did NOT touch.]

[One proving number, and what the rest of their concern actually was.]

Still needs action:
- [SKU/record] [who fixes it, how]

Your other questions: [grouped, one line each.]

Verified: [run ID, what it did.] Next run [time].
```

Drop empty sections. Never pad one to look thorough.

## When the fix is a code change

If the customer's answer depends on a diff, PR or branch we shipped, use
`explain-change` to understand it first, then write the reply from that. The
explanation is for you, not for them: rule 1 still gets one sentence of cause,
and the walkthrough stays out of the reply unless they ask for it.

## Run it through human before sending

Run the `human` skill, `/syncx:human` when this is installed as the plugin. It
knows where its own scripts live, so there is no path to get wrong.

Hand it the reply through stdin. Never write the draft to a file.

A finished reply holds store names, SKUs, profile IDs and run IDs. That is customer data, and a draft file on disk gets copied, synced and backed up. Stdin leaves nothing behind. If you need a before/after score, mask the identifiers first.

**What it will actually find.** Em dashes, and usually nothing else. A reply written to the rules above scores well before you touch it: rule 6 maxes SPECIFICITY, and writing "your feed" instead of "the user's feed" maxes VOICE. Expect the em dash pass to carry most of the gain on its own.

**Wrap the evidence in `@@`.** SKUs, profile IDs, quoted vendor strings and exact error text go inside `@@...@@`, which the lexical pass skips and the score ignores. The markers are stripped from the output.

**Read the diff anyway.** Anything you did not mark is fair game for the lexical pass. Check that every identifier, error string and field name survived byte-for-byte before you send.

**Ignore the verdict on a short reply.** Under four sentences, three of the checks return `too short to judge` and score a flat 50, which is below the 55 floor, so a two-line answer can never reach PASS no matter how good it is. A 22-word reply tops out at 62.0 REVIEW. On anything short, read the FINGERPRINT line and ignore the rest.

## Before sending

- Under 200 words?
- Does sentence one say why their products didn't import?
- Every claim traceable to a config value, log field, or row you actually read?
- Any word that only exists in our codebase?
- Every question answered, none given its own paragraph?
- Verification real, or marked as pending?
- Piped through `humanize.py`, diff read, zero em dashes left?
