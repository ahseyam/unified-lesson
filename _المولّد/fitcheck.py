# -*- coding: utf-8 -*-
"""⛔ «صغّرتُ الخط» ليست «زال الاقتطاع»: يُقاس في المتصفّح بمقارنة العرض
   المطلوب بالعرض المتاح لكل عنصرٍ في الجدول، في اللغتين.

⚠️ والقائمةُ (select) لا يكشف scrollWidth اقتطاعَها، فيُقاس نصُّ الخيار
   المعروض بقياسٍ حقيقيٍّ على canvas بخطِّ العنصر نفسِه."""
import html as H, json, os, re, subprocess, sys
import probedir as PRB   # نسخُ الفحص خارج شجرة التسليم
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = os.path.dirname(os.path.abspath(__file__))
D8 = "/Users/ahmadseyam/Desktop/نموذج تحضير الدرس - بطاقة الملاحظة الصفية/٨ - النموذج الرقمي (تجربة)"

BOOT = r"""
<script>
setTimeout(function(){
 try{
  localStorage.clear();
  LANG = "__LANG__"; applyLang();
  var SEC=D.sectors[0], CX=D.complexlist[0], b=(D.bands[CX]||[])[0];
  var ROLE = "__ROLE__", PHX = __PH__, TAB = "__TAB__";
  ME={role:ROLE, name:"Sample", emp:"", spec:D.specs[0]};
  if(ROLE==="principal"||ROLE==="deputy"){ ME.sector=SEC; ME.complex=CX; ME.school=b.stage; }
  localStorage.setItem(KEY+"_me", JSON.stringify(ME));
  /* ⛔ **الشاشةُ الخاليةُ لا تُقاس**: كانت ثلاثُ شاشاتٍ من الخمس تُرجع
     «٠ مقيَّدُ العرض» لأن لا حصةَ ولا تحضيرَ فيها — فكلُّ ما فيها أزرارٌ
     تتمدّد بمحتواها، والقياسُ على لا شيء. فتُزرع حصةٌ وتحضيرٌ، فتفتح
     الشاشاتُ على استمارتها الحقيقية. (١ أكتوبر ٢٠٢٦) */
  var L={id:"fit1", gk:[SEC,CX,b.stage,b.per,D.weeks[0],D.days[0],D.specs[0]].join("|"),
    sector:SEC, complex:CX, stage:b.stage, school:b.stage, week:D.weeks[0], day:D.days[0],
    period:b.per.replace(/\D/g,""), time:b.time, teacher:"Sample", teacherNo:"",
    subject:D.specs[0], spec:D.specs[0], klass:"5/A",
    strategy:(D.bank[0]||{}).name||"", approach:D.approaches[0]};
  DB.sched.push(L);
  DB.prep[L.id] = {i_topic:"درسُ القياس", i_dur:"45", i_pages:"٣٢ – ٣٥",
    f_q_main:"ما العلاقةُ بين ما نراه وما نستنتجه في هذا الدرس؟",
    f_obj_know_1:"يُحدِّد المتعلمُ ثلاثةَ مفاهيمَ أساسيةٍ في الدرس"};
  /* وشاشةُ تقارير المدرسة لا تُقاس بلا رصدٍ — فيُزرع رصدٌ كامل */
  DB.obs[L.id + "|Sample"] = {__lid:L.id, __by:"Sample", role:D.evalroles[2],
    sc:{0:10,1:10,2:10,3:10,4:10,5:10,6:10,7:10,8:10,9:10}, ind:{"0_0":"4","0_1":"3"},
    res:{got:7, max:8, pct:87.5, lvl:"جيد جداً", na:0, sgot:100, m23:4, rel:83.3,
         weak:"المجال ١ · التخطيط", weakpct:87.5}};
  save(); CUR = L.id;
  GS=null; PH=PHX; shell(); if(TAB){ setctx("tab",TAB); shell(); }
  var cv = document.createElement("canvas"), cx = cv.getContext("2d");
  var bad = [], seen = 0, total = 0;
  /* ⛔ «٠ عنصراً» عمًى لا نجاح: يُقاس كلُّ عنصرِ إدخالٍ في الصفحة */
  /* ⛔ وكان فرعُ «الخليةُ تلتفُّ فلا تُقتطع» **ميتاً**: لا `td` ولا `th` في
     المحدِّد أصلاً — فشاشاتُ التقارير (وكلُّها جداول) تُرجع صفراً مقيساً
     ويُعلن النجاح. فأُضيفتا، فصار الفرعُ حيّاً والتقاريرُ تُقاس.
     (١ أكتوبر ٢٠٢٦) */
  [].slice.call(document.querySelectorAll("select,input,button,td,th,.cin,.cme"))
    .forEach(function(e){
      total++;
      var st = getComputedStyle(e);
      var avail = e.clientWidth
        - parseFloat(st.paddingLeft) - parseFloat(st.paddingRight)
        - (e.tagName === "SELECT" ? 16 : 0);   /* سهمُ القائمة */
      var txt = e.tagName === "SELECT"
        ? (e.options[e.selectedIndex] || {}).text || ""
        : (e.value || e.placeholder || e.textContent || "");
      /* الخلايا تلتفُّ على أسطرٍ فلا تُقتطع — تُستثنى إن سمح لها بالالتفاف */
      if(st.whiteSpace !== "nowrap" && (e.tagName === "TD" || e.tagName === "TH")) return;
      /* الزرُّ يتمدّد بمحتواه إلا إن قُيّد عرضُه — فيُقاس المقيَّدُ وحدَه */
      if(e.tagName === "BUTTON" && st.overflow === "visible"
         && st.maxWidth === "none" && st.width.indexOf("%") < 0) return;
      if(e.type === "checkbox" || e.type === "radio") return;
      if(!txt.trim()) return;
      cx.font = st.fontWeight + " " + st.fontSize + " " + st.fontFamily;
      var need = cx.measureText(txt).width;
      seen++;
      if(need > avail + 0.5)
        bad.push([txt.slice(0,44), Math.round(need), Math.round(avail)]);
    });
  var u = {};
  bad.forEach(function(x){ u[x[0]] = x; });
  document.title = "OK";
  window.__OUT = JSON.stringify({seen: seen, total: total,
    bad: Object.keys(u).map(function(k){return u[k];})});
 }catch(e){ document.title = "ERR|" + e.message; }
}, 400);
</script>
<script>setTimeout(function(){var d=document.createElement("pre");d.id="dump";
 d.textContent=window.__OUT||"";document.body.appendChild(d);},1400);</script>
"""

ok = True
VIEWS = [("teacher",1,"fill"),("deputy",1,"assign"),("supervisor",1,"visits"),
         ("principal",5,"school"),("teacher",2,"")]
for tag, fn in (("بنين", "منصة الحصة الموحَّدة — ابن خلدون.html"),):
  for role, ph, tab in VIEWS:
    for lang in ("ar", "en"):
        src = os.path.join(D8, fn)
        p = PRB.probe("fit_%s_%s_%s%d.html" % (tag, lang, role, ph))
        open(p, "w", encoding="utf-8").write(
            open(src, encoding="utf-8").read()
            + BOOT.replace("__LANG__", lang).replace("__ROLE__", role)
                  .replace("__PH__", str(ph)).replace("__TAB__", tab))
        out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                              "--window-size=1500,1000", "--virtual-time-budget=12000",
                              "--dump-dom", "file://" + p], capture_output=True, text=True).stdout
        m = re.search(r'<pre id="dump">(.*?)</pre>', out, re.S)
        if not m or not m.group(1).strip():
            t = re.search(r"<title>(.*?)</title>", out, re.S)
            print("  ⛔ %s/%s/%s%d لم يُقس: %s" % (tag, lang, role, ph, H.unescape(t.group(1)) if t else "?"))
            ok = False; continue
        r = json.loads(H.unescape(m.group(1)))
        # ⛔ يُفرَّق بين «لا عنصرَ مقيَّدَ العرض» و«المحدِّقُ لم يجد شيئاً»:
        #    الأولُ حالٌ سليمةٌ (أزرارٌ تتمدّد بمحتواها)، والثاني عمًى يُفشل.
        # ⛔ كان الحكمُ على `total` — وهو عددُ **المرشَّحين** لا المقيسين.
        #    فلو لم يُقَس عنصرٌ واحدٌ (تعذّر القياسُ · تغيّر المحدِّد) مرَّ
        #    الحارسُ وقد لم يفحص شيئاً. فصار على `seen`. (١ أكتوبر ٢٠٢٦)
        good = (not r["bad"]) and r["seen"] > 0
        ok &= good
        print("  %s %-12s %-3s  %4d عنصراً (%d مقيَّدُ العرض) · %d مقتطَع"
              % ("✓" if good else "⛔", role + "/" + str(ph) + "/" + (tab or "-"),
                 lang, r["total"], r["seen"], len(r["bad"])))
        for t_, need, avail in r["bad"][:8]:
            print("       «%s»  يحتاج %dبك · متاح %dبك" % (t_, need, avail))
sys.exit(0 if ok else 1)
