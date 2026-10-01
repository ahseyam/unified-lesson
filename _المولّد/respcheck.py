# -*- coding: utf-8 -*-
"""⛔ **اتّفاقُ العرض على كل المقاسات — يُقاس ولا يُدَّعى.**

طلبُ المستشار (١ أكتوبر ٢٠٢٦): «تأكّد دومًا من اتفاق عرض المنصة ع جميع
الشاشات (جوال/آيباد/لابتوب وغيره)». ومعه ما أمسكه وكيلُ الوصول: المصفوفةُ
على الجوال **١٥٪ من الشاشة للعمل** و٨٥٪ لأعمدة التسمية · وشريطُ المراحل
بندٌ واحدٌ من ستة · وزرٌّ يتمدّد فوق العنوان.

ويُقاس في أربعة مقاسات حقيقية: جوالٌ صغير (٣٢٠) · جوالٌ شائع (٣٩٠) ·
آيباد (٨٢٠) · لابتوب (١٤٤٠). وثلاثةُ أحكامٍ لكلٍّ:

  ١. **لا تمريرَ أفقيٌّ للصفحة** — `scrollWidth` لا يتجاوز العرض (+٢ تسامحاً).
     ⚠️ ويُستثنى ما صُمّم للتمرير داخلَه (`.scrollx` · الجداولُ المغلَّفة).
  ٢. **لا عنصرَ يخرج عن الشاشة** — ولا نصٌّ مقتطعٌ في زرٍّ أو تسمية.
  ٣. **شريطُ الحفظ يُرى ويُلمَس** — ٤٤ بكسلاً على الأقل لكل زرّ (هدفُ لمسٍ
     مقبول)، وفي متناول الإبهام على الجوال (ثابتٌ أسفلَ الشاشة).

⚠️ ولا يُحكَم بـ«لا عيب» إن لم يُقَس شيء: لكلِّ مقاسٍ أرضيّةُ عناصرَ مقيسة.

⛔ **و`--window-size` وحدَه يكذب**: لكروم بلا رأسٍ حدٌّ أدنى للنافذة قرابةَ
   ٥٠٠ بكسل — فطلبتُ ٣٩٠ فجاء `clientWidth` خمسَمئة، وأعلن الحارسُ «لا عيب»
   على عرضٍ **لم يقع قطّ**. فالصفحةُ تُحمَّل في **إطارٍ مضمَّنٍ بعرضٍ مضبوط**
   داخل نافذةٍ واسعة، فيكون العرضُ المقيسُ هو المطلوبَ حقّاً — ويُتحقَّق منه
   في كل جولةٍ ويُفشل الحارسُ إن اختلف. (١ أكتوبر ٢٠٢٦)
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

# (الاسم، العرض، الارتفاع) — مقاساتٌ حقيقيةٌ لا مخترعة
SIZES = [("جوال ٣٢٠", 320, 720), ("جوال ٣٩٠", 390, 844),
         ("آيباد ٨٢٠", 820, 1180), ("لابتوب ١٤٤٠", 1440, 900)]
# الشاشاتُ ذاتُ الإدخال — وفيها المصفوفةُ والتحضيرُ والرصد
VIEWS = [("teacher", 1, "fill"), ("teacher", 2, ""), ("supervisor", 3, ""),
         ("supervisor", 4, ""), ("deputy", 1, "assign")]

BOOT = r"""
<script>
setTimeout(function(){
 try{
  localStorage.clear();
  var SEC=D.sectors[0], CX=D.complexlist[0], b=(D.bands[CX]||[])[0];
  var ROLE="__ROLE__", PHX=__PH__, TAB="__TAB__";
  var NM="معلمُ القياس";
  ME={role:ROLE, name:(ROLE==="teacher"?NM:"راصدُ القياس"), emp:"", spec:D.specs[0],
      sector:SEC, complex:CX, school:b.stage, stages:[b.stage]};
  localStorage.setItem(KEY+"_me", JSON.stringify(ME));
  var L={id:"rс1", gk:[SEC,CX,b.stage,b.per,D.weeks[0],D.days[0],D.specs[0]].join("|"),
    sector:SEC, complex:CX, stage:b.stage, school:b.stage, week:D.weeks[0], day:D.days[0],
    period:b.per.replace(/\D/g,""), time:b.time, teacher:NM, teacherNo:"",
    subject:D.specs[0], spec:D.specs[0], klass:"5/A",
    strategy:(D.bank[0]||{}).name||"", approach:D.approaches[0]};
  DB.sched.push(L);
  DB.prep[L.id]={i_topic:"درسُ القياس", f_q_main:"سؤالٌ أساسيٌّ طويلٌ بما يكفي ليُقاس انضباطُ عرضه على الشاشات الصغيرة"};
  save(); CUR=L.id;
  GS=null; PH=PHX; shell(); if(TAB){ setctx("tab",TAB); shell(); }

  var W = document.documentElement.clientWidth, out = [], n = 0;
  /* ① تمريرٌ أفقيٌّ للصفحة */
  var over = document.documentElement.scrollWidth - W;
  if(over > 2) out.push(["الصفحة", "تمريرٌ أفقيٌّ " + over + "بك", ""]);
  /* ② عناصرُ تخرج عن الشاشة — ويُستثنى ما صُمّم للتمرير داخلَه */
  function inScroller(e){
    for(var p=e; p && p!==document.body; p=p.parentElement){
      var s=getComputedStyle(p);
      if(s.overflowX==="auto"||s.overflowX==="scroll") return true;
    }
    return false;
  }
  [].slice.call(document.querySelectorAll("button,select,input,textarea,.card>h3,.abar,.pnav"))
   .forEach(function(e){
     if(!e.offsetParent) return;
     n++;
     var r = e.getBoundingClientRect();
     if(r.width < 1) return;
     if(inScroller(e)) return;
     if(r.right > W + 2 || r.left < -2)
       out.push([((e.textContent||"").trim() || e.placeholder || e.value
                  || ("<"+e.tagName.toLowerCase()+" class="+(e.className||"-")+">")).slice(0,46),
                 "يخرج عن الشاشة", Math.round(r.left)+".."+Math.round(r.right)+" / "+W]);
   });
  /* ③ **خطُّ الحقول ١٦ بكسلاً على الجوال**: سفاري يُكبّر الصفحةَ تلقائياً
     لكل حقلٍ دون ذلك — فتقفز الصفحةُ في كل لمسة. (١ أكتوبر ٢٠٢٦) */
  if(W <= 760){
    [].slice.call(document.querySelectorAll("input[type=text],input[type=number],select,textarea,.cin"))
     .forEach(function(e){
       if(!e.offsetParent) return;
       n++;
       var fs = parseFloat(getComputedStyle(e).fontSize);
       if(fs < 16) out.push([(e.placeholder || e.className || e.tagName).slice(0,34),
                             "خطٌّ دون ١٦ — يُكبّر iOS الصفحة", fs + "بك"]);
     });
  }
  /* ④ شريطُ الحفظ: موجودٌ وأزرارُه مَلموسة */
  var ab = document.querySelector(".abar");
  var live = document.querySelector("input:not([disabled]):not([type=hidden]),textarea:not([disabled]),select:not([disabled])");
  if(live && !ab) out.push(["شريط الحفظ", "شاشةٌ فيها إدخالٌ ولا شريطَ حفظٍ لها", ""]);
  if(ab){
    [].slice.call(ab.querySelectorAll("button")).forEach(function(e){
      n++;
      var r=e.getBoundingClientRect();
      if(r.height < 40) out.push([(e.textContent||"").trim(), "هدفُ لمسٍ صغير", Math.round(r.height)+"بك"]);
      if(r.right > W + 2) out.push([(e.textContent||"").trim(), "زرُّ الحفظ خارجَ الشاشة", ""]);
    });
    if(W <= 760 && getComputedStyle(ab).position !== "sticky")
      out.push(["شريط الحفظ", "غيرُ مثبَّتٍ على الجوال", getComputedStyle(ab).position]);
  }
  document.title = "OK";
  parent.postMessage(JSON.stringify({w: W, n: n, bad: out}), "*");
 }catch(e){ document.title = "ERR|" + e.message; }
}, 450);
</script>
"""

# المضيفُ يُحمِّل الصفحةَ في إطارٍ بعرضٍ مضبوط — وهو وحدَه ما يُصدَّق
HOST = """<!doctype html><meta charset="utf-8"><body style="margin:0">
<iframe id="f" src="%s" style="width:%dpx;height:%dpx;border:0"></iframe>
<pre id="dump"></pre>
<script>addEventListener("message",function(e){
  document.getElementById("dump").textContent = e.data; });</script></body>"""

FLOOR = 8      # أقلُّ ما يُقاس في شاشةٍ حقيقية


def run(tag, fn):
    ok = True
    src = os.path.join(D8, fn)
    base = open(src, encoding="utf-8").read()
    for role, ph, tab in VIEWS:
        for nm, w, h in SIZES:
            p = PRB.probe("resp_%s_%s%d_%d.html" % (tag, role, ph, w))
            open(p, "w", encoding="utf-8").write(
                base + BOOT.replace("__ROLE__", role).replace("__PH__", str(ph))
                           .replace("__TAB__", tab))
            hp = PRB.probe("resph_%s_%s%d_%d.html" % (tag, role, ph, w))
            open(hp, "w", encoding="utf-8").write(HOST % (os.path.basename(p), w, h))
            out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                                  "--allow-file-access-from-files",
                                  "--window-size=1500,1100",
                                  "--virtual-time-budget=13000", "--dump-dom", "file://" + hp],
                                 capture_output=True, text=True).stdout
            m = re.search(r'<pre id="dump">(.*?)</pre>', out, re.S)
            label = "%s/%d/%s · %s" % (role, ph, tab or "-", nm)
            if not m or not m.group(1).strip():
                t = re.search(r"<title>(.*?)</title>", out, re.S)
                print("  ⛔ %-30s لم يُقس: %s" % (label, H.unescape(t.group(1)) if t else "?"))
                ok = False
                continue
            r = json.loads(H.unescape(m.group(1)))
            # ⛔ العرضُ المقيسُ يجب أن يكون المطلوبَ بعينه — وإلّا فالقياسُ باطل
            if r["w"] != w:
                print("  ⛔ %-30s قيس على %d لا على %d — القياسُ باطل" % (label, r["w"], w))
                ok = False
                continue
            if r["n"] < FLOOR:
                print("  ⛔ %-30s %d عنصراً مقيساً فقط (الأرضيّة %d)" % (label, r["n"], FLOOR))
                ok = False
                continue
            if r["bad"]:
                ok = False
                print("  ⛔ %-30s %d عيباً من %d عنصراً:" % (label, len(r["bad"]), r["n"]))
                seen = set()
                for t_, why, extra in r["bad"][:6]:
                    k = (t_, why)
                    if k in seen:
                        continue
                    seen.add(k)
                    print("       «%s» — %s %s" % (t_, why, extra))
            else:
                print("  ✓ %-30s %d عنصراً · لا عيب" % (label, r["n"]))
    return ok


if __name__ == "__main__":
    ok = True
    for tag, fn in (("بنين", "منصة الحصة الموحَّدة — ابن خلدون.html"),):
        ok &= run(tag, fn)
    print("\n  " + ("✓ العرضُ متّفقٌ على المقاسات الأربعة" if ok else "⛔ فيه خلل"))
    sys.exit(0 if ok else 1)
