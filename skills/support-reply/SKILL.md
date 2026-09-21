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

**2. Never explain a mechanism you have not verified.** The worst failure in this repo's history was a confident generic answer, sent mid-escalation:

> "Shopify store titles do not affect SKU matching directly, matching happens at the variant identifier level."

Titles were the entire cause. Four days and the customer's trust. "Checking that now" always beats a plausible sentence.

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

Pipe it. Never write the draft to a file. Paths are relative to the `human`
skill's base directory, which you get when that skill is invoked:

```bash
pbpaste | python3 humanize.py - --report
```

A finished reply holds store names, SKUs, profile IDs and run IDs. That is customer data, and a draft file on disk gets copied, synced and backed up. Stdin leaves nothing behind. If you need a before/after score, mask the identifiers first.

**What it will actually find.** Em dashes, and usually nothing else. A reply written to the rules above scores well before you touch it: rule 6 maxes SPECIFICITY, and writing "your feed" instead of "the user's feed" maxes VOICE. The worked example below went `60.9 REVIEW -> 84.5 PASS` on the em dash pass alone, with zero structural flags.

**Read the diff, do not trust the output.** The lexical pass does not know it is inside a quoted vendor string or a SKU. Check that every identifier, error string and field name survived byte-for-byte before you send.

**Ignore the verdict on a short reply.** Under four sentences, three of the five checks return `too short to judge` and score a flat 50, which is below the 55 floor, so a two-line answer can never reach PASS no matter how good it is. A 22-word reply tops out at 62.0 REVIEW. On anything short, read the FINGERPRINT line and ignore the rest.

## Before sending

- Under 200 words?
- Does sentence one say why their products didn't import?
- Every claim traceable to a config value, log field, or row you actually read?
- Any word that only exists in our codebase?
- Every question answered, none given its own paragraph?
- Verification real, or marked as pending?
- Piped through `humanize.py`, diff read, zero em dashes left?

## Worked example, profile 100200, store-A

Identifiers below are masked. Profile IDs, SKUs, catalogue sizes, store and
supplier names are illustrative, the shape is what matters.

Found: grouping keyed on `handle` while `match_field` was `product_title`, so the merge never matched and every group tripped the group-level existing check. 3 eligible SKUs. One blocked by a store-side rename, one duplicated by the supplier. Customer asked nine questions.

The reply, as it went out after the humanize pass:

> Your Add feed grouped supplier rows by the supplier's handle, but your merge setting matches on product title, so every new variant was treated as already existing and skipped.
>
> **Fixed:** feed 100200 now groups by Product Title. Live now. Your filter, prices, product statuses and feed 100201 are untouched.
>
> 3 of your 4,812 rows were genuinely new, the three you sent us. Your audit was right. The ~430 others are excluded by your own BO-/LO- filter or sit at zero quantity. Those are working as configured.
>
> **Still needs action:**
> - `LO-03-****-00016-00`, this product was renamed in your store. supplier-B calls it *Harbour Leather Business Briefcase / Laptop Case 16" with Case*; your store says *Harbour 16-Inch Leather Laptop Case*. Rename it back, or ask us to map the title.
> - `LO-02-****-042MM-00`, supplier-B sends one SKU for two sizes (qty 14 and 11). They need a separate SKU for 40/41/42mm.
>
> **Your other questions:** none of the three are in your store, we checked all 4,310 variants. All three have stock, so "skip zero quantity" isn't involved. Your filter evaluated correctly and passed all three. The "887 already existing" figure counts products, not variants; that label is wrong on our side.
>
> **Verified:** run [ID] merged [variant]. Next daily run 08:30.

Nine questions, one paragraph. The mechanism gets one sentence, he can ask for more. Three causes split by owner. The untouched feed named explicitly, because that was his real fear.

Scored 84.5 PASS. Five em dashes came out, nothing else changed, and every SKU survived the pass intact.
