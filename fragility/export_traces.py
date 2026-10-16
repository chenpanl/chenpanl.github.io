"""Export the traces behind the trace viewer to data/traces/<dataset>/<model>.json.

For every dataset one task is drawn at random among those whose traces are clean
(thinking closed, every answer readable) in all ten prompts at every k for every
model. Each prompt that contains it is cut into per-task segments with the paper's
label parser, and every segment's tokens are counted with the model's own
tokenizer (a token belongs to the segment holding its first character, as in
`token_breakdown`). Long segments keep their start and end around "[...]".

Run from this folder with the experiment repository's environment:

    HF_HUB_OFFLINE=1 ../../.venv/bin/python export_traces.py
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from llm import paths, specs  # noqa: E402
from llm.core.analysis.question_sections import parse_label_sections  # noqa: E402
from llm.core.parser.math_parser import strip_bpe_sentinels  # noqa: E402

STAGE = "per-term-trace"
SEEDS = 10
FULL, HEAD, TAIL = 260, 170, 70      # segment text kept whole up to FULL chars


def lst(value):
    if isinstance(value, str):
        import ast
        return ast.literal_eval(value)
    return value


def clip(text):
    # undecodable bytes the model emitted show as U+FFFD; they carry no text worth keeping
    text = " ".join(text.replace("\ufffd", "").split())
    if len(text) <= FULL:
        return text
    return text[:HEAD].rstrip() + " [...] " + text[-TAIL:].lstrip()


def sections_rows(dataset, model):
    """Section rows of every run of the pair, keyed by k."""
    by_k = defaultdict(list)
    for run in paths.runs(STAGE, dataset, model):
        f = run / "sections.jsonl"
        if not f.exists():
            continue
        for line in f.open(encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                r["_run"] = run
                by_k[int(r["k"])].append(r)
    return by_k


def clean(r):
    k = int(r["k"])
    tc = lst(r.get("term_correct")) or []
    return bool(r["parse"].get("think_closed")) and len(tc) == k


def anchor_rows(by_k, ks):
    """item -> k -> rows where the item is an actual (counted) position."""
    out = defaultdict(lambda: defaultdict(list))
    for k in ks:
        for r in by_k.get(k, []):
            ids, act = lst(r["component_ids"]), lst(r["component_actual"])
            for pos, (item, a) in enumerate(zip(ids, act)):
                if a:
                    out[item][k].append((pos, r))
    return out


def valid_items(per_item, ks):
    return {item for item, by in per_item.items()
            if all(len(by.get(k, [])) == SEEDS and all(clean(r) for _, r in by[k]) for k in ks)}


def load_texts(rows, filter_name):
    """raw.text for each selected row, read from its run's trace.jsonl."""
    want = defaultdict(set)
    for r in rows:
        want[r["_run"]].add((r["doc_id"], int(r.get("trial") or 0)))
    texts = {}
    for run, keys in want.items():
        ids = {d for d, _ in keys}
        with open(run / "trace.jsonl", encoding="utf-8") as fh:
            for line in fh:
                i = line.find('"doc_id": "')
                if i < 0:
                    continue
                j = line.find('"', i + 11)
                if line[i + 11:j] not in ids:
                    continue
                t = json.loads(line)
                key = (t["doc_id"], int(t.get("trial") or 0))
                if t.get("filter") == filter_name and key in keys:
                    texts[(run, key)] = t["raw"]["text"]
    return texts


def segments(text, k, tokenizer):
    text, _ = strip_bpe_sentinels(text)
    parse = parse_label_sections(text, k)
    offsets = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)["offset_mapping"]
    starts = [s for s, _ in offsets]
    first = min((s.start for s in parse.sections), default=parse.think_end)

    def count(a, b):
        return sum(1 for s in starts if a <= s < b)

    segs = []
    if first > 0 and count(0, first):          # thinking before the first label (and any preamble)
        segs.append([0, count(0, first), clip(text[parse.think_start:first])])
    for s in sorted(parse.sections, key=lambda s: s.start):
        segs.append([s.label, count(s.start, s.end), clip(text[s.start:s.end])])
    answer = text[parse.think_end:].replace("</think>", "", 1)
    segs.append([-1, count(parse.think_end, len(text) + 1), clip(answer)])
    return segs


def export(dataset, models):
    from transformers import AutoTokenizer

    ds = specs.dataset(dataset)
    ks = ds.trace_ks
    pairs = {m: sections_rows(dataset, m) for m in models}
    pairs = {m: by for m, by in pairs.items() if all(by.get(k) for k in ks)}
    if not pairs:
        print(dataset, "no complete runs"); return
    per = {m: anchor_rows(by, ks) for m, by in pairs.items()}
    common = set.intersection(*(valid_items(p, ks) for p in per.values()))   # clean for every model
    shared = random.Random(f"trace-viewer-{dataset}").choice(sorted(common)) if common else None
    for model, p in per.items():
        pool = sorted(valid_items(p, ks))
        if not pool:
            # no task is clean in all its prompts: take the one with the most clean prompts
            full = [i for i, by in p.items() if all(len(by.get(k, [])) == SEEDS for k in ks)]
            score = {i: sum(clean(r) for k in ks for _, r in p[i][k]) for i in full}
            best = max(score.values(), default=0)
            pool = sorted(i for i in full if score[i] == best)
        if not shared and not pool:
            print(dataset, model, "no task in every prompt"); continue
        item = shared or random.Random(f"trace-viewer-{dataset}-{model}").choice(pool)
        chosen = {k: sorted(p[item][k], key=lambda pr: pr[1].get("batch_seed") or 0) for k in ks}
        rows = [r for k in ks for _, r in chosen[k]]
        texts = load_texts(rows, ds.filter)
        run0 = json.loads((rows[0]["_run"] / "run.json").read_text())
        tok = AutoTokenizer.from_pretrained(run0["model"]["model_id"])
        out = {"dataset": dataset, "model": model, "item": item, "shared": bool(common), "ks": ks, "traces": {}}
        for k in ks:
            lst_k = []
            for pos, r in chosen[k]:
                text = texts[(r["_run"], (r["doc_id"], int(r.get("trial") or 0)))]
                segs = segments(text, k, tok)
                per_q = r["tokens"]["per_question"]
                mine = defaultdict(int)
                for lab, n, _ in segs:
                    if lab > 0:
                        mine[str(lab)] += n
                assert all(mine[q] == n for q, n in per_q.items()), (dataset, model, k, r["doc_id"])
                lst_k.append({"seed": r.get("batch_seed"), "anchor": pos + 1,
                              "actual": lst(r["component_actual"]),
                              "correct": lst(r.get("term_correct")) or [], "segs": segs})
            out["traces"][str(k)] = lst_k
        f = HERE / "data" / "traces" / dataset / f"{model}.json"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
        print(dataset, model, item, "shared" if common else "own", f"{f.stat().st_size / 1e6:.2f} MB", flush=True)


if __name__ == "__main__":
    only = sys.argv[1:]
    for dataset in specs.TRACE_DATASETS:
        if not only or dataset in only:
            export(dataset, specs.MODELS)
