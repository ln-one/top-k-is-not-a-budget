"""Verify released evidence and recompute the three manuscript tables."""
import csv
import hashlib
import json
import math
import zipfile
from collections import defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/paper-experiments-v3"
TABLES = ROOT / "paper/icassp2027/latex/tables"
NAMES = {
    "msmarco-passage-trec-dl-2019": "TREC-DL 2019",
    "msmarco-passage-trec-dl-2020": "TREC-DL 2020",
    "nfcorpus": "NFCorpus", "scifact": "SciFact", "trec-covid": "TREC-COVID",
}


def rows(name):
    with (RESULTS / name).open() as handle:
        return list(csv.DictReader(handle))


def check_table(name, expected):
    content = (TABLES / name).read_text().split(r"\midrule", 1)[1].split(r"\bottomrule", 1)[0]
    actual = [line.strip().removesuffix(r"\\").strip().split(" & ")
              for line in content.splitlines() if line.strip()]
    assert actual == expected, f"Table differs from query records: {name}"


def main():
    hashes = json.loads((RESULTS / "delivery-manifest.json").read_text())
    # The original delivery manifest also names three editorial documents.
    # Those documents have been rewritten/archived; scientific evidence is immutable.
    editorial = {"README.md", "PROTOCOL.md", "RESULTS-REVIEW.md"}
    checked = 0
    for name, expected in hashes.items():
        if name in editorial:
            continue
        path = RESULTS / name
        if name.startswith("sources/"):
            with zipfile.ZipFile(RESULTS / "sources.zip") as archive:
                content = archive.read(name)
        else:
            content = path.read_bytes()
        assert hashlib.sha256(content).hexdigest() == expected, name
        checked += 1
    costs = defaultdict(list)
    for row in rows("fixed-k.csv"):
        if row["k"] == "20":
            assert row["completed"] == "1"
            if row["policy"] == "dibud" and row["batch"] == "1":
                costs[row["dataset"]].append(float(row["cost"]))
    assert sum(map(len, costs.values())) == 770
    table = []
    for ds, name in NAMES.items():
        values = sorted(costs[ds]); n = len(values)
        table.append([name, str(n)] + [f"{v:.0f}" for v in
                     (values[math.ceil(.5*n)-1], values[math.ceil(.95*n)-1], values[-1])])
    check_table("cost-v3.tex", table)
    budgets = rows("budget-yield.csv")
    assert len(budgets) == 24640
    assert all(float(x["accesses"]) <= float(x["budget"]) and x["known"] == "1" for x in budgets)
    groups = defaultdict(list)
    for row in budgets:
        if row["batch"] == "1" and row["budget"] == "2048":
            groups[row["dataset"], row["policy"]].append(float(row["k"]))
    table = [[name] + [f"{mean(min(v, cap) for v in groups[ds, policy]):.2f}"
                      for cap in (100, 20) for policy in ("balanced", "dibud")]
             for ds, name in NAMES.items()]
    check_table("yield-v2.tex", table)
    quality = defaultdict(list)
    for row in rows("quality-budget-heldout.csv"):
        if float(row["target"]) == .95:
            quality[row["dataset"]].append(row)
    table = []
    for ds, name in NAMES.items():
        group = quality[ds]
        assert len(group) == len(costs[ds])
        retained = sum(float(x["ndcg20"]) for x in group) / sum(float(x["full_ndcg20"]) for x in group)
        saved = 1 - sum(float(x["budget20_cost"]) for x in group) / sum(float(x["cost20"]) for x in group)
        table.append([name, f"{100*retained:.2f}", f"{100*saved:.2f}"])
    check_table("quality-v3.tex", table)
    print(f"Verified {checked} evidence files, 770 Top-20 costs, 24640 budget records, and all three paper tables.")


if __name__ == "__main__":
    main()
