"""Export the data behind fig. 2 and fig. 3b to data/figures.json.

Reads the CSVs that the paper's analyses write under $RUN_DIR/results:

    II-token-ratio/token-ratio-points.csv   mean token ratio per dataset, model, bin and k
    II-token-ratio/power-law-fits.csv       the paper's overall fit (m, R^2) per dataset and model
    III-budget-forcing/composed-bins.csv    token reduction and accuracy change per bin and k

Each bin's slope is fitted the way the paper's plot does it: least squares on log r
against log k with no intercept, so the line passes through (1, 1).

    RUN_DIR=/path/to/runs python3 export_data.py
"""
import collections
import csv
import json
import math
import os
import pathlib

RESULTS = pathlib.Path(os.environ["RUN_DIR"]) / "results"
OUT = pathlib.Path(__file__).parent / "data" / "figures.json"
BINS = {"High": "high", "Med.": "medium", "Low": "low"}


def origin_slope(points):
    xs = [math.log(k) for k, _ in points]
    ys = [math.log(r) for _, r in points]
    return sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)


def rows(path):
    with open(RESULTS / path) as f:
        return list(csv.DictReader(f))


def token_ratio():
    points = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows("II-token-ratio/token-ratio-points.csv"):
        if r["bin"] in BINS:
            points[r["dataset"], r["model"]][BINS[r["bin"]]].append((int(r["k"]), float(r["ratio"])))
    fits = {(r["dataset"], r["model"]): r for r in rows("II-token-ratio/power-law-fits.csv")}
    out = {}
    for (dataset, model), bins in points.items():
        fit = fits[dataset, model]
        entry = {"m": round(float(fit["slope"]), 3), "r2": round(float(fit["r2"]), 3), "bins": {}}
        for name, pts in bins.items():
            pts.sort()
            entry["bins"][name] = {"k": [k for k, _ in pts], "r": [round(v, 4) for _, v in pts],
                                   "m": round(origin_slope(pts), 3)}
        out.setdefault(dataset, {})[model] = entry
    return out


def accuracy_drop():
    out = {}
    for r in sorted(rows("III-budget-forcing/composed-bins.csv"), key=lambda r: int(r["k"])):
        g = out.setdefault(r["dataset"], {}).setdefault(r["model"], {}).setdefault(r["group"], {"k": [], "x": [], "y": []})
        g["k"].append(int(r["k"]))
        g["x"].append(round(float(r["saved_tokens"]), 4))
        g["y"].append(round(float(r["acc_change_pp"]), 3))
    return out


if __name__ == "__main__":
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"fig2": token_ratio(), "fig5": accuracy_drop()}, separators=(",", ":")))
    print("wrote", OUT)
