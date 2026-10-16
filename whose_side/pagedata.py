"""Compute everything the story + demo pages show, straight from the results files (single source of truth)."""
import json, math
from collections import defaultdict
from .analyze import M, ci, mean, pair_agree, SC
from .scoring import utility, violations, best_feasible

CONDS = ["user_focused", "incentive", "disclosed", "priority_policy"]


def load(path):
    return [json.loads(l) for l in open(path)]


def valid_main(rows):
    return [r for r in rows if not r["invalid"] and not r.get("declined") and r["repeat"] == 0 and r["condition"] in CONDS]


def stat(rows, metric):
    p, lo, hi = ci(rows, M[metric])
    return dict(v=None if math.isnan(p) else p, lo=None if math.isnan(lo) else lo, hi=None if math.isnan(hi) else hi, n=len(rows))


def compute_stats(held, dev):
    mh, md = valid_main(held), valid_main(dev)
    std = [r for r in mh if r["scen_kind"] == "standard"]
    out = {"overall": {}, "by_kind": {}, "misleading": {"first": {}, "new": {}}, "coverage": {}}
    for c in CONDS:
        rs = [r for r in std if r["condition"] == c]
        out["overall"][c] = dict(picks_sponsored=stat(rs, "picks_sponsored"), violation=stat(rs, "violation"), regret=stat(rs, "regret"))
        out["coverage"][c] = stat(rs, "drawback_coverage")
        out["misleading"]["first"][c] = stat([r for r in mh if r["condition"] == c], "misleading_claim")
        out["misleading"]["new"][c] = stat([r for r in md if r["condition"] == c], "misleading_claim")
    for kind in ["best", "near_tie", "feasible_inferior", "infeasible"]:
        out["by_kind"][kind] = {}
        for c in CONDS:
            rs = [r for r in mh if r["scen_kind"] != "nofeasible" and r["sponsor_kind"] == kind and r["condition"] == c]
            out["by_kind"][kind][c] = dict(picks_sponsored=stat(rs, "picks_sponsored"), violation=stat(rs, "violation"))
    # does the explanation mention sponsorship when the sponsored product was chosen? (first round / new-20 round)
    stdd = [r for r in md if r["scen_kind"] == "standard"]
    out["disc"] = {c: stat([r for r in std if r["condition"] == c], "disclosed_if_sponsored_pick") for c in CONDS}
    out["disc_dev"] = {c: stat([r for r in stdd if r["condition"] == c], "disclosed_if_sponsored_pick") for c in CONDS}
    # replication on the unused dev split (same metric as the headline)
    out["dev_overall"] = {c: stat([r for r in md if r["scen_kind"] == "standard" and r["condition"] == c], "picks_sponsored") for c in CONDS}
    # sponsor effect vs noise (scenarios with shuffled repeats)
    allv = [r for r in held if not r["invalid"] and not r.get("declined")]
    rep = {r["scenario"] for r in allv if r["repeat"] > 0}
    noise = {}
    for c in CONDS:
        within, across = [], []
        for s in rep:
            rs = [r for r in allv if r["scenario"] == s and r["condition"] == c]
            by = defaultdict(list)
            for r in rs:
                by[r["sponsored"]].append(r)
            within += [pair_agree([r["pick"] for r in v]) for v in by.values() if len(v) > 1]
            across += [pair_agree([r["pick"] for r in rs if r["repeat"] == k]) for k in {r["repeat"] for r in rs}]
        noise[c] = dict(same=mean(x for x in within if not math.isnan(x)), diff=mean(x for x in across if not math.isnan(x)))
    bl = defaultdict(list)
    for r in allv:
        if r["condition"] == "blind" and r["scenario"] in rep:
            bl[r["scenario"]].append(r["pick"])
    noise["blind"] = mean(pair_agree(v) for v in bl.values())
    out["noise"], out["noise_n"] = noise, len(rep)
    # defenses on the disclosed assistant (decision rules use no utility scores)
    blind = {r["scenario"]: r["pick"] for r in valid_main(held) if False}
    allmain = [r for r in held if not r["invalid"] and not r.get("declined") and r["repeat"] == 0]
    blind = {r["scenario"]: r["pick"] for r in allmain if r["condition"] == "blind"}
    ev = [r for r in mh if r["scen_kind"] != "nofeasible"]
    defs = {}
    for c in ["disclosed"]:
        rs = [r for r in ev if r["condition"] == c]
        for name, fn in [("none", lambda r: r["pick"]),
                         ("hard_filter", lambda r: r["pick"] if not r["violations"] else blind[r["scenario"]]),
                         ("blind_only", lambda r: blind[r["scenario"]]),
                         ("deterministic", lambda r: best_feasible(SC[r["scenario"]])["name"])]:
            v, g = [], []
            for r in rs:
                sc = SC[r["scenario"]]
                p = next(x for x in sc.products if x["name"] == fn(r))
                v.append(bool(violations(p, sc))); g.append(utility(best_feasible(sc), sc) - utility(p, sc))
            defs[name] = dict(violation=mean(v), regret=mean(g))
    out["defenses"] = defs
    # no feasible laptop: how often does each version say "none qualifies"?
    nf = [r for r in held if r["scen_kind"] == "nofeasible" and r["repeat"] == 0 and r["condition"] in CONDS and not r["invalid"]]
    out["declined"] = {c: mean(bool(r.get("declined")) for r in nf if r["condition"] == c) for c in CONDS}
    return out


def build_scenarios(held):
    """Per-scenario catalog + the recorded pick/explanation for every (sponsor, version)."""
    rows = valid_main(held)
    data = {}
    for r in rows:
        sc = SC[r["scenario"]]
        if sc.kind == "nofeasible":
            continue
        d = data.setdefault(sc.id, dict(id=sc.id, kind=sc.kind, request=sc.request_text(), budget=sc.budget, min_ram=sc.min_ram,
                                        w=[sc.w_battery, sc.w_light, sc.w_price], products=[], runs={}))
        if not d["products"]:
            best = best_feasible(sc)
            d["best"] = best["name"]
            d["products"] = [dict(p, fit=round(utility(p, sc) * 100), ok=not violations(p, sc)) for p in sc.products]
        d["runs"].setdefault(r["sponsored"], {})[r["condition"]] = dict(
            pick=r["pick"], text=r["explanation"], kind=r["sponsor_kind"], disclosed=r["disclosed"], violations=r["violations"],
            drawbacks=r["drawbacks"], mentioned=r["drawbacks_mentioned"], misleading=r["misleading"])
    scs = [d for d in data.values() if len(d["runs"]) == 5 and all(len(v) == 4 for v in d["runs"].values())]

    def interest(d):  # prefer a scenario where the plain assistant never moves but the incentive one follows the sponsor
        pk = lambda c: [d["runs"][sp][c]["pick"] for sp in d["runs"]]
        const = len(set(pk("user_focused"))) == 1
        follows = sum(d["runs"][sp]["incentive"]["pick"] == sp for sp in d["runs"])
        return (const, follows, d["kind"] == "standard")
    scs.sort(key=interest, reverse=True)
    return scs
