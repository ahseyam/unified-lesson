# -*- coding: utf-8 -*-
"""ملفُّ الختم — به تعرف الصفحةُ المفتوحةُ أن بناءً أحدثَ قد نُشر.

⛔ **المعلّمُ لا يُطلب منه تحديثُ صفحته**: من يُصلح عطلاً ليس له يفقد الثقةَ
   بما يُصلحه (قرارُ المستشار ٥ أكتوبر ٢٠٢٦). فالصفحةُ تسأل عن الختم كلَّ
   بضع دقائق، فإن اختلف أعادت تحميلَ نفسها — بعد حفظ ما لم يُحفظ.
⚠️ وملفٌّ صغيرٌ مستقلٌّ لا الصفحةُ نفسُها: سحبُ ١٫٥ م.ب من كل جهازٍ كلَّ
   خمس دقائق عبءٌ بلا فائدة.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D8 = os.path.join(ROOT, "٨ - النموذج الرقمي (تجربة)")
PAGES = {"ikm": "منصة الحصة الموحَّدة — ابن خلدون.html",
         "ikf": "منصة الحصة الموحَّدة — ابن خلدون (بنات).html"}
RX = re.compile(r'"build":\s*"([^"]+)"')


def main():
    out = {}
    for ns, fn in PAGES.items():
        p = os.path.join(D8, fn)
        if not os.path.exists(p):
            print("⛔ مفقود:", fn); return 1
        m = RX.search(open(p, encoding="utf-8").read(1 << 21))
        if not m:
            print("⛔ لا ختمَ في:", fn); return 1
        out[ns] = m.group(1)
    with open(os.path.join(ROOT, "ver.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print("  ✓ ver.json:", " · ".join("%s=%s" % (k, v.split("·")[-1].strip())
                                      for k, v in out.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
