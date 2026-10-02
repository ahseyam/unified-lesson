# -*- coding: utf-8 -*-
"""⛔ **مفاتيحُ تُشحَن إلى الصفحة ولا يقرؤها أحد.**

الشحنةُ `D` تُبنى في `platform.py` وتُقرأ في `platform_app.js`. وكلُّ مفتاحٍ
فيها لا يقرؤه موضعٌ **وصفٌ ثانٍ لشيءٍ قائم**: يَلزمه التحديثُ ولا أحدَ
يُحدّثه، فيفترق عن الحقيقة بلا أن يصرخ شيء.

وقِيس ١ أكتوبر ٢٠٢٦ فكانت أربعةً: `sched` (عشرونَ حقلاً تصف خانةَ الحصة —
وخانتُها تُبنى في الشفرة) · `stages_sch` · `site` · `gender`. حُذفت كلُّها.

⚠️ ويُقرأ المفتاحُ بأي صيغة: `D.x` أو `D["x"]` أو `D[k]` عند التوجيه — فما
   كان يُنادى بمتغيّرٍ يُضمُّ إلى `DYN` صريحاً ويُقال لماذا.

الاستعمال: python3 deadkeys.py
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGE = os.path.join(ROOT, "٨ - النموذج الرقمي (تجربة)",
                    "منصة الحصة الموحَّدة — ابن خلدون.html")
JS = [os.path.join(HERE, "platform_app.js"), os.path.join(HERE, "planimport.js")]
# ⚠️ مفاتيحُ تُقرأ بمتغيّرٍ لا باسمٍ حرفيّ — تُستثنى بذكرِ سببها لا بالسكوت
DYN = {
    # (لا شيءَ الآن — ومن أضاف واحداً فليكتب هنا من يقرؤه وكيف)
}
FLOOR = 40          # ⛔ أرضيّةُ شواهد: الشحنةُ عشراتُ المفاتيح، فإن قلَّت لم يُقَس شيء


def keys(raw):
    """مفاتيحُ المستوى الأعلى من كائن JSON نصّاً — بعدِّ الأقواس."""
    out, d, i = [], 0, 0
    while i < len(raw):
        c = raw[i]
        if c == '"' and d == 1:
            j = raw.index('"', i + 1)
            if raw[j + 1:j + 2] == ":":
                out.append(raw[i + 1:j])
            i = j + 1
            continue
        if c in "{[":
            d += 1
        elif c in "}]":
            d -= 1
            if d == 0:
                break
        i += 1
    return out


def main():
    if not os.path.exists(PAGE):
        print("  ⛔ لا صفحةَ مبنيّةٌ — ولا يُفحص ما لم يُبنَ")
        return 1
    h = io.open(PAGE, encoding="utf-8").read()
    m = re.search(r'\bD\s*=\s*(\{"[^\n]*)', h)
    if not m:
        print("  ⛔ لم أجد شحنةَ `D` في الصفحة — والفحصُ باطل")
        return 1
    ks = sorted(set(keys(m.group(1))))
    print("  مفاتيحُ الشحنة: %d" % len(ks))
    if len(ks) < FLOOR:
        print("  ⛔ %d فقط والأرضيّةُ %d — قراءةٌ لم تكتمل" % (len(ks), FLOOR))
        return 1
    src = "\n".join(io.open(f, encoding="utf-8").read() for f in JS)
    dead = []
    for k in ks:
        if k in DYN:
            continue
        if re.search(r"D\.%s(?![\w$])" % re.escape(k), src):
            continue
        if re.search(r'D\[\s*"%s"\s*\]' % re.escape(k), src):
            continue
        dead.append(k)
    if dead:
        print("  ⛔ تُشحَن ولا تُقرأ: " + " · ".join(dead))
        print("\n  احذفها من `DATA` ومعها ما يبنيها، أو — إن كانت تُقرأ"
              "\n  بمتغيّرٍ — فأضفها إلى `DYN` في هذا الملفّ واكتب من يقرؤها.")
        return 1
    print("  ✓ كلُّ مفتاحٍ مشحونٍ له قارئ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
