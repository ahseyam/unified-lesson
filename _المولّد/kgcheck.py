# -*- coding: utf-8 -*-
"""⛔ **رياضُ الأطفال لقسم البنات وحدَه** — ويُقاس في الحزمة المبنيّة.

⛔ ولماذا؟ تبويبُ «رياض الأطفال» كان يُستدعى بلا شرط، فظهرت الورقةُ في منصة
   البنين، وسجّل فيها معلمٌ حصّتين في روضة عرقة (قِيستا في المخزن الحيّ
   ٩ أكتوبر ٢٠٢٦ وحُذفتا). والورقةُ وُضعت لقسم البنات: مشرفةٌ واحدةٌ في
   العالمي ولا مشرفةَ في الوطني.
⚠️ **والقياسُ على البيانات لا على النصّ**: اسمُ التبويب نصٌّ قد يُترجَم أو
   يُغيَّر، أمّا `kgbands` فهو مصدرُ الحكم في الصفحة — فإن خلا بناءُ البنين
   منه فلا ورقةَ ولا زرَّ ولا خلية، ولو بقي النصُّ في مكانٍ من الشفرة.
⚠️ **وبناءُ البنات يُقاس أيضاً**: حارسٌ يشترط الغيابَ وحدَه يمرُّ على بناءٍ
   حُذفت منه الروضةُ كلُّها — فيُشترط الوجودُ هناك.
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D8 = os.path.join(ROOT, "٨ - النموذج الرقمي (تجربة)")
PAGES = [("بنين", os.path.join(D8, "منصة الحصة الموحَّدة — ابن خلدون.html"), False),
         ("بنات", os.path.join(D8, "منصة الحصة الموحَّدة — ابن خلدون (بنات).html"), True)]


def kgdata(src):
    """`kgbands` كما شُحن فعلاً إلى الصفحة."""
    m = re.search(r'"kgbands"\s*:\s*(\{.*?\})\s*,\s*"kgspec"', src, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def main():
    bad, seen = 0, 0
    for nm, path, want in PAGES:
        if not os.path.exists(path):
            print("  ⛔ لا حزمةَ مبنيّةٌ لـ%s" % nm)
            return 1
        src = io.open(path, encoding="utf-8").read()
        kb = kgdata(src)
        if kb is None:
            print("  ⛔ %s: لم أجد `kgbands` في الحزمة — فالقياسُ لم يقع" % nm)
            bad += 1
            continue
        seen += 1
        got = len(kb) > 0
        if got != want:
            print("  ⛔ %s: بياناتُ الروضة %s والمنتظَر %s (%d روضةً)"
                  % (nm, "موجودة" if got else "غائبة",
                     "وجودُها" if want else "غيابُها", len(kb)))
            bad += 1
            continue
        print("  ✓ %s: %s (%d روضةً)" % (nm, "الروضةُ مشحونة" if got
                                         else "لا بياناتِ روضةٍ البتّة", len(kb)))
        # ⚠️ والتبويبُ مشروطٌ بها لا مكتوبٌ بلا شرط — وإلّا ظهر زرٌّ لورقةٍ خاوية
        if "if(hasKG()) tab(\"kg\"" not in src and 'if(hasKG())tab("kg"' not in src:
            print("  ⛔ %s: تبويبُ الروضة غيرُ مشروطٍ بوجود بياناتها" % nm)
            bad += 1
    if seen < 2:
        print("  ⛔ لم تُقَس الحزمتان معاً — فلا يُعتمد")
        return 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
