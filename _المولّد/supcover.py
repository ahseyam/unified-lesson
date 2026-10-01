# -*- coding: utf-8 -*-
"""مصفوفةُ التغطية: لكل خليةِ جدولٍ (قطاع×مجمع×مرحلة×تخصص) مَن مشرفُها.
   ⛔ الخليةُ بلا مشرفٍ تُسلَّم لفريق المتابعة البديل — وهذا الملفُّ يعدُّها."""
import sys, collections, supdb, scheddata as SD

SECT_CX = {"وطني": ["النفل", "عرقة", "المنار", "الياسمين"],
           "عالمي": ["عرقة", "المنار", "الياسمين"]}
STAGES  = {"m": ["الابتدائية", "المتوسطة", "الثانوية"],
           "f": ["رياض الأطفال", "الابتدائية", "المتوسطة", "الثانوية"]}
SPECS   = SD.SPECS                                   # ثمانيةٌ مفردة

def owners(g, sector, cx, stage, spec):
    out = []
    for r in supdb.recs(g):
        f = r["flags"]
        if f.get("nolesson"): continue
        if sector not in r["sectors"]: continue
        if cx not in r["complexes"]: continue
        if stage not in r["stages"]: continue
        if f.get("allsubj"):                         # إشرافٌ بالمرحلة لا بالمادة
            out.append((r, "مرحلة")); continue
        if spec in r["subjects"]: out.append((r, "مادة"))
    return out

def report(g):
    lbl = "بنات" if g == "f" else "بنين"
    print("\n" + "█"*74); print("█  %s" % lbl); print("█"*74)
    gaps, dupes, cells = [], [], 0
    for sector in ("وطني", "عالمي"):
        for cx in SECT_CX[sector]:
            for stage in STAGES[g]:
                for spec in SPECS:
                    cells += 1
                    o = owners(g, sector, cx, stage, spec)
                    sub = [x for x in o if x[1] == "مادة"]
                    if not o: gaps.append((sector, cx, stage, spec))
                    elif len(sub) > 1: dupes.append((sector, cx, stage, spec, [x[0]["name"] for x in sub]))
    print("\n◾ الخلايا المفحوصة: %d" % cells)
    print("◾ خلايا بلا مشرف: %d" % len(gaps))
    byspec = collections.defaultdict(list)
    for s, c, st, sp in gaps: byspec[(s, sp)].append((c, st))
    print("\n── الفجوات مجمَّعةً بالتخصص ──")
    for (s, sp), lst in sorted(byspec.items()):
        cxs = sorted({c for c, _ in lst}); sts = sorted({st for _, st in lst})
        print("  ✗ %-6s %-10s → %-34s | %s  (%d خلية)"
              % (s, sp, " · ".join(cxs), " · ".join(sts), len(lst)))
    if dupes:
        print("\n── تخصصٌ له أكثرُ من مشرفٍ في الخلية نفسها ──")
        seen = set()
        for s, c, st, sp, ns in dupes:
            k = (s, sp, tuple(ns))
            if k in seen: continue
            seen.add(k); print("  ⚠ %-6s %-10s → %s" % (s, sp, " + ".join(ns)))
    print("\n── حِملُ كل مشرفٍ (عددُ خلايا تخصصه) ──")
    load = collections.Counter()
    for sector in ("وطني", "عالمي"):
        for cx in SECT_CX[sector]:
            for stage in STAGES[g]:
                for spec in SPECS:
                    for r, why in owners(g, sector, cx, stage, spec):
                        load[(r["name"], r["emp"])] += 1
    for r in supdb.recs(g):
        k = (r["name"], r["emp"]); n = load.get(k, 0)
        tag = "—" if r["flags"].get("nolesson") else ("بالمرحلة" if r["flags"].get("allsubj")
              else " · ".join(r["subjects"]))
        print("  %-32s %-6s %4d خلية   %s" % (r["name"][:32], r["emp"], n, tag))
    return gaps

for g in ("f", "m"): report(g)
