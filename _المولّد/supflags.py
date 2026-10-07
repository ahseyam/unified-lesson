# -*- coding: utf-8 -*-
"""⛔ **علمٌ يُكتب في سجلّ الإشراف ولا يقرؤه شيء — مرّتين.**

① `schoolhelp`: كُتب في `supdb.py` بقرار المستشار («حيثُ لا تحضر تساعدها مديرةُ
   المدرسة والوكيلةُ التعليميةُ بذات المدرسة») ثم **لم يقرأه شيء**، فبقيت حصةُ
   الروضة العالمية محجوزةَ الرصد على مشرفةٍ قد لا تحضر. أُحيي في ١ أكتوبر ٢٠٢٦.

② `nat`: مكتوبٌ لمشرف الهوية الوطنية ومعه نصُّه («فريقُ الهوية… ثلاثُ موادَّ في
   اليوم الواحد»)، و`supclash` يقرؤه فيقول «تعارض ٠» — **وتصديرُ `DATA["sups"]`
   أسقطه**. فعاملته المنصةُ مشرفَ موادَّ يركب الدورانَ في ثلاثة مجمعات، وأعلنت
   عليه تعارضاً **كلَّ يومٍ من أيام الأسبوع**. (٧ أكتوبر ٢٠٢٦)

فالعلّةُ واحدةٌ ونمطُها واحد، ولا يمسكها حارسٌ قائم: `deadkeys` يمسك مفاتيحَ
البيانات الميتة، و`guard_js` يمسك النداءاتِ المعلّقة — ولا يسأل أحدٌ: **هل كلُّ
علمٍ في السجلّ يصل المنصةَ ويُقرأ فيها؟**

ويُقاس ثلاثةً:
  ١. كلُّ علمٍ مكتوبٍ في `supdb.py` إمّا **مصدَّرٌ** في `DATA["sups"]`، وإمّا
     **مُستهلَكٌ عند المصدر** (يُرشِّح السجلَّ فلا يصل) — ويُذكر سببُه هنا.
  ٢. وكلُّ علمٍ مصدَّرٍ **يُقرأ في شفرة المنصة** — وإلّا فهو ميتٌ كالأولين.
  ٣. والمُستهلَكُ عند المصدر لا يصل فعلاً — يُقاس على البناء لا على الدعوى.
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D8 = os.path.join(ROOT, "٨ - النموذج الرقمي (تجربة)")
BUILDS = [("بنين", "منصة الحصة الموحَّدة — ابن خلدون.html"),
          ("بنات", "منصة الحصة الموحَّدة — ابن خلدون (بنات).html")]

# أعلامٌ تُستهلَك عند المصدر فلا تُصدَّر — ولكلٍّ سببُه المكتوب
CONSUMED = {
    "nolesson": "لا حصةَ له في الجدول — يُرشَّح من السجلّ قبل التصدير، فلا يصل أصلاً",
}

# ⚠️ **أعلامٌ وصفيّةٌ لا وظيفيّة**: تُسمّي قرارَ المستشار في السجلّ، وسلوكُها
#    مُشفَّرٌ في حقولٍ **تُقرأ فعلاً** — فليست ميتةً وإن لم تُصدَّر. ولكلٍّ
#    هنا **أينَ سلوكُه**، فلا يُسكَت علمٌ بدعوى الوصف بلا بيان.
LABEL = {
    "early": "الصفوفُ الأولية — وسلوكُه في `subjects=[\"لغتي\"]` و`stages=[\"الابتدائية\"]`",
    "kg":    "مشرفةُ رياض الأطفال — وسلوكُه في `stages=ST_KG` و`allsubj` و`schoolhelp`",
}


def data_of(path):
    s = io.open(path, encoding="utf-8").read()
    i = s.index("const D = {")
    j = i + len("const D = ")
    d = 0
    for k in range(j, len(s)):
        if s[k] == "{":
            d += 1
        elif s[k] == "}":
            d -= 1
            if d == 0:
                return json.loads(s[j:k + 1]), s
    raise SystemExit("⛔ لم تُقرأ بياناتُ المنصة")


def main():
    src = io.open(os.path.join(HERE, "supdb.py"), encoding="utf-8").read()
    # الأعلامُ المكتوبةُ في السجلّ: مفاتيحُ القواميس في صفوف المشرفين
    written = set(re.findall(r'\{\s*"([a-zA-Z_]+)"\s*:', src))
    written |= set(re.findall(r',\s*"([a-zA-Z_]+)"\s*:\s*(?:True|False)', src))
    if not written:
        print("  ⛔ لم يُقرأ علمٌ واحدٌ من `supdb.py` — فحصٌ لم يَقِس شيئاً")
        return 1

    app = io.open(os.path.join(HERE, "platform_app.js"), encoding="utf-8").read()
    ok = True
    for gname, fn in BUILDS:
        path = os.path.join(D8, fn)
        if not os.path.exists(path):
            print("  ⛔ لم تُبنَ نسخةُ %s — ولا يُفحص ما لم يُبنَ." % gname)
            return 1
        D, _ = data_of(path)
        sups = D.get("sups") or []
        if not sups:
            print("  ⛔ %s: لا سجلَّ إشرافٍ في البناء" % gname)
            return 1
        exported = set()
        for r in sups:
            exported |= set(r.keys())
        print("  ── %s · %d مشرفاً · أعلامٌ مكتوبةٌ %d · مصدَّرةٌ %d"
              % (gname, len(sups), len(written), len(exported)))
        for f in sorted(written):
            if f in exported:
                # ② وهل تقرؤه المنصة؟
                used = re.search(r"[\.\[]\s*[\"']?" + re.escape(f) + r"[\"']?\s*\]?", app)
                hit = bool(re.search(r"\br\.%s\b|\bx\.%s\b|\[\"%s\"\]|\.%s\b" % (f, f, f, f), app))
                print("     %s %-12s مصدَّرٌ %s" % ("✓" if hit else "⛔", f,
                                                   "ويُقرأ في المنصة" if hit else "**ولا يقرؤه شيء**"))
                ok &= hit
            elif f in CONSUMED:
                # ③ ويُتحقَّق أنه لا يصل فعلاً
                leaked = any(f in r for r in sups)
                print("     %s %-12s مُستهلَكٌ عند المصدر — %s%s"
                      % ("✓" if not leaked else "⛔", f, CONSUMED[f],
                         "" if not leaked else "  ⛔ لكنه وصل البناء!"))
                ok &= not leaked
            elif f in LABEL:
                print("     ⓘ %-12s وصفيٌّ لا وظيفيّ — %s" % (f, LABEL[f]))
            else:
                print("     ⛔ %-12s مكتوبٌ في السجلّ ولا هو مصدَّرٌ ولا مُستهلَكٌ ولا موصوف"
                      % f)
                ok = False
    print("\n  %s" % ("✓ كلُّ علمٍ في السجلّ يصل المنصةَ ويُقرأ فيها"
                      if ok else "⛔ في السجلّ علمٌ ميت — لا يُنشر"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
