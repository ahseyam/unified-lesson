# -*- coding: utf-8 -*-
"""⛔ **الترجمةُ كانت «كاملةً» على ١٣٪ من الشاشات.**

`i18ncheck_en` يفحص **٢٧ شاشةً** مكتوبةً بقائمةٍ بيد، و`sweepcheck` يمسح
**٢٠٢** — فما بينهما لم يُفحص إنجليزياً قطّ. وأمر المستشار: «قم بالترجمة
الكاملة» (١ أكتوبر ٢٠٢٦).

فهذا يمسح **كلَّ شاشة** بالتعداد نفسِه الذي يستعمله `sweepcheck` (الأدوارُ
الثمانية × مراحلُ كلِّ دورٍ × تبويباتُها × حالتَي بيانات) **بالإنجليزية**،
ويُبلّغ كلَّ كلمةٍ عربيةٍ بقيت — ما خلا ما يبقى عربياً بالقرار.

⚠️ ولا يُحكَم بالنجاح إن لم تُمسح شاشاتٌ تكفي: أرضيّةُ ١٥٠ شاشة.
⚠️ وما يبقى عربياً بالقرار يُكتب هنا بالاسم لا بالصمت: أسماءُ الأشخاص
   والمجمعاتِ والمدارسِ وزرُّ «عربي» — وهي بياناتٌ لا تسميات.
"""
import html as H
import json
import os
import re
import subprocess
import sys

import probedir as PRB

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D8 = os.path.join(ROOT, "٨ - النموذج الرقمي (تجربة)")

FLOOR = 150          # أقلُّ ما يُمسح — ودونه لم يُفحص شيءٌ يُعتدّ به

BOOT = r"""
<script>
setTimeout(function(){
 var R=[];
 try{
  localStorage.clear();
  LANG="en"; try{ applyLang(); }catch(e){}
  var SEC=D.sectors[0],CX=D.complexlist[0],b=(D.bands[CX]||[])[0];
  var NM="Sample Name";
  function me(role){
    var m={role:role,name:NM,emp:"",spec:D.specs[0],sector:SEC,complex:CX,
           school:b.stage,stages:[b.stage]};
    localStorage.setItem(KEY+"_me",JSON.stringify(m));
    return m;
  }
  function seed(){
    var L={id:"sw1",gk:[SEC,CX,b.stage,b.per,D.weeks[0],D.days[0],D.specs[0]].join("|"),
      sector:SEC,complex:CX,stage:b.stage,school:b.stage,week:D.weeks[0],day:D.days[0],
      period:b.per,time:b.time,teacher:NM,teacherNo:"",subject:D.specs[0],
      spec:D.specs[0],klass:"5/A",strategy:(D.bank[0]||{}).name||"",approach:D.approaches[0]};
    DB.sched=[L]; DB.prep[L.id]={i_topic:"Sample topic"};
    DB.obs[L.id+"|"+NM]={__lid:L.id,__by:NM,role:D.evalroles[2],sc:{0:10},ind:{"0_0":"4"},
      res:{got:4,max:4,pct:100,lvl:"متميّز",na:0,sgot:10,m23:1,rel:100}};
    save(); CUR=L.id;
  }
  function look(role,ph,tab,state){
    var err=null;
    try{
      GS=null; PH=ph; shell();
      if(tab && ["fill","assign","log","visits","sup","school"].indexOf(tab)>=0){ setctx("tab",tab); shell(); }
      else if(tab){ setctx("rpt",tab); shell(); }
    }catch(e){ err=e.message; }
    var main=document.querySelector("main")||document.body;
    var txt=(main.innerText||"").replace(/\s+/g," ").trim();
    R.push([role+" · "+ph+(tab?"/"+tab:"")+" · "+state, txt, err]);
  }
  var TABS={1:["fill","visits","sup","assign","school"], 5:["school","teacher","spec","ind","active","pending"]};
  var OWNRPT={teacher:1, peer:1};
  ["teacher","peer","principal","deputy","supervisor","cxmgr","intqa","admin"].forEach(function(role){
    ME=me(role);
    var items; try{ items=navItems(); }catch(e){ items=[]; }
    items.forEach(function(it){
      var tabs=(it.id===5 && OWNRPT[role]) ? [null] : (TABS[it.id]||[null]);
      tabs.forEach(function(tb){
        ["empty","data"].forEach(function(st){
          if(st==="data") seed(); else { DB.sched=[]; DB.prep={}; DB.obs={}; save(); CUR=null; }
          look(role,it.id,tb,st);
        });
      });
    });
  });
  localStorage.clear();
  document.title="DONE"; window.__OUT=JSON.stringify(R);
 }catch(e){ document.title="ERR|"+e.message; window.__OUT=JSON.stringify(R); }
}, 500);
</script>
<script>setTimeout(function(){var d=document.createElement("pre");d.id="dump";
 d.textContent=window.__OUT||"";document.body.appendChild(d);},14000);</script>
"""


def allow_words(src):
    """ما يبقى عربياً بالقرار — بياناتٌ لا تسميات."""
    import i18ncheck_en as T          # يُعاد استعمالُ قائمته لا تُكتب ثانيةً
    h = open(src, encoding="utf-8").read()
    i = h.index("{", h.index("const D ="))
    Dd, _ = json.JSONDecoder().raw_decode(h[i:])
    allow = set()
    for v in (Dd.get("roster") or {}).values():
        allow |= {str(v.get(k) or "") for k in v}
    allow |= set(Dd.get("complexlist") or []) | set(Dd.get("bands") or {})
    for m in sum((Dd.get("models") or {}).values(), []):
        allow |= {str(m.get(k) or "") for k in m}
    for bb in sum((Dd.get("bands") or {}).values(), []):
        allow |= {str(bb.get(k) or "") for k in bb}
    for g, wk in (Dd.get("sup") or {}).items():
        for w, dd in wk.items():
            allow |= set(dd.values())
    allow |= {str(r.get("name") or "") for r in (Dd.get("sups") or [])}
    allow |= {"أ. أحمد صيام", "أ. محمود كامل", "أ. هدى المشجري", "عربي"}
    # أسماءٌ مزروعةٌ في الفحص نفسِه
    allow |= {"Sample Name", "Sample topic"}
    AR = re.compile(r"[ؠ-يٱ-ۓ]+")
    out = set()
    for a in allow:
        out |= set(AR.findall(a or ""))
    return out


def run(tag, fn):
    src = os.path.join(D8, fn)
    p = PRB.probe("i18nsweep_%s.html" % tag)
    open(p, "w", encoding="utf-8").write(open(src, encoding="utf-8").read() + BOOT)
    out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                          "--window-size=1500,1000", "--virtual-time-budget=26000",
                          "--dump-dom", "file://" + p], capture_output=True, text=True).stdout
    t = re.search(r"<title>(.*?)</title>", out, re.S)
    m = re.search(r'<pre id="dump">(.*?)</pre>', out, re.S)
    rows = json.loads(H.unescape(m.group(1))) if (m and m.group(1).strip()) else []
    ttl = H.unescape(t.group(1)) if t else "?"
    if ttl.startswith("ERR"):
        print("  ⛔ %s — %s" % (tag, ttl))
        return False
    if len(rows) < FLOOR:
        print("  ⛔ %s — %d شاشةً فقط (الأرضيّة %d). المسحُ لم يقع." % (tag, len(rows), FLOOR))
        return False
    allow = allow_words(src)
    AR = re.compile(r"[ؠ-يٱ-ۓ]+")
    bad = {}
    errs = 0
    for name, txt, err in rows:
        if err:
            errs += 1
        words = [w for w in AR.findall(txt or "") if w not in allow]
        for w in set(words):
            bad.setdefault(w, []).append(name)
    if errs:
        print("  ⚠️ %s — %d شاشةً سقطت أثناء الرسم" % (tag, errs))
    if not bad:
        print("  ✓ %s — %d شاشةً · لا كلمةَ عربيةً في الشاشة الإنجليزية" % (tag, len(rows)))
        return not errs
    print("  ⛔ %s — %d شاشةً · %d كلمةً عربيةً باقية:" % (tag, len(rows), len(bad)))
    for w, where in sorted(bad.items(), key=lambda x: -len(x[1]))[:25]:
        print("       «%s» × %d  (%s)" % (w, len(where), where[0]))
    return False


if __name__ == "__main__":
    ok = True
    for tag, fn in (("بنين", "منصة الحصة الموحَّدة — ابن خلدون.html"),
                    ("بنات", "منصة الحصة الموحَّدة — ابن خلدون (بنات).html")):
        ok &= run(tag, fn)
    print("\n  " + ("✓ الترجمةُ كاملةٌ على كل الشاشات" if ok else "⛔ بقي عربيٌّ في الشاشة الإنجليزية"))
    sys.exit(0 if ok else 1)
