#!/usr/bin/env python3
"""Self-check for @@protected@@ spans. Run it: python3 test_protect.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import detect
import humanize as hz

LEX = json.load(open(os.path.join(HERE, "slop.json"), encoding="utf-8"))


def clean(text):
    return hz.humanize(text, LEX)[0].strip()


def report(text):
    return hz.humanize(text, LEX)[1]


def score(text):
    results, overall, verdict, protected = detect.run(text, LEX)
    return results, protected


# --- the case this feature exists for -----------------------------------------
src = ("@@first thing is fast-paced@@ ever-evolving "
       "@@this second thing also hard truth@@")
out = clean(src)
assert "first thing is fast-paced" in out, out
assert "this second thing also hard truth" in out, out
assert "ever-evolving" not in out, out
assert "changing" in out, out
assert "@@" not in out, out
assert len(report(src)["protected"]) == 2, report(src)["protected"]

# --- evidence survives byte-for-byte ------------------------------------------
err = '@@Shopify said "delve into the robust — tapestry" verbatim@@'
out = clean(err)
assert 'Shopify said "delve into the robust — tapestry" verbatim' == out, out

# --- protected text is excluded from scoring ----------------------------------
results, protected = score("@@in today's fast-paced world@@ "
                           "the feed ran at 08:30 and merged 3 of 4,812 rows.")
assert protected == 1, protected
assert results["SLOP DENSITY"][0] == 100.0, results["SLOP DENSITY"]

# --- a protected tell is not flagged ------------------------------------------
tell = "@@The vendor wrote: it's not just a sync, it's a transformation.@@ We fixed it."
assert report(tell)["structures"] == [], report(tell)["structures"]
# ... but the same sentence unprotected still flags
bare = "It's not just a sync, it's a transformation. We fixed it."
assert report(bare)["structures"], "unprotected tell should still flag"

# --- edge cases ---------------------------------------------------------------
assert clean("@@unclosed and ever-evolving") == "@@unclosed and changing", \
    clean("@@unclosed and ever-evolving")          # no closer, no protection
assert clean("@@@@ ever-evolving") == "@@@@ changing"   # empty span never matches
assert clean("@@spans\nnewline ever-evolving@@") == "@@spans\nnewline changing@@", \
    "a span must not cross a newline"
assert "nik@syncx.com" in clean("mail nik@syncx.com about ever-evolving")
# Leftmost non-greedy, so the markers pair 1st-2nd and 3rd-4th. The text
# between the 2nd and 3rd marker is NOT protected, which is why nesting is
# documented as unsupported. No space appears around the restored spans.
assert clean("@@a ever-evolving@@b ever-evolving@@ c@@") == "a ever-evolvingb changing c", \
    clean("@@a ever-evolving@@b ever-evolving@@ c@@")

# --- a marked span containing a dot ------------------------------------------
# URL_RE's email arm (\S+@\S+\.\S+) used to swallow these whole and restore
# them with the markers still attached, so protect_spans runs first.
assert clean("Set @@core.hooksPath@@ to @@.githooks@@ now.") == \
    "Set core.hooksPath to .githooks now.", clean("Set @@core.hooksPath@@ to @@.githooks@@ now.")
assert clean("Read @@slop.json@@ and @@skills/human/detect.py@@ ever-evolving.") == \
    "Read slop.json and skills/human/detect.py changing.", \
    clean("Read @@slop.json@@ and @@skills/human/detect.py@@ ever-evolving.")
assert clean("Mail @@ops@store.myshopify.com@@ about ever-evolving.") == \
    "Mail ops@store.myshopify.com about changing.", \
    clean("Mail @@ops@store.myshopify.com@@ about ever-evolving.")
# unmarked URLs and emails are still protected by URL_RE itself
out = clean("See https://github.com/niksyncx/agent-skills and mail nik@syncx.com re ever-evolving.")
assert "https://github.com/niksyncx/agent-skills" in out, out
assert "nik@syncx.com" in out, out
assert "changing" in out, out

# --- regression: unmarked text behaves exactly as before ----------------------
assert clean("We leverage robust synergy to delve into it.") == \
    "We use solid overlap to look at it.", clean("We leverage robust synergy to delve into it.")

print("all protected-span checks passed")
