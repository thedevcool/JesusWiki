# Contributing

Thank you for helping. The wiki is only as trustworthy as its entries, so these rules matter.

## What makes a good entry

1. **A specific claim.** One plain sentence, such as "Jesus was crucified under Pontius Pilate."
2. **The biblical passage(s)** where the claim appears, with a short note in your own words.
3. **At least one outside source**, meaning someone who is not a Bible author. Give the author, the work, an approximate date, and what it says.
4. **A link** to a translation or reputable scholarship whenever possible.
5. **The strongest objection**, stated fairly. Entries without one are not merged.

## Grading

- `strong`: independent sources agree and most historians accept it, including non-Christian scholars.
- `probable`: good evidence from at least one outside source, with open questions.
- `debated`: scholars disagree about the source or what it shows.
- `weak`: the source is lost, late, or does not actually mention Jesus. Kept so nobody overclaims it.

Reviewers may change a grade. A claim graded down is still welcome.

## What helps an outside source count for more

- Written by someone hostile or indifferent to Christianity.
- Written close in time to the events.
- Independent of the Gospels, not just repeating them.

Say plainly when any of these is missing, or when a text may have been edited later.

## Format

Create `entries/short-descriptive-name.json`:

```json
{
  "claim": "One plain sentence",
  "strength": "strong",
  "bible": [{ "ref": "Mark 15:1-15", "note": "What it says, in your words" }],
  "outside": [
    {
      "source": "Author and work",
      "date": "c. 116 AD",
      "note": "What it says, in your words",
      "link": "https://link-to-a-translation-or-scholarship"
    }
  ],
  "counter": "The strongest objection, stated fairly"
}
```

Run `node scripts/build.mjs` before opening a pull request. It checks required fields, the strength value, link format, and note length.

## Rules

- Summarize in your own words. Do not paste long passages from copyrighted translations or books. Short quotations of public domain texts are fine.
- No attacks on people or groups. Disagree with sources and arguments, not with contributors.
- Do not add sources that are known forgeries or unverifiable unless the entry is graded `weak` and says so.
