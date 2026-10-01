# -*- coding: utf-8 -*-
"""صور العرض التعريفي — تُقتطع من المستندات المسلَّمة نفسها لا من رسومٍ عامة.

لكل شريحةٍ صورةٌ تُظهر ما يُشرح فيها: صفحةٌ كاملة، أو قصاصةٌ من موضعٍ بعينه،
أو صورتان متجاورتان، أو لوحةٌ مجمّعة. والمصدر ملفات PDF المنشورة وصفحات النموذج الرقمي.
الاستعمال: python3 deckshots.py            (يكتب في ٩ - العرض التعريفي/صور)
"""
import os
import subprocess
import sys

import fitz
from PIL import Image

ROOT = "/Users/ahmadseyam/Desktop/نموذج تحضير الدرس - بطاقة الملاحظة الصفية"
OUT = os.path.join(ROOT, "٩ - العرض التعريفي", "صور")
SCRATCH = "/private/tmp/claude-501/-Users-ahmadseyam-Desktop--------------------/0867de99-3862-4f08-89c9-d58bbdaafa97/scratchpad"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
os.makedirs(OUT, exist_ok=True)

P = lambda *a: os.path.join(ROOT, *a)
PDF = " (للعرض والطباعة).pdf"

SRC = dict(
    prep=P("١ - نموذج تحضير الحصة", "بنين", "نموذج تحضير الحصة — ابن خلدون" + PDF),
    obs=P("٢ - استمارة الملاحظة الصفية", "بنين", "استمارة الملاحظة الصفية — ابن خلدون" + PDF),
    nashra_prep=P("١ - نموذج تحضير الحصة", "نشرة الاستخدام", "نشرة استخدام نموذج التحضير — ابن خلدون.pdf"),
    guide=P("٣ - الأدوات المساندة", "دليل مستويات الأداء", "بنين", "دليل مستويات الأداء — ابن خلدون" + PDF),
    plan=P("٣ - الأدوات المساندة", "خطة الاستعداد", "بنين", "خطة الاستعداد — ابن خلدون" + PDF),
    bridge=P("٣ - الأدوات المساندة", "بطاقة الجسر", "بنين", "بطاقة الجسر — ابن خلدون" + PDF),
    card=P("٤ - بطاقات إستراتيجيات التدريس", "بنين", "بطاقة تشخيص — جيكسو — ابن خلدون" + PDF),
    approach=P("٥ - الاتجاهات التدريسية", "بنين", "الاتجاه التدريسي — التعليم المتمايز — ابن خلدون" + PDF),
    peer=P("٦ - بطاقة زيارة الأقران", "بنين", "بطاقة زيارة الأقران — ابن خلدون" + PDF),
    mech=P("٧ - آلية جداول الحصص الموحَّدة", "بنين", "آلية الحصص الموحَّدة — ابن خلدون" + PDF),
    filled_m=P("١ - نموذج تحضير الحصة", "نماذج معبّأة استرشادية", "المرحلة الثانوية", "بنين",
               "الفيزياء — أول ثانوي — منحنى الموقع والزمن" + PDF),
    filled_f=P("١ - نموذج تحضير الحصة", "نماذج معبّأة استرشادية", "المرحلة الثانوية", "بنات",
               "الفيزياء — أول ثانوي — منحنى الموقع والزمن (بنات)" + PDF),
    web=P("٨ - النموذج الرقمي (تجربة)", "صفحة الحصة الموحَّدة — ابن خلدون.html"),
    # ⛔ صفحةُ الاستضافة أُخرجت من المنشور (٢٩ سبتمبر ٢٠٢٦)
)


def page(src, n=0, dpi=150, clip=None):
    """صفحةٌ أو قصاصةٌ منها كصورة PIL."""
    d = fitz.open(SRC[src] if src in SRC else src)
    pg = d[n]
    r = pg.rect
    if clip:                                   # نِسَبٌ من الصفحة: (يسار, أعلى, يمين, أسفل)
        clip = fitz.Rect(r.width * clip[0], r.height * clip[1],
                         r.width * clip[2], r.height * clip[3])
    pm = pg.get_pixmap(dpi=dpi, clip=clip)
    return Image.frombytes("RGB", (pm.width, pm.height), pm.samples)


def shot(html, out, w=1500, h=980, wait=3500, q=""):
    """لقطة لصفحة HTML عبر متصفحٍ بلا واجهة."""
    tmp = os.path.join(SCRATCH, "shot.png")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", f"--window-size={w},{h}",
                    f"--virtual-time-budget={wait}", f"--screenshot={tmp}",
                    "file://" + html + q], capture_output=True)
    return Image.open(tmp).convert("RGB")


def frame(im, pad=14, bg=(255, 255, 255), line=(53, 94, 145)):
    """إطارٌ كحليٌّ رفيع وظلٌّ خفيف — ليبدو المستند وثيقةً لا صورة."""
    from PIL import ImageOps
    im = ImageOps.expand(im, border=2, fill=line)
    return ImageOps.expand(im, border=pad, fill=bg)


def duo(a, b, gap=22, bg=(255, 255, 255)):
    """صورتان متجاورتان بارتفاعٍ واحد."""
    h = max(a.height, b.height)
    a = a.resize((int(a.width * h / a.height), h), Image.LANCZOS)
    b = b.resize((int(b.width * h / b.height), h), Image.LANCZOS)
    out = Image.new("RGB", (a.width + b.width + gap, h), bg)
    out.paste(b, (0, 0))                      # الأولى يميناً (ترتيب عربي)
    out.paste(a, (b.width + gap, 0))
    return out


def grid(ims, cols=4, gap=16, bg=(255, 255, 255)):
    """لوحةٌ مجمّعة من صفحاتٍ صغيرة."""
    w = max(i.width for i in ims)
    h = max(i.height for i in ims)
    rows = (len(ims) + cols - 1) // cols
    out = Image.new("RGB", (cols * w + (cols - 1) * gap, rows * h + (rows - 1) * gap), bg)
    for k, im in enumerate(ims):
        r, c = divmod(k, cols)
        c = cols - 1 - c                       # من اليمين لليسار
        out.paste(im, (c * (w + gap), r * (h + gap)))
    return out


def save(im, name, width=1460):
    if im.width > width:
        im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    p = os.path.join(OUT, name + ".jpg")
    im.save(p, "JPEG", quality=84, optimize=True)
    return os.path.getsize(p) // 1024


# رابط زيارةٍ تجريبي لالتقاط صفحة الزائر
VISIT = ""
_vp = os.path.join(SCRATCH, "visit_link.txt")
if os.path.exists(_vp):
    VISIT = open(_vp).read().strip()

JOBS = {}


def J(name, fn):
    JOBS[name] = fn


# ═════════ الشرائح ═════════
J("s01", lambda: duo(frame(page("prep", 0, 110)), frame(page("obs", 0, 110))))
J("s02", lambda: frame(page("obs", 0, 150, (0.06, 0.30, 0.95, 0.72))))
J("s03", lambda: duo(frame(page("prep", 0, 110)), frame(page("obs", 0, 110))))
J("s04", lambda: frame(page("obs", 0, 150)))
J("s05", lambda: duo(frame(page("prep", 0, 110)), frame(page("prep", 1, 110))))
J("s06", lambda: frame(page("prep", 1, 165, (0.05, 0.10, 0.96, 0.34))))
J("s07", lambda: frame(page("guide", 1, 150)))
J("s08", lambda: frame(page("card", 0, 150)))
J("s09", lambda: frame(page("approach", 0, 150)))
J("s10", lambda: frame(page("obs", 2, 165, (0.05, 0.42, 0.96, 0.70))))
J("s11", lambda: duo(frame(page("peer", 0, 110)), frame(page("bridge", 0, 110))))
J("s12", lambda: frame(page("mech", 0, 150)))
J("s13", lambda: frame(page("mech", 0, 175, (0.05, 0.40, 0.96, 0.66))))
J("s14", lambda: duo(frame(page("filled_m", 0, 110)), frame(page("filled_m", 1, 110))))
J("s15", lambda: duo(frame(page("filled_m", 1, 150, (0.05, 0.12, 0.96, 0.30))),
                     frame(page("filled_f", 1, 150, (0.05, 0.12, 0.96, 0.30)))))
J("s16", lambda: frame(shot(SRC["web"], None, 1500, 1000)))
J("s17", lambda: frame(shot(SRC["web"], None, 1500, 1000, 4500, "#v=" + VISIT)))
# ⛔ س١٨ كانت لقطةَ صفحة الاستضافة، وأُخرجت من المنشور (٢٩ سبتمبر ٢٠٢٦)
J("s19", lambda: frame(page("plan", 0, 150)))
J("s20", lambda: grid([frame(page(k, 0, 46), 6) for k in
                       ("prep", "obs", "guide", "plan", "card", "approach", "peer", "mech")], cols=4))
J("s21", lambda: frame(page("nashra_prep", 0, 150)))
J("s22", lambda: duo(frame(page("prep", 0, 110)), frame(page("obs", 0, 110))))

if __name__ == "__main__":
    only = sys.argv[1:] or sorted(JOBS)
    for name in only:
        try:
            kb = save(JOBS[name](), name)
            print(f"✓ {name}  {kb} ك.ب", flush=True)
        except Exception as e:
            print(f"✗ {name}  ← {type(e).__name__}: {e}", flush=True)
