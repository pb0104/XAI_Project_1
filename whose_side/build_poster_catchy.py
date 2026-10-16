"""Build poster/catchy.html: a clean, high-impact 36x24 in poster (one claim, one number, one chart per panel).
Usage: python -m whose_side.build_poster_catchy"""
from .pagedata import load, compute_stats, valid_main
from .analyze import M, ci

MODEL = "GPT-4o mini"
B, O, G, Y = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"      # validated categorical slots 1-4
pct = lambda v: f"{round(v * 100)}%"


def hbars(items, maxv, fmt, ref=None, ref_label=None):
    """items: [(label, color, value)] -> horizontal bars, label above each bar, value at the tip."""
    out = ['<div class="hb">']
    if ref_label:
        out.append(f'<div class="reflab"><i></i>{ref_label}</div>')
    for label, color, v in items:
        w = max(v / maxv * 100, .8)
        r = f'<i class="ref" style="left:{ref / maxv * 100}%"></i>' if ref is not None else ""
        out.append(f'<div class="hrow"><div class="hl"><i style="background:{color}"></i>{label}</div>'
                   f'<div class="ht"><div class="hbar" style="width:{w}%;background:{color}"></div>'
                   f'<span class="hv" style="left:calc({w}% + 16px)">{fmt(v)}</span>{r}</div></div>')
    out.append("</div>")
    return "".join(out)


def build(held="results/results_v2.jsonl", dev="results/results_dev.jsonl", out="poster/catchy.html"):
    hrows, drows = load(held), load(dev)
    S = compute_stats(hrows, drows)
    ov, bk, df = S["overall"], S["by_kind"], S["defenses"]
    std = [r for r in valid_main(hrows) if r["scen_kind"] == "standard"]
    di = ci([r for r in std if r["condition"] == "incentive"], M["disclosed_if_sponsored_pick"])[0]
    u, i = ov["user_focused"]["picks_sponsored"]["v"], ov["incentive"]["picks_sponsored"]["v"]
    inf = bk["infeasible"]
    p1 = hbars([("No secret note", B, u), ("Secret note: favour sponsors", O, i)], 1, pct, ref=.2, ref_label="20% = ignoring sponsorship")
    p2 = hbars([("No secret note", B, inf["user_focused"]["picks_sponsored"]["v"]), ("Secret note: favour sponsors", O, inf["incentive"]["picks_sponsored"]["v"]),
                ("+ must say when sponsored", G, inf["disclosed"]["picks_sponsored"]["v"]), ("+ shopper’s limits first", Y, inf["priority_policy"]["picks_sponsored"]["v"])], 1, pct)
    p3 = hbars([("Secret note: favour sponsors", O, di), ("+ must say when sponsored", G, 1.0), ("+ shopper’s limits first", Y, 1.0)], 1, pct)
    p4 = hbars([("No fix", "#b9b3a4", df["none"]["regret"]), ("Check the shopper’s limits", "#b9b3a4", df["hard_filter"]["regret"]),
                ("A 2nd AI that doesn’t know the sponsor", "#14284b", df["blind_only"]["regret"])], .16, lambda v: f"{v:.3f}")
    rep = {"__P1__": p1, "__P2__": p2, "__P3__": p3, "__P4__": p4, "__MODEL__": MODEL,
           "__U__": pct(u), "__I__": pct(i), "__INF_D__": pct(inf["disclosed"]["picks_sponsored"]["v"]), "__SILENT__": pct(1 - di),
           "__WORSE_P__": pct(bk["feasible_inferior"]["priority_policy"]["picks_sponsored"]["v"]),
           "__REG0__": f"{df['none']['regret']:.3f}", "__REG1__": f"{df['blind_only']['regret']:.3f}"}
    html = TEMPLATE
    for k, v in rep.items():
        html = html.replace(k, v)
    open(out, "w").write(html)
    print(f"wrote {out}")


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Whose Side Is Your AI On? · Poster</title>
<style>
@page{size:36in 24in;margin:0}
:root{--navy:#14284b;--ink:#161616;--ink2:#454545;--mut:#6f6f6f;--bg:#fbf7ef;--card:#fff;--rule:#e9e2d2;--b:#2a78d6;--o:#eb6834;--g:#1baf7a;--y:#eda100;--bad:#c2362f}
*{box-sizing:border-box}html,body{margin:0;background:#7b8088}
body{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.bar-top{position:fixed;top:0;left:0;right:0;z-index:9;background:#111;color:#fff;display:flex;gap:16px;align-items:center;padding:10px 20px;font-size:14px}
.bar-top button{background:var(--o);color:#fff;border:0;border-radius:6px;padding:8px 16px;font-weight:700;font-size:14px;cursor:pointer}.bar-top span{opacity:.85}.bar-top b{color:#fff}
.stage{padding:64px 20px 30px}
.poster{width:3456px;height:2304px;transform-origin:top left;position:relative;overflow:hidden;background:var(--bg)}
header{height:384px;background:var(--navy);color:#fff;padding:52px 100px 0;display:grid;grid-template-columns:1fr 1100px;gap:90px}
.tag{font-size:28px;letter-spacing:.22em;text-transform:uppercase;color:#aab8d4;font-weight:700}
h1{font-size:150px;line-height:1;margin:12px 0 14px;font-weight:900;letter-spacing:-.035em}
.sub{font-size:44px;color:#dfe6f4;line-height:1.2}.by{font-size:32px;color:#aebcd8;margin-top:16px}.by b{color:#fff}
.verdict{background:#fff;color:var(--ink);border-radius:28px;padding:30px 42px;align-self:center;border-left:20px solid var(--o)}
.verdict small{font-size:26px;letter-spacing:.16em;text-transform:uppercase;color:var(--mut);font-weight:800}
.verdict b{display:block;font-size:56px;line-height:1.08;letter-spacing:-.02em;margin:10px 0 12px;color:var(--navy);font-weight:900}.verdict span{font-size:32px;color:var(--ink2);line-height:1.3;display:block}
.setup{margin:36px 100px 0;display:grid;grid-template-columns:1fr 1500px;gap:80px;align-items:center;height:190px}
.setup h2{font-size:54px;margin:0 0 8px;font-weight:900;letter-spacing:-.02em}.setup p{font-size:34px;line-height:1.3;margin:0;color:var(--ink2)}.setup p b{color:var(--ink)}
.chips{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}.chips div{background:var(--card);border-radius:22px;border-top:14px solid var(--c);padding:22px 24px;font-size:32px;font-weight:700;line-height:1.2;color:var(--ink)}
.panels{margin:36px 100px 0;display:grid;grid-template-columns:repeat(4,1fr);gap:48px;height:1276px}
.panel{background:var(--card);border-radius:34px;padding:44px 46px 40px;display:flex;flex-direction:column;border-top:18px solid var(--c)}
.step{font-size:30px;font-weight:900;letter-spacing:.14em;text-transform:uppercase;color:var(--c)}
.big{font-size:150px;font-weight:900;letter-spacing:-.05em;line-height:1;margin:18px 0 6px;color:var(--ink)}.big small{font-size:54px;letter-spacing:0;color:var(--mut);font-weight:700;margin:0 10px}.big em{font-style:normal;color:var(--c)}
.big-l{font-size:30px;color:var(--mut);line-height:1.3;margin:0 0 26px}
.claim{font-size:56px;line-height:1.06;font-weight:900;letter-spacing:-.03em;margin:0 0 30px;color:var(--ink)}
.hb{position:relative;padding-top:0;flex:1;display:flex;flex-direction:column;justify-content:space-evenly;margin-bottom:20px}
.hrow{margin:0}.hl{font-size:33px;font-weight:700;color:var(--ink);display:flex;align-items:center;gap:14px;line-height:1.15;margin-bottom:10px}.hl i{width:26px;height:26px;border-radius:8px;flex:none}
.ht{position:relative;height:52px;margin-right:170px;background-image:linear-gradient(to right,#efe9da 3px,transparent 3px);background-size:25% 100%;border-right:3px solid #efe9da}
.hbar{position:absolute;left:0;top:5px;height:42px;border-radius:0 12px 12px 0}
.hv{position:absolute;top:1px;font-size:44px;font-weight:900;font-variant-numeric:tabular-nums;color:var(--ink)}
.ref{position:absolute;top:-8px;bottom:-8px;border-left:5px solid var(--ink);opacity:.55}.reflab{display:flex;align-items:center;gap:14px;font-size:29px;font-weight:700;color:var(--ink2);margin-bottom:6px}.reflab i{display:block;width:0;height:34px;border-left:5px solid var(--ink);opacity:.55}
.cap{margin-top:auto;font-size:30px;line-height:1.35;color:var(--ink2);border-top:3px solid var(--rule);padding-top:22px}.cap b{color:var(--ink)}
.cap q{display:block;font-style:italic;color:var(--ink);margin-bottom:10px;quotes:"“" "”"}
.take{margin:36px 100px 0;background:var(--navy);color:#fff;border-radius:34px;padding:34px 60px;display:grid;grid-template-columns:420px 1fr 1fr 1fr;gap:56px;align-items:center;height:272px}
.take h2{font-size:60px;line-height:1.02;margin:0;font-weight:900;letter-spacing:-.025em;color:#fff}
.take .t b{display:flex;gap:16px;align-items:baseline;font-size:46px;line-height:1.1;margin-bottom:10px;color:#fff;font-weight:900}.take .t b i{font-style:normal;color:var(--o);font-size:64px}
.take .t span{font-size:32px;line-height:1.3;color:#cfd8ec;display:block}
footer{position:absolute;left:0;right:0;bottom:0;height:56px;background:#0c1730;color:#a9b6d2;display:flex;align-items:center;justify-content:space-between;padding:0 100px;font-size:24px}
@media print{html,body{background:none}.bar-top{display:none}.stage{padding:0;display:block}.poster{transform:none!important}.panel{box-shadow:none!important}}
</style></head><body>
<div class="bar-top"><button onclick="window.print()">Download as PDF</button><span>In the print dialog choose <b>Save as PDF</b>, paper size <b>36 × 24 in</b> (or “Fit to page”), margins <b>None</b>, tick <b>Background graphics</b>.</span></div>
<div class="stage" id="stage"><div class="poster" id="poster">
<header>
 <div><div class="tag">Explainable AI · Project 1</div>
  <h1>Whose Side Is Your AI On?</h1>
  <div class="sub">What if a store quietly pays to promote some laptops? Would the AI still look out for you?</div>
  <div class="by"><b>Pranshul Bhatnagar</b> · Duke University</div></div>
 <div class="verdict"><small>What we found</small><b>A store can push the AI, and you often can’t tell.</b><span>Saying “sponsored” and the AI’s own explanation did not protect the shopper.</span></div>
</header>

<div class="setup"><div><h2>How we tested it</h2><p>Same laptops, same shopper. <b>Only a secret note from the store changes.</b> (“Sponsored” = a company paid to promote the laptop.)</p></div>
 <div class="chips"><div style="--c:var(--b)">No secret note</div><div style="--c:var(--o)">Secret note: favour sponsors</div><div style="--c:var(--g)">+ must say when sponsored</div><div style="--c:var(--y)">+ shopper’s limits first</div></div></div>

<div class="panels">
 <div class="panel" style="--c:var(--b)"><div class="step">1 · The obvious part</div>
  <div class="big"><em>__U__</em><small>→</small><span style="color:var(--o)">__I__</span></div><div class="big-l">picked the sponsored laptop</div>
  <div class="claim">When the store pushes, the AI pushes.</div>
  __P1__
  <div class="cap">Obvious. It only proves our test works. The real findings come next.</div></div>

 <div class="panel" style="--c:var(--g)"><div class="step">2 · The label</div>
  <div class="big"><em style="color:var(--bad)">__INF_D__</em></div><div class="big-l">still recommended a sponsored laptop that broke the shopper’s limits</div>
  <div class="claim">Saying “sponsored” did not make it safer.</div>
  __P2__
  <div class="cap">Shorter bar = safer. Only requests where the sponsored laptop was over budget or had too little RAM.</div></div>

 <div class="panel" style="--c:var(--o)"><div class="step">3 · The explanation</div>
  <div class="big"><em>__SILENT__</em></div><div class="big-l">of sponsored picks never said “sponsored”</div>
  <div class="claim">The explanation skips the real reason.</div>
  __P3__
  <div class="cap"><q>…assurance of quality and support from the brand.</q>A real answer. Nothing in the store data says this.</div></div>

 <div class="panel" style="--c:#14284b"><div class="step">4 · What worked</div>
  <div class="big"><em>__REG0__</em><small>→</small>__REG1__</div><div class="big-l">distance from the shopper’s best laptop (0 = perfect)</div>
  <div class="claim">Take the sponsor out of the decision.</div>
  __P4__
  <div class="cap">Shorter bar = closer to the best laptop. Telling the AI “limits first” still picked a <b>worse</b> sponsored laptop __WORSE_P__ of the time.</div></div>
</div>

<div class="take"><h2>So what does this mean?</h2>
 <div class="t"><b><i>1</i>Easy to push an AI</b><span>One hidden sentence from the store was enough.</span></div>
 <div class="t"><b><i>2</i>Hard to notice</b><span>Neither the label nor the explanation showed it.</span></div>
 <div class="t"><b><i>3</i>Don’t let it check itself</b><span>Compare with your own limits, or let a second AI decide.</span></div></div>

<footer><span>Fictional products · recorded runs of __MODEL__ · 20 requests × 5 sponsors, repeated on 20 new requests · one model, no user study</span><span>Explainable AI · Project 1 · Pranshul Bhatnagar</span></footer>
</div></div>
<script>
(function(){var p=document.getElementById('poster'),s=document.getElementById('stage');
 function fit(){if(matchMedia('print').matches){p.style.transform='none';s.style.height='auto';s.style.paddingLeft='0';return}var k=Math.min(1,(innerWidth-40)/3456);p.style.transform='scale('+k+')';s.style.height=(2304*k+94)+'px';s.style.display='block';s.style.paddingLeft=((innerWidth-3456*k)/2)+'px'}
 addEventListener('resize',fit);addEventListener('beforeprint',fit);addEventListener('afterprint',fit);fit()})();
</script></body></html>
"""

if __name__ == "__main__":
    build()
