# -*- coding: utf-8 -*-
"""⛔ **الجوالُ يُقاس بالمسافة حتى أولِ حقلِ إدخال، لا بـ«يبدو جيداً».**

بلاغُ المستشار ٦ أكتوبر ٢٠٢٦: «مبالغٌ في حجم الخطوط فلا تظهر الصفحةُ بشكلٍ
يناسب الاستعراض… والمنصةُ تحتاج إدخالاتٍ لا تصفّحاً». وقِيس فكان:

  المتنُ ١٧بك بسطرٍ ١٫٧ **بلا أي تخفيضٍ للجوال** · العنوانُ ٢٣بك يلتفُّ سطرين
  · الترويسةُ ٢٦٢–٤٢٧ بكسلاً من ٨٤٤ · والشريطُ الجانبيُّ فوق المتن ٣٦٤
  · **فأولُ حقلِ إدخالٍ عند ١٦٤٧ بكسل** — شاشتان من التمرير قبل أن يكتب
  المعلمُ حرفاً. وفي لقطة «التحضير» على ٣٩٠ لم يظهر حقلٌ واحدٌ في الشاشة
  الأولى كلِّها.

⚠️ **ويُقاس في إطارٍ مضمَّنٍ بعرضٍ مضبوط**: لكروم بلا رأسٍ حدٌّ أدنى للنافذة
   قرابةَ ٥٠٠بك، فطلبُ ٣٩٠ يُعطي ٥٠٠ — ويُعلَن «لا عيب» على عرضٍ لم يقع.
   ويُتحقَّق من العرض المقيس في كل جولة.

⚠️ **ولا يُفحص على حالةٍ لا تقع**: الجهازُ **مرتبطٌ** كحال المعلمين، وإلّا
   قِيست لوحةُ «غير متصل بالمنظومة» (١٢٠بك) وهي لا تظهر عندهم.

⚠️ **وحدودُه مجموعُ الأثر لا كلُّ قاعدةٍ على حدة**: جُرِّب بنزع إخفاءِ اسم
   المدرسة وحدَه فمرّ — لأنه يزيد الترويسةَ عشرين بكسلاً، وهو دون حدِّه عمداً.
   فالحارسُ يمسك **رجوعَ الحالِ** لا كلَّ تعديلٍ صغير، وتشديدُ الحدِّ ليمسكه
   يُسقط كلَّ إضافةٍ مشروعة. ومجرَّبٌ على ثلاثة عيوبٍ لها وزن: نزعُ كتلة
   الجوال كلِّها · فتحُ الشرح افتراضاً · إنزالُ خطّ الإدخال دون ١٦.

⚠️ **وخطُّ حقول الإدخال لا ينزل عن ١٦بك**: ما دونه يجعل iOS يُكبّر الصفحةَ
   عند اللمس فينكسر العرض. فيُقاس صعوداً كما يُقاس المتنُ نزولاً.
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
BUILDS = [("بنين", "منصة الحصة الموحَّدة — ابن خلدون.html"),
          ("بنات", "منصة الحصة الموحَّدة — ابن خلدون (بنات).html")]
SIZES = [("٣٢٠", 320, 720), ("٣٩٠", 390, 844), ("٤٣٠", 430, 932)]
VIEWS = [("الجدول", "teacher", 'PH=1; GS=null; setctx("tab","fill"); shell();'),
         ("التحضير", "teacher", 'PH=2; CUR="m1"; GS=null; shell();'),
         ("إسناد الوكيل", "deputy", 'PH=1; GS=null; setctx("tab","assign"); shell();')]

# حدودٌ مأخوذةٌ من قياسٍ بعد العلاج، بهامشٍ يسمح بنموٍّ معقولٍ ولا يسمح بالعودة
TOP_MAX = 185        # الترويسة (كانت ٢٦٢–٤٢٧ باسمٍ واقعيّ)
FIRST_MAX = 1200     # حتى أولِ حقلِ إدخال (كان ١٦٤٧)
BODY_MIN, BODY_MAX = 15.0, 16.0
H1_MAX = 18.0        # عنوانُ الترويسة (كان ٢٣ فيلتفُّ سطرين)
INPUT_MIN = 16.0

SEED = r"""
<script>
window.__M = null;
setTimeout(function(){ try{
  localStorage.clear();
  /* جهازٌ مرتبطٌ كحال المعلمين */
  localStorage.setItem(API, "https://example.invalid/srv");
  localStorage.setItem(SKEY, "k");
  var SEC=D.sectors[0], CX=D.complexlist[0], bands=D.bands[CX]||[], b=bands[0];
  var L={id:"m1", sector:SEC, complex:CX, stage:b.stage, school:b.stage, period:b.per,
    week:D.weeks[0], day:D.days[0], spec:D.specs[0], teacher:"أ. عبدالرحمن محمد العتيبي",
    teacherNo:"30888", klass:"٥/أ", time:b.time, subject:D.specs[0],
    strategy:(D.bank[0]||{}).name, approach:D.approaches[0]};
  L.gk=[L.sector,L.complex,L.stage,L.period,L.week,L.day,L.spec].join("|");
  DB.sched=[L];
  DB.prep["m1"]={i_teacher:"أ. عبدالرحمن محمد العتيبي", i_subject:D.specs[0], i_klass:"٥/أ"};
  ME={role:"__ROLE__", name:"أ. عبدالرحمن محمد العتيبي", emp:"30888", spec:D.specs[0],
      sector:SEC, complex:CX, school:b.stage};
  localStorage.setItem(KEY+"_me", JSON.stringify(ME)); save();
  __AFTER__
  var main = document.querySelector("main") || document.body;
  var vis = function(x){ var r=x.getBoundingClientRect(); return r.width>0 && r.height>0; };
  var ins = [].slice.call(main.querySelectorAll("input:not([type=hidden]),textarea,select")).filter(vis);
  var h = function(sel){ var e=document.querySelector(sel); return e? Math.round(e.getBoundingClientRect().height):0; };
  var fs = function(e){ return e? parseFloat(getComputedStyle(e).fontSize):0; };
  var small = ins.map(fs).filter(function(v){ return v>0 && v<__INMIN__; });
  window.__M = {w: document.documentElement.clientWidth,
    top: h(".top"), inputs: ins.length,
    first: ins.length ? Math.round(ins[0].getBoundingClientRect().top + scrollY) : -1,
    body: fs(document.body), h1: fs(document.querySelector(".top h1")),
    small: small.length, smallest: small.length? Math.min.apply(null,small):0};
}catch(e){ window.__M = {err: e.message}; } }, 500);
</script>
"""
HOST = ('<!doctype html><meta charset=utf-8><style>html,body{margin:0}'
        'iframe{border:0;display:block;width:%dpx;height:%dpx}</style>'
        '<iframe id=f src="%s"></iframe><pre id=o></pre>'
        '<script>setTimeout(function(){ var w=f.contentWindow;'
        ' o.textContent = JSON.stringify(w.__M || {err:"لم يُقَس"}); }, 6500);</script>')


def run(src, w, h, role, after, tag):
    inner = PRB.probe("mob_%s.html" % tag)
    open(inner, "w", encoding="utf-8").write(
        open(src, encoding="utf-8").read()
        + SEED.replace("__ROLE__", role).replace("__AFTER__", after)
              .replace("__INMIN__", str(INPUT_MIN)))
    host = PRB.probe("mobh_%s.html" % tag)
    open(host, "w", encoding="utf-8").write(HOST % (w, h, os.path.basename(inner)))
    out = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
         "--allow-file-access-from-files", "--virtual-time-budget=12000",
         "--window-size=%d,%d" % (max(w + 40, 520), h + 20),
         "--dump-dom", "file://" + host], capture_output=True, text=True).stdout
    m = re.search(r'<pre id="o">(.*?)</pre>', out, re.S)
    try:
        return json.loads(H.unescape(m.group(1)))
    except Exception:
        return {"err": "لم يُقرأ"}


def main():
    ok = True
    measured = 0
    for gname, fn in BUILDS:
        src = os.path.join(D8, fn)
        if not os.path.exists(src):
            print("  ⛔ لم تُبنَ نسخةُ %s — ولا يُفحص ما لم يُبنَ." % gname)
            return 1
        print("  ── %s ──" % gname)
        for sname, w, h in SIZES:
            for vname, role, after in VIEWS:
                r = run(src, w, h, role, after, "%s_%d_%s" % (gname, w, vname))
                if r.get("err"):
                    print("    ⛔ %s · %-12s %s" % (sname, vname, r["err"]))
                    ok = False
                    continue
                if r["w"] != w:
                    print("    ⛔ %s · %-12s العرضُ المقيس %d لا %d — القياسُ باطل"
                          % (sname, vname, r["w"], w))
                    ok = False
                    continue
                bad = []
                if r["top"] > TOP_MAX: bad.append("ترويسة %d>%d" % (r["top"], TOP_MAX))
                if r.get("h1", 0) > H1_MAX:
                    bad.append("عنوان %.1f>%.0f" % (r["h1"], H1_MAX))
                if not (BODY_MIN <= r["body"] <= BODY_MAX):
                    bad.append("متن %.1f خارج [%.0f,%.0f]" % (r["body"], BODY_MIN, BODY_MAX))
                if r["small"]:
                    bad.append("%d حقلاً خطُّه %.1f<%.0f (iOS يُكبّر)"
                               % (r["small"], r["smallest"], INPUT_MIN))
                if r["inputs"] and r["first"] > FIRST_MAX:
                    bad.append("أولُ حقلٍ عند %d>%d" % (r["first"], FIRST_MAX))
                measured += 1
                print("    %s %s · %-12s ترويسة %3d · متن %.1f · عنوان %.1f · حقول %4d · أولُ حقلٍ %s%s"
                      % ("✓" if not bad else "⛔", sname, vname, r["top"], r["body"], r.get("h1", 0),
                         r["inputs"], r["first"] if r["inputs"] else "—",
                         ("   [" + " · ".join(bad) + "]") if bad else ""))
                ok &= not bad
    floor = len(BUILDS) * len(SIZES) * len(VIEWS)
    if measured < floor:
        print("\n  ⛔ قِيس %d من %d — فحصٌ لم يكتمل" % (measured, floor))
        ok = False
    print("\n  %s" % ("✓ الجوالُ يبدأ بالعمل لا بالتمرير" if ok else "⛔ لا يُنشر"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
