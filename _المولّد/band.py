# -*- coding: utf-8 -*-
"""عنوان المستند داخل الشريط الأزرق للكليشة (طلب المستشار 2026-09-21).

الشريط جزء من صورة الكليشة، فيُكتب العنوان في إطار نصّي (framePr) مثبَّت بإحداثيات الصفحة داخل الترويسة،
فيظهر في الشريط على كل صفحة. الإحداثيات مقيسة بالبكسل من kl_portrait.jpg (1196×1550 ↔ 21×29.7 سم):
الأزرق الصافي من y=58 إلى y=114، وحافته اليسرى مائلة من x=705 أعلاه إلى x=664 أسفله، ويمتد إلى x=1192.
"""
import os
from dox import run, rtl_par, par_space, _add_pPr_el

HERE = os.path.dirname(os.path.abspath(__file__))
JAZ_BOLD = os.path.expanduser("~/Library/Fonts/ArbFONTS-Al-Jazeera-Arabic-Bold.ttf")

# صندوق الكتابة الآمن داخل شريط ابن خلدون (سم من أعلى الصفحة ويسارها) — بعيداً عن الحافة المائلة
IK_BAND = dict(x=12.75, y=1.02, w=7.85, h=0.98)


def _fit_size(text, max_pt, box_w_cm, ttf=None):
    """أكبر مقاس لا يتجاوز فيه العنوان عرض الصندوق. PIL يقيس الحروف منفصلة (أعرض من المتصلة)
    فالتقدير متحفّظ؛ ويُترك 8٪ هامشاً."""
    try:
        from PIL import ImageFont
    except ImportError:
        return max_pt
    size = max_pt
    while size > 9:
        f = ImageFont.truetype(ttf or JAZ_BOLD, int(size * 10))
        w_pt = f.getlength(text) / 10
        if w_pt / 72 * 2.54 <= box_w_cm * 0.92:
            break
        size -= 0.5
    return size


def band_title(section, text, band=IK_BAND, max_pt=16, color="FFFFFF",
               font=None, ttf=None, latin=False):
    """يضع العنوان أبيض في منتصف الشريط، أفقياً وعمودياً.

    ⚠️ و`font`/`ttf`/`latin` للعنوان الإنجليزي: خطُّ الجزيرة بلا حروفٍ لاتينية،
       ولو قِيس عرضُ الإنجليزية به خرج المقاسُ خطأً. والافتراضُ عربيٌّ كما كان."""
    size = _fit_size(text, max_pt, band["w"], ttf)
    p = section.header.add_paragraph()
    if not latin:
        rtl_par(p)
    tw = lambda cm: str(int(round(cm * 566.93)))
    _add_pPr_el(p, 'framePr', {'w': tw(band["w"]), 'h': tw(band["h"]), 'hRule': 'exact',
                               'x': tw(band["x"]), 'y': tw(band["y"]),
                               'hAnchor': 'page', 'vAnchor': 'page', 'wrap': 'notBeside'})
    line = size * 1.25                      # سطر الجزيرة بلا قصّ
    before = max(0.0, (band["h"] / 2.54 * 72 - line) / 2)
    _add_pPr_el(p, 'spacing', {'before': str(int(before * 20)), 'after': '0',
                               'line': str(int(line * 20)), 'lineRule': 'exact'})
    _add_pPr_el(p, 'jc', {'val': 'center'})
    run(p, text, size=size, bold=True, color=color,
        **({"font": font, "latin": latin} if font else {}))
    return size
