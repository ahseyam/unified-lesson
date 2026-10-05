# -*- coding: utf-8 -*-
"""صفحة المشروع المجمَّعة — مسارٌ واحد لكل ما يخصّ نظام الحصة الموحَّدة.

تُبنى بمسحِ شجرة التسليم فعلياً، فلا تذكر ملفاً غير موجود ولا تُغفل ملفاً موجوداً.
الهوية: ألوان الكليشة المعتمدة وخط الجزيرة بأوزانه الثلاثة (مضمَّنة، فتعمل بلا إنترنت).
الروابط نسبية، فتعمل محلياً وعلى GitHub Pages سواء.
الاستعمال: python3 hub.py            (يكتب index.html في جذر مجلد التسليم)
"""
import base64
import glob
import html
import io
import json
import os
import re
import sys
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONTS = os.path.expanduser("~/Library/Fonts")
RLM = "‏"
D1, D2, D3, D4 = ("١ - نموذج تحضير الحصة", "٢ - استمارة الملاحظة الصفية",
                  "٣ - الأدوات المساندة", "٤ - بطاقات إستراتيجيات التدريس")
D5, D6, D7, D8, D9 = ("٥ - الاتجاهات التدريسية", "٦ - بطاقة زيارة الأقران",
                      "٧ - آلية جداول الحصص الموحَّدة", "٨ - النموذج الرقمي (تجربة)",
                      "٩ - العرض التعريفي")
D10 = "١٠ - أدلّة استخدام المنصة"
PDF = " (للعرض والطباعة).pdf"


def b64(p):
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()


def face(name, file, weight="normal", digits=False):
    p = os.path.join(FONTS, file)
    if not os.path.exists(p):
        return ""
    ur = "" if digits else "  unicode-range:U+0000-065F,U+066A-FFFF;\n"
    return (f"@font-face{{font-family:{name};font-weight:{weight};font-display:swap;\n"
            f"  src:url(data:font/ttf;base64,{b64(p)}) format('truetype');\n{ur}}}\n")


FONTCSS = (face("JZ", "ArbFONTS-Al-Jazeera-Arabic-Regular.ttf")
           + face("JZ", "ArbFONTS-Al-Jazeera-Arabic-Bold.ttf", "700")
           + face("JZL", "ArbFONTS-Al-Jazeera-Arabic-Light.ttf")
           + face("SK", "Sakkal Majalla Regular.ttf", digits=True))

# ═════════════ جمع الملفات ═════════════
MISSING = []


def rel(*parts):
    """مسارٌ نسبيٌّ إن وُجد الملف، وإلا سُجّل في النواقص."""
    p = os.path.join(*parts)
    if os.path.exists(os.path.join(ROOT, p)):
        return quote(p)
    MISSING.append(p)
    return None


def pair(folder, base, g=""):
    """وورد وPDF لملفٍ واحد."""
    return {"docx": rel(folder, base + g + ".docx"), "pdf": rel(folder, base + g + PDF)}


def item(title, note, files, tags="", btn=None, hero=False, rows=None, warn=None):
    """⚠️ `rows` لبطاقةٍ فيها أكثرُ من ملفَّين: سطرٌ لكل مرحلةٍ بروابطها،
    وإلا ضاعت ملفاتٌ لأن البطاقة المسطَّحة لا تحمل إلا خمسة مفاتيح."""
    d = {"t": title, "n": note, "f": files, "g": tags}
    if rows:
        d["rows"] = rows
    if btn:
        d["b"] = btn
    if hero:
        d["h"] = 1
    if warn:
        d["w"] = warn
    return d


SEC = []


def section(sid, title, sub, items):
    SEC.append({"id": sid, "t": title, "s": sub, "items": items})


# ── ١) ابدأ من هنا ──
# ⛔ **بابان إلى المنصة، وأحدُهما يُوقع المستخدمَ في طريقٍ مسدود**: من فتحها
#    من هنا فجهازُه غيرُ مربوطٍ بالمخزن — فيكتب تحضيرَه كاملاً ولا يبلغ
#    مدرستَه. ومن فتحها برابط الدخول رُبط جهازُه من أول فتحة.
#    أمسكه المستشارُ على جواله ٥ أكتوبر ٢٠٢٦: «فلماذا تظهر مثل تلك الرسالة
#    فتربك المستخدم». فصار البابُ يقول ما وراءه **قبل** أن يُفتح.
_SRVNOTE = ("⚠️ هذا الزرُّ للاطّلاع والتجربة — وجهازُك لا يُربط بمخزن المدرسة منه. "
            "وللعمل الفعلي افتح **رابط الدخول** الذي وصلك من إدارة التخطيط والاعتماد، "
            "فيُربط جهازُك من أول فتحةٍ ولا يُطلب منك شيءٌ بعدها. "
            "وإن فتحتَ من هنا فالمنصةُ تسألك عن الرابط وتربطك به.")

section("start", "ابدأ من هنا", "المنصة أولاً — ثم النشرتان اللتان تشرحان النموذج والاستمارة", [
    item("★ منصة الحصة الموحَّدة — بنين",
         "التطبيق نفسه: جدول الحصص الموحَّدة مصفوفةً · شريطٌ جانبي للمراحل الخمس · "
         "ثلاثة أدوار · سبعة تقارير — يُفتح ويُعمل عليه مباشرةً",
         {"html": rel(D8, "منصة الحصة الموحَّدة — ابن خلدون.html")}, "بنين رقمي",
         btn="افتح المنصة ←", hero=True, warn=_SRVNOTE),
    item("★ منصة الحصة الموحَّدة — بنات", "النسخة المؤنَّثة كاملةً — بالمصفوفة والشريط الجانبي نفسيهما",
         {"html": rel(D8, "منصة الحصة الموحَّدة — ابن خلدون (بنات).html")}, "بنات رقمي",
         btn="افتح المنصة ←", hero=True, warn=_SRVNOTE),
    item("نشرة استخدام نموذج التحضير", "بالونات شارحة على النموذج نفسه: ما المطلوب في كل خانة",
         {"pdf": rel(D1, "نشرة الاستخدام", "نشرة استخدام نموذج التحضير — ابن خلدون.pdf"),
          "pdf2": rel(D1, "نشرة الاستخدام", "نشرة استخدام نموذج التحضير — ابن خلدون (بنات).pdf")}, "بنين بنات"),
    item("نشرة استخدام الاستمارة", "بالونات شارحة على الاستمارة: كيف يُرصد كل مجال",
         {"pdf": rel(D2, "نشرة الاستخدام", "نشرة استخدام الاستمارة — ابن خلدون.pdf"),
          "pdf2": rel(D2, "نشرة الاستخدام", "نشرة استخدام الاستمارة — ابن خلدون (بنات).pdf")}, "بنين بنات"),
    item("فهرس الأدوات بروابطها — PDF", "ثماني صفحات فيها كل أداةٍ برابطها القابل للنقر",
         {"pdf": rel("فهرس نظام الحصة الموحَّدة — بروابط.pdf")}, "عام"),
])

# ── ٢) نموذج التحضير ──
prep = [item("نموذج تحضير الحصة — بنين", "القالب الفارغ · وجهان بترتيب مجالات الاستمارة",
             pair(os.path.join(D1, "بنين"), "نموذج تحضير الحصة — ابن خلدون"), "بنين"),
        item("نموذج تحضير الحصة — بنات", "القالب الفارغ بصيغة المؤنَّث كاملةً: الاسم والفعل والضمير",
             pair(os.path.join(D1, "بنات"), "نموذج تحضير الحصة — ابن خلدون", " (بنات)"), "بنات")]
# ⚠️ النماذجُ المعبّأة تُصنَّف **مادةً ثم مرحلة** لا قائمةً مسطَّحة: المعلمُ يبحث
#    عن مادته أولاً، فبطاقةٌ لكل مادةٍ تجمع مراحلَها الثلاث ونسختَي الجنس.
STAGES = [("المرحلة الابتدائية", "ابتدائي"), ("المرحلة المتوسطة", "متوسط"), ("المرحلة الثانوية", "ثانوي")]
SUBJ_ORDER = ["لغتي الجميلة", "لغتي الخالدة", "الكفايات اللغوية", "الدراسات الإسلامية",
              "الرياضيات", "العلوم", "الأحياء", "الكيمياء", "الفيزياء",
              "الدراسات الاجتماعية", "اللغة الإنجليزية", "المهارات الرقمية", "التقنية الرقمية",
              "التربية البدنية", "التربية الفنية", "المهارات الحياتية والأسرية"]
by_subj = {}
for stage, tag in STAGES:
    for g, fold, sfx in (("بنين", "بنين", ""), ("بنات", "بنات", " (بنات)")):
        base = os.path.join(D1, "نماذج معبّأة استرشادية", stage, fold)
        for d in sorted(glob.glob(os.path.join(ROOT, base, "*.docx"))):
            n = os.path.basename(d)[:-5]
            if n.startswith("~$"):
                continue
            clean = n.replace(sfx, "").strip()
            parts = [x.strip() for x in clean.split("—")]
            subj = parts[0] if parts else clean
            grade = parts[1] if len(parts) > 1 else ""
            topic = parts[-1] if len(parts) > 2 else ""
            e = by_subj.setdefault(subj, {})
            e.setdefault((stage, tag, grade, topic), {})[g] = (base, n)
def _ord(x):
    return SUBJ_ORDER.index(x) if x in SUBJ_ORDER else len(SUBJ_ORDER)


for subj in sorted(by_subj, key=lambda x: (_ord(x), x)):
    ent = by_subj[subj]
    rows, tags, n_files = [], set(), 0
    for (stage, tag, grade, topic), gs in sorted(
            ent.items(), key=lambda kv: [s2 for s2, _ in STAGES].index(kv[0][0])):
        files = {}
        for g, (base, n) in sorted(gs.items()):
            if g == "بنين":
                files["pdf"] = rel(base, n + PDF)
                files["docx"] = rel(base, n + ".docx")
            else:
                files["pdf2"] = rel(base, n + PDF)
                files["docx2"] = rel(base, n + ".docx")
            tags.add(g)
        n_files += len(files)
        tags.add(tag)
        rows.append({"l": grade + (" · " + topic if topic else ""), "f": files})
    prep.append(item(f"نماذج معبّأة · {subj}",
                     f"{len(rows)} مرحلة · نسختا بنين وبنات — اختر مرحلتك",
                     {}, " ".join(sorted(tags)) + " معبّأ", rows=rows))

section("prep", "نموذج تحضير الحصة",
        "القالبان الفارغان · وأربعةٌ وخمسون نموذجاً معبّأً مصنَّفةً بالمادة ثم المرحلة", prep)

# ── ٣) الاستمارة وأدواتها ──
section("obs", "استمارة الملاحظة الصفية وأدواتها",
        "ثمانية مجالات · خمسون مؤشراً · مئتا درجة — ومعها ما يضبط الحكم عليها", [
    item("استمارة الملاحظة الصفية — بنين", "ثلاثة أوجه: المؤشرات · الشواهد · النتيجة والاتفاق",
         pair(os.path.join(D2, "بنين"), "استمارة الملاحظة الصفية — ابن خلدون"), "بنين"),
    item("استمارة الملاحظة الصفية — بنات", "النسخة المؤنَّثة كاملةً",
         pair(os.path.join(D2, "بنات"), "استمارة الملاحظة الصفية — ابن خلدون", " (بنات)"), "بنات"),
    item("دليل مستويات الأداء — بنين", "لكل مؤشر: ما الذي يُعدّ شاهداً وما الذي لا يُعدّ",
         pair(os.path.join(D3, "دليل مستويات الأداء", "بنين"), "دليل مستويات الأداء — ابن خلدون"), "بنين"),
    item("دليل مستويات الأداء — بنات", "النسخة المؤنَّثة",
         pair(os.path.join(D3, "دليل مستويات الأداء", "بنات"), "دليل مستويات الأداء — ابن خلدون", " (بنات)"), "بنات"),
    item("خطة الاستعداد للزيارة — بنين", "خمس قواعد تحكم الأسابيع الأخيرة قبل وصول الفريق",
         pair(os.path.join(D3, "خطة الاستعداد", "بنين"), "خطة الاستعداد — ابن خلدون"), "بنين"),
    item("خطة الاستعداد للزيارة — بنات", "النسخة المؤنَّثة",
         pair(os.path.join(D3, "خطة الاستعداد", "بنات"), "خطة الاستعداد — ابن خلدون", " (بنات)"), "بنات"),
])

# ── ٤) بطاقات الإستراتيجيات ──
cards = []
for g, fold, sfx in (("بنين", "بنين", ""), ("بنات", "بنات", " (بنات)")):
    base = os.path.join(D4, fold)
    for d in sorted(glob.glob(os.path.join(ROOT, base, "*.docx"))):
        n = os.path.basename(d)[:-5]
        if n.startswith("~$"):
            continue
        name = n.replace("بطاقة تشخيص — ", "").replace(" — ابن خلدون", "").replace(sfx, "").strip()
        cards.append(item(name, f"بطاقة تشخيص · عشرة مؤشرات من مئة درجة · {g}",
                          {"docx": rel(base, n + ".docx"), "pdf": rel(base, n + PDF)}, g))
section("cards", "بنك إستراتيجيات التدريس",
        "تسع عشرة بطاقة تشخيص لأداء المعلم — ودرجتها تدخل في مؤشر تطبيق الإستراتيجيات", cards)

# ── ٥) الاتجاهات التدريسية ──
appr = []
for g, fold, sfx in (("بنين", "بنين", ""), ("بنات", "بنات", " (بنات)")):
    base = os.path.join(D5, fold)
    for d in sorted(glob.glob(os.path.join(ROOT, base, "*.pdf"))):
        n = os.path.basename(d)[:-4]
        name = n.replace("الاتجاه التدريسي — ", "").replace(" — ابن خلدون", "").replace(PDF[:-4], "").replace(sfx, "").strip()
        appr.append(item(name, f"نشرة تربوية · ما هو ولماذا وأربع خطوات وشواهد وأمثلة من كل مادة · {g}",
                         {"pdf": rel(base, n + ".pdf")}, g))
section("appr", "الاتجاهات التدريسية الستة",
        "نشراتٌ موجزة يعلن المعلم واحداً منها في تحضيره فتُقاس شواهده في حصته", appr)

# ── ٦) الزيارة والمتابعة ──
section("visit", "الزيارة والمتابعة", "أن تنتهي كل زيارة بإجراءٍ واحدٍ يُتابَع لا بانطباعٍ عام", [
    item("بطاقة زيارة الأقران — بنين", "«شاهدتُ وأطبّق» — زيارتان لكل معلم في الفصل",
         pair(os.path.join(D6, "بنين"), "بطاقة زيارة الأقران — ابن خلدون"), "بنين"),
    item("بطاقة زيارة الأقران — بنات", "النسخة المؤنَّثة",
         pair(os.path.join(D6, "بنات"), "بطاقة زيارة الأقران — ابن خلدون", " (بنات)"), "بنات"),
    item("بطاقة الجسر — بنين", "إجراءٌ واحد يُنقل من الزيارة إلى الحصص ويُتحقق منه في التالية",
         pair(os.path.join(D3, "بطاقة الجسر", "بنين"), "بطاقة الجسر — ابن خلدون"), "بنين"),
    item("بطاقة الجسر — بنات", "النسخة المؤنَّثة",
         pair(os.path.join(D3, "بطاقة الجسر", "بنات"), "بطاقة الجسر — ابن خلدون", " (بنات)"), "بنات"),
])

# ── أدلّةُ استخدام المنصة: لكل دورٍ دليلُه ──
# ⛔ خمسٌ لا ثلاث، بطلب المستشار ٢٩ سبتمبر ٢٠٢٦: «للخمسة أدوار كل ع حدة».
#    وكلُّ لقطةٍ فيها من المنصة نفسِها — تُلتقط بـnshshots.py لا تُرسم.
NSH = [("teacher", "المعلم القائم بالحصة", "المعلمة القائمة بالحصة",
        "من خانته في الجدول إلى درجته وإجراء جسره — خمسُ خطواتٍ مصوّرة"),
       ("peer", "المعلم الزائر", "المعلمة الزائرة",
        "الزياراتُ المسنَدة · قراءةُ التحضير · بطاقةُ الأقران · الإجراء"),
       ("principal", "مدير المدرسة", "مديرة المدرسة",
        "مدرستُه وحدها: الجدولُ والرصدُ والاعتمادُ ولوحةُ التقارير"),
       ("deputy", "الوكيل التعليمي", "الوكيلة التعليمية",
        "وله وحده إسنادُ المعلمين الزائرين بالرقم الوظيفي"),
       ("supervisor", "المشرف التربوي", "المشرفة التربوية",
        "تخصصُه عبر المجمعات: «زيارتي اليوم» وخطةُ الأسبوع ودورانُ الفرق")]
nsh = []
for _k, _m, _f, _d in NSH:
    # ⚠️ لا تُستعمل pair(): تفترض لاحقةَ «(للعرض والطباعة)» وهذه بلا لاحقة
    nsh.append(item(f"دليل {_m}", _d,
                    {"pdf": rel(D10, "بنين", f"دليل استخدام المنصة — {_m} — ابن خلدون.pdf"),
                     "docx": rel(D10, "بنين", f"دليل استخدام المنصة — {_m} — ابن خلدون.docx")},
                    "بنين رقمي"))
    nsh.append(item(f"دليل {_f}", "النسخة المؤنَّثة",
                    {"pdf": rel(D10, "بنات", f"دليل استخدام المنصة — {_f} — ابن خلدون (بنات).pdf"),
                     "docx": rel(D10, "بنات", f"دليل استخدام المنصة — {_f} — ابن خلدون (بنات).docx")},
                    "بنات رقمي"))
section("nsh", "دليل استخدام المنصة",
        "لكل دورٍ دليلُه — خطوةً خطوةً بلقطاتٍ حيّةٍ من المنصة نفسِها", nsh)

# ── ٧) الآلية والجداول ──
mech = [item("نشرة الآلية — بنين", "من يحضر كل حصة · خمس قواعد · دوران المشرفين · مسار الحصة",
             pair(os.path.join(D7, "بنين"), "آلية الحصص الموحَّدة — ابن خلدون"), "بنين وطني"),
        item("نشرة الآلية — بنات", "النسخة المؤنَّثة",
             pair(os.path.join(D7, "بنات"), "آلية الحصص الموحَّدة — ابن خلدون", " (بنات)"), "بنات وطني"),
        ]
# ⛔ أُخرجت أربعةُ ملفات إكسل (الوطني والعالمي × بنين وبنات) من الفهرس ٢٩ سبتمبر
#    ٢٠٢٦: «لا داعي لل ٤ إكسل هذه الآن طالما نبني الجداول من خلال المنصة».
#    فالجدولُ يُملأ في المصفوفة داخل الصفحة ويُطبع منها، ووجودُ نسختين يفترق.
for g, fold, sfx in (("بنين", "بنين", ""), ("بنات", "بنات", " (بنات)")):
    base = os.path.join(D7, fold, "القطاع العالمي")
    mech.append(item(f"نشرة الآلية — القطاع العالمي — {g}", "ثلاثة مجمعات: عرقة · المنار · الياسمين",
                     pair(base, "آلية الحصص الموحَّدة — ابن خلدون", sfx + " — عالمي"), f"{g} عالمي"))

section("mech", "آلية الحصص الموحَّدة وجداولها",
        # ⛔ «ثلاثة مقيّمين» قاعدةٌ ملغاة: الرصدُ للمشرف المختص وحدَه (٣٠ سبتمبر ٢٠٢٦)
        "المشرف المختص يرصد، ومعه معلمان زائران — ودورانٌ يمنع التقاء مشرفَين في مجمع", mech)

# ── ٨) النموذج الرقمي ──
# ⚠️ المنصةُ أولاً: الصفحةُ المفردة تشبهها في الاسم فيُنقر عليها بالخطأ، وهي أقدمُ وأبسط.
section("web", "النموذج الرقمي", "المنصةُ الكاملة أولاً — والصفحةُ المفردة تحتها للتحضير وحده", [
    item("★ منصة الحصة الموحَّدة — بنين",
         "الكاملة: جدول الحصص الموحَّدة مصفوفةً · شريطٌ جانبي للمراحل · خمسةُ أدوار · سبعة تقارير",
         {"html": rel(D8, "منصة الحصة الموحَّدة — ابن خلدون.html")}, "بنين رقمي",
         btn="افتح المنصة ←", hero=True),
    item("★ منصة الحصة الموحَّدة — بنات", "النسخة المؤنَّثة كاملةً",
         {"html": rel(D8, "منصة الحصة الموحَّدة — ابن خلدون (بنات).html")}, "بنات رقمي",
         btn="افتح المنصة ←", hero=True),
    item("صفحة الحصة الموحَّدة — بنين",
         "الصفحةُ المفردة الأقدم: تحضيرٌ بتلميحاتٍ ورابطٌ للزائر — بلا جدولٍ ولا مراحل",
         {"html": rel(D8, "صفحة الحصة الموحَّدة — ابن خلدون.html")}, "بنين رقمي"),
    item("صفحة الحصة الموحَّدة — بنات", "النسخة المؤنَّثة من الصفحة المفردة",
         {"html": rel(D8, "صفحة الحصة الموحَّدة — ابن خلدون (بنات).html")}, "بنات رقمي"),
    # ⛔ لا بطاقةَ لدليل الربط ولا لدليل الاستضافة: المستودعُ عامّ، ومن
    #    يقرأ الدليلَ يُنشئ منظومةً موازيةً أو يعرف عقدَ الخادم. الدليلان في
    #    «خادم الحصة الموحَّدة (خاصّ — لا يُنشر)» على سطح المكتب. (٢٩ سبتمبر ٢٠٢٦)
])

def arnum(n):
    return "".join("٠١٢٣٤٥٦٧٨٩"[int(c)] for c in str(n))


COUNT = sum(len(s["items"]) for s in SEC)
FILES = sum(len(it.get('f') or {}) + sum(len(r['f']) for r in it.get('rows', []))
            for sec in SEC for it in sec['items'])

CSS = """
:root{--navy:#2F5384;--navy2:#1d3760;--teal:#2F7F95;--teal2:#1d5d70;--tealbg:#E4F1F4;
 --ink:#16202e;--grey:#6b7a8d;--line:#d7dfe9;--head:#EDF2F8;--gold:#B8862B;--bg:#f2f5f9}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font-family:JZ,SK,"Geeza Pro",Tahoma,sans-serif;
 font-size:17px;line-height:1.75}
a{color:inherit;text-decoration:none}
.top{background:linear-gradient(105deg,var(--navy2),var(--navy) 45%,var(--teal));color:#fff;padding:26px 0 22px}
.wrap{max-width:1680px;margin:0 auto;padding:0 20px}
.top .row{display:flex;align-items:center;gap:20px;flex-wrap:wrap}
.top img{height:54px;width:auto;object-fit:contain;border-radius:6px;background:#fff;padding:4px 8px}
.top h1{font-size:34px;font-weight:700;line-height:1.2}
.top p{font-family:JZL,SK;font-size:18px;opacity:.93;margin-top:4px}
.kpi{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}
.kpi div{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22);border-radius:9px;
 padding:7px 14px;font-size:15px;font-family:JZL,SK}
.kpi b{font-family:SK;font-size:21px;font-weight:700;margin-inline-end:6px}
nav{position:sticky;top:0;z-index:20;background:#fff;border-bottom:1px solid var(--line);
 box-shadow:0 2px 10px rgba(20,40,70,.07)}
nav .wrap{display:flex;gap:6px;flex-wrap:wrap;padding-top:9px;padding-bottom:9px}
nav button{border:1px solid transparent;background:transparent;color:var(--navy);font:inherit;
 font-size:16px;padding:8px 15px;border-radius:9px;cursor:pointer;white-space:nowrap;font-weight:700}
nav button:hover{background:var(--head)}
nav button.on{background:var(--navy);color:#fff}
.tools{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:18px 0 6px}
.tools input{flex:1;min-width:230px;border:1px solid var(--line);border-radius:10px;padding:10px 14px;
 font:inherit;font-size:16px;background:#fff}
.tools input:focus{outline:2px solid var(--teal);border-color:var(--teal)}
.chip{border:1px solid var(--line);background:#fff;border-radius:20px;padding:7px 15px;font:inherit;
 font-size:15px;cursor:pointer;color:var(--navy2);font-family:JZL,SK}
.chip.on{background:var(--teal);border-color:var(--teal);color:#fff}
.cnt{color:var(--grey);font-family:JZL,SK;font-size:15px}
section{margin:22px 0 30px}
section h2{font-size:24px;color:var(--navy2);display:flex;align-items:center;gap:12px}
.card .warn{background:#fdf3e3;border:1px solid #e8cf9f;border-inline-start:4px solid #c08a2e;
 border-radius:8px;padding:9px 12px;margin:4px 0 10px;font-size:14px;line-height:1.75;color:#6b4e14}
.card .warn b{color:#8a5b00}
section h2::before{content:"";width:7px;height:26px;background:var(--gold);border-radius:4px}
section .sub{font-family:JZL,SK;color:var(--grey);font-size:16px;margin:4px 0 14px;padding-inline-start:19px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.card{background:#fff;border:1px solid var(--line);border-radius:13px;padding:14px 16px;
 display:flex;flex-direction:column;gap:9px;transition:.15s}
.card.hero{border:2px solid var(--teal);background:linear-gradient(170deg,#fff,var(--tealbg))}
.card.hero h3{color:var(--teal2)}
.card.hero .lnk.html{background:var(--teal);color:#fff;border-color:var(--teal2);font-size:16px;padding:8px 18px}
.card:hover{border-color:var(--teal);box-shadow:0 6px 20px rgba(20,60,90,.10);transform:translateY(-2px)}
.card h3{font-size:18.5px;color:var(--navy2);font-weight:700;line-height:1.35}
.card p{font-family:JZL,SK;font-size:15px;color:var(--grey);line-height:1.6;flex:1}
.links{display:flex;gap:7px;flex-wrap:wrap}
.subrow{border-top:1px dashed var(--line);padding-top:8px;margin-top:2px}
.subrow:first-of-type{border-top:0}
.subrow b{display:block;font-size:14.5px;color:var(--navy2);margin-bottom:5px}
.lnk{border-radius:8px;padding:5px 12px;font-size:14.5px;font-weight:700;border:1px solid transparent;display:inline-block}
.lnk.pdf{background:#fdeceb;color:#a52018;border-color:#f3c8c4}
.lnk.docx{background:#e9f0fb;color:var(--navy);border-color:#c9dcf5}
.lnk.xlsx{background:#e8f6ec;color:#1d6b35;border-color:#bfe3c9}
.lnk.html{background:var(--tealbg);color:var(--teal2);border-color:#b6dbe4}
.lnk:hover{filter:brightness(.94)}
.empty{text-align:center;color:var(--grey);font-family:JZL,SK;padding:34px}
footer{background:var(--navy2);color:#cfdbe8;font-family:JZL,SK;font-size:15px;padding:20px 0;margin-top:34px}
footer .wrap{display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;align-items:center}
@media(max-width:620px){.top h1{font-size:26px}.grid{grid-template-columns:1fr}}
"""

JS = """
const SEC = __SEC__;
let tab = "all", q = "", gen = "";
const $ = s => document.querySelector(s);
const el=(t,c,x)=>{const e=document.createElement(t); if(c)e.className=c; if(x!=null)e.textContent=x; return e;};
const LBL = {pdf:"PDF", pdf2:"PDF (بنات)", docx:"وورد", docx2:"وورد (بنات)",
             xlsx:"إكسل", html:"افتح الصفحة"};
const ORD = ["html","pdf","docx","pdf2","docx2","xlsx"];
function card(it){
  const c = el("div", it.h ? "card hero" : "card");
  c.appendChild(el("h3", null, it.t));
  c.appendChild(el("p", null, it.n));
  /* ⚠️ تحذيرُ البطاقة يسبق أزرارَها: من قرأه قبل الضغط لم يُفاجأ بعده.
     والتوكيدُ `**نصّ**` يُحوَّل وسماً — ولا يُطبع كما هو. */
  if(it.w){
    const wd = el("div","warn");
    it.w.split(/[*][*]/).forEach((part, i)=>{
      wd.appendChild(i % 2 ? el("b", null, part) : document.createTextNode(part));
    });
    c.appendChild(wd);
  }
  const mk = (files, btn) => {
    const L = el("div","links");
    for(const k of ORD){
      if(!files[k]) continue;
      const a = el("a", "lnk " + (k === "pdf2" ? "pdf" : (k === "docx2" ? "docx" : k)),
                   k === "html" && btn ? btn : LBL[k]);
      a.href = files[k]; if(k !== "html") a.target = "_blank";
      L.appendChild(a);
    }
    return L;
  };
  if(it.rows){
    it.rows.forEach(r=>{
      const w = el("div","subrow");
      w.appendChild(el("b",null,r.l));
      w.appendChild(mk(r.f));
      c.appendChild(w);
    });
  } else c.appendChild(mk(it.f, it.b));
  return c;
}
function draw(){
  const m = $("#main"); m.innerHTML = "";
  let n = 0;
  SEC.forEach(s=>{
    if(tab !== "all" && tab !== s.id) return;
    const items = s.items.filter(it=>{
      const hay = (it.t + " " + it.n + " " + it.g);
      return (!q || hay.includes(q)) && (!gen || it.g.includes(gen));
    });
    if(!items.length) return;
    n += items.length;
    const sec = el("section");
    sec.appendChild(el("h2", null, s.t));
    sec.appendChild(el("div","sub", s.s));
    const g = el("div","grid");
    items.forEach(it=>g.appendChild(card(it)));
    sec.appendChild(g); m.appendChild(sec);
  });
  if(!n) m.appendChild(el("div","empty","لا نتائج مطابقة — جرّب كلمةً أخرى أو أزل المرشّحات."));
  $("#cnt").textContent = "المعروض: " + arn(n) + " من " + arn(SEC.reduce((a,s)=>a+s.items.length,0));
}
const arn = n => String(n).replace(/[0-9]/g, c => "٠١٢٣٤٥٦٧٨٩"[+c]);
function boot(){
  const nv = $("#nav");
  [["all","الكل"]].concat(SEC.map(s=>[s.id, s.t])).forEach(([id,t])=>{
    const b = el("button", id === tab ? "on" : "", t);
    b.addEventListener("click", ()=>{ tab = id; [...nv.children].forEach(x=>x.classList.remove("on"));
      b.classList.add("on"); draw(); window.scrollTo({top:0,behavior:"smooth"}); });
    nv.appendChild(b);
  });
  $("#q").addEventListener("input", e=>{ q = e.target.value.trim(); draw(); });
  document.querySelectorAll(".chip").forEach(ch=>{
    ch.addEventListener("click", ()=>{
      const v = ch.dataset.g;
      gen = (gen === v) ? "" : v;
      document.querySelectorAll(".chip").forEach(x=>x.classList.toggle("on", x.dataset.g === gen && gen));
      draw();
    });
  });
  draw();
}
boot();
"""

HTML = """<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>نظام الحصة الموحَّدة — مدارس ابن خلدون</title>
__ICON__
<meta name="description" content="مسارٌ واحد يجمع نموذج تحضير الحصة واستمارة الملاحظة الصفية وبنك الإستراتيجيات والاتجاهات التدريسية وآلية الزيارات والنموذج الرقمي.">
<style>__FONTS____CSS__</style></head><body>
<header class="top"><div class="wrap">
  <div class="row">
    __LOGO__
    <div><h1>نظام الحصة الموحَّدة</h1>
      <p>من التحضير إلى الدرجة — مدارس ابن خلدون</p></div>
  </div>
  <div class="kpi">
    <div><b>٨</b>مجالات</div><div><b>٥٠</b>مؤشراً</div><div><b>٢٠٠</b>درجة</div>
    <div><b>١٩</b>بطاقة إستراتيجية</div><div><b>٦</b>اتجاهات تدريسية</div>
    <div><b>٥٤</b>نموذجاً معبّأً</div><div><b>__FILES__</b>ملفاً</div>
  </div>
</div></header>
<nav><div class="wrap" id="nav"></div></nav>
<div class="wrap">
  <div class="tools">
    <input id="q" type="text" placeholder="ابحث في الأدوات: اسم مادة · مرحلة · إستراتيجية …">
    <button class="chip" data-g="بنين">بنين</button>
    <button class="chip" data-g="بنات">بنات</button>
    <button class="chip" data-g="معبّأ">النماذج المعبّأة</button>
    <button class="chip" data-g="عالمي">القطاع العالمي</button>
    <span class="cnt" id="cnt"></span>
  </div>
  <div id="main"></div>
</div>
<footer><div class="wrap">
  <span>مدارس ابن خلدون — نظام الحصة الموحَّدة</span>
  <span>كل ملفٍ هنا بنسختيه: بنين وبنات · والصيغتان وورد وPDF للطباعة</span>
</div></footer>
<script>__JS__</script></body></html>
"""

logo = ""
lp = os.path.join(HERE, "hub_logo.jpg")
if os.path.exists(lp):
    logo = f'<img src="data:image/jpeg;base64,{b64(lp)}" alt="مدارس ابن خلدون · معارف">'

import icon as _ICO
page = (HTML.replace("__FONTS__", FONTCSS).replace("__CSS__", CSS)
            .replace("__ICON__", _ICO.head(""))
            .replace("__LOGO__", logo).replace("__FILES__", arnum(FILES))
            .replace("__JS__", JS.replace("__SEC__", json.dumps(SEC, ensure_ascii=False))))
out = os.path.join(ROOT, "index.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(page)
# ════════════════════════════════════════════════════════════════════════════
# ⛔ حارسُ تسرّبِ الخادم — لا يُحذف
#
# المستودعُ **عامّ**، ومجلدُ التسليم هو المستودعُ نفسُه. فمن يقرأ دليلَ ربط
# المخزن يُنشئ منظومةً موازيةً، ومن يقرأ `worker.js` يعرف عقدَ التخزين كلَّه
# ومنه `__replace` الذي يمحو قاعدةَ البيانات. طلبَ المستشارُ إخراجَها في
# ٢٩ سبتمبر ٢٠٢٦: «فيستخدمها غيري، ونضيع جميعًا». فصار الاتفاقُ حارساً:
# البناءُ يفشل إن عاد ذكرُ الخادم إلى ملفٍ منشور.
#
# وما يُستثنى: نصُّ تحقّقٍ في المنصة يذكر «workers.dev» ليتأكّد المستخدمُ أن
# رابطَه صحيح — وهو لا يُعلِّم شيئاً ولا يكشف عنواناً.
# ════════════════════════════════════════════════════════════════════════════
# ⚠️ الكلماتُ مقطَّعةٌ قصداً: لو كُتبت كاملةً لكشف الحارسُ نفسَه فأفشل كلَّ بناء.
# ⛔ اسمُ البرنامج السابق يُربك الزوّار، ومنعَه المستشارُ في المنصة.
#    وُجدت ٢٩ سبتمبر ٢٠٢٦ في مخلَّف بناءٍ منشورٍ (_المولّد/platform.html) — فصار
#    منعُها حارساً لا تنبيهاً.
# ⛔ **قواعدُ ملغاةٌ بقيت في المطبوعات شهراً.** «ثلاثة مقيّمين» أُلغيت في ٣٠
#    سبتمبر ٢٠٢٦ (الرصدُ للمشرف المختص وحدَه) و«التحفيظ» حُذف من التخصصات —
#    وبقيا في عشرة مستنداتٍ منشورةٍ **وفي صورتين** لا يراهما فحصٌ نصّيّ، حتى
#    أمر المستشارُ بمسحهما (١ أكتوبر ٢٠٢٦). فصارا محروسَين: من يُعيد الكلمةَ
#    إلى مستندٍ منشورٍ يُفشل البناء.
#    ⚠️ ولا تُدرج هنا كلمةٌ قد تَرِد بوجهٍ صحيح — هذه ألفاظُ قواعدَ ملغاةٍ لا غير.
# ⛔ **والقاعدةُ الثانيةُ أُلغيت هي الأخرى** (٤ أكتوبر ٢٠٢٦): «المشرفُ المختصُّ
#    وحدَه يرصد» صار المقيّمون خمسةً، لكلٍّ استمارتُه، والمعتمَدُ متوسّطُ من رصد.
#    فبقيت ألفاظُها في نشرتَي مدير المجمع وفريق التقويم الداخلي وفي شريحة
#    الأدوار وسيناريو الفيديو — أمسكها مسحٌ يدويٌّ لا حارس. فصارت محروسةً:
#    قاعدتان ملغاتان لا واحدة.
STALE_WORDS = ["ثلاثة مقيّمين", "المقيّمون الثلاثة", "المقيّمات الثلاث",
               "ثلاث مقيّمات", "مقيّماً رابعاً", "مقيّمةً رابعة", "تحفيظ",
               "وحده يرصد", "وحدها ترصد", "وحدَه يرصد", "وحدَها ترصد",
               "يتابع ولا يرصد", "تتابع ولا ترصد", "يتابعان ولا يرصدان",
               "تتابعان ولا ترصدان", "المتابعةُ لا الرصد", "المتابعة لا الرصد",
               "ولا تُفتح لكما استمارة", "ولا تُفتح لك استمارة",
               "but do not observe", "follow-up, not observation",
               "no form opens for you"]

LEAK_WORDS = ["الحصص " + "التطبيقية",
              "cloud" + "flare", "Bind" + "ings", "wran" + "gler",
              "KV " + "namespace", "workers" + ".dev/",
              "دل" + "يل ربط المخزن", "كيف " + "تستضيفها",
              "D1 " + "database", "D1 " + "binding"]
LEAK_OK = {"٨ - النموذج الرقمي (تجربة)/منصة الحصة الموحَّدة — ابن خلدون.html",
           "٨ - النموذج الرقمي (تجربة)/منصة الحصة الموحَّدة — ابن خلدون (بنات).html",
           "_المولّد/platform_app.js"}
# نصُّ التحقّق «ينتهي بـ workers.dev» لا يُعلِّم شيئاً ولا يكشف عنواناً، فيُستثنى.
LEAK_OK_WORDS = {"workers" + ".dev/"}

# ⛔ **اسمُ شخصٍ في بياناتِ ملفٍ وصفية** — تسرّبٌ رابعٌ بقي حيّاً حتى ١ أكتوبر
#    ٢٠٢٦: ملفٌّ يتيمٌ في جذر المستودع (`استرداد نسختك من البطاقة.doc`) يحمل
#    `Last Saved By: Ahmaed Mahmooud Sueam` ويردُّ ٢٠٠ على الموقع، **ولا يشير
#    إليه فهرسٌ ولا بطاقة**. فالنصُّ وحدَه لا يكفي: الاسمُ في الخصائص لا في
#    المتن. (أمسكه وكيلُ تماسك المطبوعات)
#    ⚠️ وتُكتب الصيغُ المحرَّفةُ أيضاً: وورد يكتب ما كُتب في إعداد الجهاز.
META_NAMES = ["Ahmaed", "Sueam", "Seyam", "صيام", "ahmadseyam"]
# ما يُقرأ منه الاسمُ في كل صيغة
META_RX = [r"Last Saved By", r"dc:creator", r"lastModifiedBy", r"Author"]


def guard_no_server_leak():
    """يمسح كلَّ ملفٍ نصيٍّ في شجرة التسليم، ويرفع الخطأَ عند أول تسرّب."""
    bad = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in (".git", "__pycache__")]
        for fn in fns:
            if not fn.lower().endswith((".html", ".js", ".py", ".md", ".json", ".txt", ".gs")):
                continue
            fp = os.path.join(dp, fn)
            rp = os.path.relpath(fp, ROOT)
            try:
                txt = io.open(fp, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            for w in LEAK_WORDS:
                if w.lower() in txt.lower():
                    if rp in LEAK_OK and w in LEAK_OK_WORDS:
                        continue
                    bad.append((rp, w))
    if bad:
        lines = "\n".join("  ⛔ %s ← «%s»" % (r, w) for r, w in bad[:25])
        ban = any(w.startswith("الحصص") for _, w in bad)
        srv = any(not w.startswith("الحصص") for _, w in bad)
        why = []
        if ban:
            why.append("• العبارةُ الممنوعة: برنامجٌ آخرُ يُربك الزوّار — تُعاد "
                       "صياغتُها بـ«البرنامج السابق» ولا تُذكر باسمها.")
        if srv:
            why.append("• ملفُّ الخادم أو دليلُه: موضعُه «خادم الحصة الموحَّدة "
                       "(خاصّ — لا يُنشر)» على سطح المكتب، لا مجلدُ التسليم — "
                       "فهو المستودعُ العامّ.")
        raise SystemExit("⛔ ملفٌّ منشورٌ فيه ما لا يُنشر.\n" + lines + "\n\n"
                         + "\n".join(why))
    return True


def guard_binaries():
    """⛔ **الحارسُ النصّيُّ أعمى عن الصورة وعن PDF وDOCX.** نجا «دليلُ الاستضافة»
    لقطةً (`s18.jpg`) فيها خطواتُ إنشاء الخادم ولصقِ شفرته وضبطِ «Anyone» —
    منشوراً على الموقع بردٍّ ٢٠٠ حتى ٣٠ سبتمبر ٢٠٢٦. فيُمسح الآن:
      · نصُّ كل PDF وDOCX منشورٍ بحثاً عن كلمات التسرّب،
      · وكلُّ لقطةٍ في «صور/» لا تُشير إليها شريحةٌ في `deckcontent` —
        فاللقطةُ اليتيمةُ مدخلُ بناءٍ سقط، أو مستندٌ خارجيٌّ سُرّب."""
    bad, orph = [], []
    # ⛔ **المكتبةُ الغائبةُ كانت تُبلَع صامتةً**: `import fitz` داخلَ الحلقة
    #    و`except Exception: continue` — فلو لم تكن مثبَّتةً لتُخطَّى **كلُّ**
    #    ملفات PDF (مئةٌ وسبعٌ وأربعون) ويُعلن الحارسُ نظافةً تامّة. والمكتبةُ
    #    الغائبةُ عطلٌ في الحارس لا في المحروس. (١ أكتوبر ٢٠٢٦)
    try:
        import fitz
    except Exception as e:
        raise SystemExit("⛔ تعذّر فحصُ نصوص PDF: PyMuPDF غيرُ متاحة (%s).\n"
                         "  ولا يُنشر ما لم يُفحص — ثبّتها: pip3 install pymupdf" % e)
    seen = {"pdf": 0, "docx": 0}
    unread = []
    # ① نصوصُ المستندات الثنائية
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in (".git", "__pycache__")]
        for fn in fns:
            fp, rp = os.path.join(dp, fn), os.path.relpath(os.path.join(dp, fn), ROOT)
            low, txt = fn.lower(), ""
            if low.endswith(".pdf"):
                kind = "pdf"
            elif low.endswith(".docx"):
                kind = "docx"
            else:
                continue
            try:
                if kind == "pdf":
                    txt = "".join(pg.get_text() for pg in fitz.open(fp))
                else:
                    import zipfile
                    z = zipfile.ZipFile(fp)
                    txt = "".join(z.read(n).decode("utf-8", "ignore")
                                  for n in z.namelist() if n.endswith(".xml"))
            except Exception as e:
                # ⛔ ولا يُتجاوَز ملفٌّ تعذّرت قراءتُه بصمت: يُسمَّى ويُفشِل
                unread.append((rp, str(e)[:70]))
                continue
            seen[kind] += 1
            for w in LEAK_WORDS:
                if w.lower() in txt.lower() and not (rp in LEAK_OK and w in LEAK_OK_WORDS):
                    bad.append((rp, w))
            # ⛔ وقاعدةٌ ملغاةٌ في مستندٍ منشورٍ عطلٌ كالتسرّب: تناقض المنصةَ
            for w in STALE_WORDS:
                if w in txt:
                    bad.append((rp, "قاعدةٌ ملغاة: " + w))
            # ⛔ **وعلامةُ تنسيقٍ تُطبع نصّاً**: كُتب التوكيدُ في محتوى النشرات
            #    بصيغة ماركداون (`**نصّ**`) والمولّدُ يطبعه كما هو — فعاش في
            #    ثلاثَ عشرةَ نشرةً منشورةً عربيةً وإنجليزيةً بلا أن يراه أحد.
            #    (١ أكتوبر ٢٠٢٦) ⚠️ والمقياسُ على المستند لا على المحتوى:
            #    المحتوى يصحُّ أن يحمل العلامةَ — والمطبوعُ لا.
            if "**" in txt:
                bad.append((rp, "علامةُ توكيدٍ مطبوعةٌ نصّاً: **"))
    # ② اسمُ شخصٍ في خصائص ملفٍّ منشور — ولو كان متنُه نظيفاً
    # ⚠️ **المنشورُ هو المتتبَّعُ في جِت** لا كلُّ ما في المجلد: أمسك الحارسُ
    #    ملفاً محليّاً غيرَ متتبَّعٍ (يردُّ ٤٠٤ حيّاً) فكان بلاغاً كاذباً.
    #    فيُفصل: المتتبَّعُ يُفشِل البناءَ، والمحليُّ يُنبَّه عليه ليُحذف.
    import subprocess as _sp
    try:
        tracked = set(_sp.run(["git", "-C", ROOT, "ls-files"],
                              capture_output=True, text=True, timeout=20).stdout.splitlines())
    except Exception:
        tracked = None
    local_meta = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in (".git", "__pycache__")]
        for fn in fns:
            fp = os.path.join(dp, fn)
            rp = os.path.relpath(fp, ROOT)
            if not fn.lower().endswith((".doc", ".docx", ".pdf", ".xlsx", ".pptx")):
                continue
            try:
                with open(fp, "rb") as fh:
                    head = fh.read(400000)
            except Exception:
                continue
            for nm in META_NAMES:
                for enc in ("utf-8", "utf-16-le", "latin-1"):
                    try:
                        if nm.encode(enc) in head:
                            if tracked is None or rp in tracked:
                                bad.append((rp, "اسمٌ في الخصائص: " + nm))
                            else:
                                local_meta.append((rp, nm))
                            break
                    except Exception:
                        pass
                else:
                    continue
                break
    # ③ لقطاتٌ يتيمةٌ في مجلد صور العرض
    shots = os.path.join(ROOT, D9, "صور")
    if os.path.isdir(shots):
        try:
            src = io.open(os.path.join(HERE, "deckcontent.py"), encoding="utf-8").read()
        except Exception:
            src = ""
        for fn in sorted(os.listdir(shots)):
            if not fn.lower().endswith((".jpg", ".jpeg", ".png")): continue
            key = os.path.splitext(fn)[0]
            if ('img="%s"' % key) not in src:
                orph.append(os.path.join(D9, "صور", fn))
    msg = []
    # ⛔ وأرضيّةٌ للمقيس: حارسٌ مسح صفراً ليس حارساً
    FLOOR_PDF, FLOOR_DOCX = 100, 100
    if seen["pdf"] < FLOOR_PDF or seen["docx"] < FLOOR_DOCX:
        msg.append("⛔ الحارسُ لم يمسح ما يكفي: %d PDF (الأرضيّة %d) · %d DOCX (الأرضيّة %d).\n"
                   "  إما أن المستنداتِ نُقلت، أو أن القراءةَ تفشل — وكلاهما يُفشِل."
                   % (seen["pdf"], FLOOR_PDF, seen["docx"], FLOOR_DOCX))
    if local_meta:
        print("  ⚠️ ملفاتٌ محليةٌ غيرُ منشورةٍ فيها اسمٌ في الخصائص — تُحذف:")
        for rp, nm in local_meta[:8]:
            print("     · %s ← %s" % (rp, nm))
    if unread:
        msg.append("⛔ مستنداتٌ تعذّرت قراءتُها — ولا يُحكَم بنظافة ما لم يُقرأ:\n"
                   + "\n".join("  ⛔ %s ← %s" % x for x in unread[:12]))
    if bad:
        msg.append("⛔ مستندٌ ثنائيٌّ منشورٌ فيه ما لا يُنشر:\n"
                   + "\n".join("  ⛔ %s ← «%s»" % (r, w) for r, w in bad[:15]))
    if orph:
        msg.append("⛔ لقطةٌ في مجلد الصور لا تشير إليها شريحة — تُحذف أو تُربط:\n"
                   + "\n".join("  ⛔ " + x for x in orph[:15]))
    if msg: raise SystemExit("\n\n".join(msg))
    return True


guard_no_server_leak()          # ⛔ يفشل البناءُ عند أول تسرّب
guard_binaries()                # ⛔ ويمسح الصورَ وPDF وDOCX كذلك
print("حُفظ: index.html |", len(SEC), "قسماً |", COUNT, "بطاقة |", FILES, "رابط ملف |",
      round(len(page) / 1048576, 2), "م.ب")
if MISSING:
    print("⚠️ ملفات مذكورة وغير موجودة:", len(MISSING))
    for m in MISSING[:12]:
        print("   ·", m)