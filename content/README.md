# Site copy — edit the words here

This folder holds the **written content** for each page of the site, one Markdown
file per page:

| File | Page |
|------|------|
| `motivation.md` | Motivation (landing) |
| `datasets.md` | Datasets & Experiments |
| `results.md` | Results |
| `models.md` | Try the Models |
| `discover.md` | Discover Dogs |

## How to edit

Open the file for the page you want to change and edit the text. Each file is
split into **named blocks** that start with `@name` on its own line:

```markdown
@tagline
**A working tool — and an honest account of what ML can and can't do.**
```

- Edit the text under a block. Keep the `@name` line — the page uses it to find
  the block.
- It's Markdown: `**bold**`, `*italic*`, `### headings`, `- bullets` all work.
- Some blocks contain a `{placeholder}` (e.g. `{spearman}`, `{lift}`) — that's a
  **live number** the page fills in from the verified findings. Leave the
  `{braces}` exactly as they are; just edit the words around them.

You do **not** need to touch the Python files in `sections/` to change wording —
those hold the layout, the numbers, and the logic.

## Seeing your change

The app watches Python files, not Markdown. After editing a `.md`, press **R**
in the running app (or restart it) to see the new text.

## The rule that matters (see 7.4)

Don't put a claim on the site you haven't verified against its source. Numbers
stay wired to `lib/data.py` (`FINDINGS`); change the *words* here, not the
*numbers*.
