# -*- coding: utf-8 -*-
"""جدوى الزيارة: المشرفُ في مجمعٍ واحدٍ يومَ واحد. فإن طلبت موادُّه مجمعينِ في
   اليوم نفسه فذاك تعارضٌ لا يُحلُّ بالجدولة وحدها — وهذا الملفُّ يعدُّه."""
import collections, supdb, scheddata as SD
CXN = {"عرقه": "عرقة"}
n = lambda c: CXN.get(c, c)
ROT = {n(cx): wk for cx, wk in SD.ROT6.items()}
PAIRS = dict(SD.PAIRS); PAIRS[SD.NAT_GROUP] = SD.NAT_SPECS
WEEKS = [c["w"] for c in SD.CAL]

def demand(r, week):
    """{ يوم → [مجمعات] } التي تطلبها موادُّ هذا المشرف في هذا الأسبوع"""
    out = collections.defaultdict(list)
    subs = set(r["subjects"])
    for cx in r["complexes"]:
        if cx not in ROT: continue
        for day, gp in ROT[cx][week].items():
            if r["flags"].get("nat"):                 # فريقُ الهوية رحلتُه ثابتة
                if SD.NAT_DAYS.get(day) == n(cx): out[day].append(cx)
                continue
            if r["flags"].get("allsubj") or (subs & set(PAIRS.get(gp, []))):
                out[day].append(cx)
    return out

for g in ("f", "m"):
    print("\n" + "█"*72); print("█  %s — جدوى الزيارات" % ("بنات" if g=="f" else "بنين")); print("█"*72)
    for r in supdb.recs(g):
        if r["flags"].get("nolesson"): continue
        tot = cl = 0; worst = []
        for w in WEEKS:
            d = demand(r, w)
            for day, cxs in d.items():
                tot += len(cxs)
                if len(cxs) > 1:
                    cl += len(cxs) - 1
                    if len(worst) < 2: worst.append("%s/%s → %s" % (w.replace("الأسبوع ",""), day, "+".join(cxs)))
        flag = "⛔ تعارض" if cl else "✅"
        print("  %s %-30s %-6s طلب:%3d زيارة · تعارض:%2d   %s"
              % (flag, r["name"][:30], r["emp"], tot, cl, " | ".join(worst)))
