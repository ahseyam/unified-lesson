# -*- coding: utf-8 -*-
"""مولّدُ رزنامة التطبيق ودورانِها — من التقويم الأكاديمي الرسمي لا بيد.

⛔ **المنصةُ كانت متأخّرةً أسبوعاً كاملاً**: سمَّت ٤ أكتوبر ٢٠٢٦ «الأسبوع
   السادس» وهو **السابعُ** في التقاويم الأكاديمية الستّة (ابتدائي/متوسط/ثانوي
   × وطني/عالمي) — وكلُّها متطابقةُ التواريخ. كشفه المستشارُ ٤ أكتوبر ٢٠٢٦.

⛔ **وإجازةُ الخريف (٢٠ — ٢٨ نوفمبر) تقطع التتابع**: الجمعُ البسيطُ سبعةً
   سبعةً يضع «الرابع عشر» في ٢٢ نوفمبر — **داخلَ الإجازة**. فالتواريخُ
   منقولةٌ من التقويم حرفياً، ولا تُحسب.

⚠️ والدورانُ بالقانون المستخرَج من الإكسل الأصلي، وقد تحقّقتُ منه على
   ١٩٢ خليةً من الجدول القائم (ROT6 و SUP6) بلا مخالفةٍ واحدة:
       المجموعة = CYCLE[(إزاحةُ المجمع + رقمُ الأسبوع + رتبةُ اليوم + ٢) % ٤]

الاستعمال:  python3 calgen.py          # يطبع الفرق
            python3 calgen.py --write  # يكتبه في scheddata.py
وحارسُه `calcheck.py` في `checkall` — فيُمسَك أيُّ انحرافٍ بين المولِّد والمصدر.
"""
import datetime as dt
import json
import os
import re
import sys
import warnings

warnings.filterwarnings("ignore")
from hijri_converter import Gregorian          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "scheddata.py")

# ════ المصدرُ الرسميُّ: بدايةُ كل أسبوعٍ كما في التقويم الأكاديمي ٢٠٢٦-٢٠٢٧ ════
# IK_{Primary,Middle,Secondary}_{Natl,Intl}_Academic Calendar_2026-27.docx
# الفصلُ الأول — والستَّةُ متطابقة. وما بين الثالث عشر والرابع عشر إجازةُ خريف.
OFFICIAL = {6: "2026-09-27", 7: "2026-10-04", 8: "2026-10-11", 9: "2026-10-18",
            10: "2026-10-25", 11: "2026-11-01", 12: "2026-11-08", 13: "2026-11-15",
            14: "2026-11-29", 15: "2026-12-06", 16: "2026-12-13"}

# ⚠️ الأسابيعُ المعروضةُ في المنصة — قرارُ المستشار ٤ أكتوبر ٢٠٢٦:
#    «تبدأ بالأسبوع الثامن ولمدة ٨ أسابيع».
SHOW = list(range(8, 16))

ORD = {4: "الرابع", 5: "الخامس", 6: "السادس", 7: "السابع", 8: "الثامن",
       9: "التاسع", 10: "العاشر", 11: "الحادي عشر", 12: "الثاني عشر",
       13: "الثالث عشر", 14: "الرابع عشر", 15: "الخامس عشر", 16: "السادس عشر"}
GMON = {1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو", 6: "يونيو",
        7: "يوليو", 8: "أغسطس", 9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"}
# ⚠️ المحوّلُ يكتب «ربيع الثاني» والمدارسُ تكتب «ربيع الآخر» — وهو المعتمَد هنا.
HFIX = {"ربيع الثاني": "ربيع الآخر"}
DAYS = ["الأحد", "الاثنين", "الثلاثاء", "الخميس"]
DOFF = {"الأحد": 0, "الاثنين": 1, "الثلاثاء": 2, "الخميس": 4}

CYCLE = ["رياضيات واجتماعيات", "E", "لغتي + إسلامية", "علوم + حاسب آلي"]
OFFSETS = {"النفل": 0, "عرقه": 3, "المنار": 1, "الياسمين": 2}
SHIFT = 2                      # الإزاحةُ الثابتةُ المستخرَجة من الجدول القائم

AR = "٠١٢٣٤٥٦٧٨٩"


def arn(n):
    return "".join(AR[int(c)] if c.isdigit() else c for c in str(n))


def hij(d):
    x = Gregorian(d.year, d.month, d.day).to_hijri()
    m = x.month_name("ar")
    return arn(x.day), HFIX.get(m, m), arn(x.year)


def week(n):
    s = dt.date(*map(int, OFFICIAL[n].split("-")))
    e = s + dt.timedelta(days=4)
    hs, he = hij(s), hij(e)
    days = {}
    for d in DAYS:
        g = s + dt.timedelta(days=DOFF[d])
        hd, hm, hy = hij(g)
        days[d] = {"g": g.isoformat(), "gt": "%s %s" % (arn(g.day), GMON[g.month]),
                   "ht": "%s %s %sهـ" % (hd, hm, hy)}
    return {"w": "الأسبوع " + ORD[n], "n": n, "from": s.isoformat(), "to": e.isoformat(),
            "range": "%s %s — %s %s %sم" % (arn(s.day), GMON[s.month],
                                            arn(e.day), GMON[e.month], arn(s.year)),
            "hrange": "%s %s — %s %s %sهـ" % (hs[0], hs[1], he[0], he[1], he[2]),
            "days": days}


def build(show):
    cal = [week(n) for n in show]
    grp = lambda cx, n, d: CYCLE[(OFFSETS[cx] + n + DAYS.index(d) + SHIFT) % 4]
    rot = {cx: {c["w"]: {d: grp(cx, c["n"], d) for d in DAYS} for c in cal}
           for cx in OFFSETS}
    sup = {g: {c["w"]: {d: next(cx for cx in OFFSETS if grp(cx, c["n"], d) == g)
                        for d in DAYS}
               for c in cal} for g in CYCLE}
    return cal, rot, sup


def js(o):
    return json.dumps(o, ensure_ascii=False)


BLOCK = re.compile(r"(?ms)^START = .*?^SUP6 = .*?$")


def render(show):
    cal, rot, sup = build(show)
    return ("START = %s\nCAL = %s\n\nROT6 = %s\n\nSUP6 = %s"
            % (js(cal[0]["from"]), js(cal), js(rot), js(sup)))


def main():
    cur = open(SRC, encoding="utf-8").read()
    new = render(SHOW)
    if "--verify-current" in sys.argv:
        # ⚠️ الجدولُ القائمُ مبنيٌّ على الترقيم **المتأخّر أسبوعاً**، فيُعاد
        #    توليدُه بإزاحةِ أسبوعٍ واحدةٍ ليُقارَن حرفاً بحرف. فإن طابق،
        #    فالآلةُ (التواريخُ والهجريُّ والصياغةُ والدوران) سليمةٌ كلُّها،
        #    ولا يبقى من الفرق إلا الترقيمُ المقصودُ تصحيحُه.
        import scheddata as S
        global OFFICIAL
        OFFICIAL = {n: OFFICIAL[n + 1] for n in OFFICIAL if n + 1 in OFFICIAL}
        want = render([c["n"] for c in S.CAL])
        m = BLOCK.search(cur)
        same = m and m.group(0).strip() == want.strip()
        print("✓ المولّدُ يُعيد الجدولَ القائمَ حرفاً بحرف" if same
              else "⛔ المولّدُ يخالف القائم — لا يُكتب به شيء")
        return 0 if same else 1
    m = BLOCK.search(cur)
    if not m:
        print("⛔ لم يُعثر على كتلة START…SUP6")
        return 1
    if m.group(0).strip() == new.strip():
        print("✓ scheddata مطابقٌ للمولّد — لا تغيير")
        return 0
    if "--write" in sys.argv:
        open(SRC, "w", encoding="utf-8").write(cur[:m.start()] + new + cur[m.end():])
        print("✓ كُتب: %d أسبوعاً — %s … %s"
              % (len(SHOW), "الأسبوع " + ORD[SHOW[0]], "الأسبوع " + ORD[SHOW[-1]]))
        return 0
    print("⚠️ scheddata يخالف المولّد (شغّل --write)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
