"""Recompute text metrics with textcheck v2 from stored explanations (no API calls).
Usage: python -m whose_side.rescore results/results_v2.jsonl"""
import json, sys
from .catalog import make_scenarios, make_extra_scenarios
from .textcheck import analyze_text

SC = {s.id: s for s in make_scenarios(40) + make_extra_scenarios()}


def rescore_row(r):
    if r.get("invalid") or r.get("declined") or not r.get("pick"):
        return r
    sc = SC[r["scenario"]]
    p = next(x for x in sc.products if x["name"] == r["pick"])
    r = dict(r)
    for k in ("drawbacks", "drawbacks_mentioned", "disclosed"):
        r[k + "_v1"] = r.get(k)
    r.update(analyze_text(r["explanation"], p, sc))
    return r


if __name__ == "__main__":
    for path in sys.argv[1:]:
        rows = [rescore_row(json.loads(l)) for l in open(path)]
        with open(path, "w") as f:
            f.writelines(json.dumps(r) + "\n" for r in rows)
        print("rescored", path, len(rows))
