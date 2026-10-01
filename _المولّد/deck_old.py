# -*- coding: utf-8 -*-
"""مولّد العرض التعريفي — شرائح ١٦:٩ تُعرض ملء الشاشة بلا إنترنت.

التنقّل: الأسهم · المسافة · النقر. وF أو زرّ «ملء الشاشة» للتسجيل.
ورقم كل شريحة ظاهرٌ ليطابق سيناريو القراءة.
الاستعمال: python3 deck.py <الملف.html>
"""
import base64
import html as H
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deckcontent import SLIDES

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(HERE, "kl_portrait.jpg")          # الكليشة: يُقتطع منها رأسها للشعارين


def logo_b64():
    """رأس الكليشة يُستعمل شعاراً في ركن الشريحة."""
    try:
        from PIL import Image
        import io
        im = Image.open(LOGO)
        w, h = im.size
        im = im.crop((0, 0, w, int(h * 0.11)))        # الشريط العلوي وحده
        buf = io.BytesIO()
        im.convert("RGB").save(buf, "JPEG", quality=88)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return ""


CSS = """
:root{--navy:#355E91;--navy2:#24406a;--teal:#2F7F95;--tealbg:#E2F0F3;--red:#C00000;
      --ink:#16202e;--grey:#6b7a8d;--line:#C9D2DE;--head:#E9EEF6}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:#0e1724;overflow:hidden;
  font-family:"Sakkal Majalla","Geeza Pro","Segoe UI",Tahoma,sans-serif;color:var(--ink)}
#stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center}
#slide{position:relative;width:min(100vw,177.78vh);height:min(56.25vw,100vh);
  background:#fff;overflow:hidden;box-shadow:0 0 60px rgba(0,0,0,.6)}
.hdr{position:absolute;inset-inline:0;top:0;height:11.5%;background:linear-gradient(90deg,var(--navy),var(--teal));
  display:flex;align-items:center;justify-content:space-between;padding:0 3.4%}
.hdr .t{color:#fff;font-size:3.1vh;font-weight:700;letter-spacing:.2px}
.hdr .n{color:#cfe3ea;font-size:2vh}
.sub{position:absolute;inset-inline:0;top:11.5%;background:var(--tealbg);color:#14424f;
  padding:.9vh 3.4%;font-size:2.3vh;border-bottom:1px solid #bcd7de}
.body{position:absolute;inset-inline:0;top:19%;bottom:8%;padding:2.4vh 4%;display:flex;flex-direction:column;gap:1.6vh;justify-content:center}
.ftr{position:absolute;inset-inline:0;bottom:0;height:8%;display:flex;align-items:center;
  justify-content:space-between;padding:0 3.4%;border-top:3px solid var(--navy);background:#f7f9fc}
.ftr span{color:var(--grey);font-size:1.9vh}
.ftr b{color:var(--navy);font-size:2.4vh}
ul{list-style:none;display:flex;flex-direction:column;gap:1.5vh}
li{display:flex;gap:1.4vh;align-items:flex-start;font-size:2.9vh;line-height:1.55}
li::before{content:"◆";color:var(--teal);font-size:1.9vh;margin-top:.9vh;flex:none}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:1.6%;margin-bottom:1vh}
.stat{background:var(--navy);color:#fff;border-radius:1.4vh;padding:2.2vh 1vh;text-align:center}
.stat b{display:block;font-size:5.4vh;line-height:1.1;font-weight:700}
.x{display:flex;flex-direction:column;gap:1.1vh}
.x div{background:var(--head);border-inline-start:.6vh solid var(--teal);border-radius:.7vh;
  padding:1.1vh 1.6vh;font-size:2.35vh;color:#20364f}
.grid6{display:grid;grid-template-columns:repeat(3,1fr);gap:2%;height:100%}
.g6{background:linear-gradient(160deg,var(--navy),var(--teal));color:#fff;border-radius:1.6vh;
  display:flex;align-items:center;justify-content:center;text-align:center;padding:2vh;font-size:3vh;font-weight:700;line-height:1.4}
.chain{display:flex;flex-direction:column;gap:1.4vh}
.ch{display:flex;align-items:center;gap:1.6vh;background:#fff;border:2px solid var(--line);
  border-radius:1.2vh;padding:1.6vh 2vh;font-size:2.8vh}
.ch i{width:4.4vh;height:4.4vh;border-radius:50%;background:var(--teal);color:#fff;font-style:normal;
  display:flex;align-items:center;justify-content:center;font-size:2.4vh;font-weight:700;flex:none}
.ch:last-child{background:var(--navy);color:#fff;border-color:var(--navy);font-weight:700}
.roles{display:grid;grid-template-columns:1fr 1fr;gap:2%;height:100%}
.role{background:#fff;border:2px solid var(--line);border-inline-start:.8vh solid var(--navy);
  border-radius:1.2vh;padding:2vh;font-size:2.6vh;display:flex;align-items:center;line-height:1.5}
.steps{display:flex;flex-direction:column;gap:1.5vh}
.step{display:flex;gap:1.6vh;align-items:center;background:var(--head);border-radius:1.2vh;padding:1.7vh 2vh;font-size:2.7vh}
.cmp{display:flex;flex-direction:column;gap:1.5vh}
.cmp div{font-size:2.9vh;background:#fff;border:2px dashed var(--line);border-radius:1.2vh;padding:1.6vh 2vh}
.cover{height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3vh;text-align:center}
.cover h1{font-size:8vh;color:var(--navy);font-weight:700;line-height:1.2}
.cover h2{font-size:3.4vh;color:var(--teal);font-weight:400}
.cover p{font-size:2.6vh;color:var(--grey);max-width:78%}
.logo{height:5.6%;position:absolute;bottom:1.2%;inset-inline-end:3.4%;opacity:.92;border-radius:.4vh}
#bar{position:fixed;inset-inline:0;bottom:0;height:.5vh;background:rgba(255,255,255,.12)}
#bar i{display:block;height:100%;background:var(--teal);transition:width .25s}
#help{position:fixed;inset-inline-start:1.4vh;bottom:1.4vh;color:#dbe7f0;font-size:1.7vh;transition:opacity .6s;
  background:rgba(14,23,36,.82);padding:.7vh 1.6vh;border-radius:2vh}
#help b{color:#cfe3ea}
body.printing{overflow:auto;background:#222}
body.printing #stage{position:static;display:block}
body.printing .sheet{position:relative;width:100%;aspect-ratio:16/9;background:#fff;margin:0 0 6px;overflow:hidden}
body.printing #bar,body.printing #help{display:none}
@media print{html,body{overflow:visible;background:#fff}#stage{position:static}
  .sheet{page-break-after:always;margin:0;box-shadow:none;width:338mm;height:190mm;aspect-ratio:auto}
  #slide{width:100%;height:auto;aspect-ratio:16/9;page-break-after:always;box-shadow:none}
  #bar,#help{display:none}@page{size:338mm 190mm;margin:0}}
"""

JS = """
const S = __DATA__;
let i = 0;
const el = (t,c,x)=>{const e=document.createElement(t); if(c)e.className=c; if(x!=null)e.textContent=x; return e;};
function render(){
  const s = S[i], d = document.querySelector("#slide") || document.querySelector(".sheet:last-child");
  d.innerHTML = "";
  if(s.kind === "cover"){
    const c = el("div","cover");
    c.appendChild(el("h1", null, s.t));
    c.appendChild(el("h2", null, s.s));
    (s.b||[]).forEach(x=>c.appendChild(el("p", null, x)));
    d.appendChild(c);
  } else {
    const h = el("div","hdr");
    h.appendChild(el("div","t", s.t));
    h.appendChild(el("div","n", ""));
    d.appendChild(h);
    if(s.s) d.appendChild(el("div","sub", s.s));
    const b = el("div","body");
    if(s.kind === "stats"){
      const g = el("div","stats");
      (s.b||[]).forEach(x=>{ const k=el("div","stat"); const p=x.split(" ");
        k.appendChild(el("b",null,p[0])); k.appendChild(el("span",null,p.slice(1).join(" ")||"")); g.appendChild(k); });
      b.appendChild(g);
      const xx = el("div","x"); (s.x||[]).forEach(t=>xx.appendChild(el("div",null,t))); b.appendChild(xx);
    } else if(s.kind === "grid6"){
      const g = el("div","grid6"); (s.b||[]).forEach(t=>g.appendChild(el("div","g6",t))); b.appendChild(g);
    } else if(s.kind === "chain"){
      const g = el("div","chain");
      (s.b||[]).forEach((t,k)=>{ const r=el("div","ch"); r.appendChild(el("i",null,arn(k+1))); r.appendChild(el("span",null,t)); g.appendChild(r); });
      b.appendChild(g);
    } else if(s.kind === "roles"){
      const g = el("div","roles"); (s.b||[]).forEach(t=>g.appendChild(el("div","role",t))); b.appendChild(g);
    } else if(s.kind === "steps"){
      const g = el("div","steps"); (s.b||[]).forEach(t=>g.appendChild(el("div","step",t))); b.appendChild(g);
    } else if(s.kind === "compare"){
      const g = el("div","cmp"); (s.b||[]).forEach(t=>g.appendChild(el("div",null,t))); b.appendChild(g);
    } else {
      const u = el("ul"); (s.b||[]).forEach(t=>u.appendChild(el("li",null,t))); b.appendChild(u);
    }
    d.appendChild(b);
    const f = el("div","ftr");
    f.appendChild(el("span",null,"نظام الحصة الموحَّدة — مدارس ابن خلدون"));
    f.appendChild(el("b",null, arn(i+1) + " / " + arn(S.length)));
    d.appendChild(f);
    if(LOGO){ const im=document.createElement("img"); im.className="logo"; im.src="data:image/jpeg;base64,"+LOGO; d.appendChild(im); }
  }
  document.querySelector("#bar i").style.width = ((i+1)/S.length*100) + "%";
  location.hash = "#" + (i+1);
}
function arn(n){ return String(n).replace(/[0-9]/g, c=>"٠١٢٣٤٥٦٧٨٩"[+c]); }
function go(n){ i = Math.max(0, Math.min(S.length-1, n)); render(); }
document.addEventListener("keydown", e=>{
  if(["ArrowLeft","ArrowDown"," ","PageDown"].includes(e.key)) { go(i+1); e.preventDefault(); }
  else if(["ArrowRight","ArrowUp","PageUp"].includes(e.key)) { go(i-1); e.preventDefault(); }
  else if(e.key === "Home") go(0);
  else if(e.key === "End") go(S.length-1);
  else if(e.key.toLowerCase() === "f"){ if(document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen(); }
});
const hp=document.getElementById("help");
const hide=()=>{ if(hp) hp.style.opacity=0; };
setTimeout(hide, 6000);
document.addEventListener("keydown", hide, {once:true});
document.getElementById("stage").addEventListener("click", e=>{ go(i + (e.clientX < innerWidth/2 ? 1 : -1)); });
if(location.search.indexOf("print") >= 0){      /* وضع الطباعة: كل الشرائح مكدّسة */
  document.body.classList.add("printing");
  const st = document.getElementById("stage");
  st.innerHTML = "";
  for(let k=0; k<S.length; k++){
    const d = document.createElement("div"); d.id = "slide"; d.className = "sheet";
    st.appendChild(d); i = k; render();  d.removeAttribute("id");
  }
} else {
  go(parseInt((location.hash||"#1").slice(1),10) - 1 || 0);
}
"""

HTML = """<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>نظام الحصة الموحَّدة — عرض تعريفي</title>
<style>__CSS__</style></head><body>
<div id="stage"><div id="slide"></div></div>
<div id="bar"><i></i></div>
<div id="help">الأسهم أو المسافة للتنقّل · <b>F</b> لملء الشاشة · النقر يميناً للخلف ويساراً للأمام</div>
<script>const LOGO = "__LOGO__";</script>
<script>__JS__</script></body></html>
"""

import re

RLM = "\u200f"          # علامة من اليمين لليسار


def bidi(t):
    """⚠️ الأرقام الهندية تلتصق عبر الفواصل المحايدة («٤ · ٧٥» ← «٧٥٠٤»)،
    فتُعزل كل مجموعة أرقام بعلامة اتجاه بعدها."""
    if not isinstance(t, str):
        return t
    return re.sub(r"([٠-٩]+٪?)", r"\1" + RLM, t)


def fix(v):
    return [bidi(x) for x in v] if isinstance(v, list) else bidi(v)


data = [{k: fix(v) for k, v in s.items() if k in ("t", "s", "b", "x", "kind")} for s in SLIDES]
out = sys.argv[1] if len(sys.argv) > 1 else "deck.html"
page = (HTML.replace("__CSS__", CSS)
            .replace("__JS__", JS.replace("__DATA__", json.dumps(data, ensure_ascii=False)))
            .replace("__LOGO__", logo_b64()))
with open(out, "w", encoding="utf-8") as f:
    f.write(page)
print("حُفظ:", os.path.basename(out), "|", len(SLIDES), "شريحة |", len(page) // 1024, "ك.ب |",
      "زمن القراءة التقديري:", sum(s["d"] for s in SLIDES) // 60, "دقيقة و",
      sum(s["d"] for s in SLIDES) % 60, "ثانية")
