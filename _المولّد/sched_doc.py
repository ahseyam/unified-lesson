# -*- coding: utf-8 -*-
"""نشرة آلية الحصص الموحَّدة — صفحة تُطبع وتُعلَّق: القواعد الخمس · الأدوار · دوران المشرفين.
الاستعمال: CLS_FONTSET=js CLS_GENDER=m|f CLS_SECTOR=nat|intl python3 sched_doc.py <الملف>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx import Document
from docx.shared import Cm
from docx.oxml.ns import qn, nsdecls
from docx.oxml import OxmlElement, parse_xml
from dox import *
from dox import GENDER, _add_pPr_el, _trPr_set, _tcPr_set, _insert_ordered

NAVY, TEAL, TEALBG = "355E91", "2F7F95", "E2F0F3"
RED, HEADBG, NUMBG, ZEBRA, INNER = "C00000", "D9D9D9", "E9EEF6", "F6F8FB", "C9D2DE"
GREY, INK = "7F7F7F", "1A1A1A"
W = 19.0
HERE = os.path.dirname(os.path.abspath(__file__))
KLISHA = os.path.join(HERE, "kl_portrait.jpg")
G = lambda m, f: f if GENDER == "f" else m

doc = Document(); set_doc_defaults(doc); set_compat15(doc)
s = doc.sections[0]
s.page_width, s.page_height = Cm(21.0), Cm(29.7)
s.left_margin = s.right_margin = Cm(1.0)
s.top_margin, s.bottom_margin = Cm(2.85), Cm(2.7)
s.header_distance, s.footer_distance = Cm(0.2), Cm(1.6)
s._sectPr.append(OxmlElement('w:bidi'))
hp = s.header.paragraphs[0]; hp.text = ""
par_space(hp, 0, 0)
r = hp.add_run(); r.add_picture(KLISHA, width=Cm(21.0), height=Cm(29.7))
inline = r._r.find('.//' + qn('wp:inline')); graphic = inline.find(qn('a:graphic'))
anchor = parse_xml(f'<wp:anchor {nsdecls("wp")} distT="0" distB="0" distL="0" distR="0" simplePos="0" '
    'relativeHeight="0" behindDoc="1" locked="1" layoutInCell="1" allowOverlap="1">'
    '<wp:simplePos x="0" y="0"/><wp:positionH relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionH>'
    '<wp:positionV relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionV>'
    '<wp:extent cx="7560000" cy="10692000"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
    '<wp:wrapNone/><wp:docPr id="901" name="klisha"/><wp:cNvGraphicFramePr/></wp:anchor>')
anchor.append(graphic); inline.getparent().replace(inline, anchor)


def frame(t, outer=NAVY, osz=16, inner=INNER, isz=4):
    tblPr = t._tbl.tblPr
    for old in tblPr.findall(qn('w:tblBorders')): tblPr.remove(old)
    bd = OxmlElement('w:tblBorders')
    for side, col, sz in (('top', outer, osz), ('left', outer, osz), ('bottom', outer, osz),
                          ('right', outer, osz), ('insideH', inner, isz), ('insideV', inner, isz)):
        e = OxmlElement('w:' + side)
        e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), str(sz)); e.set(qn('w:space'), '0'); e.set(qn('w:color'), col)
        bd.append(e)
    from dox import TBLPR_ORDER
    _insert_ordered(tblPr, bd, TBLPR_ORDER)
    return t


def table(rows, widths, **kw): return frame(make_table(doc, rows, widths, header_rows=0), **kw)
def auto_line(p, mult=1.0):
    _add_pPr_el(p, 'spacing', {'after': '0', 'line': str(int(240 * mult)), 'lineRule': 'auto'}); return p
def heading(text, hint=None, sb=5):
    p = doc.add_paragraph(); rtl_par(p); par_space(p, sb, 2); par_keep(p)
    par_border_bottom(p, TEAL, "8")
    run(p, "❖  " + text, size=10.5, bold=True, color=RED)
    if hint: run(p, "    " + hint, size=7.8, color=GREY, light=True)

from band import band_title
band_title(s, "الحصص الموحَّدة")
p = doc.add_paragraph(); rtl_par(p); par_space(p, 0, 4); _add_pPr_el(p, 'jc', {'val': 'center'})
run(p, "◆  ", size=7, color=RED)
run(p, "آلية الجدولة والزيارة  ·  من التحضير إلى الدرجة", size=10, bold=True, color=RED)
run(p, "  ◆", size=7, color=RED)

heading("ما الحصة الموحَّدة؟", sb=3)
p = doc.add_paragraph(); rtl_par(p); auto_line(p); par_space(p, 0, 4)
run(p, G("حصةٌ عادية من جدول المعلم، يُعلن فيها اتجاهه التدريسي وإستراتيجيته، ويحضرها المقيّمون والزملاء. "
         "وليست «حصة تطبيقية» تُعدّ للعرض: ما يراه فريق التقويم الخارجي يجب أن يكون حال المدرسة لا استثناءها.",
         "حصةٌ عادية من جدول المعلمة، تُعلن فيها اتجاهها التدريسي وإستراتيجيتها، وتحضرها المقيّمات والزميلات. "
         "وليست «حصة تطبيقية» تُعدّ للعرض: ما يراه فريق التقويم الخارجي يجب أن يكون حال المدرسة لا استثناءها."),
    size=9, color=INK)

heading("من يحضر كل حصة؟")
# ⛔ **جدولٌ ثانٍ في المستند بقي على قاعدةٍ ملغاة**: أصلحتُ `RULES` أعلاه ٤
#    أكتوبر ٢٠٢٦ وتركتُ هذا — ولم يمسكه حارسُ القاعدة الملغاة لأن ألفاظَه
#    المحروسةَ ليست فيه. فالمستندُ الواحدُ يحمل قاعدتين متناقضتين. (٥ أكتوبر)
# ⚠️ المقيّمون خمسةٌ كلٌّ في نطاقه، لكلٍّ استمارتُه، والمعتمَدُ متوسّطُ من رصد.
#    ولا يُعتمد قبل رصد مشرف المادة إن كان لها مشرف.
ROLES = [(G("المشرف التربوي المختص", "المشرفة التربوية المختصة"),
          G("يرصد حصص تخصصه في سجل الإشراف ويعتمد نتيجتها — ولا تُعتمد قبل رصده",
            "ترصد حصص تخصصها في سجل الإشراف وتعتمد نتيجتها — ولا تُعتمد قبل رصدها")),
         (G("مدير المدرسة", "مديرة المدرسة"),
          G("يرصد أيَّ حصةٍ في مدرسته باستمارته المستقلة، ويكتب تعليقَه النوعي",
            "ترصد أيَّ حصةٍ في مدرستها باستمارتها المستقلة، وتكتب تعليقَها النوعي")),
         (G("الوكيل التعليمي", "الوكيلة التعليمية"),
          G("يُسنِد المعلمَين الزائرَين ويرصد حصص مدرسته — وعليه أولاً ما لا مشرف لتخصصه كالفنية والبدنية",
            "تُسنِد المعلمتين الزائرتين وترصد حصص مدرستها — وعليها أولاً ما لا مشرفة لتخصصه كالفنية والبدنية")),
         (G("مدير المجمع", "مديرة المجمع"),
          G("يرصد حصص مجمعه كلِّه، ويقارن بين مدارسه بالأرقام",
            "ترصد حصص مجمعها كلِّه، وتقارن بين مدارسها بالأرقام")),
         (G("فريق متابعة التقويم الداخلي", "فريق متابعة التقويم الداخلي"),
          G("نطاقه المنظومة كلُّها: يتابع ألّا تبقى حصةٌ بلا راصد، ويرصد هو أيضاً",
            "نطاقه المنظومة كلُّها: يتابع ألّا تبقى حصةٌ بلا راصدة، ويرصد هو أيضاً")),
         (G("معلمان زائران", "معلمتان زائرتان"), G("يملأ كلٌّ بطاقة زيارة الأقران، وينقل إجراءً واحداً لنفسه", "تملأ كلٌّ بطاقة زيارة القرينات، وتنقل إجراءً واحداً لنفسها"))]
t = table(1 + len(ROLES), [4.6, 14.4])
for i, lb in enumerate(["الدور", "ما يفعله في الحصة"]):
    cell_text(t.rows[0].cells[i], lb, size=8.6, bold=True, color=NAVY, shd=HEADBG, align='center')
row_height(t.rows[0], 0.46); row_nosplit(t.rows[0])
for i, (a, b) in enumerate(ROLES, 1):
    r = t.rows[i]; row_height(r, 0.52); row_nosplit(r)
    cell_text(r.cells[0], a, size=8.6, bold=True, color=NAVY, shd=NUMBG, align='center', valign='center')
    auto_line(cell_text(r.cells[1], b, size=8.8, color=INK, valign='center', shd=ZEBRA if i % 2 == 0 else None))

heading("خمس قواعد تضبط الجدول")
# ⛔ **القاعدةُ هنا تعاقبت ثلاثاً** وبقي المطبوعُ على أوسطها: «المقيّم واحد»
#    نُقضت ٤ أكتوبر ٢٠٢٦ — المقيّمون خمسةٌ كلٌّ في نطاقه، لكلٍّ استمارتُه،
#    والمعتمَدُ متوسّطُ من رصد. ولا يُعتمد قبل رصد مشرف المادة إن كان لها مشرف.
RULES = [G("المقيّمون خمسة كلٌّ في نطاقه: المشرف التربوي لتخصصه، ومدير المدرسة ووكيلها لمدرستهما، ومدير المجمع لمجمعه، وفريق متابعة التقويم الداخلي للمنظومة. ولكلٍّ استمارته المستقلة، والدرجة المعتمدة متوسط من رصد. ومعهم معلمان زائران يملآن بطاقة الأقران.",
           "المقيّمات خمس كلٌّ في نطاقها: المشرفة التربوية لتخصصها، ومديرة المدرسة ووكيلتها لمدرستهما، ومديرة المجمع لمجمعها، وفريق متابعة التقويم الداخلي للمنظومة. ولكلٍّ استمارتها المستقلة، والدرجة المعتمدة متوسط من رصد. ومعهن معلمتان زائرتان تملآن بطاقة الأقران."),
         G("لا يتجاوز عبء المقيّم حصتين في اليوم، فالتقدير يضعف مع الإرهاق.",
           "لا يتجاوز عبء المقيّمة حصتين في اليوم، فالتقدير يضعف مع الإرهاق."),
         G("لا تُجدول حصتان لمعلم واحد في أسبوع واحد؛ والثلث الأضعف يُزار مرتين في الفصل.",
           "لا تُجدول حصتان لمعلمة واحدة في أسبوع واحد؛ والثلث الأضعف يُزار مرتين في الفصل."),
         G("دوران المشرفين يضع كل مشرف في مجمع واحد كل يوم، فتُغطّى حصص تخصصه في المجمعات كلها.",
           "دوران المشرفات يضع كل مشرفة في مجمع واحد كل يوم، فتُغطّى حصص تخصصها في المجمعات كلها."),
         "ترصد الحصة ثلاث نتائج: الاستمارة من ٢٠٠ · بطاقة الاستراتيجية من ١٠٠ · إجراء واحد في بطاقة الجسر."]
for i, txt in enumerate(RULES, 1):
    p = doc.add_paragraph(); rtl_par(p); auto_line(p); par_space(p, 0, 3)
    _add_pPr_el(p, 'ind', {'right': '170'})
    run(p, "٠١٢٣٤٥٦٧٨٩"[i] + "  ", size=9, bold=True, color=TEAL)
    run(p, txt, size=9, color=INK)

# ⚠️ من منصة الخطط المدرسية 2026-09-27: الوطني أربعة مجمعات، والعالمي ثلاثة (لا نفل فيه)
# ⛔ كان هنا مربّعٌ لاتينيٌّ مصنوعٌ في الورقة لا يطابق جدولَ المنصة، وأسماءُ
#    مجموعاتٍ تخالف أسماءَها فيها. فصار يُقرأ من `scheddata` مصدرِه الوحيد.
import scheddata as _SD
_n = lambda c: {"عرقه": "عرقة"}.get(c, c)
_W0 = _SD.CAL[0]["w"]
# ⛔ **وكان العنوانُ يقول «الأسبوع السادس» نصّاً والجدولُ تحته من أسبوعٍ آخر**:
#    البياناتُ تُقرأ من الرزنامة والعنوانُ مكتوبٌ بيد، فلمّا صار الجدولُ يبدأ
#    بالثامن (٤ أكتوبر ٢٠٢٦) تناقض المطبوعُ مع نفسه. فصار العنوانُ من المصدر.
heading(G("دوران المشرفين على المجمعات", "دوران المشرفات على المجمعات"),
        "جدولُ " + _W0 + " — ويزحف يوماً واحداً في كل أسبوع بعده")
INTL = os.environ.get("CLS_SECTOR", "nat") == "intl"
DAYS = list(_SD.DAYS)
COMPLEXES = ["عرقة", "المنار", "الياسمين"] if INTL else ["النفل", "عرقة", "المنار", "الياسمين"]
GROUPS = list(_SD.GROUPS) + ([_SD.NAT_GROUP] if INTL else [])
def _visit(grp, day):
    """أين يزور فريقُ هذه المادة في هذا اليوم من أول أسابيع الجدول؟"""
    if grp == _SD.NAT_GROUP: cx = _n(_SD.NAT_DAYS.get(day, ""))
    else: cx = _n(((_SD.SUP6.get(grp) or {}).get(_W0) or {}).get(day, ""))
    return cx if cx in COMPLEXES else "—"
t = table(1 + len(GROUPS), [5.0] + [14.0 / len(DAYS)] * len(DAYS))
cell_text(t.rows[0].cells[0], "التخصص \\ اليوم", size=8.4, bold=True, color=NAVY, shd=HEADBG, align='center')
for j, d in enumerate(DAYS, 1):
    cell_text(t.rows[0].cells[j], d, size=8.6, bold=True, color=NAVY, shd=HEADBG, align='center')
row_height(t.rows[0], 0.46); row_nosplit(t.rows[0])
for gi, grp in enumerate(GROUPS, 1):
    r = t.rows[gi]; row_height(r, 0.5); row_nosplit(r)
    cell_text(r.cells[0], grp, size=8.2, bold=True, color=NAVY, shd=NUMBG, valign='center')
    for di in range(len(DAYS)):
        cell_text(r.cells[di + 1], _visit(grp, DAYS[di]), size=8.6, color=INK,
                  align='center', valign='center', shd=ZEBRA if gi % 2 == 0 else None)

heading("مسار الحصة من التحضير إلى الدرجة")
STEPS = [("قبل الحصة", G("يسلّم المعلم نموذج التحضير معلناً اتجاهه وإستراتيجيته",
                          "تسلّم المعلمة نموذج التحضير معلنةً اتجاهها وإستراتيجيتها")),
         ("في الحصة", G("يرصد المشرف المختص الاستمارة (٢٠٠) وبطاقة الاستراتيجية (١٠٠)، ويكتب الزملاء بطاقاتهم",
                        "ترصد المشرفة المختصة الاستمارة (٢٠٠) وبطاقة الاستراتيجية (١٠٠)، وتكتب الزميلات بطاقاتهن")),
         ("بعد الحصة", "جلسة تغذية راجعة في اليوم نفسه أو التالي، تنتهي بإجراء واحد في بطاقة الجسر"),
         ("الزيارة القادمة", G("يبدأ الزائر بالتحقق من تنفيذ الإجراء السابق قبل رصد أي شيء جديد",
                               "تبدأ الزائرة بالتحقق من تنفيذ الإجراء السابق قبل رصد أي شيء جديد"))]
t = table(1 + len(STEPS), [3.6, 15.4])
for i, lb in enumerate(["المرحلة", "ما يحدث فيها"]):
    cell_text(t.rows[0].cells[i], lb, size=8.6, bold=True, color=NAVY, shd=HEADBG, align='center')
row_height(t.rows[0], 0.46); row_nosplit(t.rows[0])
for i, (a, b) in enumerate(STEPS, 1):
    r = t.rows[i]; row_height(r, 0.52); row_nosplit(r)
    cell_text(r.cells[0], a, size=8.6, bold=True, color=TEAL, shd=TEALBG, align='center', valign='center')
    auto_line(cell_text(r.cells[1], b, size=8.8, color=INK, valign='center', shd=ZEBRA if i % 2 == 0 else None))

p = doc.add_paragraph(); rtl_par(p); par_space(p, 3, 0, 10); _add_pPr_el(p, 'jc', {'val': 'center'})
run(p, "الجدول القابل للتعبئة في ملف: «جداول الحصص الموحَّدة» — ورقة «جدول المدرسة»", size=8, color=GREY, light=True)
_p = doc.add_paragraph(); rtl_par(_p); par_space(_p, 0, 0, 1); run(_p, "", size=1)

fp = s.footer.paragraphs[0]; fp.text = ""
rtl_par(fp); _add_pPr_el(fp, 'jc', {'val': 'center'}); par_space(fp, 0, 0)
run(fp, "آلية الحصص الموحَّدة — مدارس ابن خلدون", size=7, color=GREY, light=True)
normalize_tables(doc)
out = sys.argv[1] if len(sys.argv) > 1 else "sd.docx"
doc.save(out); print("حُفظ:", out)
