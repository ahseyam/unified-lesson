# -*- coding: utf-8 -*-
"""⛔ **نسخةُ التجربة لا تمسُّ بياناتِ المعلمين** — وتُقاس، لا تُفترض.

⛔ ولماذا؟ كلُّ بناءٍ كان يذهب إلى ٤٦٠ معلّماً مباشرةً، فأولُ من يجرّب التغييرَ
   هم المستخدمون. فصارت نسخةٌ قاعدتُها منفصلةٌ يُجرَّب فيها أولاً.
⚠️ وأخطرُ ما يمكن أن يقع: أن تُبنى نسخةُ التجربة بمعرّف القاعدة الحقيقيّ،
   فتكتب تجاربي فوق عمل المعلمين وأنا أحسبها معزولة. فيُقاس المعرّفُ بعينه.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D8 = os.path.join(ROOT, "٨ - النموذج الرقمي (تجربة)")
TRY = os.path.join(ROOT, "try.html")
LIVE = [("بنين", os.path.join(D8, "منصة الحصة الموحَّدة — ابن خلدون.html"), "ikm"),
        ("بنات", os.path.join(D8, "منصة الحصة الموحَّدة — ابن خلدون (بنات).html"), "ikf")]


def dbid(p):
    s = io.open(p, encoding="utf-8").read()
    m = re.search(r'"dbid":\s*"([a-z]+)"', s)
    return (m.group(1) if m else ""), s


def main():
    bad = 0
    if not os.path.exists(TRY):
        print("  ⛔ لم تُبنَ نسخةُ التجربة — ولا يُفحص ما لم يُبنَ.")
        return 1
    tid, ts = dbid(TRY)
    ok = tid == "ikmtry"
    print(("  ✓ " if ok else "  ⛔ ") + "قاعدةُ التجربة منفصلة   [%s]" % (tid or "لا معرّف"))
    bad += 0 if ok else 1
    ok = 'id="trybar"' in ts
    print(("  ✓ " if ok else "  ⛔ ") + "وعليها شريطٌ ثابتٌ يقول إنها تجربة")
    bad += 0 if ok else 1
    seen = {}
    for nm, p, want in LIVE:
        if not os.path.exists(p):
            print("  ⛔ لم تُبنَ نسخةُ %s" % nm); bad += 1; continue
        got, s = dbid(p)
        ok = got == want
        print(("  ✓ " if ok else "  ⛔ ") + "وقاعدةُ %s كما كانت   [%s]" % (nm, got))
        bad += 0 if ok else 1
        ok = 'id="trybar"' not in s
        print(("  ✓ " if ok else "  ⛔ ") + "ولا شريطَ تجربةٍ في نسخة %s" % nm)
        bad += 0 if ok else 1
        seen[nm] = got
    # ⚠️ أرضيّةُ الشواهد: ثلاثةُ معرّفاتٍ مختلفةٍ لا اثنان
    ids = set([tid] + list(seen.values()))
    ok = len(ids) == 3
    print(("  ✓ " if ok else "  ⛔ ") + "وثلاثةُ معرّفاتٍ لا يلتقي منها اثنان   [%s]"
          % " · ".join(sorted(ids)))
    bad += 0 if ok else 1
    print("\n  " + ("✓ التجربةُ معزولةٌ عن بيانات المعلمين"
                   if not bad else "⛔ عزلُ التجربة لا يُعتمد"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
