# Editing the page through draft.md

`draft.md` holds the page's text as Markdown. Chenpan edits it there, and Claude carries the edits into `src/page.html`. The conventions for coloured keywords, key-message boxes, margin notes and figure stubs are listed at the top of the draft.

The committed draft always matches the live page, so `git diff draft.md` shows exactly the edits waiting to be applied. When asked to apply the draft:

1. Read the diff, and treat any plain note in the draft (a layout or style request) as an instruction.
2. Port each change into `src/page.html`. Change the text and its markup, but leave the figure scripts alone unless a note asks for it. Keep Chenpan's wording, apart from light fixes made with the human-writing skill.
3. Run `python3 build.py` from this folder, then check the page in a browser at desktop and phone width.
4. Show the result as an artifact first, and push only when Chenpan says so.
5. Commit `draft.md` together with the page, so the next diff starts clean.

When the page text changes for any other reason, update `draft.md` in the same commit, so the two never drift apart.
