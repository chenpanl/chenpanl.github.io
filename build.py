"""Build index.html from src/page.html and data/figures.json.

The figure data is inlined, so index.html is one self-contained file that GitHub Pages
serves as is. With a path argument, the script also writes the body-only variant used
for the claude.ai preview, which wraps the page in its own document.

    python3 build.py [preview-out.html]
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
DESCRIPTION = ("Language models fail on compositions of tasks they solve alone, because they cut "
               "every task's thinking by the same factor. Fragility-aware batching saves 43% of "
               "tokens at unchanged accuracy.")
FAVICON = ("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'>"
           "<rect width='16' height='16' rx='3' fill='%231A1A1A'/>"
           "<text x='8' y='12.5' font-size='12' font-weight='700' text-anchor='middle' "
           "font-family='monospace' fill='%23E6B33D'>%23</text></svg>")

src = (HERE / "src/page.html").read_text()
data = json.dumps(json.loads((HERE / "data/figures.json").read_text()), separators=(",", ":"))
page = src.replace("__FIGDATA__", data.replace("</", "<\\/"))
head, body = page.split("<!--BODY-->")

(HERE / "index.html").write_text(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{DESCRIPTION}">
<meta property="og:type" content="website">
<meta property="og:title" content="On the Fragility of Tasks under Composition: Implicit Budgeting in Language Models">
<meta property="og:description" content="{DESCRIPTION}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="{FAVICON}">
{head}</head>
<body>
{body}</body>
</html>
""")
if len(sys.argv) > 1:
    pathlib.Path(sys.argv[1]).write_text(head + body)
