# -*- coding: utf-8 -*-
"""حارسُ الأيقونة واللون — على شجرة التسليم لا على البناء.

⛔ **كانت كلُّ صفحةٍ منشورةٍ بلا أيقونة**، فيضع المتصفّحُ كرتَه الرمادية.
   شكا المستشارُ ٤ أكتوبر ٢٠٢٦ وهو يسجّل الفيديوهات.

⚠️ **ولا يكفي وجودُ الوسم**: `apple-touch-icon` مسارٌ نسبيٌّ يختلف بعمق
   الصفحة — صفحةُ الجذر بلا بادئة، وصفحةُ مجلدِ «٨» بـ`../`. فلو نُسخ
   الوسمُ كما هو من صفحةٍ لأخرى أشار إلى لا شيء، والوسمُ موجودٌ والأيقونةُ
   غائبة. فيُحلُّ المسارُ على القرص من موضع الصفحة نفسِها.

⚠️ **والصورةُ تُفكّ وتُقاس**: data: قد تحمل بايتاتٍ فاسدةً أو صورةً فارغةً
   فيمرُّ فحصُ النصّ وهي لا تُرسم. فتُفكُّ الـPNG ويُتحقَّق من مقاسها ومن
   أنها تحمل لونَ الهوية **والأبيضَ** معاً — أي أن الحرفَ مرسومٌ فيها.

الأرضيّة: `FLOOR` صفحةً. وفحصٌ لم يَقِس شيئاً فاشلٌ لا ناجح.
"""
import base64
import io as _io
import os
import re
import sys

import icon as ICO

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FLOOR = 10          # عددُ صفحات التسليم — تُعدُّ ولا تُفترض

SVG_RE = re.compile(r'<link rel="icon" type="image/svg\+xml" href="data:image/svg\+xml;base64,([^"]+)"')
PNG_RE = re.compile(r'<link rel="icon" type="image/png" sizes="180x180" href="data:image/png;base64,([^"]+)"')
APL_RE = re.compile(r'<link rel="apple-touch-icon" href="([^"]*)"')
THM_RE = re.compile(r'<meta name="theme-color" content="([^"]*)"')


def pages():
    out = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d != "_المولّد" and not d.startswith(".")]
        for fn in fns:
            if fn.endswith(".html"):
                out.append(os.path.join(dp, fn))
    return sorted(out)


def px(data):
    """ألوانُ الصورة — بلا اعتمادٍ على مكتبةٍ خارجيةٍ إن غابت."""
    from PIL import Image
    im = Image.open(_io.BytesIO(data)).convert("RGBA")
    return im.size, im.getcolors(maxcolors=1 << 20)


def check(p):
    bad = []
    s = open(p, encoding="utf-8").read(1 << 16)     # الرأسُ وحدَه يكفي
    m = SVG_RE.search(s)
    if not m:
        bad.append("لا أيقونةَ SVG")
    else:
        svg = base64.b64decode(m.group(1)).decode("utf-8")
        if "<path" not in svg or ICO.THEME not in svg:
            bad.append("أيقونةُ SVG بلا مسارٍ أو بلا لون الهوية")
    m = PNG_RE.search(s)
    if not m:
        bad.append("لا أيقونةَ PNG")
    else:
        try:
            (w, h), cols = px(base64.b64decode(m.group(1)))
        except Exception as e:
            bad.append("PNG لا تُفكّ: %s" % e)
        else:
            if (w, h) != (180, 180):
                bad.append("مقاسُ PNG %dx%d لا 180" % (w, h))
            white = sum(n for n, c in cols if c[0] > 230 and c[1] > 230 and c[2] > 230 and c[3] > 200)
            brand = sum(n for n, c in cols if 25 < c[0] < 70 and 90 < c[1] < 130 and 100 < c[2] < 155 and c[3] > 200)
            if white < 500:
                bad.append("PNG بلا حرفٍ أبيض (%d بكسل)" % white)
            if brand < 500:
                bad.append("PNG بلا لون الهوية (%d بكسل)" % brand)
    m = APL_RE.search(s)
    if not m:
        bad.append("لا apple-touch-icon")
    else:
        tgt = os.path.normpath(os.path.join(os.path.dirname(p), m.group(1)))
        if not os.path.exists(tgt):
            bad.append("apple-touch-icon يشير إلى غير موجود: " + m.group(1))
    m = THM_RE.search(s)
    if not m:
        bad.append("لا theme-color")
    elif m.group(1) != ICO.THEME:
        bad.append("theme-color %s لا %s" % (m.group(1), ICO.THEME))
    return bad


def main():
    ps = pages()
    print("  صفحاتُ التسليم المفحوصة:", len(ps))
    if len(ps) < FLOOR:
        print("⛔ الأرضيّة %d ووُجد %d — الفحصُ لم يَقِس ما يكفي." % (FLOOR, len(ps)))
        return 1
    bad = 0
    for p in ps:
        errs = check(p)
        if errs:
            bad += 1
            print("  ⛔", os.path.relpath(p, ROOT))
            for e in errs:
                print("       ·", e)
    if bad:
        print("⛔ %d من %d صفحةً بلا أيقونةٍ سليمة." % (bad, len(ps)))
        return 1
    print("  ✓ كلُّ صفحةٍ تحمل الأيقونةَ بصيغها الثلاث ولونَ الهوية")
    return 0


if __name__ == "__main__":
    sys.exit(main())
