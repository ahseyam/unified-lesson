# -*- coding: utf-8 -*-
"""منصة الحصة الموحَّدة — تطبيقٌ واحد بأربع مراحل وثلاثة أدوار.

المراحل: ١ الجدولة · ٢ الاستعداد والتحضير · ٣ أداء الحصة · ٤ بعد الحصة.
الأدوار: المعلم القائم بالحصة · المعلم الزائر · المقيّم (مدير/وكيل تعليمي/مشرف مختص).
ولكل دورٍ ما يخصّه فقط، ولكل مرحلةٍ شرحُها ونماذجها المعينة وأداتها القابلة للتعبئة.

التخزين: محليٌّ في الجهاز دائماً، ومشتركٌ عبر Google Apps Script إن رُبط (اختياري).
⚠️ GitHub Pages يخدم التطبيق ولا يخزّن ما يُكتب فيه — فالمشترك يحتاج الخادم المجاني.

الاستعمال: CLS_GENDER=m|f python3 platform.py <الملف.html>
"""
import base64
import json
import os
import re
import sys
import unicodedata
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import zcontent as Z
import scontent as S
from femjs import fem_js, guard
import i18n
import scheddata as SD
# ⛔ تفصيلُ الاتجاهات (تعريفُه وشواهدُه) يحتاجه أمرُ الذكاء الاصطناعي، ويُبنى
#    هنا لأن `acontent` كان يُستورد بعد `DATA` فرُفع NameError. (٣٠ سبتمبر ٢٠٢٦)
import acontent as _ACX
# ⚠️ المفتاحُ **الاسمُ القصيرُ المعروض** في `TICKS["dir"]` لا الاسمُ الطويل في
#    `acontent` — وإلا لم يجد الأمرُ اتجاهَ الحصة فخرج بلا تعريفٍ ولا شواهد.
_A2SHORT = {"pbl": "حل المشكلات والمشاريع", "differentiated": "التعليم المتمايز",
            "thinking": "التفكير الناقد والإبداعي", "afl": "التقويم من أجل التعلم",
            "tech": "التقنية والذكاء الاصطناعي", "values": "القيم وبناء الشخصية"}
_APPRDET = {_A2SHORT[_a[0]]: {"what": _a[2], "evid": list(_a[5])}
            for _a in _ACX.APPROACHES if _a[0] in _A2SHORT}
assert len(_APPRDET) == len(_ACX.APPROACHES), "⛔ اتجاهٌ بلا مفتاحٍ قصير"
from prepdef import (HINTS, INFO, TICKS, STAGES, MODES, TIMEMAP_K, TIME_KEYS,
                     TIME_SUM, TIME_LEGACY, TIME_MAIN, TIME_DIFF,
                     TIME_DIFF_TITLE, SECTIONS)

FONTS = os.path.expanduser("~/Library/Fonts")
SITE = "https://ahseyam.github.io/unified-lesson/"
RLM = "‏"
GENDER = os.environ.get("CLS_GENDER", "m")


def _icorel(outpath):
    """بادئةُ المسار من موضع المخرَج إلى جذر التسليم — بعمقه لا بالظنّ."""
    d = os.path.dirname(os.path.abspath(outpath))
    r = os.path.relpath(ROOT, d) if d != ROOT else "."
    return "" if r == "." else (r.replace(os.sep, "/") + "/")

TRY = os.environ.get("CLS_ENV", "") == "try"
F = GENDER == "f"


def g(m, f):
    return f if F else m


def fem(t):
    if not F or not isinstance(t, str):
        return t
    from gender import feminize
    from lfem import lfem
    return feminize(lfem(t))


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


def doc(*parts):
    """رابط مستندٍ على الموقع المنشور."""
    return SITE + quote(os.path.join(*parts))


PDF = " (للعرض والطباعة).pdf"
D1, D2, D3 = "١ - نموذج تحضير الحصة", "٢ - استمارة الملاحظة الصفية", "٣ - الأدوات المساندة"
D4, D5, D6, D7 = ("٤ - بطاقات إستراتيجيات التدريس", "٥ - الاتجاهات التدريسية",
                  "٦ - بطاقة زيارة الأقران", "٧ - آلية جداول الحصص الموحَّدة")
D10 = "١٠ - أدلّة استخدام المنصة"
# ⛔ دليلُ كلِّ دورٍ يُعرض له وحده في المرحلة الأولى: فيجدها صاحبُها في أول
#    شاشةٍ يفتحها، ولا يرى دليلَ غيره فيقرأ ما لا يعنيه. (٢٩ سبتمبر ٢٠٢٦)
NSH_ROLE = [("teacher", "المعلم القائم بالحصة", "المعلمة القائمة بالحصة", "Teaching Teacher"),
            ("peer", "المعلم الزائر", "المعلمة الزائرة", "Peer Teacher"),
            ("principal", "مدير المدرسة", "مديرة المدرسة", "School Principal"),
            ("deputy", "الوكيل التعليمي", "الوكيلة التعليمية", "Academic Deputy"),
            ("supervisor", "المشرف التربوي", "المشرفة التربوية", "Subject Supervisor")]
SF = " (بنات)" if F else ""
GF = "بنات" if F else "بنين"

# ═════════ شرح كل مرحلة ونماذجها المعينة ═════════
PHASES = [
 dict(id=1, t="جدول الحصص الموحَّدة للتقويم الخارجي",
      s="المصفوفة الأولى — ومنها تبدأ كل حصة",
      who=["evaluator", "teacher", "peer"],
      why="هذه الشاشة هي جدولُ الحصص الموحَّدة للتقويم الخارجي داخل المنصة: "
          "لكل مجمعٍ ورقةٌ، وصفوفُها اليومُ في تخصص المعلم الزائر، وأعمدتُها الحصصُ بأوقات بدئها، "
          "وتحت كل حصةٍ خمسةُ حقول: المعلم · الإستراتيجية · الاتجاه التدريسي · الفصل · وقت البدء. "
          "فما يُكتب في الخلية يصير حصةً، ومن الخلية تبدأ الحصةُ بضخِّ بياناتها في التحضير.",
      # ⛔ **خطوةٌ تأمر بما لا يُستطاع**: كانت «واكتب اسم المدرسة» ولا حقلَ
      #    نصيّاً لها في المنصة — المدرسةُ تُختار من مربّعاتٍ أو تُفرض عند
      #    الدخول على المدير والوكيل. فمن قرأ الخطوةَ بحثَ عن حقلٍ لا وجودَ
      #    له ثم شكّ في نفسه. (أمسكه مسحُ ما بقي ١ أكتوبر ٢٠٢٦)
      # ⚠️ وتُكتب بالجنسَين صريحةً: المؤنِّثُ قلبَ «اختر» و«معلماً» وأفلتَ
      #    «رشِّح» و«من دخل … فمدرستُه» — فخرج نصفُ النصِّ مذكَّراً.
      steps=[g("اختر القطاع والمجمع، ثم رشِّح الأعمدة بمدرستك من المربّعات — "
               "ومن دخل مديراً أو وكيلاً فمدرستُه مثبَّتةٌ عليه. "
               "ثم تخصصك إن كنت معلماً.",
               "اختاري القطاع والمجمع، ثم رشِّحي الأعمدة بمدرستك من المربّعات — "
               "ومن دخلت مديرةً أو وكيلةً فمدرستُها مثبَّتةٌ عليها. "
               "ثم تخصصك إن كنتِ معلمةً."),
             "الأسبوع: اتركه «كل الأسابيع» لترى الفصل كلَّه كما في الإكسل، أو اختر أسبوعاً بعينه.",
             "اكتب في خلية الحصة: اسم المعلم، والإستراتيجية من البنك، والاتجاه التدريسي، والفصل.",
             "ومجموعةُ التخصص الزائرة لكل يوم تظهر في أول خلية من صفه وتُعدَّل منها.",
             # ⚠️ ورقةُ الروضة مستقلّةٌ ببنيتها، فتُذكر في الخطوات وإلا بحث عنها
             #    من يعمل فيها في جدولٍ لا يحوي مرحلتَه. (٦ أكتوبر ٢٠٢٦)
             "ولرياض الأطفال ورقتها: تبويب «رياض الأطفال» — صفوفها الأسبوع واليوم، "
             "والمادة تُختار في الخلية من قائمة موادها هي (حلقة · أركان · مكتبة …) "
             "لأن معلمة الصف تُدرّس أكثر من مادة.",
             "اضغط «ابدأ الحصة» في الخلية — تُفتح مرحلةُ التحضير وبياناتُها مضخوخةٌ فيها."],
      docs=[("نشرة آلية الحصص الموحَّدة",
             doc(D7, GF, f"آلية الحصص الموحَّدة — ابن خلدون{SF}" + PDF), "*")]
           # ⛔ لكل دورٍ رابطٌ واحدٌ يتبع لغةَ قارئه: العربيُّ افتراضاً،
           #    والإنجليزيُّ حين تكون الواجهةُ إنجليزية.
           + [(f"دليلُ استخدام المنصة — {(_f if F else _m)}",
               doc(D10, GF, f"دليل استخدام المنصة — {(_f if F else _m)} — ابن خلدون{SF}.pdf"),
               _k,
               doc(D10, "English", f"Platform User Guide — {_e} — Ibn Khaldun Schools.pdf"))
              for _k, _m, _f, _e in NSH_ROLE]),
      # ⛔ حُذف رابطُ «جدول الحصص (إكسل)» ٢٩ سبتمبر ٢٠٢٦: الجدولُ يُبنى في المنصة
      #    نفسِها، فنسخةُ الإكسل تفترق عنه ويصير مصدرا حقيقةٍ متناقضان.
 dict(id=2, t="الاستعداد والتحضير", s="ما يُعدّه المعلم قبل الحصة",
      who=["teacher", "evaluator"],
      # ⛔ الوعدُ كان مطلقاً وكاذباً: «كلُّ خانةٍ يقابلها مؤشر» — وتسعةُ مؤشراتٍ
      #    لا تُحضَّر أصلاً (أداءٌ يُشاهد) وواحدٌ يُتحقَّق من السجلّ. فصار الوعدُ
      #    بالعدد، وصار **مقيساً**: جدولُ التوأمة محروسٌ في البناء. (١ أكتوبر ٢٠٢٦)
      why="التحضير توأمُ الاستمارة: ستةٌ وأربعون مؤشراً من الخمسين له خانتُه هنا، "
          "ويراها الزائرُ تحت المؤشر وهو يرصد. وأربعةٌ لا تُحضَّر: ثلاثةُ أداءٍ "
          "يُشاهد في الحصة، وواحدٌ يُتحقَّق من سجلّ التخطيط. فما يُكتب هنا "
          "هو ما يُرى في الحصة — ولا يُصدَّر ناقصاً.",
      steps=["اختر حصتك من الجدول.",
             "املأ خانات التحضير بترتيب مجالات الاستمارة، واستعن بزرّ «؟» في كل خانة.",
             "وزّع خريطة الزمن حتى يساوي مجموع المراحل زمن الحصة.",
             "اكتب المهمة المكيَّفة والإثرائية — فعبارة «مراعاة الفروق» بلا مهمةٍ لا تُعدّ شاهداً.",
             # ⛔ الوعدُ كان أوسعَ من الحارس: `missing()` يفحص `req` وحدَه،
             #    وثلاثَ عشرةَ خانةً تحمل مؤشراً بلا `req`. ولا تُجعل كلُّها
             #    إلزاميةً (شاهدٌ كاذبٌ أسوأُ من فراغ) — فيُصحَّح الوعدُ ويُعدُّ المتروك.
             "اضغط «إصدار التحضير»: لا يعمل قبل اكتمال الخانات الإلزامية، ويقول لك بعدها كم مؤشراً تركتَه بلا شاهدٍ مخطَّط."],
      docs=[("نشرة استخدام نموذج التحضير",
             SITE + quote(os.path.join(D1, "نشرة الاستخدام",
                                       f"نشرة استخدام نموذج التحضير — ابن خلدون{SF}.pdf")), "*"),
            ("القالب الورقي للتحضير", doc(D1, GF, f"نموذج تحضير الحصة — ابن خلدون{SF}" + PDF), "*"),
            # ⛔ وقالبُ وورد كذلك: المعلمُ الذي يختار الورقَ يحتاج ملفاً **يُكتب
            #    فيه** لا صورةً تُطبع. (طلبُ المستشار ١ أكتوبر ٢٠٢٦)
            ("القالب الورقي للتحضير (وورد — يُكتب فيه)",
             doc(D1, GF, f"نموذج تحضير الحصة — ابن خلدون{SF}.docx"), "*"),
            # ⛔ بطاقاتُ الإستراتيجيات ١٩ تخصُّ **التحضير** قبل التنفيذ: المعلمُ
            #    يختار إستراتيجيتَه هنا فيحتاج بطاقتَها هنا. (٣٠ سبتمبر ٢٠٢٦)
            ("بنك بطاقات الإستراتيجيات التسع عشرة", SITE + quote(D4) + "/", "*"),
            ("نشرات الاتجاهات التدريسية الستة", SITE + quote(D5) + "/", "*")]),
 dict(id=6, t="تنفيذ الحصة", s="ورقةُ التنفيذ — ما يُنفَّذ وما يُقرأ قبل الدخول",
      who=["teacher", "peer", "evaluator"],
      why="بعد أن يكتمل التحضير، هذه ورقتُه جاهزةً للتنفيذ: خريطةُ الزمن ومراحلُ الحصة "
          "وبطاقةُ الإستراتيجية والمهمتان المكيَّفة والإثرائية — يُمسكها المعلم في الحصة، "
          "ويقرؤها الزائرُ قبل دخوله فيعرف ما يبحث عن شواهده.",
      steps=["اختر الحصة — وتظهر ورقةُ تنفيذها كاملةً في شاشةٍ واحدة.",
             "المعلم: نفّذ المراحل بأزمنتها، والورقةُ أمامك بلا تنقّل بين الشاشات.",
             "الزائر: اقرأها قبل الدخول — فالرصدُ قبل قراءة التحضير يُفقد الشواهد معناها.",
             "اطبعها إن شئت: تخرج في صفحةٍ أو صفحتين بلا أزرارٍ ولا زوائد."],
      docs=[("بنك بطاقات الإستراتيجيات", SITE + quote(D4) + "/", "*"),
            ("نشرات الاتجاهات التدريسية", SITE + quote(D5) + "/", "*")]),
 dict(id=3, t="رصد الحصة", s="ما يُملأ أثناء الحصة ولها",
      who=["peer", "evaluator"],
      # ⛔ كان «ثلاثة مقيّمين يرصدون» ثم صار «المشرفَ وحدَه» (٣٠ سبتمبر ٢٠٢٦)،
      #    فقِيس ٤ أكتوبر أن الأربعةَ الباقين يرون **صفرَ حقل** على حصةٍ
      #    مكتملة. فنقضه المستشارُ: المقيّمون خمسةٌ، لكلٍّ استمارتُه، والمعتمَدُ
      #    متوسّطُ من رصد.
      why="خمسةُ مقيّمين يرصدون كلٌّ في نطاقه — المشرف التربوي ومدير المدرسة "
          "والوكيل التعليمي ومدير المجمع وفريق متابعة التقويم الداخلي. "
          "ولكل مقيّمٍ استمارته المستقلة بدرجتها، والمعتمَد متوسط من رصد. "
          "ومعلمان زائران يملآن بطاقة الأقران. "
          "والشاهد يُرى لا يُفترض: ما لم يُرصد أثناء الحصة لا يُحتسب.",
      steps=["افتح الحصة، واقرأ تحضير المعلم أولاً — فهو ما تبحث عن شواهده.",
             "ارصد الاستمارة مؤشراً مؤشراً، و«لا ينطبق» للاستثناء لا للهروب.",
             "افتح بطاقة تشخيص الإستراتيجية التي أعلنها المعلم وقيّم مؤشراتها العشرة.",
             "استمارتك باسمك وحدك — لا يمحوها مقيّمٌ آخر، وتظهر درجته بجوار درجتك.",
             "المعلم الزائر يملأ بطاقة الأقران وينقل إجراءً واحداً لنفسه."],
      docs=[("نشرة استخدام الاستمارة",
             SITE + quote(os.path.join(D2, "نشرة الاستخدام",
                                       f"نشرة استخدام الاستمارة — ابن خلدون{SF}.pdf")), "peer,evaluator"),
            ("دليل مستويات الأداء",
             doc(D3, "دليل مستويات الأداء", GF, f"دليل مستويات الأداء — ابن خلدون{SF}" + PDF), "*"),
            ("الاستمارة الورقية",
             doc(D2, GF, f"استمارة الملاحظة الصفية — ابن خلدون{SF}" + PDF), "peer,evaluator"),
            ("بطاقة زيارة الأقران",
             doc(D6, GF, f"بطاقة زيارة الأقران — ابن خلدون{SF}" + PDF), "peer")]),
 dict(id=4, t="بعد الحصة", s="النتيجة وبطاقة الجسر والاعتماد",
      who=["teacher", "peer", "evaluator"],
      why="تنتهي الحصة بدرجةٍ موثَّقة وإجراءٍ واحدٍ يُتابَع — لا بانطباعٍ عام. "
          "وبطاقة الجسر هي التي تنقل الأثر إلى الحصص اليومية.",
      steps=["راجع الدرجة والنسبة والمستوى، ودرجة مؤشر الإستراتيجية.",
             "اكتب في بطاقة الجسر إجراءً واحداً محدداً يمكن رؤيته.",
             "اطبع تقرير الزيارة أو أرسله للمعلم عبر واتساب.",
             "وفي الزيارة التالية يُفتح الإجراء للتحقق من تنفيذه."],
      docs=[("بطاقة الجسر", doc(D3, "بطاقة الجسر", GF, f"بطاقة الجسر — ابن خلدون{SF}" + PDF), "*"),
            ("خطة الاستعداد للزيارة",
             doc(D3, "خطة الاستعداد", GF, f"خطة الاستعداد — ابن خلدون{SF}" + PDF), "evaluator")]),
]

# ═════════ الأدوارُ الخمسة ═════════
# ⛔ كان «المقيّم» دوراً واحداً يجمع المديرَ والوكيلَ والمشرف، ونطاقاتُهم متناقضة:
#    المديرُ والوكيلُ في مدرسةٍ واحدة، والمشرفُ يدور على المجمعات بتخصصه يوماً بيوم.
#    ففُصلوا ٢٩ سبتمبر ٢٠٢٦ بطلب المستشار: «قم بمراجعة كل ما يخص الزوار المقيمين
#    (مدير/ مشرف تربوي/ وكيل تعليمي) … وما لا يخصه قم بحذفه واستبداله بما يخصه».
# ⚠️ و`who` في المراحل يبقى "evaluator" — تُترجمه effRole() للثلاثة، فلا تُمسّ.
# scope: ما يُسأل عنه عند الدخول — "school" مدرسةٌ واحدة · "spec" تخصص · "" لا شيء.
ROLES = [
    dict(k="teacher", t=g("المعلم القائم بالحصة", "المعلمة القائمة بالحصة"),
         d=g("يحضّر حصته ويصدرها، ثم يرى نتيجتها وإجراء الجسر",
             "تحضّر حصتها وتصدرها، ثم ترى نتيجتها وإجراء الجسر"), scope="spec"),
    dict(k="peer", t=g("المعلم الزائر", "المعلمة الزائرة"),
         d=g("يرى الزيارات المسنَدة إليه، ويقرأ التحضير ويملأ بطاقة الأقران",
             "ترى الزيارات المسنَدة إليها، وتقرأ التحضير وتملأ بطاقة الأقران"), scope="spec"),
    # ⛔ **الوصفُ كان يَعِد بما تمنعه الشفرة** (١ أكتوبر ٢٠٢٦): وعدَ المديرَ
    #    برصدٍ مطلقٍ و`canScore` لا تُجيزه إلا على حصةٍ لا مشرفَ لتخصصها.
    # ⛔ **ثم انقلب فمنعَ ما تُجيزه**: فُتحت الاستمارةُ للمقيّمين الخمسة
    #    (٤ أكتوبر ٢٠٢٦) وبقي الوصفُ يقول «ما لا مشرفَ لتخصصه» — فيقرأ
    #    المديرُ في شاشة الدخول أنه لا يرصد، وهو يرصد. والوصفُ يُقاس على
    #    `canScore` لا على ذاكرةِ قرارٍ ماضٍ.
    dict(k="principal", t=g("مدير المدرسة", "مديرة المدرسة"),
         d=g("يرى حصص مدرسته وحدها ويجدولها، ويرصد أيَّ حصةٍ فيها ويعتمد نتيجتها",
             "ترى حصص مدرستها وحدها وتجدولها، وترصد أيَّ حصةٍ فيها وتعتمد نتيجتها"), scope="school"),
    dict(k="deputy", t=g("الوكيل التعليمي", "الوكيلة التعليمية"),
         d=g("يجدول حصص مدرسته ويعدّلها ويحذفها، ويسنِد المعلمين الزائرين، ويرصدها",
             "تجدول حصص مدرستها وتعدّلها وتحذفها، وتسنِد المعلمات الزائرات، وترصدها"), scope="school"),
    dict(k="supervisor", t=g("المشرف التربوي المختص", "المشرفة التربوية المختصة"),
         d=g("يرى حصص تخصصه في المجمع الذي يزوره كل يوم، ويرصدها ويعتمدها",
             "ترى حصص تخصصها في المجمع الذي تزوره كل يوم، وترصدها وتعتمدها"), scope="sup"),
    dict(k="cxmgr", t=g("مدير المجمع", "مديرة المجمع"),
         d=g("يتابع مجمعه كلَّه، ويرصد حصصه",
             "تتابع مجمعها كلَّه، وترصد حصصها"), scope="complex"),
    dict(k="intqa", t="فريق متابعة التقويم الداخلي",
         d=g("اثنان من الإدارة العامة: يتابعان المنظومة كلَّها ويرصدان حصصها",
             "اثنتان من الإدارة العامة: تتابعان المنظومة كلَّها وترصدان حصصها"), scope=""),
]
# ⚠️ **بعد فتح الاستمارة للخمسة** (٤ أكتوبر ٢٠٢٦) لم تعد هذه قائمةَ من يُؤذن
#    له بالرصد — فالرصدُ لكل مقيّمٍ في نطاقه. وبقيت لأنها قائمةُ **من يُنبَّه
#    عليه** في تقرير الحصص بلا مشرف: هؤلاء من يُذكَّرون بها نصّاً.
GAP_SCORE = ["deputy", "principal", "cxmgr"]

SECTORS = ["وطني", "عالمي"]
COMPLEX = {"وطني": ["النفل", "عرقة", "المنار", "الياسمين"],
           "عالمي": ["عرقة", "المنار", "الياسمين"]}

# ═════════ توحيدُ اسم المجمع ═════════
# ⛔ **عطلٌ صامتٌ كشفه المستشار**: القائمةُ تعرض «عرقة» (بالتاء المربوطة)
#    ومصدرُ الجداول يكتبها «عرقه» (بالهاء) — فـ`bands["عرقة"]` و`rot["عرقة"]`
#    غيرُ موجودَين. فمن اختار «عرقة» رأى **جدولاً بلا أعمدة**، ولا قائمةَ
#    مراحلَ تُختار، ولا دورانَ مشرفين. ولم يُنبّه شيءٌ لأن البحث في كائنٍ
#    عن مفتاحٍ غائبٍ يُرجع «غيرَ معرَّف» لا خطأً. (٣٠ سبتمبر ٢٠٢٦)
# ⚠️ والصيغةُ المعتمدةُ «عرقة»: هي اسمُ الحيّ، وهي المستعملةُ في أسماء
#    المراحل داخل المصدر نفسِه («الابتدائية- عرقة») وفي قائمة المجمعات.
_CXFIX = {"عرقه": "عرقة"}
_cx = lambda k: _CXFIX.get(k, k)


def _normcx(o):
    """يوحّد اسمَ المجمع مفتاحاً وقيمةً في أي بنية."""
    if isinstance(o, dict):
        return {_cx(k): _normcx(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_normcx(v) for v in o]
    if isinstance(o, str):
        return _cx(o)
    return o
# ⛔ وحُذف `SCHOOL_STAGES`: لم يبقَ له قارئٌ بعد حذف جدول الحقول الميت.
WEEKS = ["الأسبوع ٤", "الأسبوع ٥", "الأسبوع ٨", "الأسبوع ٩", "الأسبوع ١٠"]
DAYS = ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس"]
PERIODS = ["الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة", "السابعة"]
# ── مأخوذٌ حرفياً من جدول البرنامج السابق (ف٢ — ١٤٤٦هـ) ──
# الورقة الأولى: المجمع × الأسبوع × اليوم ← مجموعة تخصّصٍ زائرة (أربع مجموعات).
# وورقةُ كل مجمع: صفوفها (الأسبوع × اليوم × تخصص المعلم الزائر) وأعمدتها الحصص،
# وتحت كل حصةٍ خمسةُ حقول: المعلم · الإستراتيجية · الاتجاه التدريسي · الفصل · وقت البدء.
# ⛔ لا تُكتب التخصصاتُ هنا: كانت نسخةٌ يدويةٌ بألفاظٍ طويلة («الرياضيات» ·
#    «الدراسات الإسلامية» · «اللغة الإنجليزية») تناقض ما تعرضه المنصةُ فعلاً،
#    لأن المعروضَ يأتي من scheddata المستخرَجةِ من الإكسل («رياضيات» · «إسلامية»
#    · «E»). فكانت مصدرَ حقيقةٍ ثانياً صامتاً — كما كانت COLS. (٢٩ سبتمبر ٢٠٢٦)
SPECGROUPS = SD.GROUPS
PAIRS = SD.PAIRS
SPECS = SD.SPECS
# أوقات البدء المستعملة فعلاً في الملف — ستٌّ لا أكثر، وهي افتراضٌ يقبل التعديل في الخلية.
PTIMES = ["٧:٠٠", "٧:٤٠", "٨:٢٠", "٩:٠٠", "١٠:٤٥", "١١:٣٠"]
# ⛔ حُذفت COLS: كانت مُعرَّفةً ولا يستعملها أحد (مصدرُ حقيقةٍ ثانٍ للأعمدة)،
#    وفيها عمودُ «٣ (صفوف أولية)» الذي أُلغي ٢٩ سبتمبر ٢٠٢٦. ومصدرُ الأعمدة
#    الوحيدُ هو BANDS في scheddata.py المستخرَجةُ من الإكسل.
# ═════════ مطابقةُ تخصصات الكشف بتخصصات المنصة ═════════
# ⛔ كان الرقمُ الوظيفيُّ يعرف تخصصَ صاحبه ويعرضه عند الدخول ثم **يُهمله**، فيعيد
#    المستخدمُ اختيارَه بيده. وأسوأُ منه أن لغةَ الكشف غيرُ لغة المنصة: «E» و«حاسب
#    آلي» و«إسلامية» لا توجد في قائمة التخصصات أصلاً.
# ⚠️ و«أخرى» (٨٨ معلماً) تبقى فارغةً يختارها صاحبُها — لا يُخمَّن لها شيء.
# ⚠️ وتبيّن أن ألفاظَ الكشف **هي** ألفاظُ المنصة نفسُها (رياضيات · إسلامية · E
#    · حاسب آلي)، فلا ترجمةَ إلا لـ«أخرى» التي تبقى فارغةً يختارها صاحبُها.
#    وكنتُ قد كتبتُ ترجمةً إلى ألفاظٍ طويلةٍ لا تعرفها المنصة — فسقط الترشيح.
SPECMAP = {x: x for x in SD.SPECS}
SPECMAP["أخرى"] = ""


def guard_specmap(roster):
    """⛔ قيمةٌ في الكشف بلا مطابقةٍ تمرّ صامتةً فيدخل صاحبُها بلا تخصص."""
    seen = {v.get("s", "") for v in roster.values()}
    miss = sorted(x for x in seen if x not in SPECMAP)
    bad = sorted(v for v in SPECMAP.values() if v and v not in SD.SPECS)
    if miss or bad:
        raise SystemExit(
            "⛔ مطابقةُ التخصصات ناقصة.\n"
            + ("  بلا مطابقةٍ في الكشف: " + " · ".join(miss) + "\n" if miss else "")
            + ("  مطابقةٌ إلى تخصصٍ لا تعرفه المنصة: " + " · ".join(bad) + "\n" if bad else "")
            + "  أضِفها إلى SPECMAP في platform.py — ولا تُخمَّن، تُسأل.")
    return True


# ⚠️ الترتيبُ مرتبطٌ بخانات ev1..ev5 في الجدول — فلا يُبدَّل ولا يُدرَج في وسطه
# ⚠️ وأُلحِق **فريقُ التقويم الداخلي** خامساً (٤ أكتوبر ٢٠٢٦) حين فُتحت
#    الاستمارةُ للمقيّمين الخمسة — ويُلحَق في الآخر لا في الوسط، لأن الرتبةَ
#    هي الخانةُ: من أُدرج في الوسط نُسبت درجتُه إلى خانةِ غيره.
EVAL_ROLES = [g("مدير المدرسة", "مديرة المدرسة"), g("الوكيل التعليمي", "الوكيلة التعليمية"),
              g("المشرف المختص", "المشرفة المختصة"), g("مدير المجمع", "مديرة المجمع"),
              g("فريق متابعة التقويم الداخلي", "فريق متابعة التقويم الداخلي")]

# ⛔ **حُذف جدولُ حقول الجدولة** (عشرونَ حقلاً): كان يُشحَن إلى الصفحة ضمن
#    مفتاحٍ في الشحنة و**لا يقرؤه موضعٌ واحد** — لا الصفحةُ ولا المطبوعُ ولا
#    حارس. وخانةُ الحصة تُبنى في `platform_app.js` بحقولها، وأسماءُ المقيّمين
#    تُقرأ من `D.evalroles` الحيّ. فكان وصفاً ثانياً للخانة يَلزمه التحديثُ
#    ولا أحدَ يُحدّثه — ونسختان تفترقان. (قِيس ١ أكتوبر ٢٠٢٦ بكاشف المفاتيح
#    التي تُشحَن ولا تُقرأ: أربعةٌ منها كانت كذلك.)

DATA = {
    "school": "مدارس ابن خلدون",
    # ⛔ **نطاقُ التخزين يفصل البناءين**: `localStorage` للنطاق لا للمسار،
    #    والبناءان على `ahseyam.github.io` نفسِه — فكانا يتقاسمان المفتاحَ
    #    نفسَه ورابطَ المخزن نفسَه، فتختلط بياناتُ البنين والبنات على الجهاز
    #    الواحد. والبنونَ يبقون على «ik» فلا تضيع بياناتٌ قائمة.
    # ⛔ **ولم تكن ثَمَّ بيئةُ تجربة**: كلُّ بناءٍ يذهب إلى ٤٦٠ معلّماً مباشرةً،
    #    فأولُ من يجرّب التغييرَ هم المستخدمون — وهو سببُ أن تصلني الأعطالُ
    #    منهم لا منّي. (٧ أكتوبر ٢٠٢٦)
    # ⚠️ فنسخةُ التجربة **قاعدتُها منفصلةٌ تماماً** (`ikm_try`): تُجرَّب فيها
    #    التغييراتُ على بياناتٍ لا يملكها أحد، ولا تمسُّ حرفاً من بيانات
    #    المعلمين. والفصلُ في `dbid` وحدَه — فما سواه نسخةٌ واحدةٌ لا نسختان.
    "dbid": ("ikf" if F else "ikm") + ("try" if TRY else ""),
    # ⚠️ عنوان المستند يُؤنَّث والرابط لا يُمَسّ — وإلا انكسر المسار
    "phases": [dict(p, t=fem(p["t"]), s=fem(p["s"]), why=fem(p["why"]),
                    steps=[fem(x) for x in p["steps"]],
                    docs=[[fem(t), u, r] + ([d[3]] if len(d) > 3 else [])
                          for d in p["docs"] for t, u, r in [d[:3]]]) for p in PHASES],
    "roles": ROLES,
    "complexes": COMPLEX,
    "sectors": SECTORS,
    # ── بنيةُ جدول البرنامج السابق مستخرجةً من الإكسل حرفياً (scheddata.py) ──
    # ⚠️ الأسابيعُ الستةُ بتواريخها هي المعمولُ بها، وأسابيعُ الملف الأصلي مرجعٌ لا أكثر
    "weeks": [c["w"] for c in SD.CAL],
    "cal": SD.CAL,                   # لكل أسبوع: مداه ميلادياً وهجرياً وتاريخُ كل يوم
    "days": SD.DAYS,                 # ولا أربعاء: صفُّه فارغٌ في الأصل
    "specs": SD.SPECS,               # ثمانيةٌ مفردة
    "specgroups": SD.GROUPS,         # أربعُ مجموعاتٍ زائرة
    # ⚠️ مفتاحُ المجموعة ثابتٌ (تبنى عليه ROT6/SUP6)، واسمُها المعروضُ يتبع
    #    محتواها — فلا يُقرأ «رياضيات واجتماعيات» وفيها الرياضياتُ وحدَها.
    "grouplabel": SD.GROUP_LABEL,
    "pairs": dict(SD.PAIRS, **{SD.NAT_GROUP: SD.NAT_SPECS}),
    # ⚠️ رياضُ الأطفال تُضاف في نسخة البنات وحدها: مستهدفةٌ في التقويم الخارجي هذا العام.
    #    وأوقاتُها تُترك فارغةً لأن الملفّ الأصلي لا يذكرها — والمعلمة تكتب وقت البدء.
    # ⚠️ اسمُ مرحلة الروضة يُركَّب من اسم المجمع، فيُركَّب من **الصيغة
    #    المعتمدة** لا من مفتاح المصدر — وإلا خرج «رياض الأطفال- عرقه»
    #    ولم يُوحَّد لأنه نصٌّ مركَّبٌ لا مفتاحٌ مفرد.
    "bands": ({cx: [{"stage": "رياض الأطفال- " + _cx(cx), "per": "الحصة 1", "time": ""},
                    {"stage": "رياض الأطفال- " + _cx(cx), "per": "الحصة 2", "time": ""},
                    {"stage": "رياض الأطفال- " + _cx(cx), "per": "الحصة 3", "time": ""}] + bl
               for cx, bl in SD.BANDS.items()} if F else SD.BANDS),               # لكل مجمع: مدارسُه وحصصُ كلٍّ منها ووقتُها الغالب
    "rot": SD.ROT6,                  # من يزور المجمع: [مجمع][أسبوع][يوم] ← مجموعة
    "sup": SD.SUP6,                  # أين يزور المشرف: [مجموعة][أسبوع][يوم] ← مجمع
    # ⛔ الثلاثةُ تُوحَّد أسماءُ مجمعاتها بعد بنائها — مفاتيحَ وقيماً.
    "complexlist": [_cx(k) for k in SD.ROT.keys()],
    # الهويةُ الوطنية في العالمي: ثلاثُ موادَّ في يومٍ واحد، ورحلةٌ ثابتةٌ لا دائرة
    "natgroup": SD.NAT_GROUP, "natspecs": SD.NAT_SPECS, "natdays": SD.NAT_DAYS,
    "natsup": SD.NAT_SUP["f" if F else "m"],
    "wmig": SD.WEEK_MIGRATION,       # هجرةُ ترقيم الأسابيع إلى ترتيب الخطة

    "lab_spec": g("تخصص المعلم الزائر", "تخصص المعلمة الزائرة"),
    "lab_teacher_short": g("المعلم", "المعلمة"),
    "approaches": TICKS["dir"],
    # ⛔ الأمرُ الذي يُنسخ إلى المساعد الذكيّ يحمل **شواهدَ الاتجاه** التي
    #    يبحث عنها الزائر، لا اسمَه وحدَه — وإلا خرج تحضيرٌ لا تُرى شواهدُه.
    "apprdet": _APPRDET,
    "info": [{"k": k, "l": fem(l), "u": u} for k, l, u in INFO],
    "sections": [{"t": s["t"], "n": fem(s["n"]),
                  "rows": [dict(r, label=fem(r["label"]),
                                hint=fem(r["hint"]) if r.get("hint") else None,
                                note=fem(r["note"]) if r.get("note") else None,
                                items=[fem(x) for x in r["items"]] if r.get("items") else None)
                           for r in s["rows"]]} for s in SECTIONS],
    "stages": [[k, fem(n)] for k, n in STAGES],
    "modes": [[fem(x) for x in grp] for grp in MODES],
    # خريطةُ الزمن مجموعتان كما في المطبوع تماماً: أربعٌ ومجموعُها، ثم التمايز
    "tlabels": {k: fem(l) for k, l in TIMEMAP_K},
    "tmain": TIME_MAIN, "tdiff": TIME_DIFF, "tdifft": fem(TIME_DIFF_TITLE),
    "tkeys": TIME_KEYS, "tsum_keys": TIME_SUM, "tlegacy": TIME_LEGACY,
    "domains": [{"t": fem(n), "inds": [fem(t) for t, _ in inds]} for n, inds in Z.MAJALAT],
    "bank": [{"key": k, "name": fem(n), "inds": [fem(x) for x in items]}
             for k, n, _, items in S.BANK],
    "levels": [[fem(n), v] for n, v in [("متحقق", 4), ("متحقق لحد كبير", 3),
                                        ("متحقق جزئياً", 2), ("غير متحقق", 1)]],
    "slevels": [["ممتاز", 10], ["جيد جداً", 8], ["جيد", 6], ["مقبول", 4], ["يحتاج لتحسين", 2]],
    "convert": S.CONVERT,
    # شواهدُ م٢·٣ من دليل مستويات الأداء — تُعرض للراصد وهو يملأ البطاقة
    "m23t": fem(S.M23_TITLE), "m23e": [fem(x) for x in S.M23_EVID], "m23n": fem(S.M23_NOT),
    "tulab": [fem(x) for x in Z.TULAB],
    "peerq": [fem(x) for x in ["ما الذي شاهدتُه وأنوي تطبيقه؟",
                               "كيف سأطبّقه في حصتي؟ وفي أي درس؟",
                               "ما الأثر الذي أتوقّعه على طلابي؟"]],
}

CSS = """
/* ═════════ الأسرةُ اللونية ═════════
   ⛔ شكوى المستشار (٣٠ سبتمبر ٢٠٢٦): النافيُّ الغامقُ «يعطي إحساس الكآبة».
      وقِيست العلّةُ لا وُصفت: #1D3760 لمعانُه ٢٥٪ وتشبُّعُه ٥٤٪ ولونُه ٢١٧°
      — أزرقُ منتصفِ ليل. فأُديرت الأسرةُ كلُّها نحو **تِيلٍ أزرقَ أدفأ
      وأفتح**: اللونُ من ٢١٧° إلى ٢٠١°، واللمعانُ من ٢٥٪ إلى ٢٨٪،
      ومعه خلفياتٌ فاتحةٌ من الأسرة نفسِها فلا تتنافر.
   ⚠️ وكلُّ لونٍ فُحص: الأبيضُ عليه ≥ ٤٫٥، والنصُّ الثانويُّ على الفاتح ≥ ٤٫٥.
      ثم مُسح الموقعُ كلُّه بماسح التباين — وهو الشاهدُ لا الحساب وحدَه. */
:root{--navy:#2C6E8F;--navy2:#215570;--teal:#2A8180;--teal2:#1F6E6C;--tealbg:#E5F2F1;
 /* ⛔ لونا النصّ الثانوي والذهبيّ عُتّما بحسابٍ لا بذوق (٣٠ سبتمبر ٢٠٢٦):
     كان --grey #6B7A8D فيبلغ ٣٫٧٩ على خلفية التِيل و٤٫٣٨ على الأبيض — دون
     حدّ ٤٫٥. وكان --gold #B8862B فيبلغ ٢٫٨١–٣٫٢٤ نصّاً، وأبيضُه على الذهبي
     ٣٫٢٤. فحُسب أقلُّ تعتيمٍ يبلغ ٤٫٥ على **كلِّ** خلفيةٍ يقع عليها. */
 --ink:#16202e;--grey:#606E7F;--line:#d7dfe9;--head:#EAF2F6;--gold:#8D651E;--bg:#F2F6F8;
 --ok:#1d6b35;--okbg:#e8f6ec;--bad:#a52018;--badbg:#fdeceb;--ans:#1F5670}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font-family:JZ,SK,"Geeza Pro",Tahoma,sans-serif;font-size:17px;line-height:1.7}
/* ═════════ الوضعُ الإنجليزي ═════════
   ⛔ خطُّ الجزيرة **بلا حروفٍ لاتينية**، فلو تُرك لسقطت الإنجليزيةُ إلى خطٍّ
      بديلٍ يختاره المتصفّح فاختلفت الأسطر. فيُصرَّح بخطٍّ لاتينيٍّ أولاً.
   ⚠️ والاتجاهُ يُقلب على <html> من JS (dir=ltr)، فتتبعه الصفحةُ كلُّها؛ وما
      استُعمل فيه margin-inline/inset-inline ينقلب معه تلقائياً. */
html.en body,html.en input,html.en select,html.en textarea,html.en button{
 font-family:-apple-system,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif;
 font-size:16px;line-height:1.55}
html.en .side nav button i,html.en .pnav i,html.en .side .sh i,
html.en .side nav button small,html.en .side .cwh,html.en .side .cws{
 font-family:-apple-system,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif}
html.en h1,html.en h2,html.en h3{letter-spacing:-.01em}
/* زرُّ اللغة — في الهيدر وفي شاشة الدخول */
.lang{background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.4);
 color:#fff;border-radius:8px;padding:3px 11px;font-size:13.5px;font-weight:700;
 cursor:pointer;font-family:JZL,SK}
.lang:hover{background:rgba(255,255,255,.3)}
.login .lang{background:var(--navy);border-color:var(--navy);color:#fff}
/* ⚠️ الجدولُ مصفوفةٌ واسعة: في LTR يبدأ العمودُ الأولُ يساراً، وعمودا الأسبوع
   واليوم لاصقان (sticky) بالجهة المنطقية لا بـleft — فيتبعان الاتجاه. */
html.en table.mx th,html.en table.mx td{text-align:left}
html.en .kpi b,html.en .num,html.en table td{font-variant-numeric:tabular-nums}
/* ⛔ خانةُ الجدول ١٨٦ بكسل ثابتة، والإنجليزيةُ أطولُ من العربية في المتوسط
   بنحو الثلث — فـ«— choose Teaching approach —» تُقتطع في القائمة.
   (بلاغُ المستشار ٣٠ سبتمبر ٢٠٢٦ بصورةٍ من الجدول.)
   فيُصغَّر خطُّ الخانة في الإنجليزية وحدَها، ويُضيَّق الحشو — ولا يُمَسُّ
   شيءٌ في العربية. والمقياسُ أن يزول الاقتطاعُ فعلاً لا أن يصغر الخط. */
html.en .cin{font-size:11px;padding:3px 4px;letter-spacing:-.1px}
html.en .cin.nm{font-size:11.5px}
html.en .cin.sm{font-size:10.5px}
html.en select.cin{padding-inline-end:14px;background-position:left .28rem center}
html.en .cellbox{gap:2px;padding:3px}
html.en .cme{font-size:11px;padding:3px 4px}
html.en table.mx th,html.en table.mx td{font-size:11.5px}
html.en table.mx th b{font-size:12px}
html.en .cellbox.appr::before{font-size:9.5px}
html.en .cellbox.part::before{content:"\26a0 Incomplete \2014 not reserved";font-size:9.5px}
a{color:var(--teal2)}
.wrap{max-width:none;margin:0 auto;padding:0 14px}
.wrap.narrow{max-width:1100px}
/* ⚠️ الهيدرُ كان تدرُّجاً من ثلاثة ألوانٍ مشبعةٍ عبر عرض الشاشة — أثقلُ
   سطحٍ فيها. صار لونين متقاربين وحدّاً سفلياً رفيعاً بدل الحافّة الحادّة. */
.top{background:linear-gradient(120deg,var(--navy2),var(--navy) 78%);color:#fff;
 padding:13px 0;box-shadow:inset 0 -1px 0 rgba(255,255,255,.14),0 1px 6px rgba(20,40,70,.10)}
.top .row{display:flex;align-items:center;gap:16px;flex-wrap:wrap;justify-content:space-between;
 max-width:1760px;margin:0 auto;width:100%}
.top img{height:42px;border-radius:5px;background:#fff;padding:3px 7px}
.top h1{font-size:23px;font-weight:700}
.pnav{display:flex;align-items:center;gap:8px}
.pnav button{background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.28);color:#fff;
 font:inherit;font-size:14.5px;font-weight:700;border-radius:9px;padding:6px 14px;cursor:pointer}
.pnav button:hover:not(.off){background:rgba(255,255,255,.3)}
.pnav button.off{opacity:.35;cursor:not-allowed}
.pnav i{font-style:normal;font-family:JZL,SK;font-size:13.5px;color:#dbebf0;white-space:nowrap}
@media(max-width:820px){.pnav i{display:none}}
.top .me{font-family:JZL,SK;font-size:15px;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);
 border-radius:20px;padding:5px 14px;display:flex;gap:10px;align-items:center}
.top .me button{background:transparent;border:0;color:#cfe3ea;font:inherit;font-size:14px;cursor:pointer;text-decoration:underline}
/* ───── الشريط الجانبي الأيمن ───── */
.body{display:grid;grid-template-columns:264px minmax(0,1fr);gap:14px;align-items:start;padding:14px 0 36px}
.body.wide{grid-template-columns:44px minmax(0,1fr)}
.body.wide .side nav button span,.body.wide .side .sh i,.body.wide .side .cw,
.body.wide .side .sf,.body.wide .side .stbox{display:none}
.body.wide .side .sh{padding:9px 6px;text-align:center}
.body.wide .side .sh b{font-size:0}
.body.wide .side .sh b::after{content:"☰";font-size:17px}
.body.wide .side nav{padding:5px}
.body.wide .side nav button{justify-content:center;padding:8px 4px}
.fold{position:absolute;inset-inline-start:8px;top:8px;border:0;background:rgba(255,255,255,.18);
 color:#fff;font:inherit;font-size:12.5px;border-radius:7px;padding:3px 10px;cursor:pointer}
.fold:hover{background:rgba(255,255,255,.3)}
.side{position:relative}
.side{position:sticky;top:14px;background:#fff;border:1px solid var(--line);border-radius:14px;
 overflow:hidden;box-shadow:0 3px 14px rgba(20,40,70,.07)}
.side .sh{background:linear-gradient(120deg,var(--navy2),var(--navy) 80%);color:#fff;padding:11px 14px}
.side .sh b{display:block;font-size:16px;font-weight:700}
.side .sh i{display:block;font-style:normal;font-family:JZL,SK;font-size:12.5px;color:#dbebf0;margin-top:2px}
.side nav{padding:8px}
.side nav button{display:flex;gap:9px;align-items:flex-start;width:100%;text-align:start;border:0;
 background:transparent;color:var(--navy2);font:inherit;padding:9px 10px;border-radius:9px;cursor:pointer;margin-bottom:2px}
.side nav button:hover{background:var(--head)}
.side nav button:focus-visible{outline:2px solid var(--teal);outline-offset:-2px}
/* ⛔ البندُ المختارُ كان كتلةً نافيةً صمّاء تُثقل الشريطَ كلَّه. صار خلفيةً
   خفيفةً وشريطَ دلالةٍ جانبياً — يُعرف بلا أن يصرخ. */
.side nav button.on{background:var(--tealbg);color:var(--navy2);
 box-shadow:inset 3px 0 0 var(--teal)}
html.en .side nav button.on{box-shadow:inset -3px 0 0 var(--teal)}
.side nav button i{font-style:normal;font-family:SK;font-size:13.5px;width:23px;height:23px;flex:0 0 23px;
 border-radius:50%;display:flex;align-items:center;justify-content:center;background:var(--head);color:var(--navy);margin-top:1px}
.side nav button.on i{background:var(--teal);color:#fff}
.side nav button b{display:block;font-size:15px;font-weight:700;line-height:1.35}
.side nav button small{display:block;font-family:JZL,SK;font-size:12px;line-height:1.4;opacity:.75;margin-top:1px}
.side .cw{border-top:1px solid var(--line);background:var(--tealbg);padding:11px 13px}
.side .cwh{font-size:12.5px;font-family:JZL,SK;color:var(--teal2)}
.side .cwt{font-weight:700;font-size:14.5px;color:var(--navy2);margin:2px 0}
.side .cws{font-family:JZL,SK;font-size:11.5px;color:var(--grey);line-height:1.5}
.side .cwg{display:flex;flex-wrap:wrap;gap:4px;margin:7px 0}
.stbox{border-top:1px solid var(--line);padding:11px 13px}
.stbox.local{background:#fff6e5}
.stbox.linked{background:var(--okbg)}
.stbox b{display:block;font-size:14px;line-height:1.4}
.stbox.linked{padding:8px 13px}
.okline{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.okline b{display:inline;font-size:13.5px;color:var(--ok)}
.okline b::before{content:"●";color:#2aa14a;margin-inline-end:5px;font-size:10px}
.lnk{border:0;background:transparent;color:var(--teal2);font:inherit;font-size:12.5px;
 font-family:JZL,SK;cursor:pointer;text-decoration:underline;padding:0}
.lnk:hover{color:var(--navy)}
.stbox.local b{color:#8a5a00}
.stbox.linked b{color:var(--ok)}
.stbox span{display:block;font-family:JZL,SK;font-size:12px;color:var(--grey);line-height:1.55;margin-top:3px}
.stb{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
#syn.oksyn{color:#bfe3c9}
#syn.warnsyn{color:#ffd9a0}
.side .sf{border-top:1px solid var(--line);padding:9px 13px;font-family:JZL,SK;font-size:12px;color:var(--grey);text-align:center}
.bst{font-family:SK;font-size:11.5px;color:var(--teal2);letter-spacing:.3px;background:var(--tealbg);border-radius:20px;padding:2px 10px;display:inline-block;margin-top:4px}
.b.sm{padding:4px 11px;font-size:13.5px}
main{min-width:0}
.mwrap{min-width:0}
/* ───── مصفوفة جدول الحصص الموحَّدة ───── */
/* ⛔ **`100vh` على iOS/سفاري ليس ارتفاعَ النافذة**: يحسبها سفاري على الشاشة
   **بلا شريطَي المتصفّح**، فيزيد الارتفاعُ عمّا يُرى فعلاً — فآخرُ صفوف
   المصفوفة تقع خلف شريط العناوين ولا تُدرَك إلا بالتمرير الأعمى. وهذا
   الموضعُ وحدَه في المنصة كلِّها يستعمل `vh`، وكنتُ قد علّمتُه موضعَ الشكِّ
   الأولَ في iOS قبل أن أملك جهازاً أفحصه عليه. (٥ أكتوبر ٢٠٢٦)
   ⚠️ و`dvh` يُقاس على **المرئيِّ الحقيقيِّ** ويتبع ظهورَ الشريطَين. ويُكتب
      سطراً ثانياً: من لا يعرفه (سفاري دون ١٥٫٤) يُسقطه ويبقى على الأول،
      ومن يعرفه يأخذ الأصحّ. فلا ينكسر قديمٌ ولا يبقى حديثٌ معيباً. */
.gwrap{overflow:auto;padding:0 2px 10px;max-height:calc(100vh - 210px);
 max-height:calc(100dvh - 210px)}
table.mx{table-layout:fixed;border-collapse:separate;border-spacing:0}
table.mx th{position:relative;background:var(--navy);color:#fff;font-size:13px;padding:5px 4px;
 text-align:center;border:1px solid var(--navy2);z-index:3;word-break:normal;overflow-wrap:anywhere}
table.mx thead tr:nth-child(1) th{top:0}
table.mx th.band{background:var(--teal2);border-color:var(--teal2);font-size:14.5px;font-weight:700}
table.mx th.band.off{background:#7f8c9b;border-color:#6d7a88}
table.mx th.corner{position:sticky;inset-inline-end:0;z-index:5;background:var(--navy2)}
table.mx th.sub3{background:#3c6193;font-family:JZL,SK;font-weight:400;font-size:11px;
 line-height:1.45;white-space:normal;padding:4px 5px}
table.mx th b{display:block;font-size:13.5px;white-space:normal}
table.mx th s{display:block;text-decoration:none;font-family:JZL,SK;font-size:10.5px;
 color:#ffe9c2;line-height:1.3}
table.mx th i{display:block;font-style:normal;font-family:SK;font-size:12px;color:#dbebf0}
table.mx th.ext{background:var(--gold);border-color:#96701f}
table.mx td{border:1px solid var(--line);padding:0;vertical-align:top;background:#fff}
table.mx td.cw{position:sticky;inset-inline-end:0;z-index:2;background:var(--navy);color:#fff;width:112px;
 text-align:center;vertical-align:middle;padding:6px 4px}
table.mx td.cw b{display:block;font-size:13.5px;font-weight:700}
table.mx td.cw i,table.mx td.cw u{display:block;font-style:normal;text-decoration:none;
 font-family:SK;font-size:11px;color:#e6f0f8;line-height:1.5;margin-top:2px}
table.mx td.cd i,table.mx td.cd u{display:block;font-style:normal;text-decoration:none;
 font-family:SK;font-size:11px;color:var(--grey);line-height:1.45}
table.mx td.cd u{color:var(--teal2)}
table.mx2 th b{display:block}
table.mx2 th i{display:block;font-style:normal;font-family:SK;font-size:11px;color:#dbebf0;font-weight:400}
table.mx td.cd{position:sticky;inset-inline-end:112px;z-index:2;background:var(--head);width:96px;
 text-align:center;padding:6px 4px;vertical-align:middle}
table.mx td.cd b{display:block;font-size:14px;color:var(--navy2)}
table.mx td.cs{position:sticky;inset-inline-end:220px;z-index:2;background:#fafcfe;width:106px;
 padding:6px 5px;font-size:13px;color:var(--teal2);font-weight:700;vertical-align:middle;text-align:center}
table.mx td.cs.hit{background:var(--tealbg)}
table.mx td.cs.nat{background:#f3ecfb;box-shadow:inset 3px 0 0 #6b4a9e}
table.mx td.cs .natmark{font-family:JZL,SK;font-size:10px;font-weight:400;color:#fff;
 background:#6b4a9e;border-radius:10px;padding:1px 7px;display:inline-block;margin-top:3px}
table.mx td.cs .mark{font-family:JZL,SK;font-size:10.5px;font-weight:400;color:#fff;background:var(--teal);
 border-radius:10px;padding:1px 7px;display:inline-block;margin-top:3px}
table.mx tr.sep td{border-top:2px solid var(--navy)}
.gsel{width:100%;margin-top:4px;font-family:JZL,SK;font-size:11px;padding:2px;border:1px solid var(--line);
 border-radius:5px;background:#fff;color:var(--grey)}
.gsel.ro2{border:0;background:transparent;text-align:center;color:var(--teal2);font-weight:700}
.cellbox{padding:4px;display:flex;flex-direction:column;gap:3px}
.cellbox.on{background:var(--okbg)}
.cellbox.other{background:#f4f6f9}
.cellbox.locked{background:#f7f9fb}
.cellbox.appr{background:var(--okbg);box-shadow:inset 0 0 0 2px #7fc494}
.cellbox.appr::before{content:"◆ معتمدة";display:block;font-size:10.5px;color:var(--ok);
 font-weight:700;text-align:center;margin-bottom:2px}
/* ⛔ **خانةٌ ناقصةٌ لا تُحجز**: شكوى المستشار ٧ أكتوبر ٢٠٢٦ — «محمد العسال كتب
   اسمه فقط وحجز حصتين». فالناقصةُ صفراءُ بعلامتها، ولا تدخل المخزنَ المشترك
   حتى تكتمل — فلا يراها مشرفٌ ولا تقريرٌ حصةً مسجّلة. */
/* ⛔ شريطُ الانقطاع: تحت الترويسة لا في زاويةٍ — فمن لا يراه يظنُّ الجدولَ تامّاً */
.offbar{background:#fff4e0;border-bottom:2px solid #e9a94a;color:#7a4a05;
 padding:9px 16px;font-size:13.5px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.offbar strong{color:#8a3a00}
.offbar button{font:inherit;font-family:JZ,SK;font-size:13px;padding:4px 14px;border-radius:6px;
 border:1px solid #c98a2a;background:#fff;color:#8a3a00;cursor:pointer}
@media (max-width:760px){.offbar{padding:8px 12px;font-size:12.5px;gap:6px}}
/* ⛔ صندوقُ «الناقصة»: يقود إلى الإتمام ولا يكتفي بالتلوين */
.gapbox{background:#fff8e6;border-top:2px solid #e9c46a}
.gapttl{font-family:JZ,SK;font-weight:700;color:#8a5a0a;margin-bottom:3px}
.gaplist{display:flex;flex-wrap:wrap;gap:7px;margin-top:8px}
.gapi{display:flex;flex-direction:column;gap:1px;text-align:start;font:inherit;
 font-family:JZL,SK;background:#fff;border:1px solid #e3cf9a;border-radius:7px;
 padding:6px 10px;cursor:pointer;min-width:150px}
.gapi b{font-family:JZ,SK;font-size:12.5px;color:var(--navy2)}
.gapi span{font-size:11.5px;color:var(--grey)}
.gapi i{font-size:11.5px;color:#a9742a;font-style:normal}
.cellbox.hit{outline:3px solid var(--navy2);outline-offset:2px}
button.rep{background:transparent;border:1px solid #7fa4c8;color:#dbe9f6;
 border-radius:6px;padding:3px 9px;font-size:12.5px;font-family:JZL,SK;cursor:pointer}
@media (max-width:760px){button.rep{display:none}}
/* ⚠️ شريطُ نسخة التجربة: ثابتٌ فوق كل شيءٍ ولا يزول — فلا تُخلط بالمنشورة */
#trybar{position:fixed;inset-block-start:0;inset-inline:0;z-index:9999;
 background:#b3261e;color:#fff;text-align:center;font-family:JZ,SK;font-size:13px;
 padding:3px 8px;letter-spacing:.3px}
body:has(#trybar) .top{margin-block-start:22px}
/* ⛔ خانةُ أسبوعٍ مُقفَل: هويتُها ثابتةٌ وقد بُنيت عليها خطةُ المقيّمين */
.cellbox.wklock{box-shadow:inset 0 0 0 2px #9fb4cc}
.cellbox.wklock::after{content:"🔒 مُعتمدة";display:block;font-size:10px;color:#5b7a99;
 text-align:center;margin-top:2px}
/* ⛔ وعاءٌ يُمرَّر أفقياً لجداول التقرير: سبعةُ أعمدةٍ تفيض عن عرض الجوال،
   فيُقَصُّ آخرُها بلا علامةٍ ولا سبيلَ إليه. */
.tscroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.tscroll table{min-width:max-content}
/* اسمُ المشرف فوق جدوله */
.svname{margin:14px 0 5px;padding-top:9px;border-top:1px solid var(--line)}
.svname b{font-family:JZ,SK;font-size:15px;color:var(--navy2)}
.svname span{display:block;font-size:12.5px;color:var(--grey)}
/* ملخّصُ تقرير الأسبوع */
.wrsum{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0 6px}
.wrbox{flex:1 1 120px;min-width:118px;background:#f6f8fb;border:1px solid var(--line);
 border-radius:10px;padding:10px 12px;text-align:center}
.wrbox b{display:block;font-family:JZ,SK;font-size:22px;color:var(--navy2)}
.wrbox span{font-size:12.5px;color:var(--grey)}
.wrbox.ok b{color:var(--ok)} .wrbox.no b{color:var(--bad)} .wrbox.mid b{color:var(--teal2)}
.wrlock{background:#eef3f8;border:1px solid #c6d4e4;border-radius:10px;padding:10px 13px;margin-top:10px}
.wrlock b{display:block;font-family:JZ,SK;color:var(--navy2);margin-bottom:2px}
.cellbox.part{background:#fff8e6;box-shadow:inset 0 0 0 2px #e9c46a}
.cellbox.part::before{content:"⚠ ناقصة — لم تُحجز";display:block;font-size:10px;
 color:#a9742a;font-weight:700;text-align:center;margin-bottom:2px}
/* ⛔ خانةٌ مقفولةٌ حتى يُختار الاتجاه — تُقرأ ولا تُكتب */
.cin.lock{color:var(--grey);background:#f7f9fb;border-style:dashed;font-size:11.5px}
.cin{width:100%;font:inherit;font-size:12.5px;font-family:JZL,SK;padding:3px 5px;border:1px solid var(--line);
 border-radius:5px;background:#fff;color:var(--ink)}
.cin.nm{font-family:JZ,SK;font-size:13.5px;font-weight:700;color:var(--navy2)}
.cin.ro2{background:#f7fafc;color:var(--grey);min-height:24px;line-height:1.5;border-style:dashed}
.cin:focus{outline:2px solid var(--teal);border-color:var(--teal)}
.crow{display:grid;grid-template-columns:1fr 1fr;gap:3px}
.crow1{display:grid;grid-template-columns:1fr;gap:3px}
.cin.sm{font-size:11.5px;padding:2px 4px}
.cme{border:1px dashed var(--teal);background:#fff;color:var(--teal2);font:inherit;font-size:11.5px;
 font-weight:700;padding:3px;border-radius:5px;cursor:pointer}
.cme:hover{background:var(--tealbg)}
.crow2{display:grid;grid-template-columns:1fr 30px;gap:3px}
.cst{border:0;background:var(--teal);color:#fff;font:inherit;font-size:12px;font-weight:700;
 padding:3px;border-radius:5px;cursor:pointer}
.cclr{border:1px solid #f0c8c4;background:#fdeceb;color:var(--bad);font:inherit;font-size:12px;
 font-weight:700;border-radius:5px;cursor:pointer;padding:0;line-height:1}
.cclr:hover{background:var(--bad);color:#fff;border-color:var(--bad)}
.cin option{font-family:JZL,SK}
.cst:hover{background:var(--teal2)}
.vday{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin:16px 0 8px;
 padding-bottom:6px;border-bottom:2px solid var(--navy)}
.vday b{font-size:17px;color:var(--navy2)}
.vday i{font-style:normal;font-family:SK;font-size:13.5px;color:var(--teal2)}
.vempty{font-family:JZL,SK;color:var(--grey);font-size:14.5px;padding:8px 2px 14px}
.filt{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin-top:11px;
 padding:9px 12px;background:var(--head);border-radius:10px}
.filt input[type=text]{flex:1;min-width:190px;max-width:320px;font-size:15px;padding:6px 11px}
.filt select{max-width:190px;font-size:15px;padding:6px 11px}
table.mx td.cw.now{background:var(--gold)}
table.mx td.cw.now b::after{content:" ●";font-size:9px;vertical-align:middle}
table.mx td.cd.today{background:#fff4d6;box-shadow:inset 3px 0 0 var(--gold)}
table.mx td.cd.today b{color:#8a5a00}
.stpick{border:1px solid var(--line);border-radius:10px;padding:10px 13px;margin-top:11px;background:#fafcfe}
.stpick b{display:block;font-size:14.5px;color:var(--navy2);margin-bottom:7px}
.stpick small{display:block;font-family:JZL,SK;font-size:13px;color:var(--teal2);margin-top:7px}
table.mx2{margin-bottom:10px}
table.mx2 th{background:var(--navy);color:#fff;font-size:13.5px;padding:5px;border:1px solid var(--navy2)}
table.mx2 td{border:1px solid var(--line);padding:5px 8px;font-size:13.5px}
table.mx2 td.mid{text-align:center;font-weight:700;color:var(--navy2)}
table.mx2 td.mid.dim{color:#c3cbd6;font-weight:400}
table.mx2 td.cs{background:#fafcfe;color:var(--teal2);font-weight:700;font-size:13px;white-space:nowrap}
.wk{font-weight:700;color:var(--navy2);padding:9px 4px 4px;font-size:15px}
.wk.on{color:var(--teal2)}
.note div{color:var(--grey);font-family:JZL,SK;font-size:14px;line-height:1.6}
.srcbar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:7px 16px;background:var(--tealbg);
 font-family:JZL,SK;font-size:13px;color:var(--teal2);border-bottom:1px solid var(--line)}
td.nar{width:150px}
td.nowrap{white-space:nowrap}
@media (max-width:900px){
 .body{grid-template-columns:minmax(0,1fr)}
 .side{position:static}
 .side nav{display:flex;gap:5px;overflow-x:auto;padding:7px}
 .side nav button{flex:0 0 auto;width:auto}
 .side nav button small{display:none}
 /* ⛔ شريطُ خُطواتٍ لا قائمةَ أسماءٍ مسحوبة: الحاليةُ باسمها والبواقي بأرقامها.
    (كانت تُرى واحدةٌ من ستٍّ على ٣٩٠ بكسلاً — ١ أكتوبر ٢٠٢٦) */
 .side nav button:not(.on) span{display:none}
 .side nav button:not(.on){padding:8px 11px;justify-content:center}
 .side nav button:not(.on) i{margin:0}
 /* ⛔ **الاسمُ كان يطفو فوق أرقام المراحل**: `max-width` على الزرّ لا يقصّ
    شيئاً، لأن `b` عنصرٌ مرنٌ وأدنى عرضه `min-content` افتراضاً — فلا ينكمش
    ولا يُنقَّط، بل يفيض يساراً على الدوائر ٢ و٣ و٤. قِيس ٥ أكتوبر ٢٠٢٦ على
    ٣٢٠ و٣٩٠ و٤٣٠: تقاطعٌ ٢٣ بكسلاً في الثلاثة. وعلاجُه `min-width:0` على
    العنصر المرن و`overflow:hidden` على الزرّ — لا تصغيرُ الخطّ. */
 .side nav button.on{max-width:44vw;overflow:hidden}
 .side nav button.on b{display:block;min-width:0;flex:0 1 auto;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
 table.mx th{width:150px}
 table.mx td.cd,table.mx td.cs{position:static}
}
/* ⚠️ أهدافُ اللمس: خانةُ المصفوفة أربعةُ حقولٍ صغيرة، وعلى الإصبع لا تُصاب.
   فعلى الشاشات اللمسية والضيّقة تُكبَّر الحقولُ والمربّعاتُ والأزرار. */
@media (pointer:coarse), (max-width:900px){
 .cin{min-height:34px;font-size:14px;padding:6px 8px}
 .cin.sm{min-height:30px;font-size:13px}
 .cme,.cst{min-height:32px;font-size:13.5px}
 .cclr{min-height:32px;font-size:15px}
 .tk input{width:22px!important;height:22px!important}
 .hb{width:30px!important;height:30px!important;font-size:14px}
 .tk{font-size:15.5px;padding:3px 0}
 .ticks{gap:9px 18px}
 table input[type=radio]{width:22px!important;height:22px!important}
 .b.sm{min-height:34px}
 .lnk{min-height:30px;display:inline-flex;align-items:center}
 input,select,textarea{font-size:16px}        /* ١٦ فأكثرُ يمنع تكبيرَ iOS التلقائي */
 .g5,.g2{gap:9px}
 .g5 input,.g2 input{min-height:38px}
 table.mx th{font-size:12.5px}
 .pnav button{min-height:36px}
}
@media print{
 /* ⛔ **لا `@page` هنا**: كانت `A4 landscape` ثم تأتي `@page{size:A4}` في
    كتلةٍ لاحقةٍ فتغلبها — فيخرج الورقُ **عمودياً دائماً** والقواعدُ مكتوبةٌ
    للأفقي، فنصفُ المصفوفة خارج الورقة. وقاعدتان متعارضتان أسوأُ من واحدة.
    والاتجاهُ الآن **يتبع الشاشة** لا يُفرض واحداً: `#pagerule` يُكتب عند
    الرسم. (قِيس بطباعةٍ فعليةٍ ١ أكتوبر ٢٠٢٦: ٥٩٥×٨٤٢ أي عمودي) */
 .side,.srcbar,.cst,.cclr,.cme,.bar,.filt,.stpick,.pnav,.top .me{display:none!important}
 .body{display:block}.gwrap{max-height:none;overflow:visible}
 table.mx{font-size:9pt}table.mx th{font-size:9pt;padding:2px}
 .cin{border:0;padding:1px 2px;font-size:9pt;background:transparent}
 .cin.ro2{border:0}.card{break-inside:auto;border:0}
 .why{border:0;padding:0 0 6mm}.why .docs{display:none}
}
/* ═════════ فصلُ منطقة القراءة عن منطقة العمل ═════════
   ⛔ شكوى المستشار (٣٠ سبتمبر ٢٠٢٦): «التوهان الحاصل الآن». والعلّةُ أن
      الشرحَ والعملَ بلونٍ واحدٍ وحدودٍ واحدة، فلا تعرف العينُ أين تقرأ
      وأين تعمل. فصارا مفترقَين في اللون والحدّ والخط:
        · **منطقةُ القراءة** (`.why`): خلفيةٌ رمليةٌ خفيفةٌ وحدٌّ ذهبيٌّ
          عريضٌ وشارةُ «اقرأ أولاً» — تُقرأ مرّةً ثم تُطوى.
        · **منطقةُ العمل** (`.card`): بيضاءُ ورؤوسُها بلونٍ فاتحٍ موحَّدٍ
          يتجه إليه النظرُ مباشرة. */
.why{background:linear-gradient(180deg,#fffdf6,#fffaf0);
 border:1px solid #efe3c8;border-inline-start:6px solid var(--gold);
 border-radius:12px;padding:14px 18px 12px;margin-bottom:16px;position:relative}
.why::before{content:"اقرأ أولاً";position:absolute;top:-9px;inset-inline-start:14px;
 background:var(--gold);color:#fff;font-size:11.5px;font-weight:700;
 padding:1px 9px;border-radius:7px;letter-spacing:.2px}
html.en .why::before{content:"Read first"}
.why .fold{position:absolute;top:8px;inset-inline-end:12px;background:none;border:0;
 color:var(--gold);font-family:JZL,SK;font-size:12.5px;cursor:pointer;text-decoration:underline}
.why.min p,.why.min ol,.why.min .docs{display:none}
.why h2{font-size:21px;color:var(--navy2);margin-bottom:5px}
.why p{font-family:JZL,SK;color:#33475f;font-size:16px;max-width:105ch}
.why ol{margin:9px 0 0;padding-inline-start:22px;font-size:16px;max-width:105ch}
.why li{margin:3px 0}
.docs{display:flex;gap:8px;flex-wrap:wrap;margin-top:11px}
.mdl{margin-top:12px;padding-top:11px;border-top:1px dashed var(--line)}
.mdl b{display:block;font-size:14.5px;color:var(--navy2);margin-bottom:7px}
.mrow{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;margin:5px 0}
.mrow i{font-style:normal;font-family:JZL,SK;font-size:13px;color:var(--teal2);
 min-width:74px;font-weight:700}
.docs a.mini{background:#fff;border-color:var(--line);color:var(--navy);font-weight:400;
 font-family:JZL,SK;font-size:13.5px;padding:4px 10px}
.docs a{background:var(--tealbg);border:1px solid #b6dbe4;color:var(--teal2);border-radius:8px;
 padding:5px 12px;font-size:14.5px;font-weight:700;text-decoration:none}
/* ⚠️ والسطوحُ تُفصل بظلٍّ خفيفٍ لا بخطٍّ صلب: الخطوطُ المتجاورةُ تصنع
   شبكةً تُتعب العين، والظلُّ يفصل بلا ضجيج. */
.card{background:#fff;border:1px solid #e3e9f1;border-radius:14px;margin-bottom:16px;
 overflow:hidden;box-shadow:0 1px 3px rgba(20,40,70,.05)}
/* ⛔ رأسُ كل بطاقةِ عملٍ بلونٍ فاتحٍ **موحَّد** (طلبُ المستشار): كان نافياً
   داكناً بنصٍّ أبيض، فلا تُميَّز منطقةُ العمل من غيرها.
   ⚠️ **ويُعدَّل الأصلُ لا تُضاف قاعدةٌ فوقه**: أضفتُ في الجولة الماضية
      `background:var(--head)` **قبل** هذه القاعدة فغلبتها في الخلفية، وبقي
      `span{color:navy2}` غالباً في النص — فخرج نصٌّ داكنٌ على خلفيةٍ داكنة
      لا يكاد يُقرأ. (بلاغُ المستشار بصورةٍ من الشاشة ٣٠ سبتمبر ٢٠٢٦) */
.card>h3{background:var(--head);color:var(--navy2);font-size:16.5px;padding:9px 15px;
 display:flex;justify-content:space-between;align-items:center;gap:10px;
 border-bottom:1px solid var(--line)}
.card>h3>span{color:var(--navy2);font-weight:700}
.card>h3 small{font-family:JZL,SK;font-weight:400;color:var(--grey);font-size:14px}
.pad{padding:14px 16px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px}
label.f{display:flex;flex-direction:column;gap:4px;font-size:14.5px;color:var(--navy);font-weight:700}
input,select,textarea{border:1px solid #d3dbe6;border-radius:9px;padding:8px 11px;font:inherit;
 font-size:16px;background:#fff;color:var(--ans);width:100%;
 transition:border-color .14s ease,box-shadow .14s ease}
input:hover,select:hover,textarea:hover{border-color:#b9c6d6}
textarea{min-height:62px;resize:vertical}
/* ⚠️ التركيزُ بحلقةٍ خفيفةٍ لا بإطارٍ صلب: الإطارُ يقفز بالتخطيط ويُربك */
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--teal);
 box-shadow:0 0 0 3px rgba(47,127,149,.16)}
/* ═════════ الأزرار ═════════
   ⛔ شكوى المستشار (٣٠ سبتمبر ٢٠٢٦): «مظهرها مقبض للصدر وليست مريحة».
      والعلّةُ ثلاثٌ مقيسةٌ في الشفرة القديمة:
        · **كلُّها بوزنٍ واحد**: الأساسيُّ والثانويُّ كلاهما كتلةٌ مصمتةٌ
          عريضةُ الخطّ — فلا تعرف العينُ أيَّها الفعلُ المقصود.
        · **بلا حالات**: لا تمرير ولا ضغط ولا تركيز، فالزرُّ يبدو صورةً
          لا شيئاً يُضغط.
        · **زوايا حادّةٌ وظلٌّ معدوم**، وألوانٌ مشبعةٌ متجاورة.
      فصار سُلَّماً من أربع: أساسيٌّ مصمتٌ واحدٌ في الشاشة، وثانويٌّ محدَّدٌ
      بخطٍّ خفيف، وشفّافٌ للأفعال الصغيرة، ومحذِّرٌ للهدم. */
/* ⛔ الرابطُ الذي يبدو زرّاً يجب أن يكونه: كانت `a.b` تخرج نصّاً تحته خطّ
   لأن كلَّ قواعد الأزرار مقيَّدةٌ بـ`button`. فيُضمُّ `a.b` إليها ويُنزع عنه
   خطُّ الروابط. (٣٠ سبتمبر ٢٠٢٦) */
a.b{text-decoration:none;display:inline-flex;align-items:center}
a.b:hover{text-decoration:none}
button.b,a.b{background:var(--navy);color:#fff;border:1px solid transparent;border-radius:10px;
 padding:9px 18px;font:inherit;font-size:15.5px;font-weight:700;cursor:pointer;
 line-height:1.35;box-shadow:0 1px 2px rgba(20,40,70,.12);
 transition:background .15s ease,box-shadow .15s ease,transform .06s ease}
button.b:hover,a.b:hover{background:var(--navy2);box-shadow:0 2px 6px rgba(20,40,70,.18)}
button.b:active,a.b:active{transform:translateY(1px);box-shadow:0 1px 1px rgba(20,40,70,.16)}
button.b:focus-visible,a.b:focus-visible{outline:3px solid var(--tealbg);outline-offset:1px}
button.b.alt,a.b.alt{background:var(--teal)}
button.b.alt:hover,a.b.alt:hover{background:var(--teal2)}
/* الثانويُّ: حدٌّ خفيفٌ لا نافٍ صريح — فلا يُزاحم الأساسيَّ في النظر */
button.b.ghost,a.b.ghost{background:#fff;color:var(--navy2);border-color:var(--line);
 box-shadow:0 1px 1px rgba(20,40,70,.05);font-weight:700}
button.b.ghost:hover,a.b.ghost:hover{background:var(--head);border-color:#c3cfdf}
/* المحذِّرُ لا يُصمَت حتى يُقصد: يبدأ خفيفاً ويمتلئ عند التمرير */
button.b.warn{background:#fff;color:var(--bad);border-color:#e7b7b2}
button.b.warn:hover{background:var(--bad);color:#fff;border-color:var(--bad)}
button.b:disabled{opacity:.45;cursor:not-allowed;box-shadow:none}
button.b:disabled:hover{background:var(--navy)}
button.b.ghost:disabled:hover{background:#fff}
.bar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:12px}
table{width:100%;border-collapse:collapse;font-size:15px}
/* ⚠️ حدودُ الجدول أخفُّ، والتظليلُ المتناوبُ يكفي لتتبّع الصف */
td{border-color:#e7ecf3}
th{background:var(--head);color:var(--navy2);padding:9px 8px;border:1px solid #e0e7f0;font-size:14px;white-space:nowrap;font-weight:700}
td{border:1px solid var(--line);padding:7px 9px;vertical-align:middle}
tr:nth-child(even) td{background:#fafbfd}
tbody tr:hover td{background:#f4f8fc}
.tag{display:inline-block;border-radius:20px;padding:2px 10px;font-size:13px;font-weight:700}
.tag.ok{background:var(--okbg);color:var(--ok)}
.tag.no{background:var(--badbg);color:var(--bad)}
.tag.mid{background:#fff6e5;color:#8a5a00}
/* ⛔ حُذفت نسخةٌ مكرَّرةٌ من هذه القاعدة كانت تأتي بعد التعريف
   فتغلبه وتُعيد الزرَّ أحمرَ على أحمر — كشفه ماسحُ التباين. */
.msg{padding:11px 15px;border-radius:10px;margin:10px 0;font-size:15.5px}
/* ⛔ العنوانُ والشرحُ كانا يلتصقان سطراً واحداً: «نزّل القالبَ واكتبه بيدكوإن
   أردتَ…» — لأن `b` و`span` كلاهما سطريّ. فيُفصَلان. (قِيس بلقطةٍ ١ أكتوبر) */
.msg>b{display:block;margin-bottom:4px}
.msg>span{display:block;line-height:1.7}
.msg.ok{background:var(--okbg);border:1px solid #bcdfc4;color:var(--ok)}
.msg.bad{background:var(--badbg);border:1px solid #f5c6cb;color:var(--bad)}
/* ⛔ **`.msg.warn` كانت تُستعمل بلا تعريف**: خمسةُ إشعاراتٍ — منها «لا مشرفَ
   مختصٌّ لهذا التخصص فالتقييمُ عليك» — تُرسم نصّاً عادياً لا يُميَّز من الشرح
   حوله. فأهمُّ ما يُقال للوكيل ومدير المجمع كان بلا لونٍ ولا حدّ.
   ⚠️ واللونُ مقيسٌ على الأبيض: ٨٫٢ نسبةَ تباين. (١ أكتوبر ٢٠٢٦) */
.msg.warn{background:#fff6e5;border:1px solid #e8cf9a;color:#7a4e00}
/* ═══ شريطُ الحفظ والطباعة والتنزيل ═══
   ⛔ على الجوال يُثبَّت أسفلَ الشاشة: كان المعلمُ يكتب ويخرج ولا يعلم أحُفظ،
      لأن مؤشّرَ المزامنة كلمةٌ في الهيدر لا تُرى. والزرُّ يجب أن يكون في
      متناول الإبهام لا في أعلى صفحةٍ طولُها شاشتان. (١ أكتوبر ٢٠٢٦) */
.abar{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin:14px 0 4px;
 padding:11px 13px;background:var(--tealbg);border:1px solid var(--line);border-radius:10px}
.abar i{color:var(--grey);font-family:JZL,SK;font-size:13px;font-style:normal;margin-inline-start:auto}
.abar .b{min-height:44px;padding:9px 20px;font-size:16px}
@media (max-width:760px){
 .abar{position:sticky;bottom:0;z-index:40;margin:14px -4px 0;border-radius:10px 10px 0 0;
  background:#fff;box-shadow:0 -3px 14px rgba(0,0,0,.13)}
 .abar i{flex-basis:100%;margin-inline-start:0;order:9}
 .abar .b{flex:1 1 0;min-width:96px;padding:11px 8px}
}
/* ═══ الجداولُ العريضةُ تُمرَّر داخلَها لا تَخرج عن الشاشة ═══
   ⛔ جدولُ «الحصص المسجَّلة» تسعةُ أعمدة، وآخرُها زرّا «افتح» و«حذف» — وكانا
      **خارجَ الشاشة** على الجوال والآيباد بلا أي طريقةٍ للوصول إليهما:
      لا تمريرَ للصفحة (وهو صواب) ولا تمريرَ للجدول. فالحصةُ تُرى ولا تُفتح.
      (قِيس بإطارٍ بعرضٍ حقيقيٍّ ١ أكتوبر ٢٠٢٦ — و`--window-size` وحدَه كذب) */
.scrollx{overflow-x:auto;-webkit-overflow-scrolling:touch;
 scrollbar-width:thin;padding-bottom:3px}
.scrollx>table{min-width:max-content}
@media print{.scrollx{overflow:visible}.scrollx>table{min-width:0}}

/* ═══ قسمان في مساحة الاطّلاع: نماذجُ التخصص · والنشرات ═══ */
.sect{padding:11px 0;border-top:1px solid var(--line)}
.sect:first-child{border-top:0;padding-top:0}
.sect>b{display:block;color:var(--navy2);font-size:16.5px;margin-bottom:3px}
.sect>i{display:block;color:var(--grey);font-family:JZL,SK;font-size:13.5px;
 font-style:normal;margin-bottom:8px;line-height:1.6}

/* ═══ ثلاثُ طرقٍ للتحضير: بطاقاتٌ تُلمس لا قائمةٌ منسدلة ═══ */
.ways{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.ways .way{text-align:start;padding:13px 15px;border:2px solid var(--line);border-radius:11px;
 background:#fff;cursor:pointer;font-family:JZL,SK;min-height:84px}
.ways .way b{display:block;color:var(--navy2);font-size:16.5px;margin-bottom:4px}
.ways .way span{display:block;color:var(--grey);font-size:13.5px;line-height:1.55}
.ways .way:hover{border-color:var(--teal2)}
.ways .way.on{border-color:var(--teal2);background:var(--tealbg)}
.ways .way.on b{color:var(--teal2)}
@media (max-width:760px){.ways{grid-template-columns:1fr}.ways .way{min-height:0}}

/* ═══ النافذةُ الموحَّدة — بديلُ `alert` الأصلية ═══
   ⛔ النافذةُ الأصليةُ تخرج بخطِّ النظام وبلغته (زرُّ «OK» إنجليزياً في شاشةٍ
      عربية)، ولا تُميَّز رسالةُ المنع من الإشعار، وتُجمّد الصفحةَ على الجوال.
      وقاعدةُ المستشار تمنعها. (١ أكتوبر ٢٠٢٦) */
/* ⛔ **حوارٌ أطولُ من الشاشة كان يُقَصُّ من أعلاه** (كشفته لقطةٌ ٨ أكتوبر
   ٢٠٢٦): `align-items:center` يُوسّطه، فإن طال خرج رأسُه فوق الشاشة ولا
   سبيلَ إليه — فلا عنوانَ يُرى ولا زرَّ إغلاقٍ يُضغط. وهو أسوأُ ما يكون
   على الجوال حيث الشاشةُ أقصر.
   ⚠️ فصار يبدأ من أعلى بهامش، وسقفُه ٩٢٪ من الشاشة، **والمتنُ وحدَه هو
      الذي يُمرَّر** — فالرأسُ والذيلُ ثابتان مرئيّان دائماً. */
.udlg{position:fixed;inset:0;z-index:200;background:rgba(14,30,46,.55);
 display:flex;align-items:flex-start;justify-content:center;padding:18px;overflow:auto}
.udlgbox{background:#fff;border-radius:14px;max-width:520px;width:100%;
 box-shadow:0 18px 50px rgba(0,0,0,.3);border-top:5px solid var(--teal2);overflow:hidden;
 max-height:92vh;display:flex;flex-direction:column;margin:auto}
.udlgbox > .udlgtx{overflow:auto;min-height:0;flex:1 1 auto}
.udlgbox > .ntfhd, .udlgbox > .udlgbar{flex:0 0 auto}
.udlgbox.bad{border-top-color:var(--bad)}
.udlgbox.warn{border-top-color:#b07a00}
.udlgbox.ok{border-top-color:var(--ok)}
.udlgtx{padding:20px 22px 6px;font-family:JZL,SK;font-size:16px;line-height:1.85;color:var(--ink)}
.udlgtx div:first-child{font-family:JZ,SK;font-size:17.5px;font-weight:700;color:var(--navy2);margin-bottom:5px}
.udlgin{width:100%;margin-top:12px;padding:10px 12px;font:inherit;font-size:16px;
 font-family:JZL,SK;border:1.5px solid var(--line);border-radius:9px;background:#fff}
.udlgin:focus{outline:none;border-color:var(--teal2);box-shadow:0 0 0 3px rgba(23,122,138,.16)}
.udlgbar{display:flex;justify-content:flex-start;gap:9px;padding:10px 22px 18px}
.udlgbar .b{min-height:44px;padding:9px 30px;font-size:16px}
@media(max-width:760px){
 .udlg{align-items:flex-end;padding:0}
 .udlgbox{border-radius:14px 14px 0 0;max-width:none}
 .udlgbar .b{flex:1}
}
@media print{.udlg{display:none!important}}

/* ⛔ **حالةُ «غير متصل» كانت صفراءَ هامسة** — ولونُها يقول «تنبيه» والأمرُ
   فقدانُ العمل. فصارت حمراءَ ومعها زرُّ الربط. (٥ أكتوبر ٢٠٢٦) */
.stbox.local.bad{background:#fdeceb;border-top-color:#e0a9a2}
.stbox.local.bad b{color:#9b2c20}
.stbox .b{margin-top:8px;width:100%}

/* ═════════ زرُّ التنبيهات ولوحتُها ═════════
   ⚠️ الزرُّ ليس رابطاً تحته خطّ كبقية أزرار الهيدر: له إطارٌ يفصله، وشارةٌ
      تحمل العدد. والشارةُ **لونٌ ورقمٌ معاً** لا لونٌ وحدَه — فمن لا يميّز
      الألوان يقرأ العدد. */
.top .me .ntfb{border:1px solid rgba(255,255,255,.34);border-radius:999px;
 padding:4px 12px;text-decoration:none;display:inline-flex;align-items:center;gap:7px}
.top .me .ntfb.on{border-color:#ffd77a;color:#fff}
.top .me .ntfb b{background:#c0392b;color:#fff;border-radius:999px;
 min-width:19px;padding:0 6px;font-size:12.5px;line-height:19px;text-align:center}
.udlgbox.wide{max-width:760px}
/* ⛔ ترويسةُ التنبيهات: ما هي · لمن · وكم استجدّ — وزرُّ إغلاقٍ في أعلاها */
.ntfhd{padding:14px 22px 10px;border-bottom:1px solid var(--line);position:relative}
.ntfhl{display:flex;align-items:center;gap:10px}
.ntfhl b{font-family:JZ,SK;font-size:19px;color:var(--navy2)}
.ntfnew{background:var(--teal2);color:#fff;border-radius:999px;padding:2px 11px;
 font-size:12.5px;font-family:JZ,SK}
.ntfsub{margin-top:3px;font-size:13px;color:var(--grey)}
.ntfsub i{font-style:normal;color:var(--teal2)}
.ntfx{position:absolute;top:10px;inset-inline-end:14px;background:none;border:0;
 font-size:19px;line-height:1;color:var(--grey);cursor:pointer;padding:4px 8px;
 border-radius:7px;min-width:38px;min-height:38px}
.ntfx:hover{background:#eef2f7;color:var(--navy2)}
.ntf h3 small{display:block;font-family:JZL,SK;font-size:12px;color:var(--grey);
 font-weight:400;margin-top:2px}
.ntf h3{font-family:JZ,SK;font-size:16px;color:var(--navy2);margin:14px 0 8px;
 padding-bottom:5px;border-bottom:2px solid var(--tealbg)}
.ntf h3:first-child{margin-top:0}
.ntf .ntfr{display:grid;grid-template-columns:auto 1fr auto auto;gap:6px 11px;
 align-items:center;padding:8px 10px;border:1px solid var(--line);
 border-radius:9px;margin-bottom:6px;font-size:14px}
.ntf .ntfr.nw{border-inline-start:4px solid var(--teal2);background:var(--tealbg)}
.ntf .ntfr b{font-family:JZ,SK;color:var(--teal2);white-space:nowrap}
.ntf .ntfr i{font-style:normal;color:#5c6873;font-size:13px;white-space:nowrap}
.ntf table{width:100%;border-collapse:collapse;font-size:14px}
.ntf table th{background:var(--head);color:var(--navy2);font-family:JZ,SK;
 padding:6px 8px;border:1px solid var(--line)}
.ntf table td{padding:6px 8px;border:1px solid var(--line)}
@media (max-width:760px){
 .ntf .ntfr{grid-template-columns:1fr;gap:3px}
 .ntf .ntfr i,.ntf .ntfr b{white-space:normal}
}

/* تأكيدٌ يُرى: لا كلمةٌ في الهيدر */
.toast{position:fixed;inset-inline:0;bottom:0;margin:0 auto;max-width:460px;
 padding:13px 18px;border-radius:12px 12px 0 0;font-family:JZL,SK;font-size:15.5px;
 text-align:center;z-index:120;transform:translateY(110%);transition:transform .22s ease;
 box-shadow:0 -4px 18px rgba(0,0,0,.18)}
.toast.on{transform:translateY(0)}
.toast.ok{background:#1d6f4f;color:#fff}
.toast.warn,.toast.wait,.toast.bad{background:#7a4e00;color:#fff}
.toast.bad{background:#8a1f1f}
@media print{.abar,.toast{display:none!important}}
/* توأمةُ الاستمارة والتحضير: ما كتبه المعلمُ تحت المؤشر — أصغرَ وأخفتَ منه */
.twin{margin-top:5px;font-size:13.5px;line-height:1.65;color:#4a5560;
      border-inline-start:3px solid #d8e2e8;padding-inline-start:9px}
.twin b{color:#2d3a44;font-weight:600}
/* ⛔ **#7b8894 نسبتُه ٣٫٥٠ على خلفية البطاقة والمطلوب ٤٫٥**: نصُّ «— خانتُه»
   في خلية التوأمة — وهو ما يربط المؤشرَ بما كتبه المعلمُ في تحضيره، أي
   الشاهدُ نفسُه. ولم يظهر العيبُ إلا حين فُتحت الاستمارةُ للمقيّمين الخمسة
   (٤ أكتوبر ٢٠٢٦) فصار يُقاس على شاشة المدير أيضاً. و#636f7c نسبتُه ٤٫٩٥. */
.twin i{color:#636f7c;font-style:normal}
.twin .tag{font-size:12px;padding:1px 7px}
.msg ul{margin:6px 0 0;padding-inline-start:20px}
.login{max-width:720px;margin:44px auto;background:#fff;border:1px solid var(--line);border-radius:16px;padding:26px;text-align:center}
.login h2{font-size:27px;color:var(--navy2);margin-bottom:6px}
.login p{font-family:JZL,SK;color:var(--grey);margin-bottom:18px}
.roles{display:grid;gap:11px;margin-bottom:16px}
.role{border:2px solid var(--line);border-radius:12px;padding:13px 16px;cursor:pointer;text-align:start;transition:.15s}
/* ⛔ **أثرُ التركيز**: من ينتقل بلوحة المفاتيح يجب أن يرى أين هو — وبدونه
   يتنقّل في العمى ولو عمل الانتقال. (١ أكتوبر ٢٠٢٦) */
.role:focus{outline:none}
.role:focus-visible{outline:3px solid var(--teal);outline-offset:2px}
.b:focus-visible,a.b:focus-visible,.way:focus-visible,button:focus-visible
  {outline:3px solid var(--teal);outline-offset:2px}
.role:hover{border-color:var(--teal)}
.role.on{border-color:var(--navy);background:var(--head)}
.role b{display:block;font-size:17.5px;color:var(--navy2)}
.role span{font-family:JZL,SK;font-size:14.5px;color:var(--grey)}
.whois{font-family:JZL,SK;font-size:13.5px;min-height:20px;margin:5px 0 8px;color:var(--grey)}
.whois.ok{color:var(--ok);font-weight:700}
.whois.no{color:#8a5a00}
.login input{margin-bottom:8px}
.login input[readonly]{background:var(--okbg);border-color:#bcdfc4;font-weight:700;color:var(--ok)}
/* ⛔ وقيمةُ القراءة مثلُ حقلِ الكتابة: `plaintext` يجعل كلَّ فقرةٍ تتبع
   محتواها — فالتحضيرُ الإنجليزيُّ يُقرأ عند الوكيل والمدير كما كتبه
   صاحبُه، لا بعلاماتِ ترقيمٍ انقلبت إلى صدر الجملة. (٦ أكتوبر ٢٠٢٦) */
.ro{unicode-bidi:plaintext;text-align:start;background:#f7fafc;border:1px solid var(--line);border-radius:8px;padding:7px 10px;color:var(--ans);
 min-height:36px;white-space:pre-wrap;font-size:15.5px}
.lab{background:var(--head);color:var(--navy);font-weight:700;font-size:14.5px;padding:7px 10px;border-radius:8px}
.row2{display:grid;grid-template-columns:170px 1fr;gap:10px;align-items:start;margin-bottom:9px}
.hint{background:var(--tealbg);border-inline-start:3px solid var(--teal);color:#14424f;font-size:14.5px;
 padding:6px 10px;margin-bottom:6px;border-radius:5px}
.hb{border:1px solid var(--teal);background:#fff;color:var(--teal);border-radius:50%;width:21px;height:21px;
 font-size:12px;cursor:pointer;line-height:1;padding:0}
.ticks{display:flex;flex-wrap:wrap;gap:6px 15px}
.tk{display:flex;align-items:center;gap:6px;font-size:15px;cursor:pointer}
.tk input{width:17px;height:17px;accent-color:var(--teal)}
.g5{display:grid;grid-template-columns:repeat(5,1fr);gap:7px}
.g2{display:grid;grid-template-columns:repeat(2,1fr);gap:7px;max-width:52%}
.g5 label,.g2 label{font-size:13px;text-align:center;display:block;color:var(--navy);font-weight:700}
.g5 input,.g2 input{text-align:center}
.g2 .care label{color:var(--teal2)}
.g2 .care input,.g2 .care .ro{background:var(--tealbg);border-color:#b6dbe4}
.tdiff{margin:12px 0 6px;font-family:JZL,SK;font-size:14px;color:var(--teal2);font-weight:700;
 border-top:1px dashed var(--line);padding-top:10px}
.g7{display:grid;grid-template-columns:repeat(7,1fr);gap:6px}
.g5 label.auto::after,.g7 label.auto::after{content:" (يُحسب)";font-family:JZL,SK;font-weight:400;font-size:11px;color:var(--grey)}
/* الخانةُ قيد التعديل تُبرَز، والمعدَّلةُ تحمل أثراً خفيفاً يدلّ على أنها مُسَّت */
tr.m4 td{background:#e8f6ec}tr.m4 td:nth-child(2){box-shadow:inset 3px 0 0 #1d6b35}
tr.m3 td{background:#f2faf4}tr.m3 td:nth-child(2){box-shadow:inset 3px 0 0 #6aab7e}
tr.m2 td{background:#fff6e5}tr.m2 td:nth-child(2){box-shadow:inset 3px 0 0 #b8862b}
tr.m1 td{background:#fdeceb}tr.m1 td:nth-child(2){box-shadow:inset 3px 0 0 #a52018}
tr.mna td{background:#f2f2f2;color:#8a94a3}tr.mna td:nth-child(2){box-shadow:inset 3px 0 0 #b6bfca}
tr.editing td{outline:2px solid var(--gold);outline-offset:-2px}
.editing{background:#fff8e1!important;box-shadow:inset 0 0 0 2px var(--gold);border-radius:8px}
.row2.editing .lab{background:var(--gold);color:#fff}
input.touched,select.touched,textarea.touched{border-color:var(--teal);
 background:linear-gradient(180deg,#fff 88%,var(--tealbg))}
input:focus,select:focus,textarea:focus{outline:2px solid var(--teal);border-color:var(--teal);
 box-shadow:0 0 0 4px rgba(47,127,149,.14)}
td.cell:focus-within{box-shadow:inset 0 0 0 2px var(--gold)}
.ro.sum{text-align:center;font-family:SK;font-size:19px;font-weight:700;color:var(--navy2);
 background:var(--head);border-color:var(--navy)}
.ro.sum.good{background:var(--okbg);border-color:#7fc494;color:var(--ok)}
.ro.sum.bad{background:var(--badbg);border-color:#e8a9a4;color:var(--bad)}
.g7 input{text-align:center}
.stg{display:grid;grid-template-columns:120px 1fr 1fr 180px;gap:8px;border-top:1px solid var(--line);padding:8px 0}
.stg:first-child{border-top:0}
.stn{color:var(--navy);font-weight:700;font-size:14px;text-align:center}
.score{position:sticky;bottom:0;background:#fff;border-top:3px solid var(--navy);padding:9px 16px;
 display:flex;gap:14px;flex-wrap:wrap;align-items:center;font-weight:700;color:var(--navy);z-index:15}
.score .big{font-size:20px;color:var(--bad)}
.kpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.kpi div{background:linear-gradient(150deg,var(--navy),var(--navy2));color:#fff;border-radius:11px;padding:13px;text-align:center}
.kpi b{display:block;font-family:SK;font-size:32px;font-weight:700;line-height:1.1}
.kpi span{font-family:JZL,SK;font-size:14.5px;opacity:.93}
.empty{text-align:center;color:var(--grey);font-family:JZL,SK;padding:26px}
.runrow{display:grid;grid-template-columns:160px 1fr;gap:10px;align-items:start;
 padding:7px 0;border-top:1px solid var(--line)}
.runrow:first-child{border-top:0}
.runrow b{color:var(--navy);font-size:14.5px}
.runrow div{font-size:15.5px;white-space:pre-wrap}
@media(max-width:700px){.runrow{grid-template-columns:1fr}}
footer{background:var(--navy2);color:#b0c6dc;margin-top:28px;padding:18px 0}
.frow{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap}
footer b{display:block;font-size:15.5px;color:#fff;font-weight:700}
footer span{display:block;font-family:JZL,SK;font-size:13.5px;color:#b0c6dc;margin-top:3px;line-height:1.6}
footer .sig{text-align:start;border-inline-start:3px solid var(--teal);padding-inline-start:13px}
footer .sig b{font-size:14px;color:#dbebf0;font-weight:400;font-family:JZL,SK}
footer .sig span{font-size:16px;color:#fff;font-weight:700;font-family:JZ,SK;margin-top:1px}
footer .sig i{display:block;font-style:normal;font-family:SK;font-size:11.5px;color:#b7c6d6;margin-top:4px}
@media print{footer{background:#fff;color:var(--ink);border-top:1px solid var(--line)}
 footer b,footer .sig span{color:var(--navy2)}footer span{color:var(--grey)}}
/* ⛔ **iOS يُكبّر الصفحةَ عند كل لمسةٍ لخانة.** سفاري يفعلها تلقائياً لكل
   حقلٍ خطُّه **دون ١٦ بكسل** — وخاناتُ المصفوفة ١٢٫٥ و١١٫٥. فالمعلمُ يملأ
   التحضيرَ على جواله وهو يُصغّر بعد كل حقل، والصفحةُ تقفز في كل لمسة.
   والعلاجُ ١٦ بكسلاً على الجوال وحدَه — والمقاساتُ الصغيرةُ تبقى للحاسب
   حيث لا تكبير. (١ أكتوبر ٢٠٢٦)
   ⚠️ ولا يُعالَج بـ`maximum-scale=1` في الـviewport: يمنع التكبيرَ اليدويَّ
      أيضاً، فيُحرم ضعيفُ البصر من التكبير — وهو عطلُ وصولٍ لا علاج. */
@media(max-width:760px){
 .cin, .cin.nm, .cin.sm, .cin.lock,
 input[type=text], input[type=number], input[type=search], select, textarea
   {font-size:16px!important}
}
@media(max-width:760px){.g5{grid-template-columns:repeat(2,1fr)}.g2{max-width:100%}
 .row2{grid-template-columns:1fr}.stg{grid-template-columns:1fr}.g7{grid-template-columns:repeat(2,1fr)}}
@media print{body{background:#fff}nav,.bar,.score,.noprint,.why .docs{display:none!important}
 .card{break-inside:avoid;border-radius:0}}

/* ⚠️ **وموضعُها آخرُ الورقة قصداً**: وُضعت أولَ مرّةٍ في وسطها
   فغلبتها قواعدُ أساسيةٌ بعدها بالترتيب لا بالتخصيص (`.card>h3` بقي
   ١٦٫٥بك وقد كُتب له ١٥). والأسبقيّةُ عند تساوي التخصيص للأخير. */
/* ⛔ **الخطُّ كان مكتوباً لشاشة حاسبٍ وحدَها.** بلاغُ المستشار ٦ أكتوبر
   ٢٠٢٦: «مبالغٌ في حجم الخطوط، فلا تظهر الصفحةُ بشكلٍ يناسب الاستعراض».
   وقِيس على ٣٢٠ و٣٩٠ و٤٣٠ بإطارٍ مضمَّنٍ بعرضٍ مضبوط: المتنُ ١٧بك بسطرٍ
   ١٫٧، والعنوانُ ٢٣بك يلتفُّ سطرين — فالترويسةُ وحدَها **٢٦٢ إلى ٤٢٧
   بكسلاً من ٨٤٤**، والشريطُ الجانبيُّ فوق المتن ٣٦٤، فأولُ حقلِ إدخالٍ عند
   **١٦٠٠ بكسل**: شاشتان من التمرير قبل أن يكتب المعلمُ حرفاً. والمنصةُ
   للإدخال لا للتصفّح.
   ⚠️ **ولا يُمَسُّ خطُّ حقول الإدخال**: ما دون ١٦بك يجعل iOS يُكبّر الصفحةَ
      عند اللمس فينكسر العرضُ — وهو مضبوطٌ في كتلة اللمس أعلاه، ولا تُنقض هنا.
   ⚠️ **ولا تُمَسُّ أهدافُ اللمس**: الارتفاعاتُ الدنيا (٣٤ · ٣٦ · ٤٤) قياسُ
      إصبعٍ لا قياسُ خطّ، فتبقى كما هي ويحرسها `respcheck`. */
@media (max-width:760px){
 body{font-size:15.5px;line-height:1.6}
 /* ⛔ **قِيس بالنظر إلى لقطةٍ حقيقيةٍ لا بالأرقام** (٧ أكتوبر ٢٠٢٦): عنوانُ
    المرحلة في بطاقة الشرح يكرّر عنوانَ البطاقة التي تحتَه حرفاً بحرف، ومعه
    شريطُ المراحل — فالمعلّمُ يمرُّ بشاشتين قبل أول حقل. فيُطوى المكرَّرُ على
    الجوال ويبقى «اقرأ أولاً» و«اعرض الشرح» كما هما. */
 .why h2{font-size:16px;margin-bottom:2px;opacity:.72}
 .why{padding:11px 12px 9px}
 /* وشريطُ الانقطاع يقول ما يلزم في سطرين لا في خمسة */
 .offbar{padding:7px 12px;font-size:12px;line-height:1.45;gap:5px}
 .offbar strong{display:block;width:100%}
 .top{padding:9px 0}
 .top .row{gap:10px}
 .top h1{font-size:17px;white-space:nowrap}
 .top img{height:32px}
 .top .sch{display:none}           /* اسمُ المدرسة — في التذييل والشريط */
 .top .me{font-size:13.5px;padding:4px 11px;gap:8px}
 .top .me .rl{display:none}        /* الدورُ — في رأس الشريط الجانبي */
 .top .me button{font-size:13px}
 .pnav button{font-size:13.5px;padding:5px 11px}
 .side .sh{padding:8px 12px}
 .side .sh b{font-size:14.5px}
 .side .sh i{font-size:11.5px}
 .card>h3{font-size:15px;padding:8px 13px}
 .why{padding:11px 13px}
 .why h2{font-size:17px}
 .why p,.why ol{font-size:14.5px}
 /* ⛔ **زرُّ الطيّ كان يتراكب على العنوان**: موضعُه مطلقٌ في زاوية البطاقة،
    والعنوانُ على الجوال أعرضُ من مكانه فيمرُّ تحته — ظهر في اللقطة لا في
    النصّ. فيصير في مجرى المحتوى سطراً مستقلّاً فوق العنوان. */
 .why .fold{position:static;display:block;margin:0 0 7px auto}
 /* وتذييلُ الشريط («مدارس ابن خلدون» والختم) مكرَّرٌ في تذييل الصفحة —
    وعلى الجوال يقع **فوق** المتن فيُزاحمه بلا فائدة. */
 .side .sf{display:none}
 .stbox{padding:9px 12px}
}
"""

with open(os.path.join(HERE, "platform_app.js"), encoding="utf-8") as f:
    JS = f.read()
# ⛔ استيرادُ التحضير في ملفٍّ مستقلٍّ يُضمُّ هنا: منطقٌ قائمٌ بنفسه
#    (أمرٌ وقارئُ وورد وموزِّعٌ) لا يُخلط بمحرّك الشاشات.
with open(os.path.join(HERE, "planimport.js"), encoding="utf-8") as f:
    JS += "\n" + f.read()


JS = fem_js(guard(JS), F)


HTML = """<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>منصة الحصة الموحَّدة — مدارس ابن خلدون</title>
__ICON__
<style>__FONTS____CSS__</style></head><body>__TRYBAR__</body>
<script>__JS__</script></html>
"""

# مصادرُ الصفحة — بصمتُها هي ختمُ الإصدار
STAMP_SRC = ["platform.py", "platform_app.js", "planimport.js", "i18n.py",
             "prepdef.py", "zcontent.py", "scontent.py", "acontent.py",
             "scheddata.py", "indmap.py", "femjs.py"]


def build_stamp():
    """ختمُ الإصدار — به يُعرف أنَّ ما على الشاشة هو آخر بناءٍ لا نسخةً مخبوءة.

    ⛔ **كان الختمُ هاشَ آخر دفعةٍ في جِت** — أي الدفعةَ **السابقة** دائماً،
       لأن البناءَ يسبق الالتزام. فقارنتُ الصفحةَ الحيّةَ بالمحلية فوجدتُهما
       مختلفتَي الختم وهما سواء، وظننتُ النشرَ متعثّراً. (١ أكتوبر ٢٠٢٦)
    ⚠️ فصار بصمةَ **مصادر الصفحة نفسِها**: تتغيّر بتغيُّر ما يُبنى منه لا
       بتاريخ الالتزام، فمقارنةُ الحيِّ بالمحليِّ تصحّ بلا جِت ولا ترتيب.
    """
    import hashlib
    from datetime import date
    h = hashlib.sha256()
    for n in STAMP_SRC:
        f = os.path.join(HERE, n)
        if os.path.exists(f):
            with open(f, "rb") as fh:
                h.update(fh.read())
    d = "".join("٠١٢٣٤٥٦٧٨٩"[int(c)] if c.isdigit() else c for c in date.today().isoformat())
    return f"إصدار {d} · {h.hexdigest()[:7]}"


DATA["models"] = {k: [dict(m, u=SITE + quote(m["u"])) for m in v]
                  for k, v in {"أخرى": [{"t": "التربية البدنية — الثالث الابتدائي — التوازن الحركي", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنين/التربية البدنية — الثالث الابتدائي — التوازن الحركي (للعرض والطباعة).pdf"}, {"t": "التربية الفنية — الرابع الابتدائي — الضوء والظل في الثمار", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنين/التربية الفنية — الرابع الابتدائي — الضوء والظل في الثمار (للعرض والطباعة).pdf"}, {"t": "المهارات الحياتية والأسرية — الخامس الابتدائي — العلامات الحيوية", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنين/المهارات الحياتية والأسرية — الخامس الابتدائي — العلامات الحيوية (للعرض والطباعة).pdf"}, {"t": "التربية البدنية — الأول المتوسط — التمرير بباطن القدم", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنين/التربية البدنية — الأول المتوسط — التمرير بباطن القدم (للعرض والطباعة).pdf"}, {"t": "التربية الفنية — الثاني المتوسط — التوازن في التصميم", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنين/التربية الفنية — الثاني المتوسط — التوازن في التصميم (للعرض والطباعة).pdf"}], "إسلامية": [{"t": "الدراسات الإسلامية — الثالث الابتدائي — أركان الإسلام", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنين/الدراسات الإسلامية — الثالث الابتدائي — أركان الإسلام (للعرض والطباعة).pdf"}, {"t": "الدراسات الإسلامية — أول ثانوي — حديث إنما الأعمال بالنيات", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنين/الدراسات الإسلامية — أول ثانوي — حديث إنما الأعمال بالنيات (للعرض والطباعة).pdf"}, {"t": "الدراسات الإسلامية — الأول المتوسط — صفة الوضوء ونواقضه", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنين/الدراسات الإسلامية — الأول المتوسط — صفة الوضوء ونواقضه (للعرض والطباعة).pdf"}], "اجتماعيات": [{"t": "الدراسات الاجتماعية — السادس الابتدائي — قيام الدولة السعودية الأولى", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنين/الدراسات الاجتماعية — السادس الابتدائي — قيام الدولة السعودية الأولى (للعرض والطباعة).pdf"}, {"t": "الدراسات الاجتماعية — أول ثانوي — التنمية المستدامة ورؤية ٢٠٣٠", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنين/الدراسات الاجتماعية — أول ثانوي — التنمية المستدامة ورؤية ٢٠٣٠ (للعرض والطباعة).pdf"}, {"t": "الدراسات الاجتماعية — الثاني المتوسط — موقع المملكة وأثره", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنين/الدراسات الاجتماعية — الثاني المتوسط — موقع المملكة وأثره (للعرض والطباعة).pdf"}], "رياضيات": [{"t": "الرياضيات — الرابع الابتدائي — القيمة المنزلية ضمن مئات الألوف", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنين/الرياضيات — الرابع الابتدائي — القيمة المنزلية ضمن مئات الألوف (للعرض والطباعة).pdf"}, {"t": "الرياضيات — أول ثانوي — العلاقات والدوال", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنين/الرياضيات — أول ثانوي — العلاقات والدوال (للعرض والطباعة).pdf"}, {"t": "الرياضيات — الأول المتوسط — القوى والأسس", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنين/الرياضيات — الأول المتوسط — القوى والأسس (للعرض والطباعة).pdf"}], "علوم": [{"t": "العلوم — الخامس الابتدائي — تصنيف المخلوقات الحية", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنين/العلوم — الخامس الابتدائي — تصنيف المخلوقات الحية (للعرض والطباعة).pdf"}, {"t": "الأحياء — أول ثانوي — نظرية الخلية ومكوناتها", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنين/الأحياء — أول ثانوي — نظرية الخلية ومكوناتها (للعرض والطباعة).pdf"}, {"t": "الفيزياء — أول ثانوي — منحنى الموقع والزمن", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنين/الفيزياء — أول ثانوي — منحنى الموقع والزمن (للعرض والطباعة).pdf"}, {"t": "الكيمياء — أول ثانوي — تركيب الذرة ونماذجها", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنين/الكيمياء — أول ثانوي — تركيب الذرة ونماذجها (للعرض والطباعة).pdf"}, {"t": "العلوم — الأول المتوسط — خطوات الطريقة العلمية", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنين/العلوم — الأول المتوسط — خطوات الطريقة العلمية (للعرض والطباعة).pdf"}], "E": [{"t": "اللغة الإنجليزية — الأول الابتدائي — My Friends", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنين/اللغة الإنجليزية — الأول الابتدائي — My Friends (للعرض والطباعة).pdf"}, {"t": "اللغة الإنجليزية — أول ثانوي — Describing People", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنين/اللغة الإنجليزية — أول ثانوي — Describing People (للعرض والطباعة).pdf"}, {"t": "اللغة الإنجليزية — الأول المتوسط — Daily Routines", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنين/اللغة الإنجليزية — الأول المتوسط — Daily Routines (للعرض والطباعة).pdf"}], "لغتي": [{"t": "لغتي الجميلة — الخامس الابتدائي — أخلاق المؤمنين", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنين/لغتي الجميلة — الخامس الابتدائي — أخلاق المؤمنين (للعرض والطباعة).pdf"}, {"t": "الكفايات اللغوية — أول ثانوي — الجملة الاسمية ونواسخها", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنين/الكفايات اللغوية — أول ثانوي — الجملة الاسمية ونواسخها (للعرض والطباعة).pdf"}, {"t": "لغتي الخالدة — الأول المتوسط — الفهم القرائي في وحدة القيم", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنين/لغتي الخالدة — الأول المتوسط — الفهم القرائي في وحدة القيم (للعرض والطباعة).pdf"}], "حاسب آلي": [{"t": "التقنية الرقمية — أول ثانوي — تحليل البيانات بالجداول", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنين/التقنية الرقمية — أول ثانوي — تحليل البيانات بالجداول (للعرض والطباعة).pdf"}, {"t": "المهارات الرقمية — الثاني المتوسط — أمن المعلومات", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنين/المهارات الرقمية — الثاني المتوسط — أمن المعلومات (للعرض والطباعة).pdf"}]}.items()} if GENDER == "m" else {k: [dict(m, u=SITE + quote(m["u"])) for m in v]
                  for k, v in {"أخرى": [{"t": "التربية البدنية — الثالث الابتدائي — التوازن الحركي (بنات)", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنات/التربية البدنية — الثالث الابتدائي — التوازن الحركي (بنات) (للعرض والطباعة).pdf"}, {"t": "التربية الفنية — الرابع الابتدائي — الضوء والظل في الثمار (بنات)", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنات/التربية الفنية — الرابع الابتدائي — الضوء والظل في الثمار (بنات) (للعرض والطباعة).pdf"}, {"t": "المهارات الحياتية والأسرية — الخامس الابتدائي — العلامات الحيوية (بنات)", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنات/المهارات الحياتية والأسرية — الخامس الابتدائي — العلامات الحيوية (بنات) (للعرض والطباعة).pdf"}, {"t": "التربية البدنية — الأول المتوسط — التمرير بباطن القدم (بنات)", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنات/التربية البدنية — الأول المتوسط — التمرير بباطن القدم (بنات) (للعرض والطباعة).pdf"}, {"t": "التربية الفنية — الثاني المتوسط — التوازن في التصميم (بنات)", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنات/التربية الفنية — الثاني المتوسط — التوازن في التصميم (بنات) (للعرض والطباعة).pdf"}], "اجتماعيات": [{"t": "الدراسات الاجتماعية — السادس الابتدائي — قيام الدولة السعودية الأولى (بنات)", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنات/الدراسات الاجتماعية — السادس الابتدائي — قيام الدولة السعودية الأولى (بنات) (للعرض والطباعة).pdf"}, {"t": "الدراسات الاجتماعية — أول ثانوي — التنمية المستدامة ورؤية ٢٠٣٠ (بنات)", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنات/الدراسات الاجتماعية — أول ثانوي — التنمية المستدامة ورؤية ٢٠٣٠ (بنات) (للعرض والطباعة).pdf"}, {"t": "الدراسات الاجتماعية — الثاني المتوسط — موقع المملكة وأثره (بنات)", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنات/الدراسات الاجتماعية — الثاني المتوسط — موقع المملكة وأثره (بنات) (للعرض والطباعة).pdf"}], "إسلامية": [{"t": "الدراسات الإسلامية — الثالث الابتدائي — أركان الإسلام (بنات)", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنات/الدراسات الإسلامية — الثالث الابتدائي — أركان الإسلام (بنات) (للعرض والطباعة).pdf"}, {"t": "الدراسات الإسلامية — أول ثانوي — حديث إنما الأعمال بالنيات (بنات)", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنات/الدراسات الإسلامية — أول ثانوي — حديث إنما الأعمال بالنيات (بنات) (للعرض والطباعة).pdf"}, {"t": "الدراسات الإسلامية — الأول المتوسط — صفة الوضوء ونواقضه (بنات)", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنات/الدراسات الإسلامية — الأول المتوسط — صفة الوضوء ونواقضه (بنات) (للعرض والطباعة).pdf"}], "رياضيات": [{"t": "الرياضيات — الرابع الابتدائي — القيمة المنزلية ضمن مئات الألوف (بنات)", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنات/الرياضيات — الرابع الابتدائي — القيمة المنزلية ضمن مئات الألوف (بنات) (للعرض والطباعة).pdf"}, {"t": "الرياضيات — أول ثانوي — العلاقات والدوال (بنات)", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنات/الرياضيات — أول ثانوي — العلاقات والدوال (بنات) (للعرض والطباعة).pdf"}, {"t": "الرياضيات — الأول المتوسط — القوى والأسس (بنات)", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنات/الرياضيات — الأول المتوسط — القوى والأسس (بنات) (للعرض والطباعة).pdf"}], "علوم": [{"t": "العلوم — الخامس الابتدائي — تصنيف المخلوقات الحية (بنات)", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنات/العلوم — الخامس الابتدائي — تصنيف المخلوقات الحية (بنات) (للعرض والطباعة).pdf"}, {"t": "الأحياء — أول ثانوي — نظرية الخلية ومكوناتها (بنات)", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنات/الأحياء — أول ثانوي — نظرية الخلية ومكوناتها (بنات) (للعرض والطباعة).pdf"}, {"t": "الفيزياء — أول ثانوي — منحنى الموقع والزمن (بنات)", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنات/الفيزياء — أول ثانوي — منحنى الموقع والزمن (بنات) (للعرض والطباعة).pdf"}, {"t": "الكيمياء — أول ثانوي — تركيب الذرة ونماذجها (بنات)", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنات/الكيمياء — أول ثانوي — تركيب الذرة ونماذجها (بنات) (للعرض والطباعة).pdf"}, {"t": "العلوم — الأول المتوسط — خطوات الطريقة العلمية (بنات)", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنات/العلوم — الأول المتوسط — خطوات الطريقة العلمية (بنات) (للعرض والطباعة).pdf"}], "E": [{"t": "اللغة الإنجليزية — الأول الابتدائي — My Friends (بنات)", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنات/اللغة الإنجليزية — الأول الابتدائي — My Friends (بنات) (للعرض والطباعة).pdf"}, {"t": "اللغة الإنجليزية — أول ثانوي — Describing People (بنات)", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنات/اللغة الإنجليزية — أول ثانوي — Describing People (بنات) (للعرض والطباعة).pdf"}, {"t": "اللغة الإنجليزية — الأول المتوسط — Daily Routines (بنات)", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنات/اللغة الإنجليزية — الأول المتوسط — Daily Routines (بنات) (للعرض والطباعة).pdf"}], "لغتي": [{"t": "لغتي الجميلة — الخامس الابتدائي — أخلاق المؤمنين (بنات)", "stage": "الابتدائية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الابتدائية/بنات/لغتي الجميلة — الخامس الابتدائي — أخلاق المؤمنين (بنات) (للعرض والطباعة).pdf"}, {"t": "الكفايات اللغوية — أول ثانوي — الجملة الاسمية ونواسخها (بنات)", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنات/الكفايات اللغوية — أول ثانوي — الجملة الاسمية ونواسخها (بنات) (للعرض والطباعة).pdf"}, {"t": "لغتي الخالدة — الأول المتوسط — الفهم القرائي في وحدة القيم (بنات)", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنات/لغتي الخالدة — الأول المتوسط — الفهم القرائي في وحدة القيم (بنات) (للعرض والطباعة).pdf"}], "حاسب آلي": [{"t": "التقنية الرقمية — أول ثانوي — تحليل البيانات بالجداول (بنات)", "stage": "الثانوية", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة الثانوية/بنات/التقنية الرقمية — أول ثانوي — تحليل البيانات بالجداول (بنات) (للعرض والطباعة).pdf"}, {"t": "المهارات الرقمية — الثاني المتوسط — أمن المعلومات (بنات)", "stage": "المتوسطة", "u": "١ - نموذج تحضير الحصة/نماذج معبّأة استرشادية/المرحلة المتوسطة/بنات/المهارات الرقمية — الثاني المتوسط — أمن المعلومات (بنات) (للعرض والطباعة).pdf"}]}.items()}
# ⛔ الروستر للبنين وحدهم — كشفُ البنات غيرُ متوفّر، فتبقى الكتابةُ اليدوية فيها.
#    والرقمُ الوظيفي هو الهوية: به يزول التباسُ الأسماء المتشابهة.
import json as _json
# ⚠️ **الكشفُ وسجلُّ الإشراف خرجا من المستودع العامّ** (٣٠ سبتمبر ٢٠٢٦): فيهما
#    أسماءٌ وأرقامٌ وظيفيةٌ كانت تُنزَّل من الموقع. ويبقيان على القرص بجوار
#    المولّد ويُقرآن منه، ولا يُرفعان. فإن غابا فالبناءُ يقول ذلك ولا يصمت.
# ⛔ **ولا يُضمَّن الكشفُ في الصفحة** (١ أكتوبر ٢٠٢٦): إخراجُه من المستودع
#    لم يُخرجه من المنصة — كان أربعُمئةٍ وستون اسماً ورقماً وظيفياً مكتوبةً في
#    شفرة الصفحة المنشورة، يقرأها كلُّ من يفتح «عرض المصدر». **والرقمُ الوظيفي
#    هو كلمةُ الدخول**، فكان الكشفُ كشفَ هوياتٍ وكشفَ مفاتيحَ معاً.
#    فالصفحةُ تُبنى خاليةً، والكشفُ يُرفع مرةً إلى المخزن المشترك ويُقرأ منه
#    بعد ربطِ الخادم. ومن لا خادمَ له يكتب اسمَه كما كان يفعل قبل الكشف.
_ROSTER = {}
try:
    with open(os.path.join(HERE, "roster.json"), encoding="utf-8") as _rf:
        _ROSTER = _json.load(_rf) if not F else {}
except Exception:
    if not F: print("  ⚠️ لا كشفَ معلمين على القرص — لا حمولةَ تُكتب")
DATA["roster"] = {}
# ═════════ سجلُّ الإشراف التربوي ═════════
# ⛔ مستخرَجٌ من «قاعدة بيانات الإشراف التربوي» في `supdb.py` — لا يُكتب هنا اسمٌ
#    ولا رقم. والمشرفُ يدخل **برقمه الوظيفي** فيُعرف تخصصُه ومجمعاتُه ومراحلُه
#    ومسارُه بلا اختيارٍ يدويّ — وكان اختيارُ التخصص باباً للخطأ.
# ⚠️ ومن لا حصةَ لوظيفته (توجيهٌ · مصادرُ · نشاطٌ · موهبةٌ · مختبرات) لا يدخل
#    التوزيع، فيُصفّى هنا لا في المتصفّح.
import supdb as _SUP
# ⚠️ «الوظيفة» و«الملاحظة» نصّا مصدرٍ للمراجعة في `supdb.py`، ولا تُعرضان في
#    الشاشة — فلا تُشحنان إلى الصفحة ولا تُطلب لهما ترجمة.
DATA["sups"] = [{"emp": r["emp"], "name": r["name"],
                 "subjects": r["subjects"], "complexes": [_cx(c) for c in r["complexes"]],
                 "stages": r["stages"], "sectors": r["sectors"],
                 "allsubj": bool(r["flags"].get("allsubj")),
                 # ⛔ **علمٌ ميتٌ ثانٍ**: `nat` مكتوبٌ في `supdb.py` ومعه نصُّه
                 #    («فريقُ الهوية الوطنية… ثلاثُ موادَّ في اليوم الواحد»)،
                 #    و`supclash` يقرؤه فيقول «تعارض ٠» — وكان التصديرُ يُسقطه،
                 #    فتُعلن المنصةُ على مشرف الهوية تعارضاً كلَّ يوم. (٧ أكتوبر)
                 "nat": bool(r["flags"].get("nat")),
                 # ⛔ **علمٌ ميتٌ أُحيي**: `schoolhelp` كُتب في `supdb.py` بقرار
                 #    المستشار («حيثُ لا تحضر تساعدها مديرةُ المدرسة والوكيلةُ
                 #    التعليمية بذات المدرسة — لا فريقُ المتابعة الرباعي») ثم
                 #    لم يقرأه شيء. وأثرُه أن حصةَ الروضة العالمية **لها
                 #    مشرفةٌ فليست «بلا مشرف»**، فلا يملك أحدٌ غيرُها رصدَها:
                 #    فإن لم تحضر بقيت بلا تقييمٍ إلى الأبد. (١ أكتوبر ٢٠٢٦)
                 "schoolhelp": bool(r["flags"].get("schoolhelp"))}
                for r in _SUP.recs("f" if F else "m") if not r["flags"].get("nolesson")]
# ⛔ **مشرفةٌ مسجَّلةٌ رُدَّت بأنها «ليست في السجلّ»** (بلاغُ الأستاذة هدى
#    المشجري ٥ أكتوبر ٢٠٢٦، رقمُها ٢٨٤٢٨): فتحت نسخةَ **البنين** ورقمُها في
#    سجلّ **البنات**. فالرسالةُ صادقةٌ في هذه النسخة وكاذبةٌ في المنظومة،
#    وتُرسل صاحبَها إلى إدارة التخطيط في أمرٍ لا شأنَ لها به.
# ⚠️ فتُشحن **أرقامُ مشرفي النسخة الأخرى** (أرقامٌ بلا أسماء — ولا شيءَ فيها
#    يزيد على ما في تلك النسخة المنشورة أصلاً)، فتُميّز الرسالةُ الحالتين:
#    «رقمُك في النسخة الأخرى — افتحها» أو «راجع إدارة التخطيط».
DATA["supsother"] = [r["emp"] for r in _SUP.recs("m" if F else "f")
                     if not r["flags"].get("nolesson")]
DATA["othername"] = g("نسخة البنات", "نسخة البنين")
# ⚠️ ورقةُ الروضة: موادُّها وأعمدتُها — من `scheddata` لا تُكتب هنا
# ⛔ **ولا روضةَ في بناء البنين** (قرارُ المستشار ٩ أكتوبر ٢٠٢٦): الورقةُ
#    وُضعت لقسم البنات — مشرفةٌ واحدةٌ في العالمي ولا مشرفةَ في الوطني —
#    وكان التبويبُ غيرَ مقيَّدٍ بالجنس فظهر في البناءين، فسجّل معلمٌ حصّتين
#    في روضة عرقة (حُذفتا). والمنعُ **بحجب البيانات** لا بإخفاء الزرِّ وحدَه:
#    زرٌّ مخفيٌّ ليس منعاً، والصفحةُ تُقرأ بـ«عرض المصدر».
DATA["kgsubs"] = SD.KG_SUBS if F else []
DATA["kgbands"] = {_cx(k): v for k, v in SD.KG_BANDS.items()} if F else {}
DATA["kgspec"] = "رياض الأطفال" if F else ""
DATA["gapscore"] = GAP_SCORE
# ⛔ **الضميرُ المتّصل لا يؤنِّثه `fem()`**: كُتب «فتظهر الحصةُ في حسابه» في
#    الجافاسكربت فخرج كما هو في نسخة البنات (قِيس باللقطة ٩ أكتوبر ٢٠٢٦).
#    فالنصّان يُكتبان هنا بجنسَيهما — وهي القاعدةُ المتَّبعةُ في نصوص الشارات.
DATA["peerhintname"] = g(
    "لكل حصةٍ زائران — يُكتب اسمُ كلٍّ منهما كما يدخل به، فتظهر الحصةُ في حسابه",
    "لكل حصةٍ زائرتان — يُكتب اسمُ كلٍّ منهما كما تدخل به، فتظهر الحصةُ في حسابها")
DATA["peerhintlist"] = g(
    "لكل حصةٍ زائران — يُختاران من كشف المعلمين فتظهر الحصةُ في حسابَيهما",
    "لكل حصةٍ زائرتان — تُختاران من كشف المعلمات فتظهر الحصةُ في حسابَيهما")

# ⛔ **نصوصُ الشارات تُكتب هنا بجنسَيها لا في الجافاسكربت**: قِيس على نسخة
#    البنات فخرج «عليك — لا مشرفَ لتخصصها» مذكَّراً، و«مشرفٌ مختصٌّ لا يحضر»
#    كما هو، و«ووكيلها» بلا تاء — لأن `fem()` لا تمسح نصوصَ الشفرة إلا بقائمةٍ
#    جزئية، فقلبت «يتابع» إلى «تتابع» وفاعلُها «الفريقُ» مذكَّر فخرج لحنٌ
#    صريح. فما يُقرأ في الشاشة يُكتب بـ`g()` ويُقرأ من `D`. (١ أكتوبر ٢٠٢٦)
DATA["gaptag"] = g("عليك — لا مشرفَ لتخصصها", "عليكِ — لا مشرفةَ لتخصصها")
DATA["gaptip"] = g(
    "لا مشرفَ مختصٌّ لهذا التخصص في هذه المدرسة، فالرصدُ على الفريق المعاون — وأنت منه.",
    "لا مشرفةَ مختصةً لهذا التخصص في هذه المدرسة، فالرصدُ على الفريق المعاون — وأنتِ منه.")
DATA["asstag"] = g("عليك — مشرفُها قد لا يحضر", "عليكِ — مشرفتُها قد لا تحضر")
DATA["asstip"] = g(
    "لهذه الحصة مشرفٌ مختصٌّ لا يحضر كلَّ حصة، فالرصدُ على مدير المدرسة ووكيله بذات المدرسة.",
    "لهذه الحصة مشرفةٌ مختصةٌ لا تحضر كلَّ حصة، فالرصدُ على مديرة المدرسة ووكيلتها بذات المدرسة.")
# ⚠️ وهذه بصيغةٍ اسميةٍ في الجنسَين: فاعلُها «الفريقُ» مذكَّرٌ في النسختين،
#    فلو كُتبت بفعلٍ قلبَه المؤنِّثُ وخرج «الفريقُ تتابع».
DATA["intqanodel"] = "فريقُ متابعة التقويم الداخلي: متابعةٌ لا حذف."


def guard_sups(sups):
    """⛔ نطاقٌ يشير إلى ما ليس في المنصة يُسقط مشرفاً كاملاً بلا صوت."""
    cxs = set(DATA["complexlist"])
    sts = {b["stage"].split("- ")[0].strip() for bl in DATA["bands"].values() for b in bl}
    bad = []
    for r in sups:
        for c in r["complexes"]:
            if c not in cxs: bad.append("%s: مجمع «%s»" % (r["name"], c))
        for sp in r["subjects"]:
            if sp not in DATA["specs"]: bad.append("%s: تخصص «%s»" % (r["name"], sp))
        for st in r["stages"]:
            if st not in sts: bad.append("%s: مرحلة «%s»" % (r["name"], st))
        for sc in r["sectors"]:
            if sc not in DATA["sectors"]: bad.append("%s: قطاع «%s»" % (r["name"], sc))
        if not r["subjects"] and not r["allsubj"]:
            bad.append("%s: بلا تخصصٍ ولا إشرافٍ بالمرحلة" % r["name"])
    if bad:
        raise SystemExit("⛔ سجلُّ الإشراف يشير إلى ما ليس في المنصة:\n  "
                         + "\n  ".join(sorted(set(bad))))
    emps = [r["emp"] for r in sups]
    dup = sorted({e for e in emps if emps.count(e) > 1})
    if dup: raise SystemExit("⛔ رقمٌ وظيفيٌّ مكرَّرٌ في سجلّ الإشراف: " + " · ".join(dup))
    print("  ✓ سجلُّ الإشراف: %d مشرفاً بحصص · %d تخصصاً مغطّى"
          % (len(sups), len({sp for r in sups for sp in r["subjects"]})))


# ⛔ طولُ الرقم الوظيفي المعتمد — قاعدةُ المدرسة لا استنتاجٌ من الكشف
#    (المشرفةُ العامة ٣٠ سبتمبر ٢٠٢٦: خمسُ منازل، مثل ٣٠٨٨٨).
# ═════════ ربطُ الاتجاه التدريسي بإستراتيجياته ═════════
# ⛔ **مستخرَجٌ من نشرات الاتجاهات الستّ المعتمدة** (acontent.APPROACHES، الحقل
#    التاسع «الاستراتيجيات») لا مؤلَّفٌ هنا — فاختيارُ المعلم يُقيَّد بما اعتُمد.
# ⚠️ والنشراتُ تغطّي ١٤ من ١٩. والخمسُ الباقيةُ وُضعت باجتهادٍ مُعلَّلٍ من
#    مؤشراتها العشرة، **وتُعرض على المستشار للتصحيح**:
#      · جدول التعلم (KWL)  ← التقويم من أجل التعلم (أداةُ تقويمٍ قبليٍّ وبَعدي)
#      · خرائط المفاهيم     ← التفكير الناقد والإبداعي (تحليلُ العلاقات)
#      · نموذج فراير        ← التفكير الناقد والإبداعي (تحليلُ المفهوم وخصائصه)
#      · اللعب بالعرائس     ← القيم وبناء الشخصية (تمثيلُ مواقفَ قيمية)
#      · التدريس الصريح     ← التعليم المتمايز (سقالاتٌ تُرفع تدريجياً)
#    ⛔ ولو تُركت بلا اتجاهٍ لصارت غيرَ قابلةٍ للاختيار بعد التقييد — وهو حذفٌ
#       صامتٌ لخمس إستراتيجياتٍ من البنك.
import acontent as _AC
_EXTRA = {
    "جدول التعلم (KWL)": "التقويم من أجل التعلم",
    "خرائط المفاهيم": "التفكير الناقد والإبداعي",
    "نموذج فراير": "التفكير الناقد والإبداعي",
    "اللعب بالعرائس": "القيم وبناء الشخصية",
    "التدريس الصريح بالنمذجة المتدرجة": "التعليم المتمايز",
}
_BANK = [b["name"] for b in DATA["bank"]]
_APPSTRAT = {a: [] for a in DATA["approaches"]}
# ⛔ **المطابقةُ بالمفتاح لا بالكلمات**: اسمُ النشرة أطولُ من اسم المنصة
#    («التعلم المعزَّز بالتقنية…» مقابل «التقنية…»)، وتقاطعُ الكلمات ربط
#    نشرةَ التقنية بـ«التقويم من أجل التعلم» لاشتراك كلمة «التعلم» — فخرج
#    اتجاهٌ بتسع إستراتيجياتٍ وآخرُ بصفر. كشفه العدّادُ لا العين.
_KEY2APP = {
    "pbl": "حل المشكلات والمشاريع",
    "differentiated": "التعليم المتمايز",
    "thinking": "التفكير الناقد والإبداعي",
    "afl": "التقويم من أجل التعلم",
    "tech": "التقنية والذكاء الاصطناعي",
    "values": "القيم وبناء الشخصية",
}
for _rec in _AC.APPROACHES:
    _short = _KEY2APP.get(_rec[0])
    if _short not in _APPSTRAT:
        raise SystemExit("⛔ مفتاحُ نشرةٍ بلا نظيرٍ في المنصة: %s (%s)" % (_rec[0], _rec[1]))
    for _n in [x.strip() for x in str(_rec[9]).split("·")]:
        if _n not in _BANK:
            raise SystemExit("⛔ إستراتيجيةٌ في نشرة «%s» ليست في البنك: %s" % (_short, _n))
        if _n not in _APPSTRAT[_short]:
            _APPSTRAT[_short].append(_n)
for _n, _a in _EXTRA.items():
    if _n not in _BANK:
        raise SystemExit("⛔ إستراتيجيةٌ مقترحةٌ ليست في البنك: " + _n)
    if _n not in _APPSTRAT[_a]:
        _APPSTRAT[_a].append(_n)
# ⛔ ولا تبقى إستراتيجيةٌ بلا اتجاه — وإلا اختفت من القائمة بلا أن يُعلم أحد
# ⛔ ولا اتجاهَ بلا إستراتيجيات: صفرٌ يعني ربطاً فاسداً لا محتوىً ناقصاً
_empty = [k for k, v in _APPSTRAT.items() if len(v) < 3]
if _empty:
    raise SystemExit("⛔ اتجاهٌ بأقلَّ من ثلاث إستراتيجيات — الربطُ فاسد:\n     "
                     + "\n     ".join("%s = %d" % (k, len(_APPSTRAT[k])) for k in _empty))
_orphan = [b for b in _BANK if not any(b in v for v in _APPSTRAT.values())]
if _orphan:
    raise SystemExit("⛔ إستراتيجياتٌ بلا اتجاهٍ فتختفي من الاختيار:\n     "
                     + "\n     ".join(_orphan))
DATA["appstrat"] = _APPSTRAT
print("  ✓ الاتجاهات: " + " · ".join("%s=%d" % (k, len(v)) for k, v in _APPSTRAT.items()))

# ⛔ توحيدُ اسم المجمع بعد بناء DATA — مفاتيحَ وقيماً في كل بنيةٍ تُفهرس به.
#    وُضع هنا لا داخل القاموس كي يبقى تعريفُ البنى مقروءاً.
# ⚠️ و«natdays» مفهرسٌ بالمجمع أيضاً — فاتني في أول تطبيقٍ فبقيت فيه «عرقه»
#    وأمسكها حارسُ الترجمة. فتُعدَّ كلُّ بنيةٍ تحمل اسمَ مجمعٍ مفتاحاً أو قيمة.
for _k in ("bands", "rot", "sup", "natdays"):
    if _k in DATA:
        DATA[_k] = _normcx(DATA[_k])
DATA["complexlist"] = [_cx(x) for x in DATA.get("complexlist", [])]
DATA["complexes"] = _normcx(DATA.get("complexes", {}))
# ⚠️ وحقلُ المجمع في الكشف («c») يُوحَّد أيضاً: منه يُملأ المجمعُ تلقائياً عند
#    الدخول، وبالصيغة القديمة لا يطابق شيئاً فيُترك ١٨٦ معلماً بلا مجمعٍ مُختار.
for _r in _ROSTER.values():
    if isinstance(_r, dict) and _r.get("c"):
        _r["c"] = _cx(_r["c"])

# ⛔ حارسُ أسماء المجمعات: كلُّ مجمعٍ يُعرض في القائمة يجب أن تكون له أعمدةٌ
#    في «bands» ودورانٌ في «rot». وبدونه يفتح المستخدمُ جدولاً فارغاً ولا
#    يُنبَّه أحد — وهو ما وقع لـ«عرقة» حتى كشفه المستشار.
_shown = {c for v in DATA["complexes"].values() for c in v}
_nob = sorted(c for c in _shown if not (DATA["bands"] or {}).get(c))
_nor = sorted(c for c in _shown if not (DATA["rot"] or {}).get(c))
if _nob or _nor:
    raise SystemExit("⛔ مجمعٌ معروضٌ بلا بيانات — جدولُه سيكون فارغاً:\n"
                     + ("     بلا أعمدة: " + "، ".join(_nob) + "\n" if _nob else "")
                     + ("     بلا دوران: " + "، ".join(_nor) + "\n" if _nor else "")
                     + "  والسببُ غالباً اختلافُ رسم الاسم (عرقة/عرقه) بين المصدر والقائمة.")
# ⛔ ولا تبقى الصيغةُ القديمةُ في أي موضع: بقيت مرّةً في «natdays» ومرّةً في
#    حقل الكشف، وكلتاهما تُفشل مطابقةً صامتةً. فيُمسح البناءُ كلُّه.
def _stale(o, path=""):
    if isinstance(o, str):
        if any(k in o for k in _CXFIX):
            yield path or "؟", o
    elif isinstance(o, dict):
        for k, v in o.items():
            if isinstance(k, str) and any(x in k for x in _CXFIX):
                yield (path + "[مفتاح]"), k
            yield from _stale(v, path + "." + str(k)[:16])
    elif isinstance(o, (list, tuple)):
        for i2, v in enumerate(o):
            yield from _stale(v, path + "[%d]" % i2)


_left = list(_stale(DATA))
if _left:
    raise SystemExit("⛔ بقيت الصيغةُ القديمةُ لاسم المجمع في %d موضعاً:\n"
                     % len(_left)
                     + "\n".join("     %-38s %r" % x for x in _left[:8])
                     + "\n\n  وكلُّ موضعٍ منها مطابقةٌ تفشل صامتةً.")
print("  ✓ %d مجمعاً معروضاً ولكلٍّ أعمدتُه ودورانُه · ولا صيغةَ قديمة" % len(_shown))


# حمولةُ الكشف تُكتب بجوار المولّد ليرفعها المستشارُ من شاشة الأدوات — ولا تُنشر
if _ROSTER:
    _rp = os.path.join(HERE, "roster.payload.json")
    with open(_rp, "w", encoding="utf-8") as _pf:
        _json.dump({"kind": "platform", "id": ("ikf_roster" if F else "ikm_roster"),
                    "data": _ROSTER}, _pf, ensure_ascii=False)
    print("  ✓ حمولةُ الكشف: %d معلماً في %s (لا تُنشر)"
          % (len(_ROSTER), os.path.basename(_rp)))

# ═════════ توأمةُ الاستمارة والتحضير ═════════
# ⛔ كان الوعدُ نصّاً: «كل خانةٍ في التحضير يقابلها مؤشرٌ يبحث عنه الزائر» —
#    ولا بنيةَ تحته، وثمانيةَ عشرَ مؤشراً بلا خانةٍ أصلاً. فصار جدولاً محروساً
#    في `indmap.py`: لكل مؤشرٍ من الخمسين موضعُه، ومن لا يُحضَّر يُعلن ذلك.
import indmap as IM
import prepdef as PD
_tw, _tobs, _trec = IM.guard(DATA["domains"])
_PLAB = {r["k"]: fem(r["label"]) for sec in PD.SECTIONS for r in sec["rows"]}
DATA["preplab"] = _PLAB
DATA["indmap"] = {k: ({"obs": 1} if v is IM.OBS else {"rec": 1} if v is IM.REC
                      else {"f": v}) for k, v in IM.MAP.items()}
DATA["indcard"] = IM.CARD
print("  ✓ التوأمة: %d مؤشراً له خانتُه في التحضير · %d بالمشاهدة · %d من السجلّ"
      % (_tw, _tobs, _trec))

DATA["emplen"] = 5
DATA["sysname"] = "نظام الحصة الموحَّدة"
# التوقيعُ شخصيٌّ حصريّ — لا يُنسب العملُ إلى جهةٍ ولا إلى أداة
DATA["owner_role"] = "مدير التخطيط والاعتماد المدرسي"
DATA["owner"] = "أ. أحمد صيام"
# ⛔ لا رابطَ للدليل: المستودعُ عامّ، ودليلُ الربط يُعلِّم الغريبَ كيف يبني
#    منظومةً موازيةً. فالخانةُ تبقى فارغةً ويختفي زرُّ «كيف؟» من نافذة الربط،
#    ويأخذ الرابطَ من المستشار وحدَه. (٢٩ سبتمبر ٢٠٢٦)
DATA["guide"] = ""
# ⛔ حارسُ النداءات المعلَّقة: دالّةٌ تُنادى ولا تُعرَّف تمرّ من node --check
#    ومن البناء، ولا تسقط إلا عند أول استدعاءٍ عند المستخدم. (٢٩ سبتمبر ٢٠٢٦)
import guard_js as _GJS
# ⛔ الملفّان يُشحنان في صفحةٍ واحدة، فيُفحصان معاً: `importPanel` معرَّفةٌ
#    في planimport.js ومُنادَاةٌ من platform_app.js — وفحصُ كلٍّ وحدَه يُبلّغ
#    كاذباً عن نداءٍ معلَّق.
_GJS.main([os.path.join(HERE, "platform_app.js")],
          extra=[os.path.join(HERE, "planimport.js")])
guard_specmap(_ROSTER)          # ⛔ يفشل البناءُ عند قيمةٍ بلا مطابقة
guard_sups(DATA["sups"])                # ⛔ ونطاقُ كلِّ مشرفٍ يشير إلى موجود

# ═════════ بطاقةُ كل إستراتيجيةٍ برابطها ═════════
# ⛔ كان بنكُ البطاقات مجلداً واحداً يُفتح من مرحلة التنفيذ فقط، فيبحث المعلمُ
#    عن بطاقته بين تسع عشرة. صار لكل إستراتيجيةٍ **رابطُ بطاقتها** يُفتح من
#    التحضير ومن ورقة التنفيذ. (طلبُ المستشار ٣٠ سبتمبر ٢٠٢٦)
# ⚠️ أسماءُ الملفات على القرص بترميز NFD وأسماءُ البنك NFC — فالمطابقةُ تُطبَّع
#    أولاً، وإلا خرجت أربعُ بطاقاتٍ «مفقودة» وهي موجودة.
import unicodedata as _ud
_nfc = lambda x: _ud.normalize("NFC", x)


def _card_links():
    base = os.path.join(ROOT, D4, GF)
    have = {}
    for fn in (os.listdir(base) if os.path.isdir(base) else []):
        if fn.endswith(PDF): have[_nfc(fn)] = fn
    out, miss = {}, []
    for b in DATA["bank"]:
        fn = _nfc("بطاقة تشخيص — %s — ابن خلدون%s%s" % (b["name"], SF, PDF))
        if fn in have: out[b["name"]] = SITE + quote(os.path.join(D4, GF, have[fn]))
        else: miss.append(b["name"])
    if miss:
        raise SystemExit("⛔ إستراتيجياتٌ بلا بطاقةٍ منشورة (%d):\n  " % len(miss)
                         + "\n  ".join(miss))
    print("  ✓ بطاقاتُ الإستراتيجيات: %d من %d لها رابطٌ مباشر"
          % (len(out), len(DATA["bank"])))
    return out


_CARDS = _card_links()
for _b in DATA["bank"]:
    _b["u"] = _CARDS[_b["name"]]
DATA["specmap"] = SPECMAP

# ═════════ خريطةُ المواد إلى التخصصات ═════════
# ⛔ **«احذف أي حصة من تخصص مخالف للصف»** (المستشار ٧ أكتوبر ٢٠٢٦). ودُقِّق
#    المخزنُ الحيُّ فكان المخالفُ ٤٤ حصةً — ومثلُها ستَّ مراتٍ ليست مخالفةً:
#    «كيمياء» و«فيزياء» و«أحياء» **هي علوم** في الثانوي، و«الكفايات اللغوية»
#    لغتي، و«التقنية الرقمية» حاسب آلي. فالحذفُ بلا هذه الخريطة إتلافُ عمل.
# ⚠️ **ومرجعُها المنصةُ نفسُها**: أسماءُ مواد المناهج في نماذجها الاسترشادية
#    (`DATA["models"]`) — لا قائمةٌ تُؤلَّف هنا. فإن زاد نموذجٌ زادت المادة.
# ⚠️ والمرادفاتُ **مرصودةٌ من المخزن الحيّ** لا متخيَّلة: ما كتبه المعلمون
#    فعلاً (إملاءً ولغةً واختصاراً). وما لم يُعرف انتسابُه لا يُحكم عليه.
# ⚠️ ورياضُ الأطفال خارجَها: موادُّها ليست من التخصصات، وتكتبها المعلمةُ بنفسها.
_SUBJ_ALIAS = {
    "علوم": ["science", "sciences", "كيمياء", "chemistry", "فيزياء", "physics",
             "احياء", "أحياء", "biology", "علم أرض", "علم الأرض", "جيولوجيا"],
    "لغتي": ["عربي", "اللغة العربية", "لغة عربية", "arabic", "كفايات لغوية", "كفايات",
             "قدرات لفظي", "القدرات اللفظي", "قدرات لفظية"],
    "حاسب آلي": ["حاسب", "حاسوب", "computer", "computing", "ict", "it",
                 "تقنية رقمية", "مهارات رقمية", "تصميم رقمي", "digital skills"],
    "إسلامية": ["إسلامية", "إسلاميات", "اسلاميات", "دين", "islamic",
                "قرآن", "توحيد", "فقه", "حديث", "تجويد"],
    # ⚠️ ومقرّراتُ الثانويِّ بنصِّ المستشار ٧ أكتوبر ٢٠٢٦: «مقدمة الأعمال تتبع
    #    الاجتماعيات بالثانوي، والقدرات اللفظي تتبع لغتي بالثانوي».
    "اجتماعيات": ["اجتماعيات", "اجتماعية", "social", "تاريخ", "جغرافيا",
                  "مقدمة الأعمال", "مقدمة أعمال"],
    "E": ["english", "e", "انجليزي", "إنجليزي", "انجلش", "لغة إنجليزية"],
    "البدنية": ["بدنية", "تربية بدنية", "pe", "physical education",
                "تربية بدنية وصحية", "رياضة بدنية"],
    "الفنية": ["فنية", "فنون", "art", "arts", "مهارات حياتية", "أسرية"],
    "رياضيات": ["رياضيات", "math", "maths", "mathematics", "رياضة"],
}


def _subjnorm(t):
    """تسويةٌ واحدةٌ هنا وفي الصفحة: همزاتٌ وياءٌ وتاءٌ وأرقامُ المستويات."""
    t = unicodedata.normalize("NFKC", str(t or ""))
    t = re.sub(r"[\u064b-\u0652\u0640\u200f\u200e]", "", t)
    t = t.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ى", "ي"),
                 ("ة", "ه"), ("ؤ", "و"), ("ئ", "ي")):
        t = t.replace(a, b)
    t = re.sub(r"[0-9]+([-/][0-9]+)?", " ", t)
    t = re.sub(r"[^\w\u0600-\u06ff ]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    # ⛔ **و«ال» تُنزع من كل كلمةٍ لا من أولاها**: «التصميم الرقمي» كان لا
    #    يُطابق «تصميم رقمي» لأن «ال» الثانيةَ تبقى — فبقيت المادةُ مجهولةَ
    #    الانتساب وهي معروفة. (كشفه نصُّ المستشار عن مقرّرات الثانوي.)
    # ⚠️ ولا تُنزع إن بقي أقلُّ من ثلاثة أحرف: «آلي» ← «الي» ← «ي»، فينكسر
    #    «حاسب آلي» نفسُه. فالشرطُ حارسٌ لا تحسين.
    return " ".join(w[2:] if w.startswith("ال") and len(w) - 2 >= 3 else w
                    for w in t.split(" "))


def _build_subjfam():
    fam, src = {}, {}
    for key, lst in DATA["models"].items():
        for m in lst:
            nm = str(m.get("t", "")).split("—")[0].strip()
            if not nm:
                continue
            k = key
            if key == "أخرى":
                k = "البدنية" if "بدنية" in nm else "الفنية"
            fam[_subjnorm(nm)] = k
            src[_subjnorm(nm)] = nm
    for key, lst in _SUBJ_ALIAS.items():
        for a in lst:
            fam.setdefault(_subjnorm(a), key)
    # ⚠️ شاهدٌ: كلُّ مادةٍ في نماذج المنصة تعود إلى تخصصها — وإلّا فالخريطةُ تكذب
    bad = []
    for key, lst in DATA["models"].items():
        for m in lst:
            nm = str(m.get("t", "")).split("—")[0].strip()
            want = key if key != "أخرى" else ("البدنية" if "بدنية" in nm else "الفنية")
            if nm and fam.get(_subjnorm(nm)) != want:
                bad.append("%s ← %s (المنتظَر %s)" % (nm, fam.get(_subjnorm(nm)), want))
    if bad:
        raise SystemExit("⛔ خريطةُ المواد لا تُعيد موادَّ المنصة إلى تخصصها:\n    "
                         + "\n    ".join(bad))
    for key, lst in _SUBJ_ALIAS.items():
        for a in lst:
            if fam.get(_subjnorm(a)) != key and _subjnorm(a) not in src:
                bad.append("«%s» يؤدّي إلى %s لا %s" % (a, fam.get(_subjnorm(a)), key))
    if bad:
        raise SystemExit("⛔ مرادفٌ ينتسب إلى تخصصَين:\n    " + "\n    ".join(bad))
    return fam


# ⚠️ **ولا تُحقن في `DATA`**: مفاتيحُها نصوصُ مطابقةٍ لا تسمياتٌ تُعرض، فحارسُ
#    الترجمة يطلب لها إنجليزيةً لا معنى لها. فتُحقن في منطقةٍ محميّةٍ بعلامة
#    `@noi18n` — وهي الآليةُ عينُها التي حُمي بها نصُّ أمر الذكاء الاصطناعي.
SUBJFAM = _build_subjfam()
print("  ✓ خريطةُ المواد: %d مدخلاً لـ%d تخصصاً · وكلُّ موادِّ النماذج تعود إلى تخصصها"
      % (len(SUBJFAM), len(set(SUBJFAM.values()))))
DATA["adminrole"] = "مستشارٌ ومديرُ المنصة"
# ═════════ بوّابةُ المستشار ═════════
# ⚠️ لا كلمةَ سرٍّ هنا ولا بريد — **بصمتان** فقط: بصمةُ البريد (SHA-256) وبصمةُ
#    الكلمة (PBKDF2-HMAC-SHA256 بـ١٥٠٬٠٠٠ دورةٍ وملحٍ عشوائي). فمن يفتح مصدرَ
#    الصفحة لا يستخرج منهما شيئاً عملياً. ولو أراد المستشارُ تغييرَ الكلمة،
#    تُولَّد بصمةٌ جديدةٌ ويُستبدل هذا المقطع — ولا تُكتب الكلمةُ في أي ملف.
DATA["admin"] = {"u": "60ba67a29247c2d23db354fb53132064a9937270b2b92bcc8bee897e3b792828",
                 "s": "bc8f52a95735d3eaaf46e028cc709e30",
                 "h": "ecfade548d2db3c1eed72cfb7b7f13c8de9bd42c483673abce08c429b2d94fa4",
                 "it": 150000}
# ═════════ مفتاحُ الانضمام ═════════
# ⛔ **آليتا دخولٍ متعارضتان**: بُنيت المنصةُ على أن كلَّ جهازٍ يصله رابطٌ خاصٌّ
#    يحمل المخزنَ في `#srv=`، والمستشارُ **نشر الصفحةَ الرئيسةَ وصوّر فيديو
#    يشرح الدخولَ منها**. فمن دخل من الصفحة وقع على جهازٍ غيرِ مربوط: يكتب
#    تحضيرَه كاملاً ولا يبلغ مدرستَه، ولا يعلم. (أمسكه المستشارُ على جواله
#    ٥ أكتوبر ٢٠٢٦ وقال: «لا يمكنني الآن تغيير هذه الطريقة».)
# ⚠️ والصفحةُ ساكنةٌ على مستودعٍ عامّ، فلا ثالثَ لاثنين: إمّا أن يحمل المفتاحُ
#    داخلَها فيقرؤه من يفتح مصدرَها، وإمّا أن يصل الجهازَ من خارجها. فاختار
#    المستشارُ الأولَ صراحةً (٥ أكتوبر ٢٠٢٦) **مع تحصين الخادم**:
#      · التفريغُ الكامل (`__replace`) يحتاج مفتاحاً ثانياً لا يُنشر.
#      · والحذفُ الجماعيُّ يرفضه الخادمُ إن أسقط أكثرَ من عُشر الحصص.
# ⚠️ ويُقرأ من المجلد الخاصّ لا من هذا الملف: فلا يدخل مصدرَ المستودع، وتدويرُه
#    يمسُّ ملفاً واحداً. وإن غاب الملفُّ بُنيت الصفحةُ بلا مفتاح — ويقولها البناء.
import json as _sjson
_SRVCFG = os.path.expanduser("~/Desktop/خادم الحصة الموحَّدة (خاصّ — لا يُنشر)/store.json")
try:
    _sc = _sjson.load(open(_SRVCFG, encoding="utf-8"))
    DATA["srv"] = _sc.get("url", "")
    DATA["join"] = _sc.get("join", "")
    print("  ✓ مفتاحُ الانضمام مبنيٌّ في الصفحة — كلُّ جهازٍ يُربط من أول فتحة")
except Exception as _e:
    DATA["srv"] = ""
    DATA["join"] = ""
    print("  ⚠️ لا مفتاحَ انضمام (%s) — الأجهزةُ تحتاج رابطَ دخولٍ يدوياً" % _e.__class__.__name__)

DATA["build"] = build_stamp()
# ⛔ **لا يُطلب من المعلّم أن يُحدِّث صفحتَه**: قلتُ للمستشار «أرسل لهم: أغلقوا
#    التبويبَ وافتحوه»، فقال: «لن أستطيع — فهذا يزيد تشككهم بالمنصة. قم أنت
#    بهذا الحل بنفسك». (٥ أكتوبر ٢٠٢٦) وهو محقّ: من يُصلح عطلاً ليس له يفقد
#    الثقةَ بما يُصلحه. فتُحدِّث الصفحةُ نفسَها.
# ⚠️ ويُكتب الختمُ في ملفٍّ صغيرٍ مستقلّ (`ver.json` نحو ٨٠ بايتاً) لا يُقرأ
#    من الصفحة نفسِها: فسحبُ ١٫٥ ميجابايت كلَّ بضع دقائقَ من كل جهازٍ عبءٌ
#    لا داعيَ له، وهو ما يفعله من يقارن الصفحةَ بنفسها.
DATA["verurl"] = "../ver.json"
DATA["evalroles"] = EVAL_ROLES
DATA["tulab_t"] = fem("ما قاله الطلاب — يُسأل ثلاثة من مستويات مختلفة")
DATA["lab_t"] = fem("ما يفعله المعلم")
DATA["lab_l"] = fem("ما يفعله المتعلم — فعلٌ يُرى")


def bidi(t):
    return re.sub(r"([٠-٩]+٪?)", r"\1" + RLM, t) if isinstance(t, str) else t


logo = ""
lp = os.path.join(HERE, "hub_logo.jpg")
if os.path.exists(lp):
    logo = b64(lp)

out = sys.argv[1] if len(sys.argv) > 1 else "platform.html"
# ═════════ الإنجليزيةُ طبقةَ عرضٍ ═════════
# ⛔ **موضعُها هنا لا قبله**: كانت قبل أسطر `DATA[...] = ...` الأخيرة، فلم
#    يرَ الفحصُ «نظام الحصة الموحَّدة» و«مستشارٌ ومديرُ المنصة» وغيرَها —
#    ومرَّ الحارسُ راضياً لأنها لم تكن في قائمته أصلاً، وظهرت عربيةً على
#    الشاشة الإنجليزية. فالفحصُ بعد اكتمال DATA لا قبله. (٣٠ سبتمبر ٢٠٢٦)
# ⛔ **بعد** التأنيث لا قبله: المؤنِّثُ يعمل على النصوص المقتبسة، فلو لُفّت في
#    t("…") أولاً لصار المقتبسُ وسيطَ دالّةٍ وأُنّث كما هو — والمعجمُ مفاتيحُه
#    الصيغةُ المعروضةُ فعلاً في هذا البناء (مذكَّرةً كانت أو مؤنَّثة).
# ⚠️ ولذلك يُبنى المعجمُ على النصّ **بعد** التأنيث، ويُفحص عليه.
# ⛔ الإنجليزيةُ لا جنسَ لها: «اختر دورك» و«اختاري دورك» ترجمتُهما واحدة.
#    فلا يُكتب المعجمُ مرّتين — تُشتقُّ مفاتيحُ البناء المؤنَّث من المذكَّرة
#    بالمؤنِّث نفسِه. وكتابةُ ٢٨٤ مدخلاً بيدٍ تُخطئ ولا تُكتشف.
if F:
    from femjs import fem_of as _fem_of
    for _k, _v in list(i18n.EN.items()):
        _fk = _fem_of(_k)
        if _fk != _k and _fk not in i18n.EN:
            i18n.EN[_fk] = _v

_ar_strings = i18n.wrapped_strings(JS)
_data_strings = []
def _walk_data(o):
    if isinstance(o, str):
        if re.search(i18n.AR, o):
            _data_strings.append(o)
    elif isinstance(o, dict):
        # ⛔ **والمفاتيحُ تُمسح كما القيم**: أيامُ الأسبوع وأسماؤه مفاتيحُ في
        #    `rot` و`sup` و`natdays` **وتُعرض رؤوسَ صفوفٍ في جدول الدوران».
        #    فإغفالُ المفاتيح أبقى «الأربعاء» عربيةً في الشاشة الإنجليزية.
        for k, v in o.items():
            _walk_data(k)
            _walk_data(v)
    elif isinstance(o, (list, tuple)):
        for v in o:
            _walk_data(v)
# ⛔ **`apprdet` لا يُعرض في شاشة**: تعريفُ الاتجاه وشواهدُه الثلاثة تُشحن
#    لتدخل **نصَّ الأمر** الذي يُنسخ إلى المساعد الذكيّ — وهو عربيٌّ بطبيعته.
#    فتُستثنى من مسح الترجمة كما يُستثنى الكشف. (٣٠ سبتمبر ٢٠٢٦)
_walk_data({k: v for k, v in DATA.items() if k != "apprdet"})
# ⛔ البياناتُ التي لا تُترجَم: أسماءٌ وتواريخُ ومساراتُ ملفاتٍ ومجمعاتٌ
_names = set()
# ⛔ من الكشف: «n» **اسمُ شخصٍ** وحدَه لا يُترجَم. و«s» مادةٌ و«g» قطاعٌ
#    و«c» مجمعٌ — تسمياتٌ تُعرض في الجدول والتقارير. واستثناؤها كلَّها أخرج
#    «رياضيات» و«وطني» من المعجم فبقيا عربيَّين في الشاشة الإنجليزية.
# ⚠️ ولم يبقَ في البيانات اسمُ معلمٍ يُستثنى — الكشفُ يُحمَّل في المتصفّح.
#    وأسماءُ المجمعات تبقى مُستثناةً من مصدرها (`complexlist`) لا من الكشف.
for _v in _ROSTER.values():
    _names.add(str(_v.get("c") or ""))
# ⛔ ولا يُستثنى «cal» كلُّه: تواريخُه تعالجها القاعدةُ، و«w» **اسمُ أسبوعٍ
#    يُعرض** — واستثناؤه أخرج «الأسبوع السادس» من المعجم فبقي عربياً.
for _c in (DATA.get("cal") or []):
    _names |= {str(_c.get(_k) or "") for _k in _c if _k != "w"}
for _m in sum((DATA.get("models") or {}).values(), []):
    _names |= {str(_m.get(_k) or "") for _k in _m}
for _g, _wk in (DATA.get("sup") or {}).items():
    for _w, _dd in _wk.items():
        _names |= set(_dd.values())
# ⛔ ولا تُستثنى قيمُ «rot»: هي **أسماءُ فرق التخصص** («رياضيات واجتماعيات»)
#    تُعرض في الجدول وجدول الدوران — لا أسماءَ أعلامٍ. واستثناؤها أخرج الفرقَ
#    الأربعةَ من المعجم فبقيت عربيةً في ثمانِ شاشات.
_names |= set(DATA.get("complexlist") or []) | set(DATA.get("bands") or {})
# ⛔ ومن «bands» يُستثنى «stage» (اسمُ مدرسةٍ) وحدَه: «per» تسميةُ حصةٍ
#    تُعرض رأسَ عمودٍ («الحصة ١»)، و«time» وقتٌ تعالجه القاعدة. واستثناؤها
#    كلَّها أبقى رؤوسَ أعمدة الجدول عربيةً.
for _b in sum((DATA.get("bands") or {}).values(), []):
    _names.add(str(_b.get("stage") or ""))
_names |= {x for x in _data_strings if ".pdf" in x or ".json" in x}
_need = sorted({x for x in list(_ar_strings) + _data_strings
                if x and x.strip() and x not in _names})
i18n.guard(JS, extra=_need)
# ⛔ والمحميُّ يُعرض تسميةً وإن لم يُلَفّ: «الجميع» و«كل العمليات» قيمُ
#    مرشِّحاتٍ تُقارَن بالعربية **وتُعرض** خيارات — و`fld` يترجم التسمية
#    بـTR ويُبقي value. فتُحمَل ترجماتُها إلى الصفحة ولا يطلبها الحارس.
_prot = {k for k in i18n.protected(JS) if k in i18n.EN}
I18N = {k: i18n.EN[k] for k in set(_need) | _prot if k in i18n.EN}
JS = ("const I18N = " + json.dumps(I18N, ensure_ascii=False) + ";\n"
      + i18n.wrap(JS))
print("  ✓ الترجمة: %d مدخلاً في الصفحة · %d نصّاً مفحوصاً" % (len(I18N), len(_need)))

import icon as _ICO
page = (HTML.replace("__FONTS__", FONTCSS).replace("__CSS__", CSS)
            # ⛔ **ومسارُ الأيقونة يتبع موضعَ الملف لا يُفترض**: نسخةُ التجربة
            #    تُكتب في جذر التسليم فكان «‎../‎» يشير إلى خارجه — وأمسكه
            #    `icocheck` قبل النشر. فيُحسب من عمق المخرَج نفسِه.
            .replace("__ICON__", _ICO.head(_icorel(out)))
            .replace("__TRYBAR__",
                     ('<div id="trybar">\u26a0 \u0646\u0633\u062e\u0629\u064f '
                      '\u062a\u062c\u0631\u0628\u0629\u064d \u2014 '
                      '\u0628\u064a\u0627\u0646\u0627\u062a\u064f\u0647\u0627 '
                      '\u0645\u0646\u0641\u0635\u0644\u0629\u064c \u0648\u0644\u0627 '
                      '\u062a\u064f\u062d\u0633\u064e\u0628</div>') if TRY else "")
            .replace("__JS__", JS.replace("__SUBJFAM__", json.dumps(SUBJFAM, ensure_ascii=False))
                                 .replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
                                 .replace("__LOGO__", logo)))
with open(out, "w", encoding="utf-8") as f:
    f.write(page)
print("حُفظ:", os.path.basename(out), "|", len(DATA["phases"]), "مراحل |", len(DATA["roles"]), "أدوار |",
      sum(len(d["inds"]) for d in DATA["domains"]), "مؤشراً |",
      len(DATA["bank"]), "إستراتيجية |", round(len(page) / 1048576, 2), "م.ب")
