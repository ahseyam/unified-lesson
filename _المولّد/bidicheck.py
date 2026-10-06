# -*- coding: utf-8 -*-
"""⛔ **ما يُكتب بالإنجليزية في صفحةٍ عربيةِ الاتجاه يُعرض مكسوراً.**

الحقلُ يرث اتجاهَ الصفحة (`rtl`)، فتُدفع علامةُ الترقيم **المحايدة** إلى صدر
الجملة: «‏?How does heating change the state» و«‏.Classify 12 materials». والأقسامُ
العالميةُ في ابن خلدون تُحضّر بالإنجليزية كلَّها — فكان تحضيرُها غيرَ مقروء،
عند صاحبه وعند من يقرؤه من وكيلٍ ومديرٍ ومشرف.
(بلاغُ وكيل ثانوية عرقة عالمي بنين — ٦ أكتوبر ٢٠٢٦)

والعلاجُ في موضعين مركزيّين لا في حقلٍ بعينه:
  • حقولُ الكتابة: `dir="auto"` في `fld` — كلُّ حقلٍ يتبع محتواه.
  • قيمُ القراءة: `unicode-bidi:plaintext` على `.ro` — كلُّ فقرةٍ تتبع محتواها.

⚠️ **ويُقاس بالبكسل لا بالخاصّيّة**: `getComputedStyle().direction` يبقى `rtl`
   مع `plaintext` وإن صحَّ العرض — فالقياسُ على **موضع النصّ من حدَّي صندوقه**:
   الإنجليزيُّ يلتصق باليسار والعربيُّ باليمين. والخاصّيّةُ تُقاس أيضاً في
   حقول الكتابة، فلها معنىً هناك.
"""
import html as H
import json
import os
import re
import subprocess
import sys

import probedir as PRB

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BUILDS = [("بنين", "منصة الحصة الموحَّدة — ابن خلدون.html"),
          ("بنات", "منصة الحصة الموحَّدة — ابن خلدون (بنات).html")]
EDGE = 24          # بكسلاً: ما دون هذا «ملتصقٌ بالحافة»

BOOT = r"""
<script>
setTimeout(function(){
 var R = [];
 function A(t, ok, x){ R.push(x===undefined ? [t, !!ok] : [t, !!ok, String(x)]); }
 try{
  localStorage.clear(); load();
  var SEC=D.sectors[0], CX=D.complexlist[0], bands=D.bands[CX]||[], b=bands[0];
  var L={id:"w1", sector:SEC, complex:CX, stage:b.stage, school:b.stage, period:b.per,
    week:D.weeks[0], day:D.days[0], spec:D.specs[0], teacher:"Sarah Ahmed",
    teacherNo:"30888", klass:"5/A", time:b.time, subject:"Science",
    strategy:(D.bank[0]||{}).name, approach:D.approaches[0]};
  L.gk=[L.sector,L.complex,L.stage,L.period,L.week,L.day,L.spec].join("|");
  DB.sched=[L];
  /* نصّان نعرف جوابَهما: إنجليزيٌّ بنقطةٍ في آخره، وعربيٌّ بنقطةٍ في آخره */
  var EN = "Classify 12 materials into solids, liquids and gases.";
  var AR = "صنِّف اثنتي عشرةَ مادةً إلى صلبةٍ وسائلةٍ وغازية.";
  DB.prep["w1"]={__issued:"٥ أكتوبر", i_teacher:"Sarah Ahmed", i_subject:"Science",
    i_klass:"5/A", i_topic:EN, f_q_main:EN, f_obj_know_1:EN, f_obj_skill_1:AR};
  ME={role:"__ROLE__", name:"مستخدمُ القياس", emp:"30888", spec:L.spec,
      sector:SEC, complex:CX, school:b.stage};
  localStorage.setItem(KEY+"_me", JSON.stringify(ME)); save();
  PH=__PH__; CUR="w1"; GS=null; shell();

  /* ⚠️ **ولكلِّ شاشةٍ ما تقدر على قياسه**: شاشةُ الكتابةِ حقولٌ ولا قيمَ
     قراءةٍ، وشاشةُ القراءةِ قيمٌ ولا حقول. وكان الحارسُ يسأل كلتَيهما عن
     الاثنين — فيسقط شاهدٌ لا محلَّ له، **ويمرُّ شاهدٌ على مجموعةٍ خاوية**
     فلا يقيس شيئاً. فصار السؤالُ على قدر الشاشة. */
  var MODE = "__MODE__";
  function edge(n){
    var r = document.createRange(); r.selectNodeContents(n);
    var t = r.getBoundingClientRect(), b = n.getBoundingClientRect();
    if(!t.width || !b.width) return null;
    return {l: t.left - b.left, r: b.right - t.right};
  }
  if(MODE === "write"){
    var ins = [].slice.call(document.querySelectorAll("input[type=text],textarea"));
    var enF = ins.filter(function(x){ return /^[A-Za-z]/.test((x.value||"").trim()); });
    var arF = ins.filter(function(x){ return /^[؀-ۿ]/.test((x.value||"").trim()); });
    A("حقولٌ بمحتوىً إنجليزيٍّ في الشاشة", enF.length > 0, enF.length + " حقلاً");
    A("وحقولٌ بمحتوىً عربيٍّ أيضاً", arF.length > 0, arF.length + " حقلاً");
    if(enF.length) A("والإنجليزيُّ منها يُكتب من اليسار",
      enF.every(function(x){ return getComputedStyle(x).direction === "ltr"; }),
      enF.map(function(x){ return getComputedStyle(x).direction; }).join(","));
    if(arF.length) A("والعربيُّ من اليمين",
      arF.every(function(x){ return getComputedStyle(x).direction === "rtl"; }),
      arF.map(function(x){ return getComputedStyle(x).direction; }).join(","));
  } else {
    var ros = [].slice.call(document.querySelectorAll(".ro"))
        .filter(function(n){ return (n.textContent||"").trim().length > 12; });
    var enR = ros.filter(function(n){ return /^[A-Za-z]/.test(n.textContent.trim()); });
    var arR = ros.filter(function(n){ return /^[؀-ۿ]/.test(n.textContent.trim()); });
    A("قيمُ قراءةٍ إنجليزيةٌ معروضة", enR.length > 0, enR.length + " قيمة");
    A("وقيمُ قراءةٍ عربيةٌ أيضاً", arR.length > 0, arR.length + " قيمة");
    if(enR.length){
      var bad = [];
      enR.forEach(function(n){ var e = edge(n); if(e && e.l > __EDGE__) bad.push(Math.round(e.l)); });
      A("والإنجليزيُّ منها ملتصقٌ باليسار", bad.length === 0,
        bad.length ? ("بُعدُ " + bad.join("/") + "بك عن اليسار") : enR.length + " قيمةً ≤ __EDGE__بك");
    }
    if(arR.length){
      var bad2 = [];
      arR.forEach(function(n){ var e = edge(n); if(e && e.r > __EDGE__) bad2.push(Math.round(e.r)); });
      A("والعربيُّ ملتصقٌ باليمين", bad2.length === 0,
        bad2.length ? ("بُعدُ " + bad2.join("/") + "بك عن اليمين") : arR.length + " قيمةً ≤ __EDGE__بك");
    }
  }
  localStorage.clear();
  document.title = "DONE"; window.__OUT = JSON.stringify(R);
 }catch(e){ document.title = "ERR|" + e.message; window.__OUT = JSON.stringify(R); }
}, 600);
</script>
<script>setTimeout(function(){var d=document.createElement("pre");d.id="dump";
 d.textContent=window.__OUT||"";document.body.appendChild(d);}, 7000);</script>
"""

FLOOR = 4                 # أرضيّةُ الشواهد لكلِّ شاشة


def look(src, role, ph, mode, tag):
    p = PRB.probe("bidi_%s.html" % tag)
    open(p, "w", encoding="utf-8").write(
        open(src, encoding="utf-8").read()
        + BOOT.replace("__ROLE__", role).replace("__PH__", str(ph)).replace("__MODE__", mode).replace("__EDGE__", str(EDGE)))
    out = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
         "--allow-file-access-from-files", "--virtual-time-budget=11000",
         "--window-size=1200,2400", "--dump-dom", "file://" + p],
        capture_output=True, text=True).stdout
    m = re.search(r'<pre id="dump">(.*?)</pre>', out, re.S)
    t = re.search(r"<title>(.*?)</title>", out, re.S)
    rows = json.loads(H.unescape(m.group(1))) if (m and m.group(1).strip()) else []
    err = H.unescape(t.group(1)) if t and H.unescape(t.group(1)).startswith("ERR") else ""
    return rows, err


def main():
    ok = True
    for gname, fn in BUILDS:
        src = os.path.join(ROOT, "٨ - النموذج الرقمي (تجربة)", fn)
        if not os.path.exists(src):
            print("  ⛔ لم تُبنَ نسخةُ %s — ولا يُفحص ما لم يُبنَ." % gname)
            return 1
        for role, ph, mode, what in [("teacher", 2, "write", "كتابةُ المعلم"),
                                     ("deputy", 3, "read", "قراءةُ الوكيل")]:
            rows, err = look(src, role, ph, mode, gname + "_" + role)
            print("  ── %s · %s ──" % (gname, what))
            for r in rows:
                g = bool(r[1])
                ok &= g
                print("    %s %s%s" % ("✓" if g else "⛔", r[0],
                                       ("   [" + str(r[2]) + "]") if len(r) > 2 else ""))
            if err:
                print("    ⛔", err)
                ok = False
            if len(rows) < FLOOR:
                print("    ⛔ %d شاهداً والأرضيّةُ %d — فحصٌ لم يكتمل" % (len(rows), FLOOR))
                ok = False
    print("\n  %s" % ("✓ الإنجليزيةُ تُكتب وتُقرأ كما كُتبت" if ok else "⛔ لا يُنشر"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
