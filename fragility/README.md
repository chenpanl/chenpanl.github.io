# Project page

Project page for *On the Fragility of Tasks under Composition: Implicit Budgeting in Language Models*, served at https://chenpanl.github.io/fragility/.

`index.html` is the whole page: one self-contained file with the figure data inlined. GitHub Pages copies it unchanged, because it has no Jekyll front matter.

## Edit

Change `src/page.html`, then rebuild from this folder:

```bash
python3 build.py
```

`data/figures.json` holds the numbers behind fig. 2 and fig. 3b. To regenerate it from the paper's results:

```bash
RUN_DIR=/path/to/runs python3 export_data.py
python3 build.py
```

The results table (Table 2) is typed into `src/page.html` from the paper.

## Publish

Commit and push to `main` of `chenpanl/chenpanl.github.io`. GitHub Pages redeploys within a minute or two. The page uses relative paths only, so the folder can be renamed or moved without other changes.
