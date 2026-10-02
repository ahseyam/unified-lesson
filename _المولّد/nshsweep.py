# -*- coding: utf-8 -*-
"""⛔ **بابُ `nshcheck` الواحد.**

كُتب `nshcheck.py` ليفحص نشرةً نشرةً بوسيطٍ من سطر الأوامر، ثم **لم يناده
شيءٌ قطّ**: لا بانيَ النشرات ولا `checkall` ولا سكربت. فأربعَ عشرةَ نشرةً
عربيةً تُبنى وتُنشر ولا تُفحص — وحارسٌ لا يناديه شيءٌ يموت صامتاً.
(أمسكه مسحُ ما بقي ١ أكتوبر ٢٠٢٦)

⚠️ ولا يُنادى من `nshbuild.py` نفسِه: الفحصُ يحتاج الـPDF المقابل، وهو
   يُصدَّر من وورد **بعد** البناء — فالبانيُ لا يملكه حين يحفظ.

⚠️ وما لا PDF له **عيبٌ يُعلَن** لا ملفٌّ يُتجاوَز: نشرةٌ بلا مخرَجها
   ليست مسلَّمة.
"""
import glob
import os
import sys

import nshcheck

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE = os.path.join(ROOT, "١٠ - أدلّة استخدام المنصة")
# ⛔ **والإنجليزيةُ كانت بلا فحصٍ أصلاً** — سبعُ نشراتٍ منشورةٍ لا يقيسها شيء،
#    والشكلُ والتسرّبُ لا لغةَ لهما. فصار لـ`nshcheck` قائمةُ شواهدَ لكلِّ لغة،
#    مقروءةً من مصدر بنائها لا مخمَّنة. (١ أكتوبر ٢٠٢٦)
DIRS = ["بنين", "بنات", "English"]
FLOOR = 21          # ⛔ أرضيّةُ شواهد: سبعُ نشراتٍ × ثلاث


def main():
    files = []
    for d in DIRS:
        p = os.path.join(BASE, d)
        if not os.path.isdir(p):
            print("  ⛔ لا مجلَّد: %s" % d)
            return 1
        files += sorted(glob.glob(os.path.join(p, "*.docx")))
    files = [f for f in files if not os.path.basename(f).startswith("~$")]
    print("  نشراتٌ على القرص: %d" % len(files))
    if len(files) < FLOOR:
        print("  ⛔ %d فقط — والأرضيّةُ %d؛ فحصٌ لم يقس ما يجب" % (len(files), FLOOR))
        return 1
    ok, done = True, 0
    for f in files:
        pdf = f[:-5] + ".pdf"
        if not os.path.exists(pdf):
            print("  ⛔ %s — بلا PDF مقابل، فليست مسلَّمة"
                  % os.path.basename(f))
            ok = False
            continue
        try:
            good = nshcheck.check(
                f, "en" if os.sep + "English" + os.sep in f else "ar")
        except Exception as e:                      # noqa: BLE001
            print("  ⛔ %s — تعذَّر الفحص: %s" % (os.path.basename(f), e))
            ok = False
            continue
        done += 1
        ok &= bool(good)
    print("\n  فُحصت %d نشرةً" % done)
    if done < FLOOR:
        print("  ⛔ المقيسُ %d والأرضيّةُ %d" % (done, FLOOR))
        ok = False
    print("  %s" % ("✓ النشراتُ الحادي والعشرون سليمة" if ok else "⛔ لا تُعتمد"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
