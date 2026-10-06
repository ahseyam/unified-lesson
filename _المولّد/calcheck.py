# -*- coding: utf-8 -*-
"""حارسُ الرزنامة — أن يبقى جدولُ الأسابيع هو ما يقوله التقويمُ الرسمي.

⛔ **المنصةُ عاشت أسبوعاً متأخّرةً ولا أحدَ يعلم**: سمَّت ٤ أكتوبر ٢٠٢٦
   «الأسبوع السادس» وهو السابعُ في التقاويم الستّة. ولا حارسَ كان يقيس
   ذلك، لأن `scheddata.py` كُتبت بيدٍ فانفصلت عن مصدرها.

⚠️ فصار `calgen.py` يولّدها من التقويم، وهذا يقيس أنّ المكتوبَ هو المولَّد:
   التواريخُ الميلاديةُ والهجريةُ ونصوصُ المدى والدورانُ كلُّه.
⚠️ ويقيس ما لا يقيسه التطابق: أن لا أسبوعَ يقع في إجازةٍ معلومة، وأن
   خريطةَ الهجرة لا تحمل اسمَ أسبوعٍ حيّ (فتنقل حصصَه عند كل فتحة).
"""
import datetime as dt
import os
import re
import sys

import calgen
import scheddata as S

HERE = os.path.dirname(os.path.abspath(__file__))
FLOOR = 8                       # ثمانيةُ أسابيعَ — قرارُ المستشار ٤ أكتوبر ٢٠٢٦
# إجازاتُ الفصل الأول من التقويم الرسمي — لا يقع فيها أسبوعُ تطبيق
BREAKS = [("2026-11-20", "2026-11-28", "إجازةُ الخريف")]


def main():
    bad = []
    cur = open(os.path.join(HERE, "scheddata.py"), encoding="utf-8").read()
    m = calgen.BLOCK.search(cur)
    want = calgen.render(calgen.SHOW)
    if not m:
        print("⛔ لم تُقرأ كتلةُ الرزنامة من scheddata")
        return 1
    if m.group(0).strip() != want.strip():
        bad.append("الرزنامةُ المكتوبةُ تخالف ما يولّده calgen — شغّل: python3 calgen.py --write")

    n = len(S.CAL)
    print("  أسابيعُ الجدول:", n)
    if n < FLOOR:
        print("⛔ الأرضيّة %d ووُجد %d" % (FLOOR, n))
        return 1

    # ١ — كلُّ أسبوعٍ هو ما يقوله التقويمُ الرسمي
    for c in S.CAL:
        off = calgen.OFFICIAL.get(c["n"])
        if off != c["from"]:
            bad.append("الأسبوع %s يبدأ %s والرسميُّ %s" % (c["w"], c["from"], off))

    # ٢ — لا أسبوعَ داخل إجازة
    for c in S.CAL:
        s0 = dt.date.fromisoformat(c["from"]); s1 = dt.date.fromisoformat(c["to"])
        for a, b, nm in BREAKS:
            if s0 <= dt.date.fromisoformat(b) and s1 >= dt.date.fromisoformat(a):
                bad.append("%s يقع في %s" % (c["w"], nm))

    # ٣ — الدورانُ مغطٍّ: كلُّ مجمعٍ يُزار كلَّ يومٍ بمجموعةٍ واحدة، ولا تصادم
    cells = 0
    for c in S.CAL:
        for d in S.DAYS:
            seen = {}
            for cx in S.OFFSETS:
                g = S.ROT6[cx][c["w"]][d]
                cells += 1
                if S.SUP6[g][c["w"]][d] != cx:
                    bad.append("تعارضٌ: %s · %s · %s" % (c["w"], d, cx))
                seen[g] = seen.get(g, 0) + 1
            if len(seen) != 4:
                bad.append("يومٌ لا يغطّي المجموعاتِ الأربع: %s · %s" % (c["w"], d))
    print("  خلايا الدوران المفحوصة:", cells)
    if cells < FLOOR * len(S.DAYS) * 4:
        bad.append("الدورانُ لم يُقَس كاملاً")

    # ⛔ **وأوقاتُ الروضة لا تساوي أوقاتَ المراحل** (قرارُ المستشار ٦ أكتوبر
    #    ٢٠٢٦): «ولا يتقاطع مع توقيت حصص الابتدائي والمتوسط والثانوي». فلو
    #    تساوت بدايتان لم يستطع مقيّمٌ حضورَ الاثنتين، ويُسنَد إليه ما لا يُطاق
    #    وهو لا يعلم. والاختيارُ الصحيحُ اليومَ يُنسى غداً ما لم يُحرَس.
    stage_times = {b["time"] for bs in S.BANDS.values() for b in bs}
    kg_times = [t for _, t in S.KG_PERIODS]
    clash = [t for t in kg_times if t in stage_times]
    print("  أوقاتُ الروضة: %s" % " · ".join(kg_times))
    if clash:
        bad.append("وقتُ روضةٍ يساوي وقتَ مرحلةٍ أخرى: " + " · ".join(clash))
    if len(set(kg_times)) != len(kg_times):
        bad.append("وقتان متساويان داخل الروضة نفسِها")
    if not kg_times:
        bad.append("لا أوقاتَ للروضة")

    # ٤ — خريطةُ الهجرة لا تمسّ أسبوعاً حيّاً
    live = {c["w"] for c in S.CAL}
    for k, v in (S.WEEK_MIGRATION or {}).items():
        if k in live or v in live:
            bad.append("خريطةُ الهجرة تمسّ أسبوعاً حيّاً: %s ← %s" % (k, v))

    for b in bad:
        print("  ⛔", b)
    if bad:
        print("⛔ الرزنامةُ لا تُسلَّم: %d مخالفة" % len(bad))
        return 1
    print("  ✓ الرزنامةُ مطابقةٌ للتقويم الرسمي · ولا أسبوعَ في إجازة · والدورانُ تامّ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
