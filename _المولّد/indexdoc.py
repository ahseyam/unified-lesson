# -*- coding: utf-8 -*-
"""فهرس المشروع — مستند PDF فيه كل أداةٍ برابطها القابل للنقر.

يقرأ الأقسام من `hub.py` نفسه فلا يفترق الفهرس عن الصفحة.
⚠️ تصدير وورد إلى PDF **يُسقط الروابط**، فيُبنى الفهرس صفحةَ HTML ثم يُطبع بالمتصفح
   (`--print-to-pdf`) الذي يحفظها قابلةً للنقر — وقد فُحص بعدّ الروابط في الناتج.
⚠️ ورابط مجلد OneDrive المختصر (1drv.ms) لا تُركَّب عليه مساراتٌ فرعية فلا يصلح أساساً؛
   يصلح عنوان SharePoint/OneDrive للأعمال أو عنوان GitHub Pages.

الاستعمال: CLS_BASE=https://user.github.io/repo/ python3 indexdoc.py <الملف.pdf>
"""
import base64
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import hub                                                  # noqa: E402

BASE = os.environ.get("CLS_BASE", "").rstrip("/")
BASE = BASE + "/" if BASE else ""
FONTS = os.path.expanduser("~/Library/Fonts")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SCRATCH = "/private/tmp/claude-501/-Users-ahmadseyam-Desktop--------------------/0867de99-3862-4f08-89c9-d58bbdaafa97/scratchpad"
LBL = {"html": "الصفحة", "pdf": "PDF", "pdf2": "PDF بنات", "docx": "وورد",
       "docx2": "وورد بنات", "xlsx": "إكسل"}
AR = "٠١٢٣٤٥٦٧٨٩"


def ar(n):
    return "".join(AR[int(c)] for c in str(n))


def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


CSS = """
:root{--navy:#2F5384;--navy2:#1d3760;--teal:#2F7F95;--teal2:#1d5d70;--tealbg:#E4F1F4;
 --ink:#16202e;--grey:#6b7a8d;--line:#C9D2DE;--head:#EDF2F8;--gold:#B8862B;--link:#14539A}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:JZ,SK,"Geeza Pro",Tahoma,sans-serif;color:var(--ink);font-size:11.5pt;line-height:1.55}
/* ⛔ هوامشُ @page تقصُّ العنصرَ الثابت فتختفي الكليشة — قِيس: ٦٧٪ لونٍ قبلها وصفرٌ
   بعدها. فالهوامشُ صفرٌ، والكليشةُ تملأ الورقة، والإزاحةُ تُصنع برأسٍ يتكرّر. */
.bg{position:fixed;inset:0;width:100%;height:100%;object-fit:fill;z-index:-1}
/* ⚠️ الحشوةُ على عنصرٍ واحدٍ تُطبَّق على الصفحة الأولى وحدها، فتبدأ الصفحاتُ
   التاليةُ من أعلى الورقة فوق الكليشة. والحلُّ الذي يجمع الاثنين: جدولٌ يلفّ
   المحتوى، ورأسُه (thead) يتكرّر في كل صفحةٍ فيصنع فراغَ الترويسة، وذيلُه كذلك. */
.page{padding:0}
table.sheet{width:100%;border-collapse:collapse;table-layout:fixed}
table.sheet > thead > tr > td{height:26mm;border:0;padding:0}
table.sheet > tfoot > tr > td{height:16mm;border:0;padding:0}
table.sheet > tbody > tr > td{padding:0 15mm;border:0;vertical-align:top}
h1{font-size:21pt;color:var(--navy2);font-weight:700;text-align:center;margin-bottom:2mm}
.sub{text-align:center;color:var(--teal2);font-family:JZL,SK;font-size:11pt;margin-bottom:5mm}
.how{border:1px solid var(--line);border-radius:3mm;overflow:hidden;margin-bottom:6mm}
.how h2{background:var(--navy);color:#fff;font-size:11pt;padding:2mm 4mm;font-weight:700}
.how ul{list-style:none;padding:3mm 5mm}
.how li{font-size:10pt;font-family:JZL,SK;margin:1.4mm 0;padding-inline-start:5mm;position:relative}
.how li::before{content:"◆";color:var(--teal);position:absolute;inset-inline-start:0;font-size:7pt}
section{margin-bottom:6mm;break-inside:auto}
.sh{background:linear-gradient(105deg,var(--navy2),var(--navy) 55%,var(--teal));color:#fff;
 border-radius:2.5mm;padding:2.4mm 4mm;display:flex;align-items:baseline;gap:3mm;margin-bottom:2mm}
.sh b{font-size:12.5pt;font-weight:700}
.sh span{font-family:JZL,SK;font-size:9.5pt;color:#d7eaf0}
table{width:100%;border-collapse:collapse;table-layout:fixed}
td{border:.4pt solid var(--line);padding:1.8mm 3mm;vertical-align:middle}
tr:nth-child(even) td{background:var(--head)}
tr{break-inside:avoid}
.sh{break-after:avoid;break-inside:avoid}
td.sub{break-before:avoid}
section table{break-inside:auto}
tr:has(+ tr td.sub){break-after:avoid}
.t{font-size:10.5pt;font-weight:700;color:var(--navy2);line-height:1.35}
.n{font-size:8.6pt;color:var(--grey);font-family:JZL,SK;line-height:1.4;margin-top:.6mm}
td.sub{font-size:9.5pt;color:var(--navy2);padding-inline-start:6mm}
td.lnk{width:44mm;text-align:center;white-space:nowrap}
a{color:var(--link);font-weight:700;font-size:9.5pt;text-decoration:underline;text-underline-offset:2px}
.sep{color:var(--grey);font-size:8pt;padding:0 1mm}
.foot{text-align:center;color:var(--grey);font-family:JZL,SK;font-size:9pt;margin-top:4mm}
.warn{text-align:center;color:#C00000;font-size:9pt;margin-top:2mm}
@page{size:A4;margin:0}
"""


def face(name, file, weight="normal", digits=False):
    p = os.path.join(FONTS, file)
    if not os.path.exists(p):
        return ""
    with open(p, "rb") as f:
        d = base64.b64encode(f.read()).decode()
    ur = "" if digits else "  unicode-range:U+0000-065F,U+066A-FFFF;\n"
    return (f"@font-face{{font-family:{name};font-weight:{weight};font-display:block;\n"
            f"  src:url(data:font/ttf;base64,{d}) format('truetype');\n{ur}}}\n")


FONTCSS = (face("JZ", "ArbFONTS-Al-Jazeera-Arabic-Regular.ttf")
           + face("JZ", "ArbFONTS-Al-Jazeera-Arabic-Bold.ttf", "700")
           + face("JZL", "ArbFONTS-Al-Jazeera-Arabic-Light.ttf")
           + face("SK", "Sakkal Majalla Regular.ttf", digits=True))

with open(os.path.join(HERE, "kl_portrait.jpg"), "rb") as f:
    KL = base64.b64encode(f.read()).decode()

rows = []
tools = sum(len(s["items"]) for s in hub.SEC)
nfiles = sum(len(i.get("f") or {}) + sum(len(r["f"]) for r in i.get("rows", []))
             for s in hub.SEC for i in s["items"])
for si, sec in enumerate(hub.SEC, 1):
    body = []
    for it in sec["items"]:
        def _lk(files):
            out = []
            for k in ("html", "pdf", "docx", "pdf2", "docx2", "xlsx"):
                u = files.get(k)
                if not u:
                    continue
                out.append(f'<a href="{BASE}{u}">{LBL[k]}</a>' if BASE else f'<span>{LBL[k]}</span>')
            return "<span class=sep>·</span>".join(out)
        # ⚠️ البطاقةُ قد تحمل أسطراً فرعية (مادةٌ بمراحلها) — وإلا ضاعت روابطُها
        subrows = it.get("rows") or []      # لا تُسمَّ `rows`: تمحو قائمة الأقسام
        if subrows:
            body.append(
                f'<tr><td colspan="2"><div class="t">{esc(it["t"])}</div>'
                f'<div class="n">{esc(it["n"])}</div></td></tr>')
            for r in subrows:
                body.append(
                    f'<tr><td class="sub">{esc(r["l"])}</td>'
                    f'<td class="lnk">{_lk(r["f"])}</td></tr>')
        else:
            body.append(
                f'<tr><td><div class="t">{esc(it["t"])}</div>'
                f'<div class="n">{esc(it["n"])}</div></td>'
                f'<td class="lnk">{_lk(it["f"])}</td></tr>')
    rows.append(f'<section><div class="sh"><b>{ar(si)} · {esc(sec["t"])}</b>'
                f'<span>{esc(sec["s"])}</span></div><table>{"".join(body)}</table></section>')

HTML = f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<title>فهرس نظام الحصة الموحَّدة</title><style>{FONTCSS}{CSS}</style></head><body>
<img class="bg" src="data:image/jpeg;base64,{KL}" alt="">
<div class="page">
<table class="sheet"><thead><tr><td></td></tr></thead>
<tfoot><tr><td></td></tr></tfoot><tbody><tr><td>
<h1>نظام الحصة الموحَّدة — فهرس الأدوات بروابطها</h1>
<div class="sub">{ar(tools)} أداة · {ar(nfiles)} ملفاً · كل عنوانٍ هنا رابطٌ يُفتح بالنقر</div>
<div class="how"><h2>كيف تستعمل هذا الفهرس</h2><ul>
<li>انقر «PDF» لتفتح الملفّ للقراءة والطباعة، و«وورد» لتفتحه للتعبئة أو التعديل.</li>
<li>لكل أداةٍ نسختان: بنين وبنات — والنسخة المؤنَّثة مؤنَّثةٌ في الفعل والضمير لا في الاسم وحده.</li>
<li>«الصفحة» تعني صفحةً رقمية تُفتح في المتصفح مباشرةً بلا تنصيب.</li>
<li>وإن تعذّر فتح رابط فالملفّ نفسه في مجلده داخل الحزمة.</li>
</ul></div>
{"".join(rows)}
<div class="foot">مدارس ابن خلدون · نظام الحصة الموحَّدة</div>
{"" if BASE else '<div class="warn">⚠️ لم يُحدَّد أساس الروابط — أُنتج الفهرس بلا نقر. أعد التوليد بـCLS_BASE.</div>'}
</td></tr></tbody></table>
</div></body></html>"""

out = sys.argv[1] if len(sys.argv) > 1 else "فهرس.pdf"
tmp = os.path.join(SCRATCH, "fahras.html")
os.makedirs(SCRATCH, exist_ok=True)
with open(tmp, "w", encoding="utf-8") as f:
    f.write(HTML)
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={out}", "--virtual-time-budget=9000", "file://" + tmp],
               capture_output=True)
try:
    import fitz
    d = fitz.open(out)
    n = sum(len(p.get_links()) for p in d)
    print("حُفظ:", os.path.basename(out), "|", d.page_count, "صفحة |", tools, "أداة |",
          n, "رابطاً قابلاً للنقر |", "الأساس:", BASE or "— بلا أساس —")
except Exception as e:
    print("حُفظ:", out, "| تعذّر العدّ:", e)
