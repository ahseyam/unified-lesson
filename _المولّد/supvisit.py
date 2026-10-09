# -*- coding: utf-8 -*-
"""جدولُ زيارات الإشراف التربوي على المجمعات — بالتخصصات.

⛔ **ولماذا؟** طلبُ المستشار ٨ أكتوبر ٢٠٢٦: «أريد جدولاً للمجمعات لتحديد
   زيارات الإشراف للتخصصات». فالحصةُ الموحَّدةُ تدور: مجموعةُ موادَّ في
   مجمعٍ يومَ الأحد تكون في مجمعٍ آخرَ يومَ الاثنين. فمشرفُ الرياضياتِ لا
   يعرف أين يكون إلا بهذا الجدول.

⚠️ **ولا يُؤلَّف هنا شيء**: الدورانُ من `scheddata.SUP6` عينِه الذي يُبنى به
   الجدولُ في المنصة، وأسماءُ المشرفين من `supdb` المستخرَج من قاعدة الإشراف.
   فلو تغيّر الدورانُ تغيّر الورقُ معه — ولا نسختان تفترقان.
⚠️ و«عرقه» في جدول الدوران و«عرقة» في سجلّ الإشراف — اسمٌ واحدٌ بهجاءين،
   فيُطبَّع قبل المطابقة، وإلّا خلا جدولُ كلِّ مشرفٍ في عرقة من يومٍ واحد.
⚠️ وجدولُ كلِّ مشرفٍ **مقصورٌ على مجمعاته**: من نطاقُه مجمعان لا يُعطى
   جدولَ أربعة فيذهب حيث لا عملَ له.

الاستعمال:
    python3 supvisit.py [مجلَّدُ المخرَج]
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# ⛔ **قبل استيراد `dox`**: الطقمُ يُقرأ عند الاستيراد، فضبطُه بعده لا أثرَ له
#    وتخرج المطبوعةُ بخطّ دبي صامتةً. (طقم «js» = الجزيرة للعناوين والتسميات،
#    وسكال مجلة للمتن مكبَّراً ×١٫٢٥ لأنّه يُرسم أصغر بالمقاس نفسه.)
os.environ.setdefault("CLS_FONTSET", "js")
from docx import Document
from dox import (run, rtl_par, par_space, make_table, cell_text, cell_shd,
                 row_height, row_nosplit, normalize_tables, par_border_bottom, par_keep)
import pagekit
import scheddata as SD
import supdb

NAVY, TEAL, RED, OKC = "355E91", "2F7F95", "C00000", "2E7D32"
HEADBG, ZEBRA, OFFBG = "E9EEF6", "F6F8FB", "F0F0F0"
DAYS = SD.DAYS


def cxnorm(s):
    """«عرقه» و«عرقة» مجمعٌ واحد — والمطابقةُ تسقط بلا هذا."""
    return str(s or "").replace("عرقه", "عرقة").strip()


HERE = os.path.dirname(os.path.abspath(__file__))


# ⛔ **ولا كشفَ معلمين هنا ولا بيانات حصّة** (قرارُ المستشار ٨ أكتوبر ٢٠٢٦):
#    «ما يهمّنا جداولُ التنفيذ، ولا يعنينا اسمُ المعلم ولا بياناتُ الحصة».
#    فنُزعت قراءةُ `roster.json` وعدُّ التابعين — والمطبوعُ خريطةُ تنفيذٍ
#    خالصة: مجمعٌ ويومٌ وأسبوعٌ وتخصّص. (وكان العدُّ يُظهر صفراً كاذباً
#    لمشرفي العالمي أصلاً — فالكشفُ لا يصنّف العالميَّ.)
def G(gender, m, f):
    """⛔ ولا نصَّ مذكَّرٌ في مطبوع البنات: «مجمعاته» و«نطاقه» و«لا زيارةَ له»
       كانت تُطبَع للمشرفات. ولا مؤنِّثَ آليٌّ هنا (`femjs` للجافاسكربت
       وحدَها)، فالصيغتان مكتوبتان ويُنتقى بينهما بالقسم."""
    return m if gender == "m" else f


def sechead(doc, txt, before=12, after=3):
    """عنوانُ قسمٍ: **أحمرُ متوسَّط** — تعديلُ المستشار بيده على المطبوع
       (٨ أكتوبر ٢٠٢٦، قِيس بمقابلة نسخته بمخرَج المولّد: لونٌ ومحاذاةٌ لا
       غير). ونُقل إلى المولّد لئلّا يمحوَه توليدٌ تالٍ — ومطبوعٌ يُعدَّل
       بيدٍ ولا يتبعه مولّدُه يعود إلى حاله عند أول تشغيل."""
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    p = doc.add_paragraph(); rtl_par(p); par_space(p, before, after)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, txt, size=14, bold=True, color=RED)
    return p


def glabel(g):
    """⛔ **مفاتيحُ المجموعات داخليةٌ لا تُعرض**: «رياضيات واجتماعيات» مفتاحٌ
       أعضاؤه (رياضيات، الفنية) — نُقلت الفنيةُ محلَّ الاجتماعيات بقرار ٧
       أكتوبر، وبقي المفتاحُ لأنّ `ROT6`/`SUP6` مبنيّتان عليه. والاسمُ
       المعروضُ في `GROUP_LABEL` — وطبعُ المفتاح يُضلّل قارئَ الورق."""
    return SD.GROUP_LABEL.get(g, g)


def mins(t):
    """وقتٌ بالأرقام الهندية ← دقائقُ من منتصف الليل (وما دون السابعة مساءً)."""
    t = str(t).translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")).strip()
    h, m = t.split(":")
    h = int(h) + (12 if int(h) < 7 else 0)
    return h * 60 + int(m)


def arn(n):
    return str(n).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))


def weeks_of(g):
    return list(SD.SUP6[g].keys())


def grid(doc, rows, widths, red=(), off=(), whole=True):
    """⚠️ و`whole` يُبقي الجدولَ صفحةً واحدة: `keepNext` على فقرات كلِّ صفٍّ
       إلا الأخير. و**بعد تعبئة الخانات لا قبلها** — فتعبئتُها تمسح الفقرةَ
       التي ضُبطت، فيموت الضبطُ صامتاً (وقد قِيس من قبلُ في مطبوعٍ آخر)."""
    t = make_table(doc, len(rows), widths)
    for i, r0 in enumerate(t.rows):
        row_height(r0, 0.7 if i else 0.8)
        row_nosplit(r0)
        for j, c in enumerate(r0.cells):
            txt = rows[i][j]
            cell_text(c, txt, size=9.5 if i else 10.5, bold=(i == 0),
                      color=NAVY if i == 0 else (RED if (i, j) in red else None),
                      align="center")
            if i == 0:
                cell_shd(c, HEADBG)
            elif (i, j) in off:
                cell_shd(c, OFFBG)
            elif i % 2 == 0:
                cell_shd(c, ZEBRA)
    if whole:
        for r0 in list(t.rows)[:-1]:
            for c in r0.cells:
                for pp in c.paragraphs:
                    par_keep(pp)
    return t


def build(gender, out):
    os.environ["CLS_GENDER"] = gender
    sup = supdb.BOYS if gender == "m" else supdb.GIRLS
    ttl = "قسم البنين" if gender == "m" else "قسم البنات"
    doc = Document()
    pagekit.portrait(doc)

    p = doc.add_paragraph(); rtl_par(p); par_space(p, 0, 2)
    run(p, "جدولُ زيارات الإشراف التربوي على المجمعات", size=18, bold=True, color=NAVY)
    p = doc.add_paragraph(); rtl_par(p); par_space(p, 0, 8)
    run(p, ttl + " — الحصةُ الموحَّدة — الأسابيع " + arn(8) + " إلى " + arn(15),
        size=12.5, bold=True, color=TEAL)
    par_border_bottom(p)

    # ── تمريرةٌ أولى: من يبقى في المطبوع، وأيُّ تخصصٍ له مشرفٌ مختصّ ──
    spec2grp = {}
    for g0, subs0 in SD.PAIRS.items():
        for s0 in subs0:
            spec2grp[s0] = g0
    keep, dropped = [], []
    for row in sup:
        grps = [spec2grp[x] for x in row[3] if x in spec2grp and spec2grp[x] in SD.SUP6]
        grps = list(dict.fromkeys(grps))
        if not grps:
            dropped.append((row[0], row[2], "لا تقابله مجموعةٌ في الحصة الموحَّدة"))
            continue
        keep.append((row, grps))
    bySpec = {}
    for row, _ in keep:
        for x in row[3]:
            bySpec.setdefault(x, []).append(row[0])

    p = doc.add_paragraph(); rtl_par(p); par_space(p, 6, 10)
    run(p, "كيف يُقرأ: ", size=10.5, bold=True, color=NAVY)
    run(p, "الحصةُ الموحَّدةُ تدور بين المجمعات الأربعة، فمجموعةُ الموادِّ "
           "الواحدةُ تُنفَّذ في مجمعٍ كلَّ يوم. والخانةُ تُقرأ: في هذا الأسبوع "
           "وهذا اليوم، تكون الزيارةُ في هذا المجمع.", size=10.5)

    # ── ① المجمعاتُ ومدارسُها وأوقاتُ حصصها ──
    # ⚠️ وهي ما يحتاجه الزائرُ بعد أن يعرف مجمعَه: أيُّ مدرسةٍ في أيِّ حصة،
    #    وفي أيِّ ساعةٍ يدخل. وتُقرأ من `BANDS` نفسِه الذي يبني الجدول.
    sechead(doc, "أولاً: المجمعاتُ ومدارسُها وأوقاتُ الحصص", 10, 4)
    pers = ["الحصة %d" % i for i in range(1, 7)]
    rows = [["المجمع"] + ["الحصة " + arn(pr.split()[-1]) for pr in pers]]
    for cx in SD.ROT6:
        bd = {b["per"]: b for b in SD.BANDS.get(cx, [])}
        line = [cxnorm(cx)]
        for pr in pers:
            b = bd.get(pr)
            line.append((b["stage"].split("-")[0].strip() + "\n" + b["time"]) if b else "—")
        rows.append(line)
    # ⚠️ ويُلوَّن ما خالف الوقتَ الغالبَ في الحصة نفسِها — فتُرى الفروقُ
    #    بالعين لا بالمقابلة اليدوية.
    tmap = {}
    for i, cxn in enumerate([cxnorm(c) for c in SD.ROT6], start=1):
        for j, pr in enumerate(pers, start=1):
            tmap[(i, j)] = rows[i][j].split("\n")[-1]
    red = set()
    for j, pr in enumerate(pers, start=1):
        col = [tmap[(i, j)] for i in range(1, len(rows))]
        common = max(set(col), key=col.count)
        for i in range(1, len(rows)):
            if tmap[(i, j)] != common:
                red.add((i, j))
    grid(doc, rows, [2.6, 2.3, 2.3, 2.3, 2.3, 2.3, 2.3], red=red)
    p = doc.add_paragraph(); rtl_par(p); par_space(p, 3, 0)
    run(p, "واسمُ المدرسة يُقرأ بمجمعه: «الابتدائية» في النفل هي "
           "«الابتدائية- النفل». والأحمرُ وقتٌ يخالف سائرَ المجمعات في الحصة نفسِها.",
        size=9.5, color="666666")

    # ── تناسقُ التوقيتات — مبنيٌّ من الأوقات نفسِها لا مكتوباً بيد ──
    # ⛔ طلبُ المستشار ٨ أكتوبر ٢٠٢٦: «يهمّني تناسقُ التوقيتات لحضور الحصص
    #    سواءٌ بواسطة إدارات المدارس أو المشرفين التربويين».
    # ⚠️ **ويُحسب من `BANDS`**: نصٌّ مكتوبٌ بيدٍ يتقادم إذا بُدّل وقتُ حصة،
    #    فيبقى في الورق وعدٌ لا يفي به الجدول.
    p = doc.add_paragraph(); rtl_par(p); par_space(p, 12, 3)
    run(p, "تناسقُ التوقيتات", size=12.5, bold=True, color=TEAL)
    same, diff = [], []
    for pr in pers:
        v = {cxnorm(c): [b for b in SD.BANDS[c] if b["per"] == pr][0]["time"]
             for c in SD.BANDS}
        (same if len(set(v.values())) == 1 else diff).append((pr, v))
    if same:
        p = doc.add_paragraph(); rtl_par(p); par_space(p, 0, 2)
        run(p, "موحَّدةٌ في المجمعات الأربعة: ", size=10.5, bold=True, color=OKC)
        run(p, "، ".join(pr + " (" + list(v.values())[0] + ")" for pr, v in same),
            size=10.5)
    for pr, v in diff:
        p = doc.add_paragraph(); rtl_par(p); par_space(p, 0, 2)
        run(p, pr + " تختلف: ", size=10.5, bold=True, color=RED)
        run(p, "، ".join("%s %s" % (c, t) for c, t in v.items()), size=10.5)
    gaps = []
    for c, bl in SD.BANDS.items():
        ms = [mins(b["time"]) for b in bl]
        gaps += [ms[i + 1] - ms[i] for i in range(len(ms) - 1)]
    p = doc.add_paragraph(); rtl_par(p); par_space(p, 4, 0)
    run(p, "وأوقاتُ كلِّ مجمعٍ متصاعدةٌ بفاصلٍ لا يقلُّ عن " + arn(min(gaps)) +
           " دقيقة، فيمكن للزائر — مشرفاً كان أو من إدارة المدرسة — أن يحضر "
           "حصصَ اليوم الستَّ في مجمعٍ واحدٍ تتابعاً: الابتدائيةُ ثم المتوسطةُ "
           "ثم الثانوية. ولا تُطلب مجموعةُ تخصصٍ في مجمعين في يومٍ واحد.",
        size=10.5)

    # ── ② المعلمون: يومُ حصة كلِّ تخصصٍ في مجمعه ──
    # ⛔ طلبُ المستشار: «جدولٌ للتخصصات للمعلمين حسب اليوم المخصص لهم لإعداد
    #    حصص». وهو قلبُ جدول الزيارات: المشرفُ يسأل «أين أكون؟» والمعلمُ
    #    يسأل «متى أُعدّ حصّتي؟» — والمصدرُ واحدٌ (`ROT6`).
    sechead(doc, "ثانياً: يومُ الحصة لكل تخصصٍ في مجمعه — للمعلمين", 14, 3)
    p = doc.add_paragraph(); rtl_par(p); par_space(p, 0, 6)
    run(p, G(gender, "يقرأ المعلمُ سطرَ تخصصه في جدول مجمعه، فيعرف يومَ حصته "
                     "في كل أسبوعٍ فيُعدّ لها.",
                     "تقرأ المعلمةُ سطرَ تخصصها في جدول مجمعها، فتعرف يومَ حصتها "
                     "في كل أسبوعٍ فتُعدّ لها."), size=10.5)
    wks = weeks_of(SD.GROUPS[0])
    spec2grp = {}
    for g0, subs0 in SD.PAIRS.items():
        for s0 in subs0:
            spec2grp[s0] = g0
    for cx in SD.ROT6:
        p = doc.add_paragraph(); rtl_par(p); par_space(p, 10, 3)
        run(p, "مجمع " + cxnorm(cx), size=12.5, bold=True, color=TEAL)
        par_keep(p)
        rows = [["التخصص"] + [arn(8 + i) for i in range(len(wks))]]
        for sp in SD.SPECS:
            g0 = spec2grp.get(sp)
            if not g0 or g0 not in SD.SUP6:
                continue
            line = [sp]
            for wk in wks:
                dd = SD.ROT6.get(cx, {}).get(wk, {})
                day = next((d for d in DAYS if dd.get(d) == g0), "—")
                line.append(day)
            rows.append(line)
        grid(doc, rows, [3.1] + [1.95] * len(wks))
    p = doc.add_paragraph(); rtl_par(p); par_space(p, 3, 0)
    run(p, "والأرقامُ في الرأس أرقامُ الأسابيع (" + arn(8) + " — " + arn(15) + ").",
        size=9.5, color="666666")

    # ── ③ من يحضر حصةَ كل تخصص ──
    # ⛔ طلبُ المستشار ٨ أكتوبر ٢٠٢٦: «اكتب نصاً بجوار تخصص المواد التي ليس
    #    لها مشرفٌ مختصٌّ بأن يحضر حصصَها الوكيلُ التعليميُّ أو مديرُ المدرسة».
    #    وهو عينُ قاعدة الرصد في المنصة: ما لا مشرفَ له فمدرستُه تتولّاه.
    sechead(doc, "ثالثاً: من يحضر حصةَ كل تخصص", 14, 3)
    rows = [["التخصص", G(gender, "المشرفُ المختصّ", "المشرفةُ المختصّة"),
             "من يحضر الحصة"]]
    nosup = 0
    for sp in SD.SPECS:
        if spec2grp.get(sp) not in SD.SUP6:
            continue
        who = bySpec.get(sp) or []
        if who:
            rows.append([sp, "، ".join(who), G(gender, "مشرفُ المادة", "مشرفةُ المادة")])
        else:
            nosup += 1
            rows.append([sp, "—", G(gender,
                "لا مشرفَ مختصّ — يحضر الحصةَ الوكيلُ التعليميُّ أو مديرُ المدرسة",
                "لا مشرفةَ مختصّة — تحضر الحصةَ الوكيلةُ التعليميةُ أو مديرةُ المدرسة")])
    red = {(i, 2) for i, r0 in enumerate(rows) if i and r0[1] == "—"}
    grid(doc, rows, [2.6, 7.4, 8.0], red=red)

    # ── ④ جدولُ المجموعات: لكل مجموعةٍ أسابيعُها وأيامُها ──
    sechead(doc, "رابعاً: المجمعُ المستهدَف لكل مجموعةِ تخصصات", 14, 4)
    for g in SD.GROUPS:
        if g not in SD.SUP6:
            continue
        p = doc.add_paragraph(); rtl_par(p); par_space(p, 10, 3)
        run(p, glabel(g), size=12.5, bold=True, color=TEAL)
        run(p, "   (" + "، ".join(SD.PAIRS.get(g, [])) + ")", size=10, color="666666")
        par_keep(p)
        rows = [["الأسبوع"] + DAYS]
        for wk in weeks_of(g):
            dd = SD.SUP6[g][wk]
            rows.append([wk] + [cxnorm(dd.get(d)) or "—" for d in DAYS])
        grid(doc, rows, [4.0, 2.9, 2.9, 2.9, 2.9])

    # ── ② لكل مشرفٍ جدولُه، مقصوراً على مجمعاته ──
    doc.add_page_break()
    sechead(doc, "خامساً: " + G(gender, "جدولُ كلِّ مشرفٍ في نطاقه",
                                "جدولُ كلِّ مشرفةٍ في نطاقها"), 0, 4)
    p = doc.add_paragraph(); rtl_par(p); par_space(p, 0, 8)
    run(p, G(gender, "والخانةُ الرماديةُ مجمعٌ خارجَ نطاق المشرف — لا زيارةَ له فيه.",
                     "والخانةُ الرماديةُ مجمعٌ خارجَ نطاق المشرفة — لا زيارةَ لها فيه."),
        size=10, color="666666")

    done = 0
    greys = 0
    # ⛔ ولا يُذكر من لا تقابله مجموعةٌ البتّة — لا بجدولٍ ولا بسطرٍ أحمر:
    #    «فقط المشرفون المخصَّصُ لهم معلمون لزيارتهم».
    for row, grps in keep:
        name, emp, job, subs, cxs, stages, sectors, flags, note = row
        mine = set(cxnorm(c) for c in cxs)
        p = doc.add_paragraph(); rtl_par(p); par_space(p, 12, 2)
        run(p, name, size=12.5, bold=True, color=NAVY)
        p = doc.add_paragraph(); rtl_par(p); par_space(p, 0, 3)
        run(p, job, size=10, color="666666")
        # ⚠️ والفاصلُ بين الأسماء فاصلةٌ عربيةٌ لا «·»: المنقوطةُ تُقرأ صفراً
        #    هنديّاً في هذا الخطّ («المنار · النفل» تبدو «المنار ٠ النفل»).
        run(p, "   —   " + G(gender, "مجمعاته: ", "مجمعاتها: ") + "، ".join(sorted(mine)),
            size=10, color=TEAL)
        if stages:
            run(p, "   —   " + "، ".join(stages), size=10, color="666666")
        done += 1
        for g in grps:
            rows = [["الأسبوع"] + DAYS]
            off = []
            for wk in weeks_of(g):
                dd = SD.SUP6[g][wk]
                line = [wk]
                for j, d in enumerate(DAYS, start=1):
                    cx = cxnorm(dd.get(d))
                    if cx and cx in mine:
                        line.append(cx)
                    else:
                        line.append(cx or "—")
                        off.append((len(rows), j))
                rows.append(line)
            p = doc.add_paragraph(); rtl_par(p); par_space(p, 4, 2)
            run(p, glabel(g), size=11, bold=True, color=TEAL)
            par_keep(p)
            greys += len(off)
            grid(doc, rows, [4.0, 2.9, 2.9, 2.9, 2.9], off=set(off))

    # ── ③ فريقُ الهوية الوطنية: جدولُه ثابتٌ لا يدور ──
    sechead(doc, "سادساً: " + SD.NAT_GROUP, 14, 3)
    p = doc.add_paragraph(); rtl_par(p); par_space(p, 0, 4)
    run(p, "فريقُ ثلاثِ موادَّ في القطاع العالمي (" + "، ".join(SD.NAT_SPECS) +
           ") — وجدولُه ثابتٌ لا يدور بالأسابيع. " +
           G(gender, "ومشرفُه: ", "ومشرفتُه: ") + SD.NAT_SUP.get(gender, "—"),
        size=10.5)
    grid(doc, [["اليوم"] + DAYS, ["المجمع"] + [cxnorm(SD.NAT_DAYS.get(d)) or "—" for d in DAYS]],
         [4.0, 2.9, 2.9, 2.9, 2.9])

    p = doc.add_paragraph(); rtl_par(p); par_space(p, 14, 0)
    run(p, "صدر في " + datetime.datetime.now().strftime("%Y-%m-%d") +
           " — مبنيٌّ من جدول الدوران نفسِه الذي تعمل به المنصة.",
        size=9.5, color="666666")

    normalize_tables(doc)
    doc.save(out)
    return len(sup), done, greys, dropped, nosup


MASC = ["مجمعاته:", "في نطاقه", "لا زيارةَ له فيه", "دورانٍ له.", "ومشرفُه:",
        "كلِّ مشرفٍ"]
FEM  = ["مجمعاتها:", "في نطاقها", "لا زيارةَ لها فيه", "دورانٍ لها.", "ومشرفتُه:",
        "كلِّ مشرفةٍ"]


def audit(path, gender):
    """⛔ حارسُ الجنس والهجاء على **المطبوع نفسِه** لا على الشفرة: صياغةٌ
       تُنسى فتُطبَع للمشرفات بصيغة المذكَّر، ولا يكشفها إلا قراءةُ المخرَج.
       ⚠️ ويُقاس أنّه يقيس: يُجرَّب على مخرَج القسم الآخر فيجب أن يُنذر."""
    from docx import Document as _D
    d = _D(path)
    txt = "\n".join(x.text for x in d.paragraphs)
    for t in d.tables:
        for r in t.rows:
            for c in r.cells:
                txt += "\n" + c.text
    # ⛔ **والمطابقةُ بالحدِّ لا بالاحتواء**: «نطاقها» تحوي «نطاقه» حرفاً
    #    بحرف، فأنذر الحارسُ على نصٍّ مؤنَّثٍ صحيح. فيُشترط ألّا يتبعَ
    #    الكلمةَ حرفٌ عربيّ. (وهو عينُ مزلق «ع» في «علوم».)
    import re as _re
    pats = FEM if gender == "m" else MASC
    bad = [w for w in pats
           if _re.search(_re.escape(w) + r"(?![\u0621-\u064A])", txt)]
    if _re.search(r"عرقه(?![\u0621-\u064A])", txt):
        bad.append("هجاءُ «عرقه» (الصواب «عرقة»)")
    return bad, len(txt)


def crosscheck(path):
    """⛔ **خانةُ المطبوع تُقابَل بالمصدر خانةً خانة** — ولا يكفي أنّ المولّد
       قرأ المصدرَ صحيحاً: ترتيبُ الأعمدة في جدولٍ من اليمين إلى اليسار،
       أو سطرٌ أُزيح، يُخرج ورقاً مقلوباً والشفرةُ سليمة.
    ⚠️ وتُقابَل ثلاثُ طبقات: أوقاتُ المجمعات · يومُ كلِّ تخصصٍ في مجمعه ·
       مجمعُ كلِّ مجموعةٍ في كل أسبوعٍ ويوم. وتُحصى المقابلاتُ ويُشترط
       عددُها — فجدولٌ لم يُقرأ لا يُعلَن سليماً."""
    from docx import Document as _D
    d = _D(path)
    spec2grp = {}
    for g0, subs0 in SD.PAIRS.items():
        for s0 in subs0:
            spec2grp[s0] = g0
    wks = weeks_of(SD.GROUPS[0])
    cxs = [cxnorm(c) for c in SD.ROT6]
    bad, hit = [], 0
    for t in d.tables:
        head = [c.text.strip() for c in t.rows[0].cells]
        # ① جدولُ المجمعات والأوقات
        if head[0] == "المجمع" and head[1].startswith("الحصة"):
            for r0 in t.rows[1:]:
                cells = [c.text.strip() for c in r0.cells]
                c0 = cells[0]
                src = {b["per"]: b for b in SD.BANDS[
                    next(k for k in SD.BANDS if cxnorm(k) == c0)]}
                for j, pr0 in enumerate(head[1:], start=1):
                    # الرأسُ معروضٌ بالأرقام الهندية، ومفتاحُ المصدر لاتينيّ
                    pr = pr0.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
                    want = (src[pr]["stage"].split("-")[0].strip(), src[pr]["time"])
                    got = tuple(x.strip() for x in cells[j].split("\n"))
                    hit += 1
                    if got != want:
                        bad.append("أوقات %s/%s: %s ≠ %s" % (c0, pr, got, want))
        # ② جدولُ التخصصات في مجمعٍ (الرأس: التخصص + أرقام الأسابيع)
        elif head[0] == "التخصص" and len(head) == 1 + len(wks):
            cxn = None
            for q in d.paragraphs:
                pass
            # المجمعُ يُستنتج من مطابقة أيِّ سطرٍ بالمصدر — ولا يُفترض الترتيب
            cand = []
            r1 = [c.text.strip() for c in t.rows[1].cells]
            for c in cxs:
                ok = True
                for j, wk in enumerate(wks, start=1):
                    dd = SD.ROT6[next(k for k in SD.ROT6 if cxnorm(k) == c)][wk]
                    g0 = spec2grp[r1[0]]
                    want = next((x for x in DAYS if dd.get(x) == g0), "—")
                    if r1[j] != want:
                        ok = False; break
                if ok: cand.append(c)
            if len(cand) != 1:
                bad.append("جدولُ تخصصاتٍ لا يطابق مجمعاً واحداً بعينه: %s" % cand)
                continue
            cxn = cand[0]
            for r0 in t.rows[1:]:
                cells = [c.text.strip() for c in r0.cells]
                g0 = spec2grp.get(cells[0])
                for j, wk in enumerate(wks, start=1):
                    dd = SD.ROT6[next(k for k in SD.ROT6 if cxnorm(k) == cxn)][wk]
                    want = next((x for x in DAYS if dd.get(x) == g0), "—")
                    hit += 1
                    if cells[j] != want:
                        bad.append("تخصص %s/%s/%s: %s ≠ %s"
                                   % (cxn, cells[0], wk, cells[j], want))
        # ③ جداولُ الأسابيع × الأيام ← مجمع
        elif head[0] == "الأسبوع" and head[1:] == DAYS:
            rowsrc = {}
            for g0 in SD.SUP6:
                ok = all(cxnorm(SD.SUP6[g0][r0.cells[0].text.strip()].get(dy))
                         == r0.cells[k].text.strip()
                         for r0 in t.rows[1:] for k, dy in enumerate(DAYS, start=1)
                         if r0.cells[0].text.strip() in SD.SUP6[g0])
                if ok: rowsrc[g0] = True
            if not rowsrc:
                # جدولُ مشرفٍ: خاناتٌ خارجَ نطاقه تُطبَع كما هي، فيُقابَل بالمجموعة
                got = [[c.text.strip() for c in r0.cells] for r0 in t.rows[1:]]
                m = [g0 for g0 in SD.SUP6
                     if all(cxnorm(SD.SUP6[g0].get(r[0], {}).get(dy, "")) == r[k]
                            for r in got for k, dy in enumerate(DAYS, start=1))]
                if not m:
                    bad.append("جدولٌ أسبوعيٌّ لا يطابق أيَّ مجموعة: %s" % got[0])
                    continue
                rowsrc[m[0]] = True
            hit += (len(t.rows) - 1) * len(DAYS)
    return bad, hit


def main():
    # ⛔ ولا يُكتب في شجرة التسليم: فيه أسماءُ مشرفين، والمستودعُ عامٌّ منشور.
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
        "~/Desktop/تقارير الحصة الموحَّدة")
    os.makedirs(outdir, exist_ok=True)
    for g, nm in (("m", "بنين"), ("f", "بنات")):
        out = os.path.join(outdir, "جدول زيارات الإشراف على المجمعات — %s.docx" % nm)
        n, d, gy, dr, ns = build(g, out)
        bad, ln = audit(out, g)
        if bad:
            print("  ⛔ %s: نصٌّ بجنسٍ خاطئ أو هجاءٍ خاطئ: %s" % (nm, " · ".join(bad)))
            return 1
        print("  ✓ %s: %d مشرفاً · %d لهم جدولُ دوران · %d خانةً رماديةً خارجَ "
              "النطاق · %d حرفاً مفحوصاً → %s"
              % (nm, n, d, gy, ln, os.path.basename(out)))
        print("     · %d تخصصاً بلا مشرفٍ مختصّ ← الوكيل التعليمي أو مدير المدرسة" % ns)
        xbad, xhit = crosscheck(out)
        if xbad:
            print("  ⛔ %s: المطبوعُ يخالف المصدر في %d خانة:" % (nm, len(xbad)))
            for b in xbad[:8]:
                print("      · " + b)
            return 1
        if xhit < 400:
            print("  ⛔ %s: المقابلةُ لم تقرأ إلا %d خانة — فلا تُعتمد" % (nm, xhit))
            return 1
        print("     ✓ قوبلت %d خانةً بالمصدر خانةً خانة" % xhit)
        for x in dr:
            print("     — طُوي: %s (%s) — %s" % (x[0], x[1], x[2]))
        if not gy:
            # ⛔ فرعٌ لم يُنفَّذ مرّةً واحدةً لا يُقال إنّه يعمل
            print("  ⛔ ولا خانةَ رماديةَ البتّة — فحارسُ النطاق لم يُقَس")
            return 1
    # ⚠️ وتجربةُ الكاشف على مخرَجٍ يُعلَم عيبُه: مطبوعُ البنين يُقاس بمعيار
    #    البنات فيجب أن يُنذر — وإلّا فالحارسُ لا يقيس شيئاً.
    probe, _ = audit(os.path.join(outdir,
                     "جدول زيارات الإشراف على المجمعات — بنين.docx"), "f")
    print("  ✓ والحارسُ يقيس: مطبوعُ البنين بمعيار البنات ← %d إنذاراً" % len(probe))
    if not probe:
        print("  ⛔ الحارسُ لا يكشف شيئاً — فلا يُعتمد")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
