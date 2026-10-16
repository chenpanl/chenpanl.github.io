# Project page

Project page for *On the Fragility of Tasks under Composition: Implicit Budgeting in Language Models*, served at https://chenpanli.github.io/fragility/.

`index.html` is the page, with the figure data inlined. GitHub Pages copies it unchanged, because it has no Jekyll front matter. The trace viewer in section 2 loads its traces on demand from `data/traces/<dataset>/<model>.json`.

## Edit

To change only the text, edit `draft.md` and ask Claude to apply it (see `CLAUDE.md`). Otherwise change `src/page.html`, then rebuild from this folder:

```bash
python3 build.py
```

`data/figures.json` holds the numbers behind fig. 2 and fig. 3b. To regenerate it from the paper's results:

```bash
RUN_DIR=/path/to/runs python3 export_data.py
python3 build.py
```

`data/traces/` holds the traces behind the trace viewer: for every dataset and model, the ten prompts per k that share one randomly drawn task, cut at each tag and counted with the model's own tokenizer. It needs the experiment repository's environment and its per-term-trace runs:

```bash
HF_HUB_OFFLINE=1 ../../.venv/bin/python export_traces.py [dataset ...]
```

The results table (Table 2) is typed into `src/page.html` from the paper.

## Publish

Commit and push to `main` of `chenpanli/chenpanli.github.io`. GitHub Pages redeploys within a minute or two. The page uses relative paths only, so the folder can be renamed or moved without other changes.
