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

# ⚠️ البطيءُ يفتح كروم على عشرات الشاشات — والسريعُ شفرةٌ وبيانات
FAST = ["printsrc", "importcheck"]
SLOW = ["supcheck", "rolescheck", "orphancheck", "focuscheck", "synccheck",
        "respcheck", "fitcheck", "i18ncheck_en", "i18ncheck_ar", "i18nsweep",
        "contrastcheck", "sweepcheck"]


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
