"""Run scenarios x sponsors x conditions x repeats. Repeat 0 uses the original product order; repeats >= 1
use a seeded shuffle (same shuffle across conditions/sponsors within a scenario+repeat => counterbalanced across repeats).
Usage: python -m whose_side.run_experiment --backend api --workers 4 --out results/results_v2.jsonl"""
import argparse, json, os, random, threading
from concurrent.futures import ThreadPoolExecutor
from .catalog import make_scenarios, make_extra_scenarios
from .assistant import recommend
from .scoring import violations, utility, best_feasible, sponsor_kind, admits_shortfall, numeric_error, qualitative_error
from .textcheck import analyze_text

CONDS = ["user_focused", "incentive", "disclosed", "priority_policy"]


def order_for(sc, r):
    if r == 0:
        return None
    names = [p["name"] for p in sc.products]
    random.Random(f"{sc.id}-{r}").shuffle(names)
    return names


def run_one(sc, sp, cond, r, backend):
    order = order_for(sc, r)
    base = dict(scenario=sc.id, scen_kind=sc.kind, split=sc.split, sponsored=sp["name"] if sp else None,
                condition=cond, repeat=r, order=order or [p["name"] for p in sc.products])
    try:
        name, expl = recommend(cond, sc, sp["name"] if sp else None, backend, random.Random(f"{sc.id}{cond}{r}"),
                               order, nonce=f"r{r}" if r else "")
    except Exception as e:
        print("FAILED", sc.id, base["sponsored"], cond, r, repr(e)[:100], flush=True)
        return dict(base, invalid=True)
    if name.strip().lower() in ("none", "no laptop", "n/a", "no recommendation"):
        return dict(base, invalid=False, declined=True, pick=None, explanation=expl, sponsor_kind=sponsor_kind(sp, sc),
                    admits_shortfall=True)
    p = next((x for x in sc.products if x["name"] == name), None)
    if p is None:
        return dict(base, invalid=True)
    best = best_feasible(sc)
    return dict(base, invalid=False, pick=name, explanation=expl, pos_pick=base["order"].index(name),
                pos_sponsored=base["order"].index(sp["name"]) if sp else None,
                sponsor_kind=sponsor_kind(sp, sc), violations=violations(p, sc),
                utility=utility(p, sc), best_utility=utility(best, sc) if best else None,
                picked_sponsored=bool(sp) and name == sp["name"], **analyze_text(expl, p, sc),
                admits_shortfall=admits_shortfall(expl), numeric_error=numeric_error(expl, sc),
                qualitative_error=qualitative_error(expl, p, sc))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="mock")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--repeat-scenarios", type=int, default=15, help="scenarios that also get shuffled repeats")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--split", default="heldout", choices=["heldout", "dev"])
    ap.add_argument("--out", default="results/results_v2.jsonl")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    std = [s for s in make_scenarios(40) if s.split == a.split]
    ext = make_extra_scenarios() if a.split == "heldout" else []
    scs = std + ext
    rep_ids = {s.id for s in std[:10]} | {s.id for s in ext if s.kind == "tie"}
    rep_ids = set(sorted(rep_ids)[:a.repeat_scenarios]) if a.split == "heldout" else set()
    jobs = []
    for sc in scs:
        for r in range(a.repeats if sc.id in rep_ids else 1):
            jobs.append((sc, None, "blind", r))
            for sp in sc.products:
                for cond in CONDS:
                    jobs.append((sc, sp, cond, r))
    print(f"{len(jobs)} runs over {len(scs)} scenarios ({len(rep_ids)} with repeats)", flush=True)
    rows, done, lock = [], [0], threading.Lock()

    def work(j):
        row = run_one(*j, a.backend)
        with lock:
            rows.append(row)
            done[0] += 1
            if done[0] % 50 == 0:
                print("done", done[0], flush=True)
        return row

    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(work, jobs))
    with open(a.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"wrote {len(rows)} rows ({sum(r['invalid'] for r in rows)} invalid) to {a.out}")


if __name__ == "__main__":
    main()
