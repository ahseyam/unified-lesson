# -*- coding: utf-8 -*-
"""مولّد العرض التعريفي — شرائح ١٦:٩ بخط الجزيرة وصورٍ من المستندات نفسها.

ملفٌّ واحد مكتفٍ بنفسه: الخطوط والصور مضمَّنة، فيعمل بلا إنترنت وينتقل كما هو.
التنقّل: الأسهم · المسافة · النقر · F لملء الشاشة. و«?print» يعرض الشرائح كلها للطباعة.

⛔ **وتصديرُ PDF يحتاج «?print» وإلّا خرجت صفحةٌ واحدة.** الشرائحُ مكدَّسةٌ
   بـ`position:absolute` وتُعرض واحدةً واحدة، فطباعةُ الصفحة بلا المفتاح
   تُخرج الأولى وحدَها (٤٥٥ ك.ب بدل ٥ م.ب) — ومرَّت عليَّ فظننتُها نجحت حتى
   عددتُ صفحاتِها. فالوصفة:

     chrome --headless=new --no-pdf-header-footer \
            --print-to-pdf=OUT --virtual-time-budget=120000 \
            --run-all-compositor-stages-before-draw "file://SRC?print"

   ⚠️ ويُفحص الناتجُ قبل قبوله: **٢٢ صفحةً و٤٣ صورةً على الأقل** — ولا يُستبدل
      المنشورُ إلا بعد الفحص. (١ أكتوبر ٢٠٢٦)

⚠️ خط الجزيرة يرسم الأرقام الهندية بأشكالٍ غربية (٥ ← 5)، فتُستثنى من نطاقه
   بـunicode-range ويتكفّل بها «سكل مجلة» — وقد فُحص بصرياً.
الاستعمال: python3 deck.py <الملف.html>
"""
import base64
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deckcontent import SLIDES

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
IMGDIR = os.path.join(ROOT, "٩ - العرض التعريفي", "صور")
FONTS = os.path.expanduser("~/Library/Fonts")
RLM = "‏"


def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def face(name, file, weight="normal", digits=False):
    """وجهُ خطٍّ مضمَّن. digits=False يستثني الأرقام الهندية فتُرسم بخطٍّ آخر."""
    p = os.path.join(FONTS, file)
    if not os.path.exists(p):
        return ""
    ur = "" if digits else "  unicode-range:U+0000-065F,U+066A-FFFF;\n"
    return (f"@font-face{{font-family:{name};font-weight:{weight};font-display:block;\n"
            f"  src:url(data:font/ttf;base64,{b64(p)}) format('truetype');\n{ur}}}\n")


FONTCSS = (face("JZ", "ArbFONTS-Al-Jazeera-Arabic-Regular.ttf")
           + face("JZ", "ArbFONTS-Al-Jazeera-Arabic-Bold.ttf", "700")
           + face("JZL", "ArbFONTS-Al-Jazeera-Arabic-Light.ttf")
           + face("SK", "Sakkal Majalla Regular.ttf", digits=True))

CSS = """
:root{--navy:#2F5384;--navy2:#1d3760;--teal:#2F7F95;--teal2:#1d5d70;--tealbg:#E4F1F4;
      --ink:#16202e;--grey:#6b7a8d;--line:#C9D2DE;--head:#EDF2F8;--gold:#B8862B}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:#0d1622;overflow:hidden;color:var(--ink);
  font-family:JZ,SK,"Geeza Pro",Tahoma,sans-serif;font-weight:400}
#stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center}
#slide{position:relative;width:min(100vw,177.78vh);height:min(56.25vw,100vh);
  background:#fff;overflow:hidden;box-shadow:0 0 70px rgba(0,0,0,.65)}

/* ── الترويسة ── */
.hdr{position:absolute;inset-inline:0;top:0;height:12.5%;
  background:linear-gradient(105deg,var(--navy2),var(--navy) 42%,var(--teal));
  display:flex;align-items:center;padding:0 3.2%;gap:2%}
.hdr .num{font-family:SK;color:#fff;opacity:.55;font-size:4.6vh;line-height:1;font-weight:700;
  border-inline-end:.35vh solid rgba(255,255,255,.35);padding-inline-end:2vh}
.hdr .t{color:#fff;font-size:3.5vh;font-weight:700;line-height:1.2}
.hdr .s{color:#d5e8ee;font-family:JZL,SK;font-size:2.15vh;margin-top:.4vh}
.hdr .box{display:flex;flex-direction:column;justify-content:center;min-width:0}

/* ── الجسم ── */
.body{position:absolute;inset-inline:0;top:12.5%;bottom:7.5%;padding:2.4vh 3.2%;
  display:grid;grid-template-columns:37% 1fr;gap:2.6%;align-items:center;min-height:0}
.txt{display:flex;flex-direction:column;gap:1.5vh;min-width:0;min-height:0;max-height:100%;overflow:hidden}
.pic{height:100%;min-height:0;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:.9vh;min-width:0;overflow:hidden}
.pic img{max-width:100%;min-height:0;flex:1 1 auto;object-fit:contain;border:1px solid var(--line);
  border-radius:.8vh;box-shadow:0 1.2vh 3vh rgba(20,40,70,.22)}
.cap{font-family:JZL,SK;font-size:1.85vh;color:var(--grey)}
.cap b{color:var(--teal2);font-family:JZ,SK;font-weight:400}

ul{list-style:none;display:flex;flex-direction:column;gap:1.35vh}
li{display:flex;gap:1.2vh;align-items:flex-start;font-size:2.42vh;line-height:1.5}
li::before{content:"";width:1.05vh;height:1.05vh;border-radius:50%;background:var(--teal);
  margin-top:1.05vh;flex:none}
.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:1.2vh}
.stat{background:linear-gradient(150deg,var(--navy),var(--navy2));color:#fff;border-radius:1.2vh;
  padding:1.5vh .8vh;text-align:center}
.stat b{display:block;font-family:SK;font-size:4.6vh;line-height:1.05;font-weight:700}
.stat span{font-family:JZL,SK;font-size:1.9vh;opacity:.92}
.x{display:flex;flex-direction:column;gap:.85vh;margin-top:.6vh}
.x div{background:var(--head);border-inline-start:.5vh solid var(--teal);border-radius:.6vh;
  padding:.85vh 1.2vh;font-size:1.95vh;color:#22374f;font-family:JZL,SK}
.g6{display:grid;grid-template-columns:1fr 1fr;gap:1.1vh}
.g6 div{background:linear-gradient(155deg,var(--navy),var(--teal));color:#fff;border-radius:1.1vh;
  display:flex;align-items:center;justify-content:center;text-align:center;padding:1.4vh .8vh;
  font-size:2.05vh;font-weight:700;line-height:1.35;min-height:8vh}
.chain{display:flex;flex-direction:column;gap:1.1vh}
.ch{display:flex;align-items:center;gap:1.2vh;background:#fff;border:.25vh solid var(--line);
  border-radius:1vh;padding:1.2vh 1.4vh;font-size:2.25vh;line-height:1.4}
.ch i{width:3.7vh;height:3.7vh;border-radius:50%;background:var(--teal);color:#fff;font-style:normal;
  display:flex;align-items:center;justify-content:center;font-family:SK;font-size:2.1vh;font-weight:700;flex:none}
.ch:last-child{background:var(--navy);color:#fff;border-color:var(--navy)}
.ch:last-child i{background:var(--gold)}
.roles{display:flex;flex-direction:column;gap:1.1vh}
.role{background:#fff;border:.22vh solid var(--line);border-inline-start:.6vh solid var(--navy);
  border-radius:1vh;padding:1.2vh 1.4vh;font-size:2.2vh;line-height:1.45}
.steps{display:flex;flex-direction:column;gap:1.1vh}
.step{background:var(--head);border-radius:1vh;padding:1.25vh 1.4vh;font-size:2.25vh;line-height:1.45}
.cmp{display:flex;flex-direction:column;gap:1.2vh}
.cmp div{font-size:2.3vh;background:#fff;border:.22vh dashed var(--line);border-radius:1vh;
  padding:1.2vh 1.4vh;line-height:1.45}

/* ── الغلاف ── */
.cover{position:absolute;inset:0;display:grid;grid-template-columns:52% 1fr;align-items:center;
  padding:0 4.5%;gap:3%;background:linear-gradient(120deg,#fff 58%,var(--tealbg))}
.cover .l{display:flex;flex-direction:column;gap:2vh}
.cover h1{font-size:7.4vh;color:var(--navy2);font-weight:700;line-height:1.15}
.cover h2{font-size:3.1vh;color:var(--teal2);font-family:JZL,SK}
.cover p{font-size:2.2vh;color:var(--grey);font-family:JZL,SK;line-height:1.6}
.cover .rule{width:14vh;height:.7vh;background:var(--gold);border-radius:.4vh}
.cover .pic img{max-height:74vh}

/* ── التذييل ── */
.ftr{position:absolute;inset-inline:0;bottom:0;height:7.5%;display:flex;align-items:center;
  justify-content:space-between;padding:0 3.2%;border-top:.35vh solid var(--navy);background:#f6f9fc}
.ftr span{color:var(--grey);font-family:JZL,SK;font-size:1.85vh}
.ftr b{color:var(--navy);font-family:SK;font-size:2.2vh}
.ftr img{height:4.6vh;width:auto;opacity:.92}
#bar{position:fixed;inset-inline:0;bottom:0;height:.45vh;background:rgba(255,255,255,.12);z-index:9}
#bar i{display:block;height:100%;background:var(--teal);transition:width .25s}
#help{position:fixed;inset-inline-start:1.4vh;bottom:9.4vh;color:#dbe7f0;font-size:1.7vh;
  font-family:JZL,SK;background:rgba(13,22,34,.85);padding:.7vh 1.6vh;border-radius:2vh;
  transition:opacity .6s;z-index:10}
body.printing{overflow:auto;background:#222}
body.printing #stage{position:static;display:block}
body.printing .sheet{position:relative;width:100%;aspect-ratio:16/9;background:#fff;margin:0 0 6px;overflow:hidden}
body.printing #bar,body.printing #help{display:none}
@media print{html,body{overflow:visible;background:#fff}#stage{position:static}
  .sheet{page-break-after:always;margin:0;box-shadow:none;width:338mm;height:190mm;aspect-ratio:auto}
  #bar,#help{display:none}@page{size:338mm 190mm;margin:0}}
"""

JS = """
const S = __DATA__, IM = __IMGS__, LOGO = "__LOGO__";
let i = 0;
const el=(t,c,x)=>{const e=document.createElement(t); if(c)e.className=c; if(x!=null)e.textContent=x; return e;};
const arn=n=>String(n).replace(/[0-9]/g,c=>"٠١٢٣٤٥٦٧٨٩"[+c]);
function pic(s){
  const w = el("div","pic");
  if(IM[s.img]){ const im=document.createElement("img"); im.src="data:image/jpeg;base64,"+IM[s.img]; w.appendChild(im); }
  if(s.cap){ const c=el("div","cap"); c.appendChild(el("b",null,"من المستند: ")); c.appendChild(el("span",null,s.cap)); w.appendChild(c); }
  return w;
}
function render(){
  const s = S[i], d = document.querySelector("#slide") || document.querySelector(".sheet:last-child");
  d.innerHTML = "";
  if(s.kind === "cover"){
    const c = el("div","cover"), l = el("div","l");
    l.appendChild(el("h1", null, s.t));
    l.appendChild(el("div","rule"));
    l.appendChild(el("h2", null, s.s));
    (s.b||[]).forEach(x=>l.appendChild(el("p", null, x)));
    c.appendChild(l); c.appendChild(pic(s));
    d.appendChild(c);
    if(LOGO){ const g=document.createElement("img"); g.src="data:image/jpeg;base64,"+LOGO;
      g.style.cssText="position:absolute;bottom:3%;inset-inline-start:4.5%;height:7%;opacity:.9"; d.appendChild(g); }
    return;
  }
  const h = el("div","hdr");
  h.appendChild(el("div","num", arn(i+1)));
  const bx = el("div","box");
  bx.appendChild(el("div","t", s.t));
  if(s.s) bx.appendChild(el("div","s", s.s));
  h.appendChild(bx); d.appendChild(h);

  const b = el("div","body"), t = el("div","txt");
  if(s.kind === "stats"){
    const g = el("div","stats");
    (s.b||[]).forEach(x=>{ const k=el("div","stat"); const p=x.split(" ");
      k.appendChild(el("b",null,p[0])); k.appendChild(el("span",null,p.slice(1).join(" ")||"")); g.appendChild(k); });
    t.appendChild(g);
    const xx = el("div","x"); (s.x||[]).forEach(v=>xx.appendChild(el("div",null,v))); t.appendChild(xx);
  } else if(s.kind === "grid6"){
    const g = el("div","g6"); (s.b||[]).forEach(v=>g.appendChild(el("div",null,v))); t.appendChild(g);
  } else if(s.kind === "chain"){
    const g = el("div","chain");
    (s.b||[]).forEach((v,k)=>{ const r=el("div","ch"); r.appendChild(el("i",null,arn(k+1)));
      r.appendChild(el("span",null,v)); g.appendChild(r); });
    t.appendChild(g);
  } else if(s.kind === "roles"){
    const g = el("div","roles"); (s.b||[]).forEach(v=>g.appendChild(el("div","role",v))); t.appendChild(g);
  } else if(s.kind === "steps"){
    const g = el("div","steps"); (s.b||[]).forEach(v=>g.appendChild(el("div","step",v))); t.appendChild(g);
  } else if(s.kind === "compare"){
    const g = el("div","cmp"); (s.b||[]).forEach(v=>g.appendChild(el("div",null,v))); t.appendChild(g);
  } else {
    const u = el("ul"); (s.b||[]).forEach(v=>u.appendChild(el("li",null,v))); t.appendChild(u);
  }
  b.appendChild(t); b.appendChild(pic(s));
  d.appendChild(b);

  const f = el("div","ftr");
  f.appendChild(el("span",null,"نظام الحصة الموحَّدة — مدارس ابن خلدون"));
  const rt = el("div"); rt.style.cssText="display:flex;align-items:center;gap:1.6vh";
  rt.appendChild(el("b",null, arn(i+1) + " / " + arn(S.length)));
  if(LOGO){ const g=document.createElement("img"); g.src="data:image/jpeg;base64,"+LOGO; rt.appendChild(g); }
  f.appendChild(rt);
  d.appendChild(f);
}
function go(n){ i=Math.max(0,Math.min(S.length-1,n)); render();
  document.querySelector("#bar i").style.width=((i+1)/S.length*100)+"%"; location.hash="#"+(i+1); }
document.addEventListener("keydown", e=>{
  if(["ArrowLeft","ArrowDown"," ","PageDown"].includes(e.key)){ go(i+1); e.preventDefault(); }
  else if(["ArrowRight","ArrowUp","PageUp"].includes(e.key)){ go(i-1); e.preventDefault(); }
  else if(e.key==="Home") go(0);
  else if(e.key==="End") go(S.length-1);
  else if(e.key.toLowerCase()==="f"){ document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen(); }
});
const hp=document.getElementById("help"), hide=()=>{ if(hp) hp.style.opacity=0; };
setTimeout(hide, 6000);
document.addEventListener("keydown", hide, {once:true});
document.getElementById("stage").addEventListener("click", e=>{ go(i + (e.clientX < innerWidth/2 ? 1 : -1)); });
if(location.search.indexOf("print") >= 0){
  document.body.classList.add("printing");
  const st=document.getElementById("stage"); st.innerHTML="";
  for(let k=0;k<S.length;k++){
    const d=document.createElement("div"); d.id="slide"; d.className="sheet";
    st.appendChild(d); i=k; render(); d.removeAttribute("id");
  }
} else { go(parseInt((location.hash||"#1").slice(1),10) - 1 || 0); }
"""

HTML = """<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>نظام الحصة الموحَّدة — عرض تعريفي</title>
<style>__FONTS____CSS__</style></head><body>
<div id="stage"><div id="slide"></div></div>
<div id="bar"><i></i></div>
<div id="help">الأسهم أو المسافة للتنقّل · F لملء الشاشة</div>
<script>__JS__</script></body></html>
"""


def bidi(t):
    """⚠️ الأرقام الهندية تلتصق عبر الفواصل المحايدة، فتُعزل كلُّ مجموعةٍ بعلامة اتجاه."""
    return re.sub(r"([٠-٩]+٪?)", r"\1" + RLM, t) if isinstance(t, str) else t


def fix(v):
    return [bidi(x) for x in v] if isinstance(v, list) else bidi(v)


imgs = {}
for s in SLIDES:
    k = s.get("img")
    p = os.path.join(IMGDIR, (k or "") + ".jpg")
    if k and os.path.exists(p):
        imgs[k] = b64(p)

logo = ""
lp = os.path.join(HERE, "deck_logo.jpg")
if not os.path.exists(lp):                     # يُقتطع رأس الكليشة مرّةً واحدة
    try:
        from PIL import Image
        im = Image.open(os.path.join(HERE, "kl_portrait.jpg"))
        w, h = im.size
        im.crop((0, 0, int(w * 0.52), int(h * 0.075))).convert("RGB").save(lp, "JPEG", quality=90)
    except Exception:
        pass
if os.path.exists(lp):
    logo = b64(lp)

data = [{k: fix(v) for k, v in s.items() if k in ("t", "s", "b", "x", "kind", "img", "cap")}
        for s in SLIDES]
out = sys.argv[1] if len(sys.argv) > 1 else "deck.html"
page = (HTML.replace("__FONTS__", FONTCSS).replace("__CSS__", CSS)
            .replace("__JS__", JS.replace("__DATA__", json.dumps(data, ensure_ascii=False))
                                 .replace("__IMGS__", json.dumps(imgs))
                                 .replace("__LOGO__", logo)))
with open(out, "w", encoding="utf-8") as f:
    f.write(page)
total = sum(s["d"] for s in SLIDES)
print("حُفظ:", os.path.basename(out), "|", len(SLIDES), "شريحة |", len(imgs), "صورة |",
      round(len(page) / 1048576, 1), "م.ب | زمن القراءة:", total // 60, "د", total % 60, "ث")
