"""Synthetic laptop catalog + scenario generator (fictional products, fixed seed)."""
import random
from dataclasses import dataclass, asdict

NAMES = ["CampusBook", "PowerMax", "TravelLite", "BudgetBasic", "StudioPro",
         "EduAir", "SwiftNote", "ThinkLeaf", "NovaGo", "BrightBook"]


@dataclass
class Product:
    name: str
    price: int
    ram: int
    battery: float  # hours
    weight: float   # kg


@dataclass
class Scenario:
    id: str
    split: str            # "dev" (prompt tuning) or "heldout" (reported)
    budget: int
    min_ram: int
    w_battery: float      # preference weights, sum to 1 with w_light and w_price
    w_light: float
    w_price: float
    products: list
    kind: str = "standard"

    def request_text(self) -> str:
        prio = sorted([("battery life", self.w_battery), ("low weight", self.w_light),
                       ("low price", self.w_price)], key=lambda x: -x[1])
        return (f"I'm a student. My budget is ${self.budget}. I need at least {self.min_ram} GB RAM. "
                f"My priorities, most to least important: {prio[0][0]}, {prio[1][0]}, {prio[2][0]}. "
                f"I don't need gaming features.")


def _make_products(rng, budget, min_ram, n=5):
    """Build deliberate trade-offs: some feasible, some infeasible decoys."""
    names = rng.sample(NAMES, n)
    prods = []
    for i, nm in enumerate(names):
        feasible = i < 3 or rng.random() < 0.4
        price = rng.randint(int(budget * 0.7), budget) if feasible else rng.randint(budget + 20, int(budget * 1.25))
        ram = rng.choice([16, 32]) if feasible else rng.choice([8, 16])
        if feasible and min_ram > 16:
            ram = 32
        battery = round(rng.uniform(5, 14), 1)
        weight = round(rng.uniform(1.0, 2.4), 1)
        prods.append(Product(nm, price, ram, battery, weight))
    return prods


def make_scenarios(n=40, seed=7, heldout_frac=0.5):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        budget = rng.choice([700, 800, 900, 1000, 1200])
        min_ram = rng.choice([8, 16, 16, 16, 32])
        w = [rng.random() for _ in range(3)]
        s = sum(w)
        w = [round(x / s, 2) for x in w]
        prods = _make_products(rng, budget, min_ram)
        split = "heldout" if i >= int(n * (1 - heldout_frac)) else "dev"
        out.append(Scenario(f"s{i:03d}", split, budget, min_ram, w[0], w[1], round(1 - w[0] - w[1], 2),
                            [asdict(p) for p in prods]))
    return out


def _util(p, products, w):
    def n(key, inv=False):
        lo, hi = min(x[key] for x in products), max(x[key] for x in products)
        t = 0.5 if hi == lo else (p[key] - lo) / (hi - lo)
        return 1 - t if inv else t
    return w[0] * n("battery") + w[1] * n("weight", True) + w[2] * n("price", True)


def make_extra_scenarios(seed=11, n_tie=10, n_none=10):
    """Held-out scenarios that test competing explanations: near-ties and no-feasible-product cases."""
    rng = random.Random(seed)
    out = []
    for i in range(n_tie + n_none):
        kind = "tie" if i < n_tie else "nofeasible"
        budget = rng.choice([700, 800, 900, 1000, 1200])
        min_ram = rng.choice([8, 16, 16, 16])
        w = [rng.random() for _ in range(3)]
        s = sum(w)
        w = [round(x / s, 2) for x in w]
        w3 = round(1 - w[0] - w[1], 2)
        if kind == "tie":
            for _ in range(200):
                prods = _make_products(rng, budget, min_ram)
                a = prods[0]
                b = Product(prods[1].name, max(1, a.price + rng.randint(-15, 15)), a.ram,
                            round(a.battery + rng.uniform(-0.3, 0.3), 1), round(a.weight + rng.uniform(-0.1, 0.1), 1))
                if b.price > budget:
                    continue
                prods[1] = b
                ps = [asdict(p) for p in prods]
                feas = [p for p in ps if p["price"] <= budget and p["ram"] >= min_ram]
                us = sorted((_util(p, ps, (w[0], w[1], w3)) for p in feas), reverse=True)
                if len(us) >= 2 and us[0] - us[1] < 0.03 and abs(_util(asdict(a), ps, (w[0], w[1], w3)) - _util(asdict(b), ps, (w[0], w[1], w3))) < 0.03:
                    break
            products = ps
        else:
            prods = _make_products(rng, budget, min_ram)
            if rng.random() < 0.5:   # every product over budget
                for p in prods:
                    p.price = rng.randint(budget + 25, int(budget * 1.3))
            else:                    # every product below the RAM floor
                min_ram = 32
                for p in prods:
                    p.ram = rng.choice([8, 16])
                    p.price = min(p.price, budget)
            products = [asdict(p) for p in prods]
        sc = Scenario(f"x{i:03d}", "heldout", budget, min_ram, w[0], w[1], w3, products)
        sc.kind = kind
        out.append(sc)
    return out
