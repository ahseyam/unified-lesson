# -*- coding: utf-8 -*-
"""⛔ **عشرةُ حرّاسٍ لا يناديها أحد.**

كُتب كلُّ فحصٍ منها بعد عطلٍ حقيقيٍّ وقع، ثم بقي ملفاً على القرص: لا البناءُ
يُشغّله ولا سكربتٌ يجمعه — يُنادى بالذاكرة وحين يُتذكَّر. فثلاثةٌ منها كانت
معطّلةً شهراً (استيرادٌ باسمٍ قديم) ولا أحدَ يعلم. (أمسكه وكيلُ مراجعة
الحرّاس ١ أكتوبر ٢٠٢٦)

فهذا بابُها الواحد: يبني النسختين ثم يُشغّل الحرّاسَ كلَّها، ويخرج بفشلٍ
إن سقط واحد — فلا يُنشر ما لم يمرّ.

    python3 checkall.py          # البناءُ ثم الحرّاسُ كلُّها
    python3 checkall.py --fast   # البناءُ وحرّاسُ الشفرة (بلا متصفّح)

⚠️ وما يفتح متصفّحاً بطيءٌ بطبعه (دقائق)، فيُفصل عن السريع ليُشغَّل السريعُ
   في كل تعديل، والكاملُ قبل النشر.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D8 = os.path.join(ROOT, "٨ - النموذج الرقمي (تجربة)")
BUILDS = [("m", "منصة الحصة الموحَّدة — ابن خلدون.html"),
          ("f", "منصة الحصة الموحَّدة — ابن خلدون (بنات).html")]
# ⛔ **الصفحةُ المستقلّةُ (بلا خادم) كانت تتخلَّف صامتةً**: مولّدُها `webbuild.py`
#    لا يناديه بابٌ ولا سكربت، فبقيت على القرص كما بُنيت آخرَ مرّةٍ بيدٍ —
#    وقِيس ١ أكتوبر ٢٠٢٦ أنّ المنشورَ منها **يفتقد المجالَ الثالثَ كاملاً**
#    وحقلَ «صفحات الدرس في الكتاب». و`index.html` يربطها كما يربط المنصة،
#    فيفتحها معلمٌ فيحضّر بلا ما تَرصده الاستمارةُ عليه.
#    فصارت تُبنى مع المنصة في كل جولة. (والمحتوى مشتركٌ من `zcontent`.)
WEBS = [("m", "صفحة الحصة الموحَّدة — ابن خلدون.html"),
        ("f", "صفحة الحصة الموحَّدة — ابن خلدون (بنات).html")]

# ⚠️ البطيءُ يفتح كروم على عشرات الشاشات — والسريعُ شفرةٌ وبيانات
FAST = ["printsrc", "deadkeys", "importcheck", "icocheck", "calcheck"]
SLOW = ["supcheck", "rolescheck", "orphancheck", "focuscheck", "synccheck",
        "respcheck", "overlapcheck", "fitcheck", "i18ncheck_en", "i18ncheck_ar", "i18nsweep",
        "contrastcheck", "sweepcheck",
        # ⛔ `nshcheck` كان بلا بابٍ يناديه: أربعَ عشرةَ نشرةً تُنشر ولا تُفحص.
        #    و`nshsweep` بابُه. (١ أكتوبر ٢٠٢٦)
        "nshsweep",
        # ⛔ ولقطةٌ متخلِّفةٌ تُري المستخدمَ شاشةً لا وجودَ لها: يُفحص المضمَّنُ
        #    في المستندات هنا (سريع)، والمقارنةُ بالبكسل تُطلب بيدٍ لبطئها.
        "shotsync_docx",
        # ⛔ وخادمُ المخزن يُجرَّب بدوالّ المنصة نفسِها قبل أن يُنشر — فعقدٌ
        #    يختلف عن الدمج في الصفحة يُضيع كتابةَ جهازٍ بلا خطأ. (٢ أكتوبر)
        "srvcheck", "vercheck",
        # ⛔ ورابطُ الدعوة يُقاس وهو يُفتح عبر http: حسابُ الجذر خطأً يُنتج
        #    رابطاً ميّتاً **يُوزَّع على المدارس** ولا يُكتشف إلا عندهم.
        "invitecheck", "sharecheck"]


def run(cmd, env=None, label=""):
    t0 = time.time()
    e = dict(os.environ)
    if env:
        e.update(env)
    r = subprocess.run(cmd, cwd=HERE, env=e, capture_output=True, text=True)
    dt = time.time() - t0
    ok = r.returncode == 0
    print("  %s %-16s %6.1fث" % ("✓" if ok else "⛔", label, dt))
    if not ok:
        tail = (r.stdout + r.stderr).strip().splitlines()
        for ln in tail[-14:]:
            print("       " + ln)
    return ok


def main():
    fast = "--fast" in sys.argv
    print("══ البناء ══")
    ok = True
    for g, fn in BUILDS:
        ok &= run([sys.executable, "platform.py", os.path.join(D8, fn)],
                  {"CLS_GENDER": g}, "بناء " + ("بنين" if g == "m" else "بنات"))
    for g, fn in WEBS:
        ok &= run([sys.executable, "webbuild.py", os.path.join(D8, fn)],
                  {"CLS_GENDER": g},
                  "صفحةٌ مستقلّة " + ("بنين" if g == "m" else "بنات"))
    # ⛔ **والصفحةُ الرئيسةُ تحمل حرّاسَ التسرّب** (قواعدُ ملغاةٌ في النصّ ·
    #    أسماءُ أشخاصٍ في خصائص الملفات · مسحُ الثنائيات) — وكانت لا تُنادى
    #    إلا بيد. فحارسٌ لا يناديه شيءٌ يموت صامتاً، وهذه حرّاسُه الثلاثة.
    #    وهي تمسح شجرةَ التسليم فتصف الموجودَ لا المتوقَّع. (١ أكتوبر ٢٠٢٦)
    # ⛔ **والعرضُ التعريفيُّ كان بلا بابٍ أيضاً** — يُبنى بيدٍ فيتخلَّف.
    ok &= run([sys.executable, "deck.py",
               os.path.join(ROOT, "٩ - العرض التعريفي",
                            "العرض التعريفي — نظام الحصة الموحَّدة.html")],
              None, "العرض التعريفي")
    ok &= run([sys.executable, "hub.py"], None, "الصفحة الرئيسة")
    # ⛔ **و`shortlinks.py` كان بلا بابٍ** مثلَ `webbuild`: أربعُ صفحاتٍ في
    #    الجذر (m · f · p · pf) هي ما يُوزَّع على المدارس، وتُبنى بيدٍ فقط.
    #    فبقيت ٤ أكتوبر ٢٠٢٦ بلا أيقونةٍ بعد أن حملتها كلُّ صفحةٍ سواها.
    #    و`icon.py` قبلها: منها يُكتب ملفُّ أيقونةِ الجوال في الجذر.
    ok &= run([sys.executable, "icon.py"], None, "الأيقونة")
    # ⛔ وملفُّ الختم بعد البناءَين: به تعرف الصفحةُ المفتوحةُ أنّ أحدثَ نُشر
    ok &= run([sys.executable, "verfile.py"], None, "ملفُّ الختم")
    ok &= run([sys.executable, "shortlinks.py"], None, "الروابط القصيرة")
    if not ok:
        print("\n⛔ لم يُبنَ — ولا يُفحص ما لم يُبنَ.")
        return 1
    names = FAST if fast else FAST + SLOW
    print("\n══ الحرّاس (%d) ══" % len(names))
    bad = []
    for n in names:
        if not run([sys.executable, n + ".py"], None, n):
            bad.append(n)
    print("\n" + ("══ تمّت: %d حارساً ══" % len(names) if not bad
                  else "⛔ سقط %d من %d: %s" % (len(bad), len(names), " · ".join(bad))))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
