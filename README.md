# Prompt Playbook

A/B tests on how you brief an AI coding agent — and what actually changes in the output.

Every entry here is a real experiment: same task, two different prompts, both outputs saved. No theory, no "trust me, this works better." Just the diff.

**Model:** Claude Fable 5 (Anthropic's Mythos-class model, generally available since July 2026). Results likely generalize to other frontier models, but I've only tested on Fable 5 so far.

**Status:** work in progress. Adding entries as I run them.

---

## 1. Make it test its own work

### The prompt

```
After you write it, do these three things:
1. Create your own test files — include [edge case A], [edge case B], [edge case C]
2. Run your script against them
3. Report back: what passed, what broke, and how you fixed it

Show me the test process and results, not just the final code.
```

Swap the bracketed parts for edge cases in your own task. Can't think of any? Ask the model first: *"What edge cases would this task run into?"*

### The experiment

**Task:** Write a Python script that merges all CSV files in a folder into one and removes duplicate rows.

I ran it twice, in two fresh conversations. Both runs used Claude Fable 5.

- **Version A** — just the task, nothing else
- **Version B** — the task, plus the self-test instruction above

### What I expected

Version B would write better code on the first try.

### What actually happened

The opposite. **Version B's first draft crashed.**

It built its own test files — one with columns in a different order, one empty, one with duplicate rows — ran them, and died on the empty CSV with `EmptyDataError`. It caught this itself and fixed it.

Version A never crashed. It looked fine.

### The part that matters

Version A wrapped every file read in a catch-all:

```python
try:
    frames.append(pd.read_csv(f))
except Exception as e:
    print(f"Skipping {f.name}: {e}", file=sys.stderr)
```

Version B, after its crash, used this instead:

```python
try:
    df = pd.read_csv(f)
except pd.errors.EmptyDataError:
    print(f"  skipped {f.name}: file is empty")
    continue
```

**The catch-all isn't defensive. It's dangerous.**

`except Exception` swallows *everything* — encoding errors, corrupt files, permission issues. In a data pipeline, an entire file of sales data can disappear behind one line of stderr and you'd never know. You'd just run your analysis on a silently incomplete dataset.

Version B only swallows the one failure mode it actually verified. Anything else fails loudly — which is what you want.

### Why this happens

The model that didn't test was **guessing** at what could go wrong, so it cast a wide net.

The model that tested **knew**, so it could be precise.

### What you actually get

| | Version A | Version B |
|---|---|---|
| Code | A script | A script |
| Verification | An unverified claim that it works | Test files + a record that v1 broke + the fix |
| Numbers | None | 9 rows in → 5 unique rows out (checkable) |
| Error handling | `except Exception` (guessed) | `except EmptyDataError` (verified) |
| Bonus finding | — | Flagged that merging with the raw `csv` module instead of pandas would silently produce garbage when column order differs |

The code quality is comparable. **What differs is how much you know about it.**

Version B also surfaced a risk I hadn't asked about and wouldn't have thought of. Version A never mentioned it.

Both scripts are in this repo: [a.py](a.py) (no self-test) and [b.py](b.py) (self-tested).

---

## More entries coming

- Plan first (ask for a plan before any code)
- Define "done" before it starts
- Set the boundaries (what *not* to do)
- Structure the context

---

## Why I'm doing this

Most prompt advice is someone's opinion. I wanted to see the diff myself, so I'm running the tests and publishing both sides — including the times my prediction was wrong.

The first entry is one of those. I expected self-testing to produce a cleaner first draft. It produced a *broken* one — and that turned out to be the whole point.
