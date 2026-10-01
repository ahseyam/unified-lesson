# -*- coding: utf-8 -*-
"""فهرس المشروع — مستند PDF فيه كل أداةٍ برابطها القابل للنقر.

يقرأ الأقسام من `hub.py` نفسه فلا يفترق الفهرس عن الصفحة، ويركّب الروابط على أساسٍ واحد:
    CLS_BASE=https://user.github.io/repo/   python3 indexdoc.py <الملف.docx>

⚠️ رابط مجلد OneDrive المختصر (1drv.ms) لا تُركَّب عليه مساراتٌ فرعية — فلا يصلح أساساً.
   يصلح: عنوان SharePoint/OneDrive للأعمال (…/Documents/…) أو عنوان GitHub Pages.
"""
import os
import sys
from urllib.parse import quote

from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml.ns import qn, nsdecls
from docx.oxml import OxmlElement, parse_xml
from docx.opc.constants import RELATIONSHIP_TYPE as RT

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("CLS_HUB_QUIET", "1")
import hub                                    # noqa: E402  (يبني SEC ويكتب index.html)
from dox import *                             # noqa: F401,F403,E402
from dox import _add_pPr_el                   # noqa: E402
from band import band_title                   # noqa: E402

BASE = os.environ.get("CLS_BASE", "").rstrip("/") + "/"
NAVY, TEAL, GREY, INK, LINK = "355E91", "2F7F95", "7F7F7F", "1A1A1A", "1155CC"
HEADBG, TEALBG = "E9EEF6", "E2F0F3"
KLISHA = os.path.join(HERE, "kl_portrait.jpg")
AR = "٠١٢٣٤٥٦٧٨٩"
LBL = {"html": "الصفحة", "pdf": "PDF", "pdf2": "PDF بنات", "docx": "وورد", "xlsx": "إكسل"}


def ar(n):
    return "".join(AR[int(d)] for d in str(n))


doc = Document()
set_doc_defaults(doc)
set_compat15(doc)
s = doc.sections[0]
s.page_width, s.page_height = Cm(21.0), Cm(29.7)
s.top_margin, s.bottom_margin = Cm(3.2), Cm(1.5)
s.left_margin = s.right_margin = Cm(1.3)
W = 18.4

# الكليشة خلفيةً
hp = s.header.paragraphs[0]
rtl_par(hp)
par_space(hp, 0, 0, 1)
r = hp.add_run()
r.add_picture(KLISHA, width=Cm(21.0), height=Cm(29.7))
inline = r._r.find('.//' + qn('wp:inline'))
graphic = inline.find(qn('a:graphic'))
anchor = parse_xml(
    f'<wp:anchor {nsdecls("wp")} distT="0" distB="0" distL="0" distR="0" simplePos="0" '
    'relativeHeight="0" behindDoc="1" locked="1" layoutInCell="1" allowOverlap="1">'
    '<wp:simplePos x="0" y="0"/>'
    '<wp:positionH relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionH>'
    '<wp:positionV relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionV>'
    '<wp:extent cx="7560000" cy="10692000"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
    '<wp:wrapNone/><wp:docPr id="901" name="klisha"/><wp:cNvGraphicFramePr/></wp:anchor>')
anchor.append(graphic)
inline.getparent().replace(inline, anchor)
band_title(s, "فهرس نظام الحصة الموحَّدة")


def link(par, text, url, size=8.5):
    """رابطٌ قابل للنقر داخل فقرة."""
    rid = par.part.relate_to(url, RT.HYPERLINK, is_external=True)
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), rid)
    run(par, text, size=size, bold=True, color=LINK)
    r = par.runs[-1]._r
    rPr = r.get_or_add_rPr()
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(u)
    r.getparent().remove(r)
    h.append(r)
    par._p.append(h)


def gap(pt=5):
    p = doc.add_paragraph()
    rtl_par(p)
    par_space(p, 0, 0, pt)


# ═════════ العنوان ═════════
p = doc.add_paragraph()
rtl_par(p)
par_space(p, 3, 2)
_add_pPr_el(p, "jc", {"val": "center"})
run(p, "نظام الحصة الموحَّدة — فهرس الأدوات بروابطها", size=13.5, bold=True, color=NAVY)
p = doc.add_paragraph()
rtl_par(p)
par_space(p, 0, 5)
_add_pPr_el(p, "jc", {"val": "center"})
run(p, f"{ar(sum(len(x['items']) for x in hub.SEC))} أداة  ·  {ar(hub.FILES)} ملفاً  ·  "
        "كل عنوانٍ هنا رابطٌ يُفتح بالنقر", size=9, color=TEAL)

t = make_table(doc, 2, [W], borders_color="C9D2DE")
cell_text(t.rows[0].cells[0], "كيف تستعمل هذا الفهرس", size=9.5, bold=True,
          color="FFFFFF", shd=NAVY, align='center')
cell_lines(t.rows[1].cells[0], [
    ("انقر على «PDF» لتفتح الملفّ للقراءة والطباعة، وعلى «وورد» لتفتحه للتعبئة أو التعديل.", False),
    ("لكل أداةٍ نسختان: بنين وبنات — والنسخة المؤنَّثة مؤنَّثةٌ في الفعل والضمير لا في الاسم وحده.", False),
    ("«الصفحة» تعني صفحةً رقمية تُفتح في المتصفح مباشرةً بلا تنصيب.", False),
    ("وإن تعذّر فتح رابط، فالملف نفسه في مجلده كما هو مذكورٌ في أول كل قسم.", False),
], size=9, color=INK, space=3)
row_height(t.rows[0], 0.52)
gap(7)

# ═════════ الأقسام ═════════
for si, sec in enumerate(hub.SEC, 1):
    head = make_table(doc, 1, [W], borders_color=NAVY)
    p = cell_text(head.rows[0].cells[0], f"{ar(si)}   {sec['t']}", size=11, bold=True,
                  color="FFFFFF", shd=NAVY)
    run(p, "     " + sec["s"], size=8.5, color="D5E8EE", light=True)
    row_height(head.rows[0], 0.6)
    row_nosplit(head.rows[0])
    gap(2)

    rows = make_table(doc, len(sec["items"]), [12.6, W - 12.6], borders_color="C9D2DE")
    for ri, it in enumerate(sec["items"]):
        c = rows.rows[ri].cells[0]
        p = cell_text(c, it["t"], size=9.5, bold=True, color=NAVY,
                      shd=(HEADBG if ri % 2 else None))
        q = c.add_paragraph()
        rtl_par(q)
        par_space(q, 0, 0)
        run(q, it["n"], size=8, color=GREY, light=True)
        lc = rows.rows[ri].cells[1]
        pl = cell_text(lc, "", size=6, align='center', shd=(HEADBG if ri % 2 else None))
        par_space(pl, 1, 1)
        first = True
        for k in ("html", "pdf", "pdf2", "docx", "xlsx"):
            if not it["f"].get(k):
                continue
            if not first:
                run(pl, "   ·   ", size=8, color=GREY)
            first = False
            if BASE.strip("/"):
                link(pl, LBL[k], BASE + it["f"][k])
            else:
                run(pl, LBL[k], size=8.5, color=GREY)
        cell_valign(lc, 'center')
        row_nosplit(rows.rows[ri])
    gap(8)

p = doc.add_paragraph()
rtl_par(p)
par_space(p, 4, 0)
_add_pPr_el(p, "jc", {"val": "center"})
run(p, "مدارس ابن خلدون  ·  نظام الحصة الموحَّدة", size=8.5, color=GREY, light=True)
if not BASE.strip("/"):
    q = doc.add_paragraph()
    rtl_par(q)
    _add_pPr_el(q, "jc", {"val": "center"})
    run(q, "⚠️ لم يُحدَّد أساس الروابط — أُنتج الفهرس بلا نقر. أعد التوليد بـCLS_BASE.",
        size=8, color="C00000")

normalize_tables(doc)
out = sys.argv[1] if len(sys.argv) > 1 else "index.docx"
doc.save(out)
print("حُفظ:", os.path.basename(out), "|", sum(len(x["items"]) for x in hub.SEC), "أداة |",
      hub.FILES, "رابطاً |", "الأساس:", BASE if BASE.strip("/") else "— بلا أساس —")
