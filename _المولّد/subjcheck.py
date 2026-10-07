# -*- coding: utf-8 -*-
"""⛔ **المادةُ المكتوبةُ تُنسَب إلى تخصصها — في الصفحة المبنيّة لا في المولّد.**

⛔ **ولماذا هذا الحارس؟** في ٧ أكتوبر ٢٠٢٦ أمر المستشارُ بحذف كلِّ حصةٍ مادّتُها
   تخالف تخصصَ صفِّها، فعددتُها على مطابقةٍ حرفيةٍ فكانت **٢٨٤**. ولمّا نظرتُ في
   أعيانها وجدتُ أكثرَها فروقَ إملاءٍ ولغة: «الرياضيات» و«رياضيات»، و«إسلاميات»
   و«إسلامية»، و«Mathematics» و«رياضيات»، و«كيمياء» **هي علوم** في الثانوي.
   فالمخالفُ الحقيقيُّ **٤٤**. ولو حذفتُ على العدِّ الأول لأتلفتُ عملَ ٢٤٠ حصة.
⚠️ فصارت الخريطةُ تُبنى من **نماذج المنصة الاسترشادية** (مرجعُها فيها)، ويُقاس
   هنا أنها تُنسب كما يُنتظر — **بتشغيل شفرة الصفحة** لا بقراءتها.
⚠️ وما لا يُعرف انتسابُه (مقرّرٌ اختياريٌّ · عنوانُ درسٍ · رياضُ أطفال) يُردُّ
   خاوياً فلا يُنبَّه عليه — فالتنبيهُ الكاذبُ يُعلّم المعلمَ أن يتجاهله.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys

import probedir as PRB

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(os.path.dirname(HERE), "٨ - النموذج الرقمي (تجربة)",
                    "منصة الحصة الموحَّدة — ابن خلدون.html")

# ⚠️ وهذه الحالاتُ **من المخزن الحيّ** يومَ التدقيق لا من خيالي: ما كتبه
#    المعلمون فعلاً في خانة المادة، ومعه تخصصُ الصفِّ الذي كُتب فيه.
CASES = [
    # (المكتوب, التخصصُ المنتظَر)
    ("الرياضيات", "رياضيات"), ("رياضيات ", "رياضيات"), ("MATH", "رياضيات"),
    ("Mathematics", "رياضيات"), ("math", "رياضيات"),
    ("إسلاميات", "إسلامية"), ("اسلاميه", "إسلامية"), ("حديث", "إسلامية"),
    ("فقه : المهر ", "إسلامية"), ("قرآن", "إسلامية"),
    ("كيمياء ", "علوم"), ("Chemistry", "علوم"), ("فيزياء 2-1", "علوم"),
    ("أحياء 1", "علوم"), ("Biology", "علوم"), ("علم أرض", "علوم"),
    ("العلوم", "علوم"), ("علوم", "علوم"),
    ("حاسب آلى", "حاسب آلي"), ("حاسب الي", "حاسب آلي"),
    ("التقنية الرقمية 1", "حاسب آلي"), ("تقنية رقمية ٣ ", "حاسب آلي"),
    ("المهارات الرقمية", "حاسب آلي"), ("تصميم رقمي", "حاسب آلي"),
    ("الكفايات اللغوية 3", "لغتي"), ("كفايات لغوية", "لغتي"),
    ("لغتي الخالدة", "لغتي"), ("اللغة العربية", "لغتي"), ("Arabic", "لغتي"),
    ("English", "E"), ("انجلش", "E"), ("لغه انجليزيه", "E"), ("E1", "E"),
    ("الدراسات الاجتماعية", "اجتماعيات"), ("اجتماعيات ", "اجتماعيات"),
    ("تاريخ", "اجتماعيات"), ("جغرافيا", "اجتماعيات"),
    ("التربية البدنية", "البدنية"), ("تربية بدنية وصحية ", "البدنية"),
    ("التربية الفنية", "الفنية"), ("المهارات الحياتية والأسرية", "الفنية"),
    # ⚠️ ومقرّراتُ الثانويِّ بنصِّ المستشار ٧ أكتوبر ٢٠٢٦
    ("مقدمة الاعمال", "اجتماعيات"), ("مقدمة الأعمال", "اجتماعيات"),
    ("قدرات لفظي ", "لغتي"), ("القدرات اللفظي", "لغتي"),
    # ⛔ وهذه كانت تُردُّ مجهولةً وهي معروفةٌ: «ال» كانت تُنزع من أول الكلمة وحدَها
    ("التصميم الرقمي ", "حاسب آلي"), ("اللغة العربية", "لغتي"),
    ("الدراسات الاجتماعية", "اجتماعيات"), ("المهارات الحياتية والأسرية", "الفنية"),
    # ⚠️ وحارسُ الثلاثةِ أحرف: «آلي» لا تُنزع منها «ال» وإلّا انكسر التخصصُ نفسُه
    ("حاسب آلي", "حاسب آلي"), ("الحاسب الآلي", "حاسب آلي"),
    # ⚠️ وما لا يُعرف انتسابُه يُردُّ خاوياً — ولا يُحكم عليه بمخالفة
    ("التفكير الناقد ", ""),
    ("البحث العلمي ", ""), ("مصادر البحث", ""), ("تصميم هندسي", ""),
    ("من أنا ", ""), ("حلقة", ""), ("١٣", ""), ("٠", ""), ("ع", ""), ("", ""),
]

JS = r"""import fs from "node:fs";
const page = fs.readFileSync(process.argv[2], "utf8");
/* ⚠️ تُؤخذ الشفرةُ **من الصفحة المبنيّة** — فالمقيسُ ما يُسلَّم للمعلمين */
const g = (rx, nm) => { const m = page.match(rx); if (!m) { console.log("MISSING:" + nm); process.exit(3); } return m[0]; };
const fam = g(/const SUBJFAM = [\s\S]*?;\n/, "SUBJFAM");
const nrm = g(/function subjNorm\(t\)\{[\s\S]*?\n\}/, "subjNorm");
const fn  = g(/function subjFam\(t\)\{[\s\S]*?\n\}/, "subjFam");
const run = new Function(fam + nrm + fn + "; return {subjFam, subjNorm};")();
const cases = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
/* ⛔ **وأرضيّةُ الشواهد لا تكفي وحدَها**: أولُ تشغيلٍ ردَّ ٥١ حالةً خاويةً
   و١٠ «ناجحةً» — وهي الحالاتُ المنتظَرُ خلوُّها أصلاً. فالنجاحُ الكاذبُ
   يسكن في حالةٍ منتظَرُها الخلوّ. فيُشترط هنا **عددُ ما يُنسَب فعلاً**. */
const named = cases.filter(c=>c[1]).length;
let hit = 0, bad = 0, n = 0;
for (const [t, want] of cases) {
  const got = run.subjFam(t) || "";
  n++;
  if (want && got === want) hit++;
  if (got !== want) { bad++; console.log("  ⛔ «" + t + "» ← " + (got || "خاوٍ") + " (المنتظَر " + (want || "خاوٍ") + ")"); }
}
for (const [t, want] of JSON.parse(fs.readFileSync("norm.json", "utf8"))) {
  const got = run.subjNorm(t);
  n++;
  if (got !== want) { bad++; console.log("  \u26d4 \u062a\u0633\u0648\u064a\u0629 \u00ab" + t + "\u00bb \u2190 \u00ab" + got + "\u00bb (\u0627\u0644\u0645\u0646\u062a\u0638\u064e\u0631 \u00ab" + want + "\u00bb)"); }
}
console.log("MEASURED:" + n + ":" + bad + ":" + hit + ":" + named);
"""

FAULTS = [
    ("نزعُ تسويةِ الهمزة والياء",
     '.replace(/[أإآ]/g, "ا").replace(/ى/g, "ي")', '.replace(/zzz/g, "ا")'),
    ("نزعُ إسقاطِ أرقام المستويات",
     's.replace(/[0-9]+([-/][0-9]+)?/g, " ")', 's.replace(/zzzz/g, " ")'),
    ("نزعُ إسقاطِ «ال» المعرّفة",
     'return s.split(" ").map(w=>(w.indexOf(AL) === 0 && w.length - 2 >= 3) ? w.slice(2) : w).join(" ");',
     "return s;"),
    ("نزعُ حارسِ الثلاثةِ أحرف في «ال»",
     "w.indexOf(AL) === 0 && w.length - 2 >= 3", "w.indexOf(AL) === 0"),
    ("نزعُ المطابقةِ كلمةً كلمةً",
     "if(ws[i].length >= 3 && own(ws[i])) return SUBJFAM[ws[i]];",
     "if(false) return SUBJFAM[ws[i]];"),

]


# ⛔ **وقواعدُ التسويةِ تُقاس بعقدها لا بأثرها وحدَه**: «حاسب آلي» يصحُّ
#    انتسابُه ولو انكسرت تسويتُه (لأن «حاسب» وحدَها مفتاح) — فعيبُ التسوية
#    يمرُّ بلا كشف. فتُقاس مخرجاتُها بعينها.
NORMCASES = [
    ("حاسب آلي", "حاسب الي"),          # «ال» لا تُنزع إن بقي أقلُّ من ثلاثة أحرف
    ("التصميم الرقمي ", "تصميم رقمي"),   # وتُنزع من كل كلمة
    ("الكفايات اللغوية 3", "كفايات لغويه"),
    ("فيزياء 2-1", "فيزياء"),
    ("إسلاميات", "اسلاميات"),
    ("٠١٢", ""),
]


def run_once(page_path, d):
    io.open(os.path.join(d, "cases.json"), "w", encoding="utf-8").write(
        json.dumps(CASES, ensure_ascii=False))
    io.open(os.path.join(d, "norm.json"), "w", encoding="utf-8").write(
        json.dumps(NORMCASES, ensure_ascii=False))
    io.open(os.path.join(d, "t.mjs"), "w", encoding="utf-8").write(JS)
    io.open(os.path.join(d, "package.json"), "w", encoding="utf-8").write('{"type":"module"}')
    r = subprocess.run(["node", "t.mjs", page_path, "cases.json"], cwd=d,
                       capture_output=True, text=True)
    return r


def main():
    if not os.path.exists(PAGE):
        print("  ⛔ لا صفحةَ مبنيّة: %s" % PAGE)
        return 1
    d = PRB.probe("subj")
    os.makedirs(d, exist_ok=True)
    r = run_once(PAGE, d)
    out = r.stdout
    if "MISSING:" in out:
        print("  ⛔ لم تُوجد في الصفحة: %s" % out.split("MISSING:")[1].strip())
        return 1
    m = re.search(r"MEASURED:(\d+):(\d+):(\d+):(\d+)", out)
    if not m:
        print("  ⛔ لم يُقَس شيء:\n%s%s" % (out[-400:], r.stderr[-400:]))
        return 1
    n, bad = int(m.group(1)), int(m.group(2))
    hit, named = int(m.group(3)), int(m.group(4))
    # ⚠️ أرضيّةُ الشواهد: فحصٌ قاس أقلَّ من حالاته لم يكتمل
    if n < len(CASES) + len(NORMCASES):
        print("  ⛔ قِيس %d من %d حالة — فحصٌ لم يكتمل" % (n, len(CASES) + len(NORMCASES)))
        return 1
    print(out.strip().replace("MEASURED:%d:%d:%d:%d" % (n, bad, hit, named), "").strip())
    if bad:
        print("  ⛔ سقط %d من %d حالة" % (bad, n))
        return 1
    # ⛔ أرضيّةُ الانتساب: لو عادت كلُّ مادةٍ خاويةً «نجح» ما منتظَرُه الخلوّ
    if hit < named:
        print("  ⛔ نُسِب %d من %d مادةٍ منتظَرٍ انتسابُها — فحصٌ لا يُعتمد" % (hit, named))
        return 1
    print("  ✓ %d حالةً من المخزن الحيّ تُنسَب كما يُنتظر (%d منها إلى تخصصها)"
          % (n, hit))

    # ── الكاشفُ على عيوبٍ مزروعة: حارسٌ لم يُجرَّب على عيبٍ لا يُعتمد ──
    print("\n  ── الكاشفُ على عيوبٍ مزروعة ──")
    good = io.open(PAGE, encoding="utf-8").read()
    p2 = os.path.join(d, "bad.html")
    nbad = 0
    for name, old, new in FAULTS:
        if old not in good:
            print("  ⛔ %-30s — المرساةُ غيرُ موجودةٍ في الصفحة" % name)
            nbad += 1
            continue
        io.open(p2, "w", encoding="utf-8").write(good.replace(old, new, 1))
        q = run_once(p2, d)
        mm = re.search(r"MEASURED:(\d+):(\d+):", q.stdout)
        if mm and int(mm.group(2)) > 0:
            print("  ✓ %-30s → أسقط %s حالة" % (name, mm.group(2)))
        else:
            print("  ⛔ %-30s → **مرَّ بلا كشف**" % name)
            nbad += 1
    shutil.rmtree(d, ignore_errors=True)
    if nbad:
        print("\n  ⛔ الكاشفُ لا يُعتمد")
        return 1
    print("\n  ✓ خريطةُ المواد تفي — و%d عيباً مزروعاً كُشفت" % len(FAULTS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
