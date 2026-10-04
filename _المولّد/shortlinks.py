# -*- coding: utf-8 -*-
"""روابطُ قصيرةٌ للمنصة — لأن الأسماء العربية تُرمَّز فيطول الرابطُ تسعةَ أضعاف.

كلُّ حرفٍ عربيٍّ في الرابط يصير `%XX%XX%XX`، فاسمُ ملفٍ من ثلاثين حرفاً يصير
مئتين وسبعين رمزاً. فتُنشأ صفحاتٌ لاتينيةٌ قصيرةٌ في الجذر تُحوّل إلى العربية،
⚠️ **وتنقل معها ما بعد `#`** — وإلا ضاع `#srv=` وضاع الربطُ التلقائي بالمخزن.

الاستعمال: python3 shortlinks.py
"""
import os
import urllib.parse

import icon as _ICO

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D8 = "٨ - النموذج الرقمي (تجربة)"

LINKS = [
    ("m.html", D8 + "/منصة الحصة الموحَّدة — ابن خلدون.html", "منصة الحصة الموحَّدة — بنين"),
    ("f.html", D8 + "/منصة الحصة الموحَّدة — ابن خلدون (بنات).html", "منصة الحصة الموحَّدة — بنات"),
    ("p.html", D8 + "/صفحة الحصة الموحَّدة — ابن خلدون.html", "صفحة التحضير المفردة — بنين"),
    ("pf.html", D8 + "/صفحة الحصة الموحَّدة — ابن خلدون (بنات).html", "صفحة التحضير المفردة — بنات"),
    # ⛔ لا رابطَ قصيرٌ لدليل الربط — أُخرج من المنشور (٢٩ سبتمبر ٢٠٢٦)
]

TPL = """<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — مدارس ابن خلدون</title>
<link rel="canonical" href="{enc}">
{icon}
<style>body{{font-family:-apple-system,"Segoe UI",Tahoma,sans-serif;background:#f2f5f9;color:#16202e;
display:flex;align-items:center;justify-content:center;height:100vh;margin:0;text-align:center}}
a{{color:#1d5d70}}</style></head><body>
<div><p>يُفتح {title}…</p><p><a id="lnk" href="{enc}">اضغط هنا إن لم يُفتح</a></p></div>
<script>
/* ⚠️ الهاشُ لا ينتقل في التحويل التلقائي، فيُنقل بالكود — وفيه #srv= الذي
   يربط الجهازَ بالمخزن المشترك من أول فتحة. */
(function(){{
  var t = "{enc}" + (location.hash || "");
  document.getElementById("lnk").href = t;
  location.replace(t);
}})();
</script></body></html>"""

n = 0
for short, target, title in LINKS:
    path = os.path.join(ROOT, target)
    if not os.path.exists(path):
        print("— المقصد مفقود:", target)
        continue
    enc = urllib.parse.quote(target)
    with open(os.path.join(ROOT, short), "w", encoding="utf-8") as f:
        f.write(TPL.format(title=title, enc=enc, icon=_ICO.head("")))
    n += 1
    print(f"  /{short:9} ← {title}")
print("أُنشئت", n, "روابطَ قصيرة")
