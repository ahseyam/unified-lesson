# -*- coding: utf-8 -*-
"""مولّد الصفحة الرقمية للحصة الموحَّدة — ملفٌّ واحد يعمل بالفتح المباشر بلا خادم.

صفحتان في ملفٍ واحد:
  · صفحة المعلمة/المعلم: التحضير بترتيب مجالات الاستمارة، لكل خانة تلميحٌ يُشرح ورمز مؤشرها،
    وحارس اكتمالٍ يمنع الإصدار الناقص، ثم «إصدار التحضير» ← طباعة + رابطٌ للزائر.
  · صفحة الزائر (تُفتح بالرابط): التحضير للقراءة + استمارة الملاحظة (٥٠ مؤشراً · ٢٠٠)
    + بطاقة تشخيص الإستراتيجية (١٠ مؤشرات · ١٠٠) + بطاقة الجسر، بحسابٍ آلي، ثم طباعة وإرسال واتساب.

⚠️ المحتوى يُقرأ من مصادر المطبوع نفسها (zcontent · scontent) فلا يُكتب مرّتين ولا يفترقان.
الاستعمال: CLS_GENDER=m|f python3 webbuild.py <الملف.html>
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zcontent as Z
import scontent as S

GENDER = os.environ.get("CLS_GENDER", "m")
F = GENDER == "f"


from femjs import fem_scripts                        # noqa: E402


def g(m, f):
    return f if F else m


def fem(t):
    """تأنيث نصوص المحتوى المشترك بمعجم المطبوع نفسه.
    ⛔ ومعه طبقةُ الأفعال `lfem`: الاسم وحده لا يكفي، فالفعل يُؤنَّث مع فاعله."""
    if not F:
        return t
    from gender import feminize
    from lfem import lfem
    return feminize(lfem(t))


AR = "٠١٢٣٤٥٦٧٨٩"
def ar(n):
    return "".join(AR[int(d)] for d in str(n))


from prepdef import (HINTS, INFO, TICKS, STAGES, MODES, TIMEMAP_K, TIME_KEYS,
                     TIME_SUM, TIME_LEGACY, TIME_MAIN, TIME_DIFF,
                     TIME_DIFF_TITLE, SECTIONS, row)

# ═════════════ بيانات الزائر ═════════════
DOMAINS = [{"t": fem(name), "inds": [fem(t) for t, _ in inds]} for name, inds in Z.MAJALAT]
BANK = [{"key": k, "name": fem(n), "inds": [fem(x) for x in items]} for k, n, _, items in S.BANK]
LEVELS = [("متحقق", 4), ("متحقق لحد كبير", 3), ("متحقق جزئياً", 2), ("غير متحقق", 1)]
SLEVELS = [("ممتاز", 10), ("جيد جداً", 8), ("جيد", 6), ("مقبول", 4), ("يحتاج لتحسين", 2)]

DATA = {
    "gender": GENDER,
    "school": "مدارس ابن خلدون",
    "title": "نموذج تحضير الحصة",
    "info": [{"k": k, "l": fem(l), "u": u} for k, l, u in INFO],
    "sections": [{"t": s["t"], "n": fem(s["n"]),
                  "rows": [dict(r, label=fem(r["label"]),
                                hint=fem(r["hint"]) if r.get("hint") else None,
                                note=fem(r["note"]) if r.get("note") else None,
                                items=[fem(x) for x in r["items"]] if r.get("items") else None)
                           for r in s["rows"]]} for s in SECTIONS],
    "stages": [[k, fem(n)] for k, n in STAGES],
    "modes": [[fem(x) for x in grp] for grp in MODES],
    "tlabels": {k: fem(l) for k, l in TIMEMAP_K},
    "tmain": TIME_MAIN, "tdiff": TIME_DIFF, "tdifft": fem(TIME_DIFF_TITLE),
    "tkeys": TIME_KEYS, "tsum_keys": TIME_SUM, "tlegacy": TIME_LEGACY,
    "domains": DOMAINS,
    "bank": BANK,
    "levels": [[fem(n), v] for n, v in LEVELS],
    "slevels": [[n, v] for n, v in SLEVELS],
    "convert": S.CONVERT,
    "roles": [fem("مدير المدرسة"), fem("الوكيل التعليمي"), fem("المشرف المختص"),
              fem("المعلم الزائر")],
    "golden": fem(HINTS["golden"]),
    "tulab": [fem(x) for x in Z.TULAB],
    "athar": [fem(x if isinstance(x, str) else x[0]) for x in Z.ATHAR],
}

HTML = r"""<!doctype html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--navy:#355E91;--teal:#2F7F95;--tealbg:#E2F0F3;--red:#C00000;--head:#E9EEF6;
      --line:#C9D2DE;--zebra:#F6F8FB;--ink:#1A1A1A;--grey:#7F7F7F;--ans:#1F4E79;--bg:#F2F5F9}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
     font-family:"Sakkal Majalla","Traditional Arabic","Geeza Pro","Segoe UI",Tahoma,sans-serif;
     font-size:17px;line-height:1.7}
.band{background:linear-gradient(90deg,var(--navy),var(--teal));color:#fff;padding:14px 18px;
      display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
.band h1{margin:0;font-size:22px;font-weight:700}
.band .sub{opacity:.9;font-size:15px}
.wrap{max-width:1100px;margin:0 auto;padding:16px}
.card{background:#fff;border:1px solid var(--line);border-radius:10px;margin:0 0 14px;overflow:hidden}
.card>h2{margin:0;background:var(--navy);color:#fff;font-size:16px;padding:8px 14px;font-weight:700}
.card>h2 small{opacity:.85;font-weight:400;font-size:14px}
.row{display:grid;grid-template-columns:170px 1fr;border-top:1px solid var(--line)}
.row:first-of-type{border-top:0}
.lab{background:var(--head);color:var(--navy);font-weight:700;padding:8px 10px;font-size:15px;
     display:flex;flex-direction:column;gap:4px;justify-content:center}
.ind{font-size:12px;color:var(--teal);font-weight:400}
.fld{padding:8px 10px;min-width:0}
.hintbtn{border:1px solid var(--teal);background:#fff;color:var(--teal);border-radius:50%;
   width:20px;height:20px;font-size:12px;cursor:pointer;line-height:1;padding:0;align-self:flex-start}
.hint{background:var(--tealbg);border-inline-start:3px solid var(--teal);color:#14424f;
      font-size:14px;padding:6px 10px;margin:0 0 6px;border-radius:4px}
input[type=text],textarea,input[type=number]{width:100%;border:1px solid var(--line);border-radius:6px;
   padding:6px 8px;font:inherit;font-size:16px;color:var(--ans);background:#fff}
textarea{min-height:60px;resize:vertical}
input:focus,textarea:focus{outline:2px solid var(--teal);border-color:var(--teal)}
.ticks{display:flex;flex-wrap:wrap;gap:6px 14px}
.tk{display:flex;align-items:center;gap:6px;font-size:15px;cursor:pointer}
.tk input{width:17px;height:17px;accent-color:var(--teal)}
.num{display:flex;gap:6px;align-items:center;margin:3px 0}
.num b{color:var(--navy);min-width:16px}
.grid7 label.auto::after{content:" (يُحسب)";font-family:JZL,SK;font-weight:400;font-size:11px;color:#6b7a8d}
.ro.sum{text-align:center;font-family:SK;font-size:19px;font-weight:700;color:#1d3760;
 background:#EDF2F8;border-color:#2F5384}
.ro.sum.good{background:#e8f6ec;border-color:#7fc494;color:#1d6b35}
.ro.sum.bad{background:#fdeceb;border-color:#e8a9a4;color:#a52018}
.grid5{display:grid;grid-template-columns:repeat(5,1fr);gap:7px}
.grid2{display:grid;grid-template-columns:repeat(2,1fr);gap:7px;max-width:52%}
.grid5 label,.grid2 label{font-size:13px;color:var(--navy);font-weight:700;display:block;text-align:center}
.grid5 input,.grid2 input{text-align:center}
.grid2 .care label{color:var(--teal2)}
.grid2 .care input,.grid2 .care .ro{background:#E4F1F4;border-color:#b6dbe4}
.tdiff{margin:12px 0 6px;font-family:JZL,SK;font-size:14px;color:var(--teal2);font-weight:700;
 border-top:1px dashed var(--line);padding-top:10px}
.grid7{display:grid;grid-template-columns:repeat(7,1fr);gap:6px}
.grid7 label{font-size:13px;color:var(--navy);font-weight:700;display:block;text-align:center}
.grid7 input{text-align:center}
.stage{display:grid;grid-template-columns:122px 1fr 1fr 196px;gap:8px;border-top:1px solid var(--line);
       padding:8px 0}
.stage:first-child{border-top:0}
.stname{color:var(--navy);font-weight:700;font-size:14px;text-align:center}
.stname input{text-align:center;margin-top:4px}
.modes .ticks{gap:2px 10px}.modes label{font-size:13px}.modes>div{margin-bottom:3px}
.bar{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid var(--line);
     padding:8px 16px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
button.b{background:var(--navy);color:#fff;border:0;border-radius:8px;padding:9px 16px;font:inherit;
   font-size:16px;font-weight:700;cursor:pointer}
button.b.alt{background:var(--teal)}
button.b.ghost{background:#fff;color:var(--navy);border:1px solid var(--navy)}
button.b:disabled{opacity:.5;cursor:not-allowed}
.msg{padding:10px 14px;border-radius:8px;margin:10px 0;font-size:15px}
.msg.bad{background:#fdecea;border:1px solid #f5c6cb;color:#8a1c1c}
.msg.ok{background:#e8f5ea;border:1px solid #bcdfc4;color:#1d5b2a}
.msg ul{margin:6px 0 0;padding-inline-start:20px}
.miss{outline:2px solid var(--red)!important}
.sum{display:flex;gap:16px;flex-wrap:wrap;font-size:15px;color:var(--navy);font-weight:700}
.sum span{background:var(--head);border-radius:6px;padding:4px 10px}
table.ind{width:100%;border-collapse:collapse;font-size:15px}
table.ind th{background:var(--head);color:var(--navy);font-size:14px;padding:6px;border:1px solid var(--line)}
table.ind td{border:1px solid var(--line);padding:5px 7px;vertical-align:middle}
table.ind tr:nth-child(even) td{background:var(--zebra)}
table.ind td.c{text-align:center;width:52px}
.dh{background:var(--navy);color:#fff;font-weight:700;padding:6px 10px;font-size:15px;
    display:flex;justify-content:space-between}
.score{position:sticky;bottom:0;background:#fff;border-top:2px solid var(--navy);padding:10px 16px;
       display:flex;gap:14px;flex-wrap:wrap;align-items:center;font-weight:700;color:var(--navy);z-index:6}
.score .big{font-size:20px;color:var(--red)}
.ro{background:var(--zebra);border:1px solid var(--line);border-radius:6px;padding:6px 8px;
    color:var(--ans);min-height:32px;white-space:pre-wrap}
.note{color:var(--grey);font-size:14px;margin:0 0 4px}
.foot{color:var(--grey);font-size:13px;text-align:center;padding:14px}
@media(max-width:760px){.row{grid-template-columns:1fr}.lab{flex-direction:row;align-items:center;gap:8px}
  .stage{grid-template-columns:1fr}.grid7{grid-template-columns:repeat(2,1fr)}}
@media print{
  body{background:#fff;font-size:12px}.bar,.score,.noprint{display:none!important}
  .wrap{max-width:none;padding:0}.card{break-inside:avoid;border-radius:0;margin:0 0 6px}
  .hint{display:none}@page{size:A4;margin:10mm}
  input,textarea,.ro{border-color:#999;color:#1F4E79}
}
</style></head><body>
<div class="band"><div><h1 id="ttl">__TITLE__</h1><div class="sub" id="sub">__SCHOOL__</div></div>
  <div class="sub noprint" id="modeTag"></div></div>
<div class="bar noprint" id="bar"></div>
<div class="wrap" id="app"></div>
<div class="foot noprint">__SCHOOL__ · نسخةٌ تجريبية للمراجعة — تعمل بالفتح المباشر بلا خادم</div>
<script>
const D = __DATA__;
const $ = (s,r)=> (r||document).querySelector(s);
const el = (t,c,x)=>{const e=document.createElement(t); if(c)e.className=c; if(x!=null)e.textContent=x; return e;};
const KEY = "ik_prep_v1";
const API = "ik_api_v1";                          /* رابط خادم Apps Script — اختياري */
function api(){ try{ return localStorage.getItem(API)||""; }catch(e){ return ""; } }
/* ⚠️ text/plain يتجنّب طلب preflight الذي يرفضه Apps Script */
function post(kind, data, id){
  return fetch(api(), {method:"POST", headers:{"Content-Type":"text/plain;charset=utf-8"},
    body: JSON.stringify({kind:kind, data:data, id:id||null})}).then(r=>r.json());
}
function get(kind, id){
  return fetch(api()+"?kind="+kind+"&id="+encodeURIComponent(id)).then(r=>r.json());
}
let S = {};                                  // حالة التحضير
let V = {};                                  // حالة الزيارة

/* ───────── تخزينٌ محلي: مسوّدةٌ لا تضيع ───────── */
function save(){ try{ localStorage.setItem(KEY, JSON.stringify(S)); }catch(e){} }
function migrateTime(){
  let n=0;
  (D.tlegacy||[]).forEach((k,j)=>{ if(S["t_"+j]!=null && S["t_"+j]!==""){ S["tk_"+k]=S["t_"+j]; n++; }
                                   delete S["t_"+j]; });
  return n;
}
function load(){ try{ S = JSON.parse(localStorage.getItem(KEY)||"{}"); }catch(e){ S={}; } migrateTime(); }

/* ───────── ترميز الرابط: عربيةٌ آمنة في base64 ───────── */
function enc(o){ return btoa(unescape(encodeURIComponent(JSON.stringify(o))))
   .replace(/\+/g,"-").replace(/\//g,"_").replace(/=+$/,""); }   /* base64url: يسلم في الرابط */
function dec(s){ try{
   s = s.replace(/-/g,"+").replace(/_/g,"/");
   while(s.length % 4) s += "=";                                    /* ⚠️ atob يرفض الناقص الحشو */
   return JSON.parse(decodeURIComponent(escape(atob(s))));
 }catch(e){ console.error("تعذّر فكّ الرابط", e); return null; } }

/* ───────── أدوات الحقول ───────── */
function bind(inp, path){
  inp.value = (S[path]!=null? S[path] : "");
  inp.addEventListener("input", ()=>{ S[path]=inp.value; save(); refresh(); });
}
function txt(path, ph){ const i=el("input"); i.type="text"; if(ph)i.placeholder=ph; bind(i,path); return i; }
function area(path, ph){ const t=el("textarea"); if(ph)t.placeholder=ph; bind(t,path); return t; }
function ticks(path, items){
  const w=el("div","ticks");
  items.forEach((it,i)=>{
    const l=el("label","tk"), c=el("input"); c.type="checkbox";
    const k=path+"#"+i; c.checked=!!S[k];
    c.addEventListener("change",()=>{ S[k]=c.checked; save(); refresh(); });
    l.appendChild(c); l.appendChild(el("span",null,it)); w.appendChild(l);
  });
  return w;
}
function hasTick(path,n){ for(let i=0;i<n;i++) if(S[path+"#"+i]) return true; return false; }

/* ───────── صفحة التحضير ───────── */
function renderPrep(root, readonly){
  // بيانات الحصة
  const c0=el("div","card"); const h0=el("h2"); h0.textContent="بيانات الحصة"; c0.appendChild(h0);
  const g=el("div"); g.style.cssText="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:8px;padding:10px";
  D.info.forEach(f=>{
    const b=el("div"); const l=el("div","ind"); l.textContent=f.l+(f.u?" ("+f.u+")":"");
    l.style.cssText="color:var(--navy);font-weight:700;font-size:14px";
    b.appendChild(l);
    if(readonly){ const d=el("div","ro",S["i_"+f.k]||"—"); b.appendChild(d); }
    else b.appendChild(txt("i_"+f.k));
    if(f.k=="pct"){ const hb=hintRow(D.hints_pct); if(hb) b.appendChild(hb); }
    g.appendChild(b);
  });
  c0.appendChild(g); root.appendChild(c0);

  D.sections.forEach((sec,si)=>{
    const c=el("div","card"); const h=el("h2");
    h.textContent=sec.t+"  ·  "; const sm=el("small",null,sec.n); h.appendChild(sm); c.appendChild(h);
    sec.rows.forEach(r=>{
      const rw=el("div","row"), lb=el("div","lab"), fl=el("div","fld");
      const t=el("div"); t.textContent=r.label; lb.appendChild(t);
      if(r.ind) lb.appendChild(el("div","ind","يغذّي "+r.ind));
      if(r.hint && !readonly){
        const hb=el("button","hintbtn noprint","؟"); hb.title="ما المطلوب في هذه الخانة؟";
        hb.addEventListener("click",()=>{ const x=$(".hint",fl); x.style.display = x.style.display=="none"?"":"none"; });
        lb.appendChild(hb);
      }
      if(r.hint && !readonly){ const hd=el("div","hint",r.hint); hd.style.display="none"; fl.appendChild(hd); }
      if(r.note) fl.appendChild(el("div","note",r.note+":"));
      fl.appendChild(field(r, readonly));
      rw.appendChild(lb); rw.appendChild(fl); c.appendChild(rw);
    });
    root.appendChild(c);
  });
}
function hintRow(){ return null; }

function field(r, ro){
  const P="f_"+r.k;
  if(r.t=="line")  return ro? el("div","ro",S[P]||"—") : txt(P);
  if(r.t=="area")  return ro? el("div","ro",S[P]||"—") : area(P);
  if(r.t=="lines"){
    const w=el("div");
    for(let i=1;i<=r.n;i++){
      const ln=el("div","num"); ln.appendChild(el("b",null,String(i)+"."));
      ln.appendChild(ro? el("div","ro",S[P+"_"+i]||"—") : txt(P+"_"+i));
      w.appendChild(ln);
    }
    return w;
  }
  if(r.t=="select"){
    if(ro) return el("div","ro",S[P]||"—");
    const sl=el("select");
    sl.style.cssText="width:100%;padding:7px;font:inherit;font-size:16px;color:var(--ans);"+
                     "border:1px solid var(--line);border-radius:6px;background:#fff";
    const o0=el("option",null,"— اختر —"); o0.value=""; sl.appendChild(o0);
    r.items.forEach(x=>{ const o=el("option",null,x); o.value=x; sl.appendChild(o); });
    sl.value=S[P]||"";
    sl.addEventListener("change",()=>{ S[P]=sl.value; save(); refresh(); });
    return sl;
  }
  if(r.t=="ticks" || r.t=="ticks_note"){
    const w=el("div");
    if(ro){ const picked=r.items.filter((_,i)=>S[P+"#"+i]); w.appendChild(el("div","ro",picked.length?picked.join("  ·  "):"—")); }
    else w.appendChild(ticks(P,r.items));
    if(r.t=="ticks_note"){ const n=el("div"); n.style.marginTop="6px";
      n.appendChild(ro? el("div","ro",S[P+"_note"]||"—") : txt(P+"_note")); w.appendChild(n); }
    return w;
  }
  if(r.t=="time"){
    /* ⛔ مجموعتان كالمطبوع: الأربعُ ومجموعُها، ثم زمنا التمايز داخل التنفيذ */
    const w=el("div"), g1=el("div","grid5");
    D.tmain.forEach(k=>{
      const lb=D.tlabels[k], b=el("div");
      b.appendChild(el("label", k==="total"?"auto":null, lb));
      if(k==="total"){ const d=el("div","ro sum"); d.id="tsumcell";
        d.textContent=String(sumTime().parts).replace(/[0-9]/g,c=>"٠١٢٣٤٥٦٧٨٩"[+c]);
        b.appendChild(d); }
      else b.appendChild(ro? el("div","ro",S["tk_"+k]||"—") : txt("tk_"+k));
      g1.appendChild(b);
    });
    w.appendChild(g1);
    const hd=el("div","tdiff"); hd.textContent=D.tdifft+" — داخلَه لا يُضافان إليه:";
    w.appendChild(hd);
    const g2=el("div","grid2");
    D.tdiff.forEach(k=>{
      const b=el("div","care"); b.appendChild(el("label",null,D.tlabels[k]));
      b.appendChild(ro? el("div","ro",S["tk_"+k]||"—") : txt("tk_"+k));
      g2.appendChild(b);
    });
    w.appendChild(g2);
    const s2=el("div","sum"); s2.id="timesum"; s2.style.marginTop="10px"; w.appendChild(s2);
    return w;
  }
  if(r.t=="stages"){
    const w=el("div");
    const hd=el("div","stage");
    ["المرحلة", D.lab_teacher, D.lab_learner, "نمط العمل وتقويمه"].forEach(x=>{
      const d=el("div","stname",x); d.style.color="var(--teal)"; hd.appendChild(d); });
    w.appendChild(hd);
    D.stages.forEach(([k,name])=>{
      const st=el("div","stage");
      const c0=el("div","stname",name);
      c0.appendChild(ro? el("div","ro",(S["st_"+k+"_time"]||"—")+" د") : txt("st_"+k+"_time","الزمن بالدقائق"));
      st.appendChild(c0);
      st.appendChild(ro? el("div","ro",S["st_"+k+"_t"]||"—") : area("st_"+k+"_t"));
      st.appendChild(ro? el("div","ro",S["st_"+k+"_l"]||"—") : area("st_"+k+"_l"));
      const m=el("div","modes");
      D.modes.forEach((grp,gi)=>{
        if(ro){ const picked=grp.filter((_,i)=>S["st_"+k+"_m"+gi+"#"+i]);
                m.appendChild(el("div",null, picked.length?picked.join(" · "):"—")); }
        else m.appendChild(ticks("st_"+k+"_m"+gi, grp));
      });
      st.appendChild(m);
      w.appendChild(st);
    });
    return w;
  }
  return el("div");
}

/* ───────── حارس الاكتمال ───────── */
function missing(){
  const out=[];
  D.info.forEach(f=>{ if(["teacher","subject","klass","topic","dur"].includes(f.k) && !S["i_"+f.k]) out.push(f.l); });
  D.sections.forEach(sec=> sec.rows.forEach(r=>{
    if(!r.req) return;
    const P="f_"+r.k;
    if(r.t=="line"||r.t=="area"||r.t=="select"){ if(!(S[P]||"").trim()) out.push(r.label); }
    else if(r.t=="lines"){ if(!(S[P+"_1"]||"").trim()) out.push(r.label); }
    else if(r.t=="ticks"||r.t=="ticks_note"){
      if(!hasTick(P,r.items.length)) out.push(r.label);
      if(r.t=="ticks_note" && !(S[P+"_note"]||"").trim()) out.push(r.label+" (كيف؟)");
    }
    else if(r.t=="time"){ const s=sumTime(); if(!s.ok) out.push("خريطة الزمن (المجموع لا يساوي زمن الحصة)"); }
    else if(r.t=="stages"){
      D.stages.forEach(([k,n])=>{ if(!(S["st_"+k+"_t"]||"").trim()||!(S["st_"+k+"_l"]||"").trim()) out.push("مرحلة "+n); });
    }
  }));
  return [...new Set(out)];
}
function n2(x){ const m=String(x||"").replace(/[٠-٩]/g,d=>"٠١٢٣٤٥٦٧٨٩".indexOf(d)); const v=parseFloat(m); return isNaN(v)?0:v; }
function sumTime(){
  const parts=D.tsum_keys.reduce((a,k)=>a+n2(S["tk_"+k]),0);
  const total=n2(S["i_dur"]);
  const stages=D.stages.reduce((a,[k])=>a+n2(S["st_"+k+"_time"]),0);
  return {parts, total, stages, ok: total>0 && parts===total};
}
function refresh(){
  const tc=$("#tsumcell");
  if(tc){ const t0=sumTime();
    tc.textContent=String(t0.parts).replace(/[0-9]/g,d=>"٠١٢٣٤٥٦٧٨٩"[+d]);
    tc.className="ro sum "+(t0.total? (t0.ok?"good":"bad") : ""); }
  const s=$("#timesum");
  if(s){ const t=sumTime();
    s.innerHTML="";
    s.appendChild(el("span",null,"مجموع المراحل الأربع: "+arn(t.parts)));
    s.appendChild(el("span",null,"زمن الحصة: "+(t.total? arn(t.total):"—")));
    const st=el("span",null, t.ok? "✓ متطابق" : "✗ غير متطابق");
    st.style.background = t.ok? "#e8f5ea":"#fdecea"; st.style.color = t.ok? "#1d5b2a":"#8a1c1c";
    s.appendChild(st);
  }
  const b=$("#issueBtn"); if(b){ const m=missing();
    b.textContent = m.length? ("إصدار التحضير — ينقصه "+arn(m.length)) : "إصدار التحضير ✓"; }
}

/* ───────── استمارة الزيارة ───────── */
function renderVisit(root){
  const info=el("div","card"); const h=el("h2"); h.textContent="بيانات الزيارة"; info.appendChild(h);
  const g=el("div"); g.style.cssText="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px;padding:10px";
  [["v_name","اسم الزائر/الزائرة"],["v_role","الصفة"],["v_date","تاريخ الزيارة"],["v_phone","جوال "+D.lab_teacher_short]].forEach(([k,l])=>{
    const b=el("div"); const t=el("div"); t.textContent=l; t.style.cssText="color:var(--navy);font-weight:700;font-size:14px";
    const i=el("input"); i.type="text"; i.value=V[k]||"";
    if(k=="v_phone") i.placeholder="05xxxxxxxx";
    i.addEventListener("input",()=>{V[k]=i.value;});
    if(k=="v_role"){
      const s=el("select"); s.style.cssText="width:100%;padding:6px;font:inherit;border:1px solid var(--line);border-radius:6px";
      D.roles.forEach(r=>{const o=el("option",null,r); s.appendChild(o);});
      s.addEventListener("change",()=>{V[k]=s.value;}); V[k]=V[k]||D.roles[0];
      b.appendChild(t); b.appendChild(s); g.appendChild(b); return;
    }
    b.appendChild(t); b.appendChild(i); g.appendChild(b);
  });
  info.appendChild(g); root.appendChild(info);

  D.domains.forEach((dm,di)=>{
    const c=el("div","card");
    const hh=el("div","dh"); hh.appendChild(el("span",null,"المجال "+arn(di+1)+" · "+dm.t));
    const sc=el("span"); sc.id="dsc"+di; hh.appendChild(sc); c.appendChild(hh);
    const tb=el("table","ind");
    const tr=el("tr"); ["#","المؤشر"].forEach(x=>tr.appendChild(el("th",null,x)));
    D.levels.forEach(([n,v])=>tr.appendChild(el("th",null,n+" ("+arn(v)+")")));
    tr.appendChild(el("th",null,"لا ينطبق"));
    tb.appendChild(tr);
    dm.inds.forEach((ind,ii)=>{
      const r=el("tr");
      r.appendChild(el("td","c",arn(di+1)+"·"+arn(ii+1)));
      r.appendChild(el("td",null,ind));
      const key="s_"+di+"_"+ii;
      D.levels.concat([["NA",0]]).forEach(([n,v])=>{
        const td=el("td","c"); const rb=el("input"); rb.type="radio"; rb.name=key; rb.value=(n=="NA"?"na":v);
        if(V[key]==rb.value) rb.checked=true;
        rb.addEventListener("change",()=>{ V[key]=rb.value; score(); });
        td.appendChild(rb); r.appendChild(td);
      });
      tb.appendChild(r);
    });
    c.appendChild(tb); root.appendChild(c);
  });

  // بطاقة تشخيص الإستراتيجية
  const sc=el("div","card"); const sh=el("h2"); sh.textContent="بطاقة تشخيص الإستراتيجية  ·  ١٠ مؤشرات من ١٠٠"; sc.appendChild(sh);
  const pick=el("div"); pick.style.padding="10px";
  const sel=el("select"); sel.style.cssText="padding:6px;font:inherit;border:1px solid var(--line);border-radius:6px";
  const o0=el("option",null,"— اختر الإستراتيجية —"); o0.value=""; sel.appendChild(o0);
  D.bank.forEach(b=>{const o=el("option",null,b.name); o.value=b.key; sel.appendChild(o);});
  if(!V.strat){                                   /* ⚠️ الإستراتيجية المعلنة في التحضير هي التي تُقاس */
    const dec=D.bank.find(x=>x.name===S["f_strat"]);
    if(dec) V.strat=dec.key;
  }
  sel.value=V.strat||""; sel.addEventListener("change",()=>{ V.strat=sel.value; V.sc={}; redraw(); });
  pick.appendChild(sel); sc.appendChild(pick);
  const box=el("div"); box.id="stratbox"; sc.appendChild(box); root.appendChild(sc);
  drawStrat(box);

  // بطاقة الجسر
  const bc=el("div","card"); const bh=el("h2"); bh.textContent="بطاقة الجسر  ·  إجراءٌ واحد يُنقل إلى الحصص اليومية"; bc.appendChild(bh);
  const bb=el("div"); bb.style.padding="10px";
  const ta=el("textarea"); ta.placeholder="إجراء واحد محدد يمكن رؤيته — لا عبارة عامة";
  ta.value=V.bridge||""; ta.addEventListener("input",()=>{V.bridge=ta.value;});
  bb.appendChild(ta); bc.appendChild(bb); root.appendChild(bc);

  const nc=el("div","card"); const nh=el("h2"); nh.textContent="أبرز ما رُصد"; nc.appendChild(nh);
  const nb=el("div"); nb.style.padding="10px";
  const n1=el("textarea"); n1.placeholder="نقاط القوة"; n1.value=V.pros||"";
  n1.addEventListener("input",()=>{V.pros=n1.value;});
  const n2e=el("textarea"); n2e.placeholder="فرص التحسين"; n2e.value=V.cons||"";
  n2e.addEventListener("input",()=>{V.cons=n2e.value;});
  nb.appendChild(n1); nb.appendChild(n2e); nc.appendChild(nb); root.appendChild(nc);
}
function drawStrat(box){
  box.innerHTML="";
  const b=D.bank.find(x=>x.key==V.strat);
  if(!b){ box.appendChild(el("div","note","اختر الإستراتيجية لتظهر مؤشراتها العشرة.")); return; }
  const tb=el("table","ind");
  const tr=el("tr"); ["#","المؤشر"].forEach(x=>tr.appendChild(el("th",null,x)));
  D.slevels.forEach(([n,v])=>tr.appendChild(el("th",null,n+" ("+arn(v)+")")));
  tb.appendChild(tr);
  b.inds.forEach((ind,i)=>{
    const r=el("tr"); r.appendChild(el("td","c",arn(i+1))); r.appendChild(el("td",null,ind));
    D.slevels.forEach(([n,v])=>{
      const td=el("td","c"); const rb=el("input"); rb.type="radio"; rb.name="sx"+i; rb.value=v;
      V.sc=V.sc||{}; if(V.sc[i]==v) rb.checked=true;
      rb.addEventListener("change",()=>{ V.sc=V.sc||{}; V.sc[i]=v; score(); });
      td.appendChild(rb); r.appendChild(td);
    });
    tb.appendChild(r);
  });
  box.appendChild(tb);
  box.appendChild(el("div","note","التحويل إلى درجة م٢·٣:  "+D.convert));
}
function arn(n){ return String(n).replace(/[0-9]/g,d=>"٠١٢٣٤٥٦٧٨٩"[+d]); }

function score(){
  let got=0, max=0, na=0;
  D.domains.forEach((dm,di)=>{
    let dg=0, dm_=0;
    dm.inds.forEach((_,ii)=>{
      const v=V["s_"+di+"_"+ii];
      if(v=="na"){ na++; return; }
      dm_+=4; if(v) dg+=parseInt(v,10);
    });
    got+=dg; max+=dm_;
    const e=document.getElementById("dsc"+di);
    if(e) e.textContent = dm_? (arn(dg)+" من "+arn(dm_)) : "—";
  });
  const pct = max? Math.round(got/max*1000)/10 : 0;
  let lvl = pct>=90?"متميّز": pct>=75?"جيد جداً": pct>=50?"جيد":"يحتاج تحسيناً";
  let sgot=0; const b=D.bank.find(x=>x.key==V.strat);
  if(b){ for(let i=0;i<10;i++) sgot += (V.sc&&V.sc[i])?V.sc[i]:0; }
  const sp = b? Math.round(sgot) : 0;
  const m23 = sp>=90?4: sp>=75?3: sp>=50?2:1;
  const bar=$("#scorebar");
  if(bar){
    bar.innerHTML="";
    bar.appendChild(el("span",null,"الاستمارة: "));
    const s1=el("span","big", arn(got)+" من "+arn(max)); bar.appendChild(s1);
    bar.appendChild(el("span",null,"("+arn(pct)+"٪ · "+lvl+")"));
    bar.appendChild(el("span",null,"| لا ينطبق: "+arn(na)));
    if(b){ bar.appendChild(el("span",null,"| بطاقة الإستراتيجية: "+arn(sgot)+" من ١٠٠ ← درجة م٢·٣ = "+arn(m23))); }
  }
  return {got,max,pct,lvl,sgot,m23,na};
}
function redraw(){ drawStrat($("#stratbox")); score(); }

/* ───────── البناء ───────── */
function buildTeacher(){
  const app=$("#app"); app.innerHTML="";
  $("#modeTag").textContent="صفحة "+D.lab_teacher_short;
  const bar=$("#bar"); bar.innerHTML="";
  const b1=el("button","b","إصدار التحضير"); b1.id="issueBtn";
  b1.addEventListener("click", issue);
  const b2=el("button","b ghost","إظهار كل التلميحات");
  let shown=false;
  b2.addEventListener("click",()=>{ shown=!shown;
    document.querySelectorAll(".hint").forEach(h=>h.style.display=shown?"":"none");
    b2.textContent= shown? "إخفاء التلميحات" : "إظهار كل التلميحات"; });
  const b3=el("button","b ghost","مسح النموذج");
  b3.addEventListener("click",()=>{ if(confirm("مسح كل ما كُتب في هذا النموذج؟")){ S={}; save(); buildTeacher(); }});
  const b4=el("button","b ghost", api()? "الخادم: متصل ✓" : "ربط خادم الحفظ");
  b4.addEventListener("click",()=>{
    const cur=api();
    const v=prompt("الصق رابط خادم Apps Script (Web app URL)، أو اتركه فارغاً للعمل بلا خادم:", cur);
    if(v===null) return;
    try{ localStorage.setItem(API, v.trim()); }catch(e){}
    b4.textContent = v.trim()? "الخادم: متصل ✓" : "ربط خادم الحفظ";
  });
  bar.appendChild(b1); bar.appendChild(b2); bar.appendChild(b3); bar.appendChild(b4);
  const g=el("div","msg ok"); g.textContent=D.golden; g.className="msg ok noprint";
  app.appendChild(g);
  // شرحٌ مطويٌّ: الصفحة تشرح نفسها فلا تحتاج نشرةً منفصلة
  const dt=el("details"); dt.className="noprint";
  dt.style.cssText="background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:0 0 14px";
  const sm=el("summary","",'كيف أستعمل هذه الصفحة؟');
  sm.style.cssText="cursor:pointer;color:var(--navy);font-weight:700";
  dt.appendChild(sm);
  const ul=el("ul"); ul.style.cssText="margin:8px 0 0;padding-inline-start:22px;font-size:15px";
  [ "اكتب في الخانات كما تكتب في الورقة؛ وما تكتبه يُحفظ في جهازك تلقائياً فلا يضيع بإغلاق الصفحة.",
    "زرّ «؟» بجانب كل خانة يشرح المطلوب فيها، وتحت اسمها رمزُ المؤشر الذي تغذّيه في الاستمارة.",
    "خريطة الزمن تُنبّهك إن لم يساوِ مجموع المراحل زمنَ الحصة.",
    "«إصدار التحضير» لا يعمل قبل اكتمال كل خانة يقابلها مؤشر — وهو يعدّ لك الناقص.",
    "بعد الإصدار: اطبع التحضير، وانسخ رابط الزيارة وأرسله للزائر.",
    "الزائر يفتح الرابط فيرى تحضيرك، ويملأ الاستمارة وبطاقة الإستراتيجية، ثم يطبع التقرير ويرسله لك عبر واتساب."
  ].forEach(t=>ul.appendChild(el("li",null,t)));
  dt.appendChild(ul); app.appendChild(dt);
  const out=el("div"); out.id="issueOut"; app.appendChild(out);
  renderPrep(app,false);
  refresh();
}
function issue(){
  const out=$("#issueOut"); out.innerHTML="";
  const m=missing();
  if(m.length){
    const box=el("div","msg bad");
    box.appendChild(el("b",null,"لا يُصدَّر التحضير قبل اكتمال ما يقابله مؤشرٌ في الاستمارة — الناقص:"));
    const ul=el("ul"); m.forEach(x=>ul.appendChild(el("li",null,x))); box.appendChild(ul);
    out.appendChild(box); window.scrollTo({top:0,behavior:"smooth"}); return;
  }
  const box=el("div","msg ok");
  box.appendChild(el("b",null,"التحضير مكتمل. "));
  box.appendChild(el("span",null,"اطبعه أو احفظه PDF، وأرسل رابط الزيارة للزائر."));
  const r=el("div"); r.style.marginTop="8px";
  let link=location.origin+location.pathname+"#v="+enc(S);
  if(api()){                                        /* الخادم يعطي رابطاً قصيراً ويحفظ نسخةً للوحة */
    const inp0=el("div","note","يُحفظ في الخادم…"); r.appendChild(inp0);
    post("prep", S, S.__id).then(res=>{
      if(res && res.ok){
        S.__id=res.id; save();
        const short=location.origin+location.pathname+"#p="+res.id;
        inp0.textContent="حُفظ في الخادم · المعرّف: "+res.id;
        const i2=$("#visitlink"); if(i2){ i2.value=short; }
      } else { inp0.textContent="تعذّر الحفظ في الخادم — استُعمل الرابط الطويل."; }
    }).catch(()=>{ inp0.textContent="تعذّر الاتصال بالخادم — استُعمل الرابط الطويل."; });
  }
  const inp=el("input"); inp.type="text"; inp.id="visitlink"; inp.value=link; inp.readOnly=true;
  const b1=el("button","b alt","نسخ رابط الزيارة"); b1.style.marginTop="6px";
  b1.addEventListener("click",()=>{ inp.select(); document.execCommand("copy"); b1.textContent="نُسخ ✓"; });
  const b2=el("button","b","طباعة التحضير"); b2.style.margin="6px 8px 0 0";
  b2.addEventListener("click",()=>window.print());
  const b3=el("button","b ghost","فتح صفحة الزائر"); b3.style.margin="6px 8px 0 0";
  b3.addEventListener("click",()=>{ location.hash="v="+enc(S); location.reload(); });
  r.appendChild(inp); r.appendChild(b1); r.appendChild(b2); r.appendChild(b3);
  box.appendChild(r); out.appendChild(box);
  window.scrollTo({top:0,behavior:"smooth"});
}
function buildVisitor(data){
  S=data; const app=$("#app"); app.innerHTML="";
  $("#ttl").textContent="استمارة الملاحظة الصفية";
  $("#modeTag").textContent="صفحة الزائر";
  const bar=$("#bar"); bar.innerHTML="";
  const b1=el("button","b","طباعة تقرير الزيارة");
  b1.addEventListener("click",()=>window.print());
  const b2=el("button","b alt","إرسال عبر واتساب");
  b2.addEventListener("click",sendWA);
  const b3=el("button","b ghost","رجوع إلى التحضير");
  b3.addEventListener("click",()=>{ location.hash=""; location.reload(); });
  bar.appendChild(b1); bar.appendChild(b2); bar.appendChild(b3);

  const head=el("div","card"); const hh=el("h2"); hh.textContent="تحضير "+D.lab_teacher_short+" — للقراءة"; head.appendChild(hh);
  const inner=el("div"); head.appendChild(inner); app.appendChild(head);
  renderPrep(inner,true);
  renderVisit(app);
  const sb=el("div","score noprint"); sb.id="scorebar"; document.body.appendChild(sb);
  score();
}
function sendWA(){
  const s=score();
  if(api()){                                        /* يُسجَّل التقرير فتتغذّى لوحة المدرسة */
    post("visit", Object.assign({}, V, {score:s, prepId:V.prepId||S.__id||""}), V.__id)
      .then(res=>{ if(res&&res.ok) V.__id=res.id; }).catch(()=>{});
  }
  const ph=(V.v_phone||"").replace(/\D/g,"").replace(/^0/,"966");
  if(ph.length<11){ alert("أدخل رقم جوال صحيح في بيانات الزيارة (مثال: 05xxxxxxxx)."); return; }
  const t=[
    "تقرير زيارة صفية — "+D.school,
    (S["i_subject"]||"")+" · "+(S["i_klass"]||"")+" · "+(S["i_topic"]||""),
    "الاستمارة: "+s.got+" من "+s.max+" ("+s.pct+"٪ — "+s.lvl+")",
    (V.strat? "بطاقة الإستراتيجية: "+s.sgot+" من 100 ← درجة م٢·٣ = "+arn(s.m23) : ""),
    (V.bridge? "إجراء بطاقة الجسر: "+V.bridge : ""),
    "الزائر: "+(V.v_name||"")+" — "+(V.v_role||""),
  ].filter(Boolean).join("\n");
  window.open("https://wa.me/"+ph+"?text="+encodeURIComponent(t),"_blank");
}
D.lab_teacher = D.gender=="f" ? "ما تفعله المعلمة" : "ما يفعله المعلم";
D.lab_learner = D.gender=="f" ? "ما تفعله المتعلمة — فعلٌ يُرى" : "ما يفعله المتعلم — فعلٌ يُرى";
D.lab_teacher_short = D.gender=="f" ? "المعلمة" : "المعلم";
(function(){
  load();
  const h=location.hash||"";
  if(h.startsWith("#v=")){ const d=dec(h.slice(3)); if(d){ buildVisitor(d); return; } }
  if(h.startsWith("#p=")){                          /* معرّف قصير: يُقرأ من الخادم */
    const id=h.slice(3);
    $("#app").innerHTML="<div class='msg ok'>يُحمَّل التحضير من الخادم…</div>";
    if(!api()){ $("#app").innerHTML="<div class='msg bad'>هذا الرابط يحتاج ربط الخادم في هذا الجهاز مرّة واحدة.</div>"; return; }
    get("prep", id).then(res=>{
      if(res && res.ok){ V.prepId=id; buildVisitor(res.data); }
      else { $("#app").innerHTML="<div class='msg bad'>تعذّر جلب التحضير: "+((res&&res.error)||"")+"</div>"; }
    }).catch(e=>{ $("#app").innerHTML="<div class='msg bad'>تعذّر الاتصال بالخادم.</div>"; });
    return;
  }
  buildTeacher();
})();
</script></body></html>
"""

out = sys.argv[1] if len(sys.argv) > 1 else "prep.html"
# ⛔ نصوص الجافاسكربت تُؤنَّث قبل حقن البيانات — فالبيانات مؤنَّثةٌ أصلاً
html = fem_scripts(HTML, F)
html = (html.replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
            .replace("__TITLE__", fem(DATA["title"]))
            .replace("__SCHOOL__", DATA["school"]))
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("حُفظ:", out, "|", len(html) // 1024, "ك.ب |",
      sum(len(d["inds"]) for d in DOMAINS), "مؤشراً |", len(BANK), "إستراتيجية")
