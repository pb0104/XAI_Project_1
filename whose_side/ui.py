"""Shared design tokens (validated categorical palette, slots 1-4) + base components for the story and demo pages."""
TOKENS = r"""
:root{
 --page:#f5efe3;--surface:#fffcf5;--ink:#1f1b16;--ink2:#51493e;--muted:#6b6356;--grid:#e6dfcf;--base:#cfc6b2;--ring:rgba(60,45,20,.12);
 --s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--accent:#2a78d6;--accent-soft:rgba(42,120,214,.10);
 --good:#006300;--bad:#d03b3b;--warn:#8a5d00;--chip:#efe8d8;
 --g1:rgba(235,104,52,.09);--g2:rgba(42,120,214,.07);--g3:rgba(27,175,122,.05);--grain:.035;--shadow:0 1px 2px rgba(60,45,20,.04);
}
@media(prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){
 --page:#202226;--surface:#2a2c31;--ink:#f3f3f0;--ink2:#cacac5;--muted:#a4a6ac;--grid:#3a3d44;--base:#4b4f58;--ring:rgba(255,255,255,.09);
 --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--accent:#3987e5;--accent-soft:rgba(57,135,229,.16);
 --good:#0ca30c;--bad:#e66767;--warn:#e0a83a;--chip:#33363c;
 --g1:rgba(57,135,229,.13);--g2:rgba(144,133,233,.09);--g3:rgba(217,89,38,.06);--grain:.05;--shadow:0 1px 2px rgba(0,0,0,.2);}}
:root[data-theme="dark"]{
 --page:#202226;--surface:#2a2c31;--ink:#f3f3f0;--ink2:#cacac5;--muted:#a4a6ac;--grid:#3a3d44;--base:#4b4f58;--ring:rgba(255,255,255,.09);
 --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--accent:#3987e5;--accent-soft:rgba(57,135,229,.16);
 --good:#0ca30c;--bad:#e66767;--warn:#e0a83a;--chip:#33363c;
 --g1:rgba(57,135,229,.13);--g2:rgba(144,133,233,.09);--g3:rgba(217,89,38,.06);--grain:.05;--shadow:0 1px 2px rgba(0,0,0,.2);}
[hidden]{display:none!important}
*{box-sizing:border-box}html{scroll-behavior:smooth}
html{background:var(--page)}
body{margin:0;background:transparent;color:var(--ink);font:17px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}
body::before{content:"";position:fixed;inset:0;z-index:-2;pointer-events:none;
 background:radial-gradient(900px 600px at 88% -8%,var(--g1),transparent 62%),radial-gradient(800px 560px at 6% 8%,var(--g2),transparent 60%),radial-gradient(900px 700px at 50% 112%,var(--g3),transparent 60%)}
body::after{content:"";position:fixed;inset:0;z-index:-1;pointer-events:none;opacity:var(--grain);mix-blend-mode:multiply;
 background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 .4 0 0 0 0 .35 0 0 0 0 .3 0 0 0 .55 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
:root[data-theme="dark"] body::after{mix-blend-mode:screen}
@media(prefers-color-scheme:dark){:root:where(:not([data-theme="light"])) body::after{mix-blend-mode:screen}}
a{color:var(--accent)}button{font:inherit;color:inherit}
.wrap{max-width:880px;margin:0 auto;padding:0 20px}
.topbar{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--page) 88%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--grid)}
.topbar .wrap{display:flex;align-items:center;gap:14px;height:52px}
.brand{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:650;font-size:15px;letter-spacing:-.01em;margin-right:auto}.brand i{font-style:normal;color:var(--accent)}
.iconbtn{white-space:nowrap;border:1px solid var(--grid);background:var(--surface);border-radius:99px;padding:5px 12px;font-size:13px;cursor:pointer}
.iconbtn:hover{border-color:var(--base)}
.progress{position:absolute;left:0;bottom:-1px;height:2px;background:var(--accent);width:0}
.eyebrow{font-size:12px;font-weight:650;letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}
.card{background:var(--surface);border:1px solid var(--ring);border-radius:14px;padding:18px 20px;box-shadow:var(--shadow)}
.chip{display:inline-flex;align-items:center;gap:6px;background:var(--chip);border-radius:99px;padding:2px 10px;font-size:13px;line-height:1.6}
.chip.ok{color:var(--good)}.chip.bad{color:var(--bad)}.chip.warn{color:var(--warn)}
.badge{display:inline-block;font-size:11px;font-weight:650;letter-spacing:.06em;text-transform:uppercase;border:1px solid var(--s4);color:var(--warn);border-radius:6px;padding:0 6px;margin-left:6px;vertical-align:middle}
.dot{display:inline-block;width:10px;height:10px;border-radius:3px;flex:none}
table.t{width:100%;border-collapse:collapse;font-size:14.5px}
table.t th{font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);font-weight:600;text-align:left;padding:6px 10px;border-bottom:1px solid var(--base)}
table.t td{padding:9px 10px;border-bottom:1px solid var(--grid);vertical-align:middle}
table.t tr:last-child td{border-bottom:0}.num{text-align:right;font-variant-numeric:tabular-nums}
.fitbar{height:8px;border-radius:4px;background:var(--grid);overflow:hidden;min-width:70px}.fitbar>i{display:block;height:100%;background:var(--accent);border-radius:4px}
.fitbar.no>i{background:repeating-linear-gradient(135deg,var(--base) 0 4px,transparent 4px 8px)}
.legend{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:13.5px;color:var(--ink2);margin:0 0 10px}.legend span{display:inline-flex;align-items:center;gap:7px}
#tip{position:fixed;z-index:50;pointer-events:none;background:var(--ink);color:var(--page);border-radius:8px;padding:7px 10px;font-size:13px;line-height:1.4;max-width:260px;opacity:0;transition:opacity .08s;box-shadow:0 4px 18px rgba(0,0,0,.25)}
#tip b{display:block;font-size:15px}#tip span{opacity:.8}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}html{scroll-behavior:auto}}
"""

THEME_JS = r"""
(function(){var k='ws-theme',r=document.documentElement;
 try{var t=localStorage.getItem(k);if(t)r.setAttribute('data-theme',t)}catch(e){}
 window.toggleTheme=function(){var dark=r.getAttribute('data-theme')?r.getAttribute('data-theme')==='dark':matchMedia('(prefers-color-scheme:dark)').matches;
  var n=dark?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem(k,n)}catch(e){}};
 var tip=document.getElementById('tip');
 window.showTip=function(e,title,value,sub){if(!tip)return;tip.replaceChildren();
  var b=document.createElement('b');b.textContent=value;var s=document.createElement('span');s.textContent=title+(sub?' · '+sub:'');tip.append(b,s);
  var x=e.clientX!=null&&e.clientX>0?e.clientX:(e.target.getBoundingClientRect().left+20),y=e.clientY!=null&&e.clientY>0?e.clientY:(e.target.getBoundingClientRect().top);
  tip.style.opacity=1;var w=tip.offsetWidth;tip.style.left=Math.min(innerWidth-w-8,x+14)+'px';tip.style.top=Math.max(8,y-tip.offsetHeight-10)+'px'};
 window.hideTip=function(){if(tip)tip.style.opacity=0};
})();
"""
