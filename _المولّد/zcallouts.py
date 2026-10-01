# -*- coding: utf-8 -*-
"""نشرة استخدام استمارة الملاحظة الصفية: الاستمارة نفسها وعليها بالونات شرح (Callouts وورد الحقيقية).

قواعد التوزيع (طلب المستشار 2026-09-21): لا بالون فوق بالون، ولا خطّ فوق بالون، والهدف البعيد
يُشار إليه بخط رفيع ينتهي بنقطة. المواضع بالنقطة من أعلى الصفحة ويسارها، مقيسة من PDF الاستمارة.
الاستعمال: CLS_FONTSET=js CLS_GENDER=m|f python3 zcallouts.py <استمارة.docx> <نشرة.docx>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from dox import run, rtl_par, par_space, _add_pPr_el, GENDER

RED, INK, FILL = "C00000", "1A1A1A", "FFF6DC"
EMU = 12700
FAR = 45     # نقطة: أبعد من هذا يُستعمل بالون الخط

NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"')

# (الصفحة، الشكل، (س، ص، عرض، ارتفاع)، رأس السهم (س، ص)، العنوان، الشرح)
CALLOUTS = [
    # ── ص١: عمود الدرجات الفارغ (س ٣٣–١٦٠) بين رؤوس المجالات ──
    (1, "wedgeRoundRectCallout", (33, 224, 128, 62), (112, 196),
     "علامة واحدة لكل مؤشر",
     "ضع ✓ في عمود واحد من السلّم. ورؤوس السلّم تتكرر مع كل مجال فلا تضلّ عند انتقال الصفحة."),
    (1, "wedgeEllipseCallout", (33, 330, 128, 58), (46, 313),
     "«لا ينطبق»",
     "للاستثناء فقط كحصة اختبار؛ وغياب الشاهد درجته ١."),
    (1, "borderCallout1", (33, 394, 128, 50), (228, 118),
     "بيانات الحصة",
     "تُملأ قبل دخول الصف، و«عدد الطلاب» يلزم لمخطط عدالة التفاعل."),
    (1, "borderCallout1", (33, 452, 128, 56), (255, 158),
     "السلّم: من أين تأتي الدرجة؟",
     "من عدد الشواهد المعتمدة المرصودة للمؤشر في «دليل مستويات الأداء»، لا من الانطباع."),
    (1, "borderCallout1", (33, 540, 128, 70), (345, 150),
     "نوع الزيارة والاتجاه التدريسي",
     "حدّد نوع الزيارة، واكتب الاتجاه الذي أعلنه المعلم في تحضيره، فتُقاس شواهده في الحصة."),
    (1, "borderCallout1", (33, 656, 128, 46), (318, 527),
     "يُرصد على الطالب",
     "من شارك؟ من سأل؟ من حاور؟ فعينك على الصف لا على السبورة."),
    (1, "wedgeRectCallout", (33, 706, 128, 40), (112, 755),
     "مجموع المجال",
     "اجمع درجات المجال وانقله إلى جدول النتيجة. ولا ينقسم مجال بين صفحتين."),
    # ── ص٢ ──
    (2, "cloudCallout", (33, 232, 128, 54), (150, 300),
     "القاعدة الذهبية",
     "الدرجة لما يُرى في الحصة، لا لما يُقال عنها ولا لما في الملفات."),
    (2, "borderCallout1", (33, 390, 128, 40), (318, 438),
     "خارج مشاهدات الفريق",
     "لا يرصده الفريق الخارجي، لكنه يؤثّر في كل ما يرصده."),
    (2, "wedgeRoundRectCallout", (40, 540, 290, 50), (430, 529),
     "ما قاله الطلاب",
     "اختر ثلاثة طلاب من مستويات مختلفة أثناء العمل، واسألهم بهدوء، واكتب إجاباتهم بألفاظهم. "
     "إجابة واثقة من الثلاثة دليل على ممارسة راسخة لا حصة مُعدّة للزيارة."),
    # ── ص٣ ──
    (3, "wedgeRoundRectCallout", (40, 120, 300, 48), (372, 152),
     "مخطط عدالة التفاعل",
     "ارسم المقاعد كما تراها من خلف الصف، وضع علامة عند كل طالب شارك. "
     "المقاعد الخالية من العلامات فجوة تُناقش مع المعلم."),
    (3, "wedgeRoundRectCallout", (40, 246, 250, 42), (500, 262),
     "جوانب إبداعية",
     "ممارسة محددة بشاهدها: ماذا فعل؟ ومتى؟ لا عبارة عامة مثل «متميز»."),
    (3, "wedgeRoundRectCallout", (40, 296, 250, 42), (500, 316),
     "إجراءات متفق عليها",
     "إجراء واحد يُنقل إلى بطاقة الجسر، ويُتحقق منه في الزيارة القادمة ويُكتب تاريخ تحققه."),
    (3, "borderCallout1", (33, 620, 168, 62), (300, 412),
     "مجالات الدعم",
     "ضع ✓ للمجالات التي نزل مجموعها عن ثلاثة أرباع حدّها، ورشِّح المعلم لزيارة متابعة بتاريخها."),
    (3, "borderCallout1", (209, 620, 168, 62), (300, 470),
     "النتيجة",
     "انقل مجموع كل مجال، والنسبة = المجموع ÷ ٢. ومع «لا ينطبق» يُقسم المجموع على المقام المعدَّل ثم يُضرب في مئة."),
    (3, "borderCallout1", (385, 620, 176, 62), (480, 536),
     "بطاقة تشخيص الاستراتيجية",
     "مجموعها من ١٠٠ يُكتب هنا، وتُشتقّ منه درجة المؤشر م٢·٣ بالجدول المجاور."),
    (3, "borderCallout1", (33, 692, 250, 44), (300, 568),
     "التوقيع",
     "بعد جلسة التغذية الراجعة. وتوقيع المعلم يعني الاطلاع والاتفاق على الإجراء، لا الموافقة على كل درجة."),
]

FEM = {
    "اختر ثلاثة طلاب من مستويات مختلفة أثناء العمل، واسألهم بهدوء، واكتب إجاباتهم بألفاظهم. "
    "إجابة واثقة من الثلاثة دليل على ممارسة راسخة لا حصة مُعدّة للزيارة.":
        "اختر ثلاث طالبات من مستويات مختلفة أثناء العمل، واسألهنّ بهدوء، واكتب إجاباتهنّ بألفاظهنّ. "
        "إجابة واثقة من الثلاث دليل على ممارسة راسخة لا حصة مُعدّة للزيارة.",
    "ضع ✓ لما تراه فعلاً في الصف قبل أن يشرح المعلم شيئاً؛ فهذا أول ما يلتقطه عضو التقويم الخارجي.":
        "ضع ✓ لما تراه فعلاً في الصف قبل أن تشرح المعلمة شيئاً؛ فهذا أول ما يلتقطه عضو التقويم الخارجي.",
    "ممارسة محددة بشاهدها: ماذا فعل؟ ومتى؟ لا عبارة عامة مثل «متميز».":
        "ممارسة محددة بشاهدها: ماذا فعلت؟ ومتى؟ لا عبارة عامة مثل «متميزة».",
}


def _tb_para(txbx):
    p_el = parse_xml(f'<w:p {NS}/>')
    txbx.append(p_el)
    p = Paragraph(p_el, None)
    rtl_par(p)
    return p


def callout(anchor_par, idx, geom, box, tip, title, body, fem_ready=False):
    x, y, w, h = box
    tx, ty = tip
    far = max(x - tx, tx - (x + w), 0) + max(y - ty, ty - (y + h), 0)
    if far > FAR and geom != "cloudCallout":
        geom = "borderCallout1"
    if geom == "borderCallout1":
        sx = 0 if tx < x else (w if tx > x + w else w / 2)
        sy = 0 if ty < y else (h if ty > y + h else h / 2)
        adj = [sy / h, sx / w, (ty - y) / h, (tx - x) / w]
    else:
        adj = [(tx - (x + w / 2)) / w, (ty - (y + h / 2)) / h]
        if geom == "wedgeRoundRectCallout":
            adj.append(0.16667)   # ⚠️ إلزامية: بدونها يرفض وورد فتح المستند كله بصمت
    gd = "".join(f'<a:gd name="adj{i}" fmla="val {int(v * 100000)}"/>' for i, v in enumerate(adj, 1))
    xml = (
        f'<w:r {NS}><w:drawing>'
        f'<wp:anchor distT="0" distB="0" distL="0" distR="0" simplePos="0" relativeHeight="{251700000 + idx}" '
        'behindDoc="0" locked="0" layoutInCell="0" allowOverlap="1">'
        '<wp:simplePos x="0" y="0"/>'
        f'<wp:positionH relativeFrom="page"><wp:posOffset>{int(x * EMU)}</wp:posOffset></wp:positionH>'
        f'<wp:positionV relativeFrom="page"><wp:posOffset>{int(y * EMU)}</wp:posOffset></wp:positionV>'
        f'<wp:extent cx="{int(w * EMU)}" cy="{int(h * EMU)}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
        f'<wp:wrapNone/><wp:docPr id="{1000 + idx}" name="شرح {idx}"/><wp:cNvGraphicFramePr/>'
        '<a:graphic><a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">'
        '<wps:wsp><wps:cNvSpPr/><wps:spPr>'
        f'<a:xfrm><a:off x="0" y="0"/><a:ext cx="{int(w * EMU)}" cy="{int(h * EMU)}"/></a:xfrm>'
        f'<a:prstGeom prst="{geom}"><a:avLst>{gd}</a:avLst></a:prstGeom>'
        f'<a:solidFill><a:srgbClr val="{FILL}"/></a:solidFill>'
        f'<a:ln w="9525"><a:solidFill><a:srgbClr val="{RED}"/></a:solidFill>'
        + ('<a:tailEnd type="oval" w="med" len="med"/>' if geom == "borderCallout1" else '') + '</a:ln>'
        '</wps:spPr><wps:txbx><w:txbxContent/></wps:txbx>'
        '<wps:bodyPr rot="0" vert="horz" wrap="square" lIns="54864" tIns="18288" rIns="54864" bIns="18288" '
        'anchor="ctr" anchorCtr="0"><a:noAutofit/></wps:bodyPr>'
        '</wps:wsp></a:graphicData></a:graphic></wp:anchor></w:drawing></w:r>')
    r_el = parse_xml(xml)
    txbx = r_el.find('.//' + qn('w:txbxContent'))
    p = _tb_para(txbx); par_space(p, 0, 0.5, 9.6); _add_pPr_el(p, 'jc', {'val': 'center'})
    run(p, title, size=7.3, bold=True, color=RED, _fem=not fem_ready)
    p = _tb_para(txbx); par_space(p, 0, 0, 8.6); _add_pPr_el(p, 'jc', {'val': 'center'})
    run(p, body, size=6.6, color=INK, _fem=not fem_ready)
    anchor_par._p.append(r_el)


def build(src, out, callouts, anchor_subs, sub_old, sub_new, fem=None):
    """anchor_subs: {الصفحة: نصٌّ في فقرة متنٍ تقع عليها} — السطر الفرعي يصير عنوان النشرة."""
    doc = Document(src)
    body = doc.paragraphs
    def find(sub):
        for p in body:
            if sub in p.text: return p
        raise SystemExit("لم تُوجد المرساة: " + sub)
    anchors = {pg: find(sub) for pg, sub in anchor_subs.items()}
    for r in anchors[1].runs:
        if sub_old in r.text:
            r.text = sub_new
    from gender import feminize
    ARQ = "٠١٢٣٤٥٦٧٨٩"; n = 0
    for i, (pg, geom, box, tip, title, text) in enumerate(callouts, 1):
        ready = False
        if GENDER == "f":
            title, text = feminize(title), (fem or {}).get(text) or feminize(text)
            ready = True
        if geom != "cloudCallout":
            n += 1; title = "".join(ARQ[int(c)] for c in str(n)) + "  " + title
        callout(anchors[pg], i, geom, box, tip, title, text, fem_ready=ready)
    doc.save(out)
    print("بالونات:", len(callouts), "| حُفظ:", out)


def main(src, out):
    # ⚠️ المرساة فقرةٌ في المتن تقع على الصفحة المقصودة — تتغيّر بتغيّر التخطيط، فتُراجَع مع كل تعديل
    build(src, out, CALLOUTS, {1: "المعيار الموحَّد", 2: "الأثر المادي", 3: "مخطط عدالة"},
          "المعيار الموحَّد", "نشرة الاستخدام: ما يعنيه كل جزء وكيف يُملأ", FEM)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
