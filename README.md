# Project page

Project page for *On the Fragility of Tasks under Composition: Implicit Budgeting in Language Models*.

`index.html` is the whole site: one self-contained file with the figure data inlined. GitHub Pages serves it as is, and `.nojekyll` stops Jekyll from processing it.

## Edit

Change `src/page.html`, then rebuild:

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

Push this repository to GitHub, then open Settings → Pages and serve the `main` branch from `/ (root)`. A repository named `<user>.github.io` is served at `https://<user>.github.io/`; any other name is served at `https://<user>.github.io/<repo>/`. The page uses relative paths only, so both work.
