# -*- coding: utf-8 -*-
"""ترجمةُ منصة الحصة الموحَّدة إلى الإنجليزية — لمعلمي القطاع العالمي.

⛔ **القيدُ الحاكم: المخزنُ عربيٌّ إلى الأبد.** هويةُ الحصة مفتاحٌ مركَّب
   `القطاع|المجمع|المرحلة|الحصة|الأسبوع|اليوم|التخصص` كلُّه قيمٌ عربية. فلو
   تُرجمت هذه القيم لانفصلت كلُّ حصةٍ مسجَّلةٍ عن سجلّها، وصارت المنصةُ منصتين
   لا تريان بعضَهما — وهو نقيضُ «العمل مشتركاً». فالإنجليزيةُ **طبقةُ عرضٍ**:
   القيمةُ المحفوظةُ عربيةٌ، والتسميةُ المعروضةُ مترجَمة.

**والآلةُ هي آلةُ التأنيث نفسُها** (`femjs`): تُمسح النصوصُ العربيةُ المقتبسةُ
في الجافاسكربت وتُلَفُّ في `TR("…")`، فيُترجمها المحرّكُ عند العرض. ولا تُلَفُّ:
  1. ما كان مفتاحاً أو طرفَ مقارنةٍ (`=== "حذف"`) — ينكسر بالترجمة صامتاً.
  2. ما كان أولَ وسيطٍ لـ`logAct` — فذاك **يُخزَّن** ويُقرأ في اللغتين.
وهذان يُكشفان بالفحص لا بالعين: `KEYRX` من femjs، ونمطُ `logAct`.

⚠️ **وحارسُ الاكتمال:** كلُّ نصٍّ لُفَّ ولا ترجمةَ له يُفشل البناء ويُسمَّى —
   فلا تبقى كلمةٌ عربيةٌ في شاشةٍ إنجليزية دون أن يُعلم بها.

⚠️ **والأسماءُ لا تُترجَم** (قرارُ المستشار ٣٠ سبتمبر ٢٠٢٦): أسماءُ المعلمين
   والمدارس والمجمعات هويّاتٌ تُعرض كما كُتبت في اللغتين. وما يكتبه المستخدمُ
   في الخانات يبقى كما كتبه — عربياً كان أو إنجليزياً.
"""
import re

AR = r"[؀-ۿ]"
LIT = r'"((?:[^"\\\n]|\\.)*)"|\'((?:[^\'\\\n]|\\.)*)\''
# مفتاحٌ أو طرفُ مقارنة — من femjs حرفياً، فالخطرُ واحد
KEYRX = re.compile(r'(?:===|!==|==|!=)\s*"([^"]*[؀-ۿ][^"]*)"'
                   r'|\[\s*"([^"]*[؀-ۿ][^"]*)"\s*\]')
# ⛔ أولُ وسيطٍ لـ logAct يُخزَّن في السجلّ ويُقارن لاحقاً — لا يُترجَم
STORED = re.compile(r'logAct\(\s*"([^"]*[؀-ۿ][^"]*)"')
# ⛔ مفتاحُ كائنٍ حرفيٍّ: {"س": …} — ولفُّه يُخرج جافاسكربت غيرَ صحيح أصلاً،
#    وكشفه `node --check` في أول تجربة (خريطةُ أسماء المدارس القديمة OLDST).
# ⚠️ **والنقطتان وحدَهما لا تكفيان للحكم**: في الشرط الثلاثي
#    `cond ? "أ" : "ب"` تأتي «أ» قبل نقطتين أيضاً — فحُميت ثمانيةُ نصوصٍ
#    معروضةٍ خطأً (تسمياتُ تبويبات: «جدولي» و«جدول مدرستي» و«خطواتُ زيارتك»)
#    فبقيت عربيةً في الشاشة الإنجليزية ولم يطلبها الحارسُ لأنها «محميّة».
#    فمفتاحُ الكائن يُشترط فيه أن يسبقَه «{» أو «،» أو بدايةُ سطر.
OBJKEY = re.compile(r'(?:[{,]|^)\s*"([^"]*[؀-ۿ][^"]*)"\s*:', re.M)
# ⛔ وطرفُ switch — يُقارن كالمساواة
CASEK = re.compile(r'\bcase\s+"([^"]*[؀-ۿ][^"]*)"')
# ⛔ وبدلُ الاستبدال: `.replace(/ة/g, "ه")` تحويلُ حروفٍ لا تسميةٌ تُعرض.
#    لُفَّت «ا» و«ه» و«ي» فطلب الحارسُ ترجمةَ حرفٍ مفرد — وترجمتُها تكسر
#    التطبيعَ الذي يقوم عليه توزيعُ التحضير المستورَد.
REPLARG = re.compile(r'\.replace\([^,()]*(?:\([^()]*\))?[^,()]*,\s*"([^"]*[؀-ۿ][^"]*)"')


def protected(js):
    """النصوصُ التي تُمنع الترجمةُ عليها لأنها مفاتيحُ أو قيمٌ مخزَّنة."""
    out = set()
    for m in KEYRX.finditer(js):
        out.add(m.group(1) or m.group(2))
    for rx in (STORED, OBJKEY, CASEK, REPLARG):
        for m in rx.finditer(js):
            out.add(m.group(1))
    return out


def spans_protected(js):
    """مواضعُ النصوص المحميّة بعينها — فالنصُّ نفسُه قد يُعرض في موضعٍ آخر.

    ⚠️ «حذف» مفتاحٌ في `e.a === "حذف"` وتسميةُ زرٍّ في موضعٍ آخر. فلو مُنع
       بالنصِّ لبقي الزرُّ عربياً، ولو لُفَّ بالنصِّ لانكسرت المقارنة. فالمنعُ
       **بالموضع** لا بالنصّ.
    """
    bad = []
    # ⛔ **منطقةٌ محميةٌ بعلامةٍ صريحة**: نصُّ الأمر الذي يُنسخ إلى المساعد
    #    الذكيّ ليس تسميةً في الشاشة، بل رسالةٌ تُرسَل إلى نموذجٍ عربيٍّ عن
    #    منهجٍ سعوديّ — فلا تُترجَم ولا يُطلب لها مدخل. تُحاط بـ
    #    `/*@noi18n*/ … /*@/noi18n*/`. (٣٠ سبتمبر ٢٠٢٦)
    for m in re.finditer(r"/\*@noi18n\*/(.*?)/\*@/noi18n\*/", js, re.S):
        bad.append(m.span(1))
    for rx in (KEYRX, STORED, OBJKEY, CASEK, REPLARG):
        for m in rx.finditer(js):
            for g in (1, 2):
                try:
                    if m.group(g):
                        bad.append(m.span(g))
                except IndexError:
                    pass
    return bad


def wrap(js):
    """يلفُّ كلَّ نصٍّ عربيٍّ معروضٍ في t("…") — ويترك المحميَّ بموضعه."""
    bad = spans_protected(js)

    def inside(a, b):
        return any(a >= s - 1 and b <= e + 1 for s, e in bad)

    out, last = [], 0
    for m in re.finditer(LIT, js):
        t = m.group(1) if m.group(1) is not None else m.group(2)
        if not t or not re.search(AR, t):
            continue
        g = 1 if m.group(1) is not None else 2
        if inside(*m.span(g)):
            continue
        out.append(js[last:m.start()])
        out.append('TR(%s)' % js[m.start():m.end()])
        last = m.end()
    out.append(js[last:])
    return "".join(out)


def unesc(t):
    r"""⛔ يُفكُّ ترميزُ الجافاسكربت قبل المطابقة: المصدرُ يحمل «\n» حرفين،
       والمحرِّكُ يُعطي t() سطراً حقيقياً. فلو قِيس المعجمُ على المصدر خامًا
       لطُلبت مفاتيحُ لا تُستدعى قطُّ، وبقيت المستدعاةُ بلا ترجمة."""
    out, i = [], 0
    while i < len(t):
        c = t[i]
        if c == "\\" and i + 1 < len(t):
            n = t[i + 1]
            out.append({"n": "\n", "t": "\t", "r": "\r", "\\": "\\",
                        '"': '"', "'": "'"}.get(n, "\\" + n))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def wrapped_strings(js):
    """النصوصُ التي ستُلَفُّ فعلاً — وعليها يُقاس اكتمالُ المعجم."""
    bad = spans_protected(js)

    def inside(a, b):
        return any(a >= s - 1 and b <= e + 1 for s, e in bad)

    out = []
    for m in re.finditer(LIT, js):
        t = m.group(1) if m.group(1) is not None else m.group(2)
        if not t or not re.search(AR, t):
            continue
        g = 1 if m.group(1) is not None else 2
        if not inside(*m.span(g)):
            out.append(unesc(t))
    return sorted(set(out))


# ═════ قاعدةُ الأرقام والتواريخ والرموز — صورةُ enNum في المحرّك ═════
# ⛔ الحارسُ يجب أن يعرف القاعدةَ كما يعرف المعجم، وإلا طلب سبعين مدخلاً
#    لتواريخَ ورموزِ مؤشراتٍ تعالجها القاعدةُ أصلاً. والشاهدُ الحقيقيُّ واحد:
#    **ألّا يبقى حرفٌ عربيٌّ على شاشةٍ إنجليزية.**
_DIG = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_MONTHS = ["ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة",
           "ذو القعدة", "ذو الحجة", "محرم", "صفر", "رجب", "شعبان", "رمضان", "شوال",
           "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو",
           "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]


def by_rule(s):
    """ما تُخرجه القاعدةُ من النصّ — فإن خلا من العربية فالنصُّ مُعالَج."""
    out = s.translate(_DIG)
    for m in sorted(_MONTHS, key=len, reverse=True):
        out = out.replace(m, "M")
    out = re.sub(r"\s*هـ", " AH", out)
    out = re.sub(r"(\d)\s*م(?![؀-ۿ])", r"\1", out)
    out = re.sub(r"^إصدار\s", "Build ", out)
    return re.sub(r"(^|[\s·])م(?=\d)", r"\1D", out)


def covered(s):
    """مُغطّىً إن كان في المعجم، أو خلا من العربية بعد القاعدة."""
    return s in EN or not re.search(AR, by_rule(s))


def guard(js, extra=()):
    """⛔ يُفشل البناءَ على كل نصٍّ معروضٍ يبقى فيه عربيٌّ بالإنجليزية."""
    need = set(wrapped_strings(js)) | set(extra)
    miss = sorted(s for s in need if not covered(s))
    if miss:
        raise SystemExit(
            "⛔ %d نصّاً معروضاً بلا ترجمةٍ في i18n.EN:\n" % len(miss)
            + "\n".join('    %r: "",' % s for s in miss[:60])
            + ("\n    … و%d غيرها" % (len(miss) - 60) if len(miss) > 60 else "")
            + "\n\n  الشاشةُ الإنجليزيةُ لا تُسلَّم وفيها عربيّ. أضف الترجمةَ، أو\n"
              "  اضممِ النصَّ إلى المحميّ إن كان مفتاحاً لا تسمية، أو أضف قاعدةً\n"
              "  إن كان نمطاً متكرّراً (تاريخاً أو رمزَ مؤشرٍ) لا نصّاً مفرَداً.")
    return True


# ═════════════════════════════════════════════════════════════════
#  المعجم — الأصلُ العربيُّ مفتاحاً. ولا يُترجَم اسمُ علَمٍ ولا مدرسة.
# ═════════════════════════════════════════════════════════════════
EN = {}

# ═════════ ١) شُظايا ووصلات وأرقام ═════════
# ⚠️ الشُّظايا تُوصل في الشفرة («قبل » + العدد + « د»)، فترجمتُها تُراعي الوصل
#    والاتجاه: الإنجليزيةُ من اليسار، فما كان بادئةً في العربية قد يصير لاحقة.
EN.update({
    "؟": "?", "د": "m", "٪": "%", " د": " min", " س": " h", " و": " & ",
    "/٢": "/2", "/٣": "/3", "، ": ", ", "من": "of", " د)": " min)",
    " حصة": " lesson", " في ": " in ", " من ": " of ", "قبل ": "",
    "رصد ": "Observed ", "٪ · ": "% · ", "٪ — ": "% — ", " من ٤": " of 4",
    "٠١٢٣٤٥٦٧٨٩": "0123456789", " من ١٠٠": " of 100", " من 100 ← درجة المؤشر ":
    " of 100 → indicator score ", " من ١٠٠ ← درجة المؤشر ": " of 100 → indicator score ",
    "صدر: ": "Issued: ", "الحصة ": "Period ", "المجال ": "Domain ", "المرحلة ": "Stage ",
    "مرحلة ": "stage ", "تعديل ": "Edit ", "تقييم ": "Rating ", "فريق ": "Team ",
    "مجمع ": "Complex ", "اليوم: ": "Day: ", "الرصد ": "Observation ",
    "أقران ": "Peers ", "الأقران ": "Peers ", "غالباً ": "usually ",
    "رصدٌ ": "Observed ", "تراجع (": "Undo (", "سلّة المحذوفات (": "Trash (",
    "يغذّي ": "feeds ", "مصدرها: ": "Source: ", "الرقم الوظيفي ": "Staff no. ",
    "الرقم الوظيفي للزائر ": "Peer staff no. ", "المقيّم: ": "Observer: ",
    "زمن الحصة: ": "Lesson time: ", "الاستمارة: ": "Rubric: ", "الاستمارة:": "Rubric:",
    "| البطاقة: ": "| Card: ", "| لا ينطبق: ": "| N/A: ", "بطاقة الإستراتيجية: ":
    "Strategy card: ", " · مجمع ": " · Complex ", " صفاً · ": " rows · ",
    " — الزمن": " — time", " — مجمع ": " — Complex ", " (الفرق ": " (diff ",
    " عمود حصة": " period columns", " معتمدة ◆": " approved ◆", "معتمدة ◆": "Approved ◆",
    " مقيّماً رصد": " observers recorded", " حصة تخصّك": " lessons are yours",
    " والمطلوب ": " and required ", " يوماً": " days", " حصةً مجدولةً باسم معلمٍ":
    " lessons scheduled with a teacher", " بلا حصةٍ مسجَّلةٍ بعد": " with no lesson yet",
    " وخريطةُ الزمن ": " and the time map ", " — كان اعتمدها ": " — approved by ",
    " عملية · تُحفظ آخرُ ": " entries · keeping the latest ",
    " — داخلَه لا يُضافان إليه:": " — within it, not added to it:",
    ") — مرتَّبةً بالمرحلة:": ") — ordered by stage:",
    "إصدار التحضير — ينقصه ": "Issue plan — missing ",
    "خريطة الزمن — المجموع ": "Time map — total ",
    "أزمنةُ المراحل مجموعها ": "Stage times total ",
    "مجموع المراحل: ": "Stages total: ", "إجراء بطاقة الجسر: ": "Bridge action: ",
    "إجراء الزيارة السابقة: ": "Previous visit action: ",
    "صدر هذا التحضير في ": "This plan was issued on ",
    "عُرضت أحدثُ ٣٠٠ عملية من ": "Showing the latest 300 entries of ",
    "سيُكتب فوق ما أدخلتَه في: ": "This will overwrite your entries in: ",
    "نماذج معبّأة في تخصصك (": "Worked examples in your subject (",
    "هذه الحصة فيها ": "This lesson has ", "  (دخل باسم: ": "  (signed in as: ",
    "تعذّر الاتصال: ": "Connection failed: ",
    "تعذّر الاتصال بالخادم: ": "Could not reach the server: ",
    "تقريري — ": "My report — ", "سجلّ زياراتي — ": "My visit log — ",
    "تقرير زيارة صفية — ": "Classroom visit report — ",
    "صدر التحضير. ": "Plan issued. ", "\n\nأتُتابع؟": "\n\nContinue?",
    "✓ رُبط المخزن المشترك.\n": "✓ Shared store linked.\n",
})

# ═════════ ٢) الأدوار والأشخاص ═════════
EN.update({
    "معلم": "Teacher", "زائر": "Peer", "مقيّم": "Observer", "مدير": "Principal",
    "مشرف": "Supervisor", "وكيل": "Deputy", "مدير إشراف": "Head of Supervision",
    "مشرف المنصة": "Platform admin", "مدير المنصة": "Platform admin",
    "مديرُ المنصة": "Platform admin", "مستشارٌ ومديرُ المنصة": "Consultant & platform admin",
    "دخولُ المستشار": "Consultant sign-in",
    "دخول المستشار ومدير المنصة": "Consultant / platform admin sign-in",
    "المعلم القائم بالحصة": "Teaching teacher",
    "المعلم الزائر": "Peer teacher", "المعلم الزائر ١": "Peer teacher 1",
    "المعلم الزائر ٢": "Peer teacher 2", "الزائر ١": "Peer 1", "الزائر ٢": "Peer 2",
    "الزائران": "The two peers", "مدير المدرسة": "School principal",
    "الوكيل التعليمي": "Academic deputy", "المشرف التربوي المختص": "Subject supervisor",
    "المشرف المختص": "Subject supervisor", "المقيّم": "Observer",
    "المقيّمون": "Observers", "المقيّمون الثلاثة": "The three observers",
    "المعلم": "Teacher", "المعلمون": "Teachers", "الشخص": "Person",
    "الاسم": "Name", "الدور": "Role", "الصفة": "Capacity", "البريد": "Email",
    "كلمة المرور": "Password", "الرقم الوظيفي": "Staff number",
    "الرقم الوظيفي (اختياري)": "Staff number (optional)",
    "خروج": "Sign out", "دخول": "Sign in",
    "صفتك في هذه الزيارة": "Your capacity on this visit",
    "‹ رجوعٌ إلى اختيار الدور": "‹ Back to role selection",
})

# ═════════ ٣) أزرارٌ وأفعالٌ في الواجهة ═════════
EN.update({
    "اختر": "choose", "افتح": "Open", "املأ": "Fill", "حذف": "Delete",
    "تحديث": "Refresh", "تراجع": "Undo", "تغيير": "Change", "تفريغ": "Wipe",
    "طباعة": "Print", "استرداد": "Restore", "تصدير CSV": "Export CSV",
    "كيف": "How", "متى": "When", "كيف؟": "How?", " (كيف؟)": " (how?)",
    "الآن": "now", "تمّ": "done", "انسخ الرابط": "Copy link",
    "انسخ رابط الدعوة:": "Copy the invite link:",
    "اربط الخادم": "Link the server", "نزّل النسخة": "Download backup",
    "نسخة احتياطية": "Backup", "نسخةٌ احتياطية": "Backup",
    "تفريغ البيانات": "Wipe data", "تفريغُ البيانات": "Wipe data",
    "محوٌ نهائي": "Permanent erase", "مسحُ خانة": "Clear cell",
    "مسح خانة الحصة": "Clear lesson cell", "مسحُ هذه الخانة": "Clear this cell",
    "سجّلني هنا": "Register me here", "تسجيل الاسم": "Name registered",
    "تعديل الفصل": "Edit class", "تعديل الوقت": "Edit time",
    "تغيير الحصة": "Change lesson", "ابدأ الحصة ←": "Start lesson →",
    "إغلاق الحصة": "Close lesson", "إصدار التحضير ✓": "Issue plan ✓",
    "فكُّ الاعتماد": "Unlock approval", "حفظ البطاقة": "Save card",
    "اعتماد النتيجة وقفل الحصة": "Approve result and lock the lesson",
    "طباعة التقرير": "Print report", "طباعة السجل": "Print log",
    "اطبع تقريري": "Print my report", "اطبع سجلّي": "Print my log",
    "اطبع الخطة": "Print plan", "اطبع ورقة التنفيذ": "Print the run sheet",
    # ⛔ القراراتُ التربويةُ الخمسة — التوأمةُ وسقفُ «لا ينطبق» ومصدرُ م٢·٣
    #    وأرضيّةُ ٢٥٪ وأوزانُ المجالات (١ أكتوبر ٢٠٢٦)
    "بالمشاهدة وحدَها": "Observation only",
    " — لا شاهدَ له في التحضير، فالأداءُ لا يُكتب قبل الحصة":
        " — it has no evidence in the lesson plan; performance is not written before the lesson",
    "من سجلّ المعلم": "From the teacher\u2019s records",
    " — يُتحقَّق من سجلّ التخطيط والتوزيع الزمني لا من خانة":
        " — verified against the planning record and the curriculum timetable, not a form field",
    "لم يُكتب في التحضير": "Not written in the lesson plan",
    " — خانتُه: ": " — its field: ",
    "ولم يُكتب: ": "Left blank: ",
    "تُحسب من البطاقة": "Computed from the card",
    " — درجتُه تنزل من «بطاقة تشخيص الإستراتيجية» أدناه، ولا تُرصد هنا":
        " — its mark comes from the strategy diagnosis card below and is not rated here",
    "سببُ «لا ينطبق»": "Reason for “not applicable”",
    "للاستثناء الحقيقي لا للهروب — والسقفُ عشرةُ مؤشرات":
        "For a genuine exception, not an escape — the cap is ten indicators",
    "أيُّ المؤشرات ولماذا لا تنطبق على هذه الحصة":
        "Which indicators, and why they do not apply to this lesson",
    "مثال: م٥·١ و٥·٣ — الحصةُ في ملعبٍ بلا سبورةٍ ذكية ولا أجهزة.":
        "Example: 5.1 and 5.3 — the lesson is on a field with no smart board and no devices.",
    "«لا ينطبق» في ": "“Not applicable” on ",
    " مؤشراً — والسقفُ ": " indicators — the cap is ",
    " (خُمسُ الاستمارة). راجع رصدَك.": " (a fifth of the form). Review your rating.",
    "اكتب سببَ «لا ينطبق» في ": "Write the reason for “not applicable” on ",
    " مؤشراً — بلا سببٍ لا تُعتمد النتيجة.": " indicators — without a reason the result cannot be approved.",
    "⛔ لا تُعتمد النتيجةُ بعد:\n\n": "⛔ The result cannot be approved yet:\n\n",
    "\n\nيفتح كلُّ مقيّمٍ استمارتَه ويكتب السبب.":
        "\n\nEach evaluator opens their own form and writes the reason.",
    "⛔ «لا ينطبق» بلا سببٍ أو فوق السقف — ولا تُعتمد النتيجةُ قبل علاجه: ":
        "⛔ “Not applicable” with no reason or above the cap — the result cannot be approved until this is fixed: ",
    "| على مدى ٢٥–١٠٠: ": "| on the 25–100 range: ",
    "على مدى ٢٥–١٠٠": "On the 25–100 range",
    "أضعفُ مجال": "Weakest domain",
    "النسبةُ الرسميةُ من ٢٠٠ درجة، وأرضيّتُها ٢٥٪ لأن أضعفَ تقديرٍ درجةٌ من أربع — ":
        "The official percentage is out of 200 marks, and its floor is 25% because the weakest rating is one mark out of four — ",
    "فعمودُ «على مدى ٢٥–١٠٠» يُظهر الموقعَ الحقيقي بين الأضعفِ والأتمّ. ":
        "so the “on the 25–100 range” column shows the true position between the weakest and the fullest. ",
    "والمجالاتُ متساويةُ الوزن (أربعُ درجاتٍ لكل مؤشر) كما في الاستمارة الرسمية، ":
        "Domains carry equal weight (four marks per indicator) as in the official form, ",
    "ولذلك يُسمَّى أضعفُ مجالٍ صريحاً فلا يختفي في المجموع.":
        "and so the weakest domain is named explicitly rather than hidden in the total.",
    # ⛔ مساحةُ «طريقة التحضير» الثلاثية ومساحةُ الاطّلاع بقسمَيها (١ أكتوبر ٢٠٢٦)
    # ⛔ ما تُرك بلا شاهدٍ مخطَّط — بالعدد والدرجة (١ أكتوبر ٢٠٢٦)
    "صدر — ومعه ": "Issued — and with it ",
    " خانةً ذاتَ مؤشرٍ تركتَها فارغة: ": " indicator-bearing fields you left empty: ",
    " مؤشراً (": " indicators (",
    " درجةً من ٢٠٠) يبحث الزائرُ عن شاهدها ولا يجده في تحضيرك.":
        " marks out of 200) whose evidence the visitor will look for and not find in your plan.",
    " — واترك ما لا ينطبق على حصتك فعلاً، فالشاهدُ الكاذبُ أسوأُ من الفراغ.":
        " — and leave out whatever genuinely does not apply to your lesson: false evidence is worse than a blank.",
    # ⛔ مصادقةُ المخزن المشترك — كان العقدُ بلا مفتاحٍ البتّة (١ أكتوبر ٢٠٢٦)
    # ⛔ جدارُ التخزين: إنذارٌ قبله لا بعده (١ أكتوبر ٢٠٢٦)
    "مساحةُ هذا الجهاز تقارب الامتلاء (": "This device\u2019s storage is nearly full (",
    " م.ب من ": " MB of ",
    ") — أفرغ سلّةَ المحذوفات أو خذ نسخةً احتياطية":
        ") — empty the recycle bin or take a backup",
    "⛔ امتلأت مساحةُ هذا المتصفّح، فلم يُحفظ آخرُ تغييرٍ على الجهاز.\n\n":
        "⛔ This browser\u2019s storage is full, so the last change was not saved on the device.\n\n",
    "وما كُتب قبله سليم. والعلاج:\n": "Everything written before it is intact. To fix it:\n",
    "• أفرغ سلّةَ المحذوفات (أدوات المستشار ← السجلّ والاسترداد)\n":
        "• Empty the recycle bin (Consultant tools → Log and recovery)\n",
    "• أو خذ نسخةً احتياطيةً ثم فرّغ البيانات\n\n":
        "• Or take a backup and then clear the data\n\n",
    "ومخزنُك المشترك مربوطٌ — فبياناتُك فيه سليمة.":
        "Your shared store is connected, so your data there is intact.",
    "⚠️ ولا مخزنَ مشتركٌ مربوط — فاربطه قبل أن يضيع شيء.":
        "⚠️ No shared store is connected — connect one before anything is lost.",
    # ⛔ شواهدُ م٢·٣ — الجمعُ بين الاستمارة ودليل المستويات (١ أكتوبر ٢٠٢٦)
    "شواهدُ م٢·٣ من دليل مستويات الأداء — ":
        "Evidence for 2.3 from the performance-levels guide — ",
    "تنوّع الإستراتيجيات والتعلم النشط": "Varied strategies and active learning",
    "إستراتيجيتان فأكثر في الحصة": "Two or more strategies in the lesson",
    "إحداها: استقصاء أو تعاوني أو مشروعات":
        "One of them: inquiry, cooperative or project-based",
    "الطلاب يعملون فعلياً لا يستمعون فقط": "Students actually work, not merely listen",
    "زمن عمل الطلاب يفوق زمن كلام المعلم (٧٠ مقابل ٣٠)":
        "Student working time exceeds teacher talking time (70 to 30)",
    "ولا يُعدُّ شاهداً: ": "Not counted as evidence: ",
    "شرح المعلم ثم أسئلة للطلاب": "The teacher explains, then asks the students questions",
    " — ودرجةُ المؤشر تنزل من هذه البطاقة وحدَها، وهذه شواهدُ ما تملؤه.":
        " — the indicator\u2019s mark comes from this card alone; these are the evidence for what you fill in.",
    # ⛔ المجالُ ٣ صار له قسمُه في التحضير بعد أن كان بلا خانة (١ أكتوبر ٢٠٢٦)
    "المجال ٢": "Domain 2",
    "المجال ٣": "Domain 3",
    "مشاركة المتعلمين واندماجهم — يُرصد على الطالب، فخطّط له":
        "Learner participation and engagement — rated on the student, so plan for it",
    "ما سيقوله المتعلم ويفعله": "What the learner will say and do",
    "أفعالٌ تُرى وتُسمع: يصوغ · يناقش · يسأل · يعرض — لا «يستمع» ولا «ينتبه»":
        "Actions that are seen and heard: formulates · discusses · asks · presents — not “listens” or “pays attention”",
    "اكتب في عمود المتعلم فعلاً يُرى (يكتب · يناقش · يقيس) لا «يستمع»؛ فالمشاركة تُرصد على الطالب.":
        "In the learner column write an action that can be seen (writes · discusses · measures), not “listens”; participation is rated on the student.",
    # ⚠️ وصيغةُ البنات لها مفاتيحُها — والمعجمُ يُفحص ببناء الجنسين
    "أفعالٌ تُرى وتُسمع: تصوغ · تناقش · تسأل · تعرض — لا «تستمع» ولا «تنتبه»":
        "Actions that are seen and heard: formulates · discusses · asks · presents — not “listens” or “pays attention”",
    "من تبدأ، وكيف تُشرَك من لم تشارك، وتوزيعُ الأدوار بالأسماء":
        "Who starts, how those who have not taken part are brought in, and roles assigned by name",
    "ما ستقوله المتعلمة وتفعله": "What the learner will say and do",
    "مشاركة المتعلمات واندماجهن — تُرصد على الطالبة، فخطّطي لها":
        "Learner participation and engagement — rated on the student, so plan for it",
    "عدالة المشاركة": "Fairness of participation",
    "من يبدأ، وكيف يُشرَك من لم يشارك، وتوزيعُ الأدوار بالأسماء":
        "Who starts, how those who have not taken part are brought in, and roles assigned by name",
    "العمل التعاوني وقواعد الحوار": "Cooperative work and ground rules for dialogue",
    "كيف يعمل الطلاب معاً، وقاعدةُ الحوار المعلنة: تقبّل الرأي والمبادرة بالدعم":
        "How the students work together, and the stated rule for dialogue: accept the other view and offer help",
    "مفتاح المخزن": "Store key",
    "✓ ضُبط المفتاح.\n\nانسخ رابطَ الدعوة وأرسله من جديدٍ ليحمله إلى الأجهزة.":
        "✓ The key is set.\n\nCopy the invitation link and send it again so it carries the key to the devices.",
    "مضبوطٌ — ": "Set — ",
    " حرفاً · ويُرسَل مع كل طلب": " characters · sent with every request",
    "⚠️ غيرُ مضبوط — من يعرف عنوانَ الخادم يقرأ ويكتب ويمحو":
        "⚠️ Not set — anyone who knows the server address can read, write and erase",
    "اضبط المفتاح": "Set the key",
    "تدوير": "Rotate",
    "تدويرٌ": "rotated",
    "ضبطٌ أول": "first set",
    "ضبط مفتاح المخزن": "Store key set",
    "مفتاحُ المخزن المشترك — يُرسَل مع كل طلبٍ إلى الخادم.\n\n":
        "The shared-store key — sent with every request to the server.\n\n",
    "اكتب مفتاحاً طويلاً (٢٤ حرفاً فأكثر) لا يُخمَّن، أو اتركه فارغاً لتوليد واحد.\n":
        "Enter a long key (24 characters or more) that cannot be guessed, or leave it blank to generate one.\n",
    "\n⚠️ وتدويرُه يقطع الأجهزةَ التي تحمل القديمَ حتى يصلها رابطُ دعوةٍ جديد.\n":
        "\n⚠️ Rotating it cuts off devices holding the old key until a new invitation link reaches them.\n",
    "\n⚠️ ولا يعمل حتى يفحصه الخادمُ — راجع دليلَ الاستضافة.":
        "\n⚠️ It has no effect until the server checks it — see the hosting guide.",
    "⛔ المفتاحُ قصير: ": "⛔ The key is too short: ",
    " حرفاً، والأدنى ٢٤.": " characters; the minimum is 24.",
    "يُرسَل للمدرسة فيُربط جهازُ من يفتحه تلقائياً — ويحمل المفتاح":
        "Sent to the school; whoever opens it has their device connected automatically — and it carries the key",
    "استجاب ولم يُرجع ما كُتب فيه — راجع إعدادَ الخادم.":
        "It responded but did not return what was written — check the server setup.",
    "طريقة التحضير": "How to prepare",
    "اختر حصتك من القائمة أعلاه — فمساحةُ صياغة الأمر تُبنى من درسك وإستراتيجيتك.":
        "Choose your lesson from the list above — the prompt area is built from your lesson and your strategy.",
    "اختر طريقتك — والنموذجُ الإلكترونيُّ أسفلَها في الحالتين":
        "Choose your route — the electronic form appears below it either way",
    "القالب الورقي": "Paper template",
    "تُنزّله وتكتبه بيدك — وورد أو PDF للطباعة":
        "Download and fill it by hand — Word, or PDF to print",
    "التحضير الإلكتروني": "Electronic plan",
    "تملأ الخانات هنا في المنصة، ويُحفظ ويُطبع ويُنزَّل":
        "Fill the fields here in the platform; it saves, prints and downloads",
    "التحضير بالذكاء الاصطناعي": "Plan with AI",
    "تنسخ الأمرَ، تُلصقه في المساعد خارج المنصة، ثم تُلصق جوابَه هنا فتُملأ الخانات":
        "Copy the prompt, paste it into an assistant outside the platform, then paste its "
        "answer here and the fields fill themselves",
    "نزّل القالبَ واكتبه بيدك": "Download the template and fill it by hand",
    "وإن أردتَ أن يُرصد تحضيرُك في المنصة فأدخِله بعد ذلك في «التحضير الإلكتروني» — ":
        "If you want your plan recorded in the platform, enter it afterwards under "
        "“Electronic plan” — ",
    "أو ارفع ملفَ وورد في «التحضير بالذكاء الاصطناعي» فيُوزَّع على الخانات.":
        "or upload a Word file under “Plan with AI” and it is distributed across the fields.",
    "اخترتَ القالبَ الورقي — فخاناتُ التحضير الإلكتروني مطويّةٌ الآن. ":
        "You chose the paper template, so the electronic fields are folded away. ",
    "اختر «التحضير الإلكتروني» أعلاه لتظهر.": "Choose “Electronic plan” above to show them.",
    "القالب الورقي للتحضير (وورد — يُكتب فيه)":
        "Paper lesson-plan template (Word — writable)",
    "للاطّلاع قبل التحضير": "To read before you prepare",
    "نماذجُ في تخصصك · ونشراتٌ تشرح النموذجَ والإستراتيجيات والاتجاهات":
        "Models in your subject · and bulletins explaining the form, the strategies and the approaches",
    "نماذج تحضير للاطّلاع عليها وفق تخصصك":
        "Lesson plans to read, matched to your subject",
    "تخصصك: ": "Your subject: ",
    " — نماذجُ معبّأةٌ تُحاكي طريقةَ التحضير، مرتَّبةً بالمرحلة":
        " — completed models showing how to prepare, ordered by stage",
    "النماذجُ المعبّأةُ تُعرض للمعلم القائم بالحصة وفق تخصصه.":
        "Completed models are shown to the teacher giving the lesson, matched to their subject.",
    "لا نموذجَ معبّأٌ في تخصصك بعد — واطّلع على النشرات أدناه.":
        "No completed model in your subject yet — read the bulletins below.",
    "نشرات للاطّلاع عليها قبل التحضير": "Bulletins to read before you prepare",
    "شرحُ نموذج التحضير · بنكُ بطاقات الإستراتيجيات · شرحُ الاتجاهات التدريسية":
        "How the lesson-plan form works · the strategy-card bank · how the teaching approaches work",
    # ⛔ شريطُ الحفظ والطباعة والتنزيل في كل شاشةِ إدخال (١ أكتوبر ٢٠٢٦)
    "حفظ": "Save",
    "تنزيل الملف": "Download the file",
    "الحفظُ تلقائيٌّ أيضاً — والزرُّ يؤكّده ويرسله فوراً":
        "Saving is automatic as well — this button confirms it and sends it at once",
    "حُفظ على هذا الجهاز — ولا مخزنَ مشتركاً مربوطاً":
        "Saved on this device — no shared store is connected",
    "حُفظ على جهازك — وسيُرسَل عند عودة الشبكة":
        "Saved on your device — it will be sent when the network returns",
    "نزل الملفُّ على جهازك: ": "The file was downloaded to your device: ",
    "صفحة": "Page",
    # ⛔ الصفحةُ لا تُقفل صامتةً: السببُ يُقال ويُعطى مخرَج (١ أكتوبر ٢٠٢٦)
    "⛔ التحضيرُ مقفولٌ لأن هذه الحصةَ ليست باسمك. ":
        "⛔ The plan is locked because this lesson is not in your name. ",
    "ولا يُحضَّر عن معلمٍ غيرِه — فالتحضيرُ شاهدُ صاحبه.":
        "No one prepares on another teacher\u2019s behalf — the plan is its author\u2019s own evidence.",
    "هذه الحصةُ مسجَّلةٌ باسم «": "This lesson is recorded under the name “",
    "» وأنت داخلٌ باسم «": "” and you are signed in as “",
    "هذه الحصةُ مسجَّلةٌ بالرقم الوظيفي ": "This lesson is recorded under staff number ",
    " وأنت داخلٌ بالرقم ": " and you are signed in with number ",
    "خانةُ المعلم في هذه الحصة فارغة.": "The teacher field on this lesson is empty.",
    "هذه حصتي — صحِّح الاسمَ إلى اسمي": "This is my lesson — correct the name to mine",
    "ستُسجَّل هذه الحصةُ باسمك: ": "This lesson will be recorded in your name: ",
    "ويُسجَّل التغييرُ في سجلّ العمليات باسمك وتاريخه. أتُتابع؟":
        "The change is written to the activity log with your name and the date. Continue?",
    "تصحيح اسم المعلم": "Teacher name corrected",
    "كانت باسم ": "was under ",
    " وصارت باسم ": " and is now under ",
    # ⛔ كشفُ المعلمين صار يُرفع إلى المخزن ولا يُضمَّن في الصفحة (١ أكتوبر ٢٠٢٦)
    "كشفُ المعلمين": "Teacher roster",
    "حالُ الكشف": "Roster status",
    "ارفع الكشف": "Upload the roster",
    "محمَّلٌ — ": "Loaded — ",
    " معلماً": " teachers",
    " معلماً.": " teachers.",
    "غيرُ محمَّل — الدخولُ بالاسم كتابةً": "Not loaded — sign in by typing your name",
    "به يُعرف الاسمُ والتخصصُ والمجمعُ من الرقم الوظيفي":
        "From the staff number it identifies the name, the subject and the complex",
    "⚠️ بلا كشفٍ لا يعمل تقريرُ «من لم يُدخِل حصته» ولا الاستدعاءُ بالرقم":
        "⚠️ Without a roster, the “who has not entered a lesson” report and lookup by number do not work",
    "⛔ اربط المخزنَ المشترك أولاً — الكشفُ يُرفع إليه لا إلى الجهاز.":
        "⛔ Connect the shared store first — the roster is uploaded to it, not to this device.",
    "⛔ الملفُّ ليس JSON سليماً: ": "⛔ The file is not valid JSON: ",
    "الملفُّ ليس كشفاً — يُتوقَّع كائنٌ مفاتيحُه الأرقامُ الوظيفية.":
        "This file is not a roster — an object keyed by staff numbers is expected.",
    "الكشفُ خالٍ.": "The roster is empty.",
    "مفاتيحُ غيرُ رقمية: ": "Non-numeric keys: ",
    "سطورٌ بلا اسم: ": "Rows with no name: ",
    "موادُّ لا تعرفها المنصة: ": "Subjects the platform does not know: ",
    "\n\nراجع مديرَ التخطيط والاعتماد المدرسي قبل الرفع.":
        "\n\nConsult the Director of Planning and School Accreditation before uploading.",
    "⛔ لم يُرفع الكشف.\n\n": "⛔ The roster was not uploaded.\n\n",
    "رفعُ كشفِ ": "Uploading a roster of ",
    " معلماً إلى المخزن المشترك.\n\n": " teachers to the shared store.\n\n",
    "يحلُّ محلَّ الكشف القائم، ويراه كلُّ من فتح المنصةَ بعد ربطِ الخادم.\n\n":
        "It replaces the current roster, and everyone who opens the platform with the server connected sees it.\n\n",
    "أتُتابع؟": "Continue?",
    "⛔ لم يستجب الخادمُ للرفع.": "⛔ The server did not respond to the upload.",
    "✓ رُفع الكشف: ": "✓ Roster uploaded: ",
    "رفع كشف المعلمين": "Teacher roster uploaded",
    "افتح الكشف": "Open the roster", "افتح الجدول": "Open the schedule",
    "افتح السجلّ": "Open the log", "افتح السلّة": "Open the trash",
    "افتح التحضير كاملاً": "Open the full plan",
    "افتح تقرير التفعيل": "Open the activation report",
    "افتح تقرير المدرسة": "Open the school report",
    "أعد الضخّ من الجدول": "Re-pull from the schedule",
    "إرسال للمعلم عبر واتساب": "Send to the teacher on WhatsApp",
    "أسنِدهما": "Assign both", "رابط الدعوة": "Invite link",
    "اذهب إلى الأسبوع الجاري": "Go to the current week",
    "زيارتي اليوم": "My visit today",
    "طيُّ الشريط لتوسيع الجدول": "Collapse the sidebar to widen the grid",
    "إظهار كل التلميحات": "Show all hints",
    "اختر الحصة": "Choose the lesson",
    "اختر الحصة التي ترصدها": "Choose the lesson you are observing",
    "اختر الحصة التي تحضّر لها": "Choose the lesson you are planning",
    "اختر حصتك من الجدول.": "Choose your lesson from the schedule.",
    # ⛔ اسمُ المادةِ يُكتب في الخانة — لرياض الأطفال خاصّةً (١ أكتوبر ٢٠٢٦)
    # ⛔ **الترجمةُ كانت كاملةً على ٢٧ شاشةً من ٢٠٢** — ونسخةُ البنات لها
    #    صيغُها المؤنَّثةُ التي لا مفتاحَ لها في المعجم. (١ أكتوبر ٢٠٢٦)
    "لسريعات التعلم والموهوبات — تنمّي تفكيراً أعلى لا مزيداً من التمارين":
        "For fast learners and the gifted — it grows higher thinking, not more exercises",
    "مثال أو تطبيق من حياة الطالبات": "An example or application from the students\u2019 own lives",
    "كيف تعمل الطالبات معاً، وقاعدةُ الحوار المعلنة: تقبّل الرأي والمبادرة بالدعم":
        "How the students work together, and the stated rule for dialogue: accept the other view and offer help",
    "اللحظة التي توظّف فيها الطالبة الملاحظة لتحسين عملها":
        "The moment the student uses the feedback to improve her work",
    "بناء شخصية الطالبة": "Building the student\u2019s character",
    # ⚠️ وصيغُ البنات من شواهد م٢·٣ — يولّدها المؤنِّثُ فلا مفتاحَ لها إلا بكتابته
    "الطالبات يعملن فعلياً لا يستمعن فقط": "Students actually work, not merely listen",
    "زمن عمل الطالبات يفوق زمن كلام المعلمة (٧٠ مقابل ٣٠)":
        "Student working time exceeds teacher talking time (70 to 30)",
    "شرح المعلمة ثم أسئلة للطالبات": "The teacher explains, then asks the students questions",
    # ⛔ رحلةُ الوكيل التعليمي: الحذفُ محروسٌ بالنطاق · وما يقع عليه يُعلَن
    #    · وتقريرُ الإدخال يقيس نطاقَه لا المنظومة (١ أكتوبر ٢٠٢٦)
    "⛔ لم تُحذف: ": "⛔ Not deleted: ",
    "لم تُوجد هذه الحصة.": "This lesson was not found.",
    "هذه الحصةُ معتمدةٌ ومقفولة — يُفكّ اعتمادُها أولاً.":
        "This lesson is approved and locked — its approval must be lifted first.",
    "هذه الحصةُ ليست باسمك.": "This lesson is not in your name.",
    "الحذفُ ليس من صلاحيتك.": "Deleting is not within your permissions.",
    "هذه الحصةُ خارجَ نطاقك.": "This lesson is outside your scope.",
    "⛔ هذه الحصةُ خارجَ نطاقك.": "⛔ This lesson is outside your scope.",
    "محوٌ نهائي": "Permanent purge",
    "للاطّلاع": "View only",
    "محتوى الشاشة": "Screen content",
    "⛔ الاستردادُ ليس من صلاحيتك هنا.": "⛔ Restoring is not within your permissions here.",
    "اختر القطاع والمجمع، ثم رشِّح الأعمدة بمدرستك من المربّعات — "
    "ومن دخل مديراً أو وكيلاً فمدرستُه مثبَّتةٌ عليه. "
    "ثم تخصصك إن كنت معلماً.":
        "Choose the sector and the complex, then filter the columns by your school using the "
        "checkboxes — and whoever signed in as a principal or a deputy has their school fixed "
        "for them. Then your subject, if you are a teacher.",
    "اختاري القطاع والمجمع، ثم رشِّحي الأعمدة بمدرستك من المربّعات — "
    "ومن دخلت مديرةً أو وكيلةً فمدرستُها مثبَّتةٌ عليها. "
    "ثم تخصصك إن كنتِ معلمةً.":
        "Choose the sector and the complex, then filter the columns by your school using the "
        "checkboxes — and whoever signed in as a principal or a deputy has their school fixed "
        "for them. Then your subject, if you are a teacher.",
    "⛔ المحوُ النهائيُّ ليس من صلاحيتك هنا.": "⛔ Permanent purge is not within your permissions here.",
    "فريقُ متابعة التقويم الداخلي: متابعةٌ لا حذف.":
        "Internal evaluation follow-up team: follow-up, not deletion.",
    "عليكِ — لا مشرفةَ لتخصصها": "Yours — its subject has no supervisor",
    "عليكِ — مشرفتُها قد لا تحضر": "Yours — its supervisor may not attend",
    "لا مشرفةَ مختصةً لهذا التخصص في هذه المدرسة، فالرصدُ على الفريق المعاون — وأنتِ منه.":
        "No subject supervisor for this subject in this school, so observing falls to the "
        "supporting team — and you are part of it.",
    "لهذه الحصة مشرفٌ مختصٌّ لا يحضر كلَّ حصة، فالرصدُ على مدير المدرسة ووكيله بذات المدرسة.":
        "This lesson has a subject supervisor who does not attend every lesson, so observing "
        "falls to the principal and the deputy of the same school.",
    "لهذه الحصة مشرفةٌ مختصةٌ لا تحضر كلَّ حصة، فالرصدُ على مديرة المدرسة ووكيلتها بذات المدرسة.":
        "This lesson has a subject supervisor who does not attend every lesson, so observing "
        "falls to the principal and the deputy of the same school.",
    "عليك — مشرفُها قد لا يحضر": "Yours — its supervisor may not attend",
    "لهذه الحصة مشرفٌ مختصٌّ لا يحضر كلَّ حصة، فالرصدُ على مدير المدرسة ووكيلها بذات المدرسة.":
        "This lesson has a subject supervisor who does not attend every lesson, so observing "
        "falls to the principal and the deputy of the same school.",
    "عليك — لا مشرفَ لتخصصها": "Yours — its subject has no supervisor",
    "لا مشرفَ مختصٌّ لهذا التخصص في هذه المدرسة، فالرصدُ على الفريق المعاون — وأنت منه.":
        "No subject supervisor for this subject in this school, so observing falls to the "
        "supporting team — and you are part of it.",
    " · منها ": " · of which ",
    " عليك (لا مشرفَ لتخصصها)": " are yours (their subject has no supervisor)",
    "حصصٌ عليك": "Lessons that fall to you",
    " حصةً تنتظر رصدَك": " lessons await your observation",
    "رصدتَ ما عليك كلَّه ✓": "You have observed everything that falls to you ✓",
    "لا حصةَ بلا مشرفٍ مختصٍّ في نطاقك":
        "No lesson in your scope lacks a subject supervisor",
    "وهي الحصصُ التي لا مشرفَ لتخصصها — ولولا الفريق المعاون لبقيت بلا تقييم.":
        "These are the lessons whose subject has no supervisor — without the supporting "
        "team they would go unrated.",
    "المقياسُ على نطاقك: ": "Measured against your scope: ",
    "المنظومة كلُّها": "the whole system",
    " — ومن لا تخصصَ تعليميٌّ له في الكشف لا يُنتظر منه تسجيلُ حصة.":
        " — and anyone with no taught subject on the roster is not expected to register a lesson.",
    " بلا حصةٍ مسجَّلةٍ بعد — ": " with no lesson registered yet — ",
    "حسناً": "OK",   # زرُّ النافذة الموحَّدة — بديلِ alert الأصلية
    # ⛔ أزرارُ النوافذ الموحَّدة — كلُّ فعلٍ باسمه لا «موافق» (١ أكتوبر ٢٠٢٦)
    "إلغاء": "Cancel",
    "متابعة": "Continue",
    "القيمة": "Value",
    "اعتمدها": "Approve it",
    "فُكَّ الاعتماد": "Lift the approval",
    "ارفعه": "Upload it",
    "سجّلها باسمي": "Register it in my name",
    "احذفها": "Delete it",
    "امحُها نهائياً": "Purge it permanently",
    "امسحها": "Clear it",
    "أعِد الضخّ": "Re-inject",
    "وزّعها": "Distribute them",
    "استبدِله": "Replace it",
    "أفهم — تابِع": "I understand — continue",
    "حذفُ هذه الحصة وكلِّ ما عُلِّق بها؟\n\n":
        "Delete this lesson and everything attached to it?\n\n",
    "تُنقل إلى سلّة المحذوفات وتُستردُّ منها ثلاثين يوماً.":
        "It moves to the recycle bin and can be restored from it for thirty days.",
    "محوٌ نهائيٌّ لا يُستردُّ بعده. أتُتابع؟":
        "A permanent purge with no recovery afterwards. Continue?",
    "⛔ رقمٌ غير صحيح.": "⛔ Not a valid number.",
    "✓ أُدخل ": "✓ Entered ",
    "اسم المادة (": "Subject name (",
    "تعديل المادة": "Subject edited",
    "اختر دورك": "Choose your role",   # تسميةُ مجموعة الاختيار لقارئ الشاشة
    "اختر دورك أولاً.": "Choose your role first.",
    "اختر تخصصك لتظهر خطتك": "Choose your subject to see your plan",
    "اكتب اسمك — به تُعرف حصصك.": "Enter your name — your lessons are matched by it.",
    "اكتب البريد وكلمة المرور.": "Enter the email and password.",
    "ابحث باسم معلمٍ أو فصل": "Search by teacher or class",
    "بحثٌ في الجدول": "Search the schedule",
    "للتأكيد اكتب كلمة:  تفريغ": "To confirm, type the word:  تفريغ",
    "⚠️ الأخيرُ لا يُستردّ": "⚠️ The last one cannot be restored",
})

# ═════════ ٤) الشاشاتُ والمراحلُ والتبويبات ═════════
EN.update({
    "منصة الحصة الموحَّدة": "Unified Lesson Platform",
    "نظام الحصة الموحَّدة": "Unified Lesson System",
    "اختر دورك — ولكل دورٍ ما يخصّه فقط":
        "Choose your role — each role sees only what concerns it",
    "مراحل التطبيق": "Programme stages", "المراحل": "Stages",
    "ما يفعله كلٌّ في كل مرحلة": "What each role does at each stage",
    "الاستعداد والتحضير": "Preparation and planning",
    "ما يُعدّه المعلم قبل الحصة": "What the teacher prepares before the lesson",
    "تنفيذ الحصة": "Running the lesson",
    "ورقةُ التنفيذ": "The run sheet",
    "رصد الحصة": "Lesson observation",
    "ما يُملأ أثناء الحصة ولها": "What is filled during and for the lesson",
    "بعد الحصة": "After the lesson",
    "تحضيرُ المعلم": "The teacher's plan",
    "تحضيرُ زميلك": "Your colleague's plan",
    "اقرأه قبل دخولِ الفصل": "Read it before entering the classroom",
    "بطاقةُ الزيارة": "Visit card", "إجراؤك أنت": "Your own action",
    "تقريري": "My report", "التقارير": "Reports",
    "لوحة المدرسة والتقارير": "School dashboard and reports",
    "تقارير التفعيل والنتائج": "Activation and results reports",
    "لوحةُ المنظومة": "System dashboard", "حالُ المنظومة": "System status",
    "ما يحتاج تدخّلك": "Needs your attention",
    "آخرُ ما جرى": "Latest activity",
    "أدواتُ المنصة": "Platform tools", "أدواتُ الحصة": "Lesson tools",
    "الجدول والإسناد": "Schedule and assignment",
    "جدول التعبئة": "Entry grid", "جدول المجمع": "Complex schedule",
    "زياراتي المسنَدة": "My assigned visits",
    "خطة زياراتي": "My visit plan", "خطة الزيارات": "Visit plan",
    "أين أزور — جدول المشرفين": "Where I visit — supervisor rota",
    "جدول زيارات المشرفين": "Supervisor visit rota",
    "جدول زيارات المجمعات": "Complex visit rota",
    "إسناد الزائرين": "Assign peers",
    "إسناد المعلمين الزائرين": "Assign peer teachers",
    "سجلّ العمليات": "Activity log", "سلّة المحذوفات": "Trash",
    "الحصة المفتوحة": "Open lesson", "بيانات الحصة": "Lesson data",
    "بطاقة الحصة": "Lesson card", "تحضير المعلم — للقراءة": "Teacher's plan — read only",
    "بطاقة تشخيص الإستراتيجية": "Strategy diagnostic card",
    "بنك بطاقات الإستراتيجيات": "Strategy card bank",
    "بطاقة زيارة الأقران": "Peer visit card",
    "بطاقات الأقران": "Peer cards", "بطاقات أقران": "peer cards",
    "بطاقة الجسر": "Bridge card", "إجراء الجسر": "Bridge action",
    "نتيجة الزيارة": "Visit result", "دليل مستويات الأداء": "Performance level guide",
    "الاستمارة الورقية": "Paper rubric",
    "القالب الورقي للتحضير": "Paper planning template",
})

# ═════════ ٥) الجدولُ ومفرداتُه ═════════
# ⚠️ هذه تسمياتُ عرضٍ فقط: القيمةُ المحفوظةُ في المفتاح عربيةٌ لا تُمَسّ.
EN.update({
    "القطاع": "Sector", "نوع التعليم": "Education type",
    "وطني": "National", "عالمي": "International",
    "المجمع": "Complex", "المجمع التعليمي": "Educational complex",
    "المدرسة": "School", "مدرستك": "Your school", "مدرستك:": "Your school:",
    "المرحلة": "Stage", "الحصة": "Period", "الحصص": "Lessons",
    "الأسبوع": "Week", "اليوم": "Day", "التاريخ": "Date", "الموعد": "Time",
    "وقت البدء": "Start time", "الفصل": "Class", "الصف/الفصل": "Grade / class",
    "الصف/الشعبة": "Grade / section", "المادة": "Subject", "التخصص": "Subject",
    "تخصصك": "Your subject", "تخصص المعلم الزائر": "Peer teacher's subject",
    "التخصص الذي تزوره": "Subject you visit",
    "اسم المعلم": "Teacher's name", "عدد الطلاب": "Number of students",
    "موضوع الدرس": "Lesson topic", "رقم الدرس": "Lesson number",
    "الأسبوع واليوم": "Week and day", "اليوم \\ الأسبوع": "Day \\ Week",
    "المجمع والمدرسة": "Complex and school",
    "المدرسة والحصة": "School and period", "الحصة والمدرسة": "Period and school",
    "الحصص المسجَّلة في المجمع": "Lessons recorded in the complex",
    "ابتدائي": "Primary", "متوسط": "Intermediate", "ثانوي": "Secondary",
    "الابتدائية": "Primary", "المتوسطة": "Intermediate", "الثانوية": "Secondary",
    "الأحد": "Sunday", "الاثنين": "Monday", "الثلاثاء": "Tuesday",
    "الأربعاء": "Wednesday", "الخميس": "Thursday", "الجمعة": "Friday", "السبت": "Saturday",
    "الأولى": "First", "الثانية": "Second", "الثالثة": "Third", "الرابعة": "Fourth",
    "الخامسة": "Fifth", "السادسة": "Sixth", "السابعة": "Seventh",
    "الحصة 1": "Period 1", "الحصة 2": "Period 2", "الحصة 3": "Period 3",
    "الحصة 4": "Period 4", "الحصة 5": "Period 5", "الحصة 6": "Period 6",
    "الأسبوع ٤": "Week 4", "الأسبوع ٥": "Week 5", "الأسبوع ٨": "Week 8",
    "الأسبوع ٩": "Week 9", "الأسبوع ١٠": "Week 10",
    "الأسبوع السادس": "Week 6", "الأسبوع السابع": "Week 7",
    "الأسبوع الثامن": "Week 8", "الأسبوع التاسع": "Week 9",
    "الأسبوع العاشر": "Week 10", "الأسبوع الحادي عشر": "Week 11",
    # التخصصاتُ الثمانية
    "رياضيات": "Mathematics", "اجتماعيات": "Social studies", "لغتي": "Arabic",
    "إسلامية": "Islamic studies", "علوم": "Science", "حاسب آلي": "Computing",
    # المجمعاتُ أسماءُ أحياءٍ — تُعرض كما هي (قرارُ المستشار: الأسماءُ لا تُترجَم)
    "النفل": "النفل", "عرقة": "عرقة", "الياسمين": "الياسمين", "المنار": "المنار",
    "الابتدائية- النفل": "الابتدائية- النفل", "المتوسطة- النفل": "المتوسطة- النفل",
    "الثانوية- النفل": "الثانوية- النفل", "الابتدائية- عرقة": "الابتدائية- عرقة",
})

# ═════════ ٦) المرشِّحاتُ والحالاتُ ═════════
EN.update({
    "كل الأسابيع": "All weeks", "كل الأيام": "All days",
    "كل التخصصات": "All subjects", "كل العمليات": "All actions", "الجميع": "Everyone",
    "كلُّ الأسبوع": "Whole week", "المعبّأ فقط": "Filled only",
    "ما لم يُسنَد بعد": "Not yet assigned",
    "ترشيحٌ بالأسبوع": "Filter by week", "ترشيحٌ بالشخص": "Filter by person",
    "ترشيحٌ بنوع العملية": "Filter by action type",
    "نوع العملية": "Action type", "العملية": "Action",
    "الحال": "Status", "الحالة": "Status", "التفعيل": "Activation",
    "التقدّم": "Progress", "نسبة الإنجاز": "Completion rate",
    "الحصة المفتوحة": "Open lesson",
    "لم يُحضَّر": "Not planned", "لم يُصدَر بعد": "Not issued yet",
    "لم يصدر": "Not issued", "التحضير لم يُصدَر": "The plan is not issued",
    "تحضيرٌ مُصدَر": "Plan issued", "تحضيرٌ غيرُ مُصدَر": "Plan not issued",
    "صدر التحضير": "Plan issued", "صدر تحضيرُها": "plan issued",
    "تحضيرات صدرت": "plans issued", "تنتظر تحضيرها": "awaiting planning",
    "حُضِّرت": "planned", "لم تُملأ": "Not filled", "لم تُعلَن": "Not declared",
    "لم يُسنَد": "Not assigned", "لم يُربط بعد": "Not linked yet",
    "غيرُ مربوط": "Not linked", "رُصدت": "Observed", "بدأ رصدُها": "observation started",
    "اعتُمدت نتيجتُها": "result approved", "لا حصةَ تنتظر الاعتماد": "No lesson awaits approval",
    "لم يفعّل": "Not active", "لم يفعّلوا": "not active", "فعّلوا": "active",
    "بلا حصةٍ بعد": "with no lesson yet", "بحصةٍ في الجدول": "with a lesson scheduled",
    "في كشف المعلمين": "in the teacher roster",
    "نسبةُ الإدخال": "Entry rate", "الإدخالُ الناقص": "Missing entries",
    "حصة مجدولة": "lessons scheduled",
    "حصةً مجدولةً باسم معلم": "lessons scheduled with a teacher",
    "حصصه المجدولة": "their scheduled lessons",
    "كلُّ الحصص صدر تحضيرُها": "Every lesson's plan is issued",
    "حصةً لك": "lessons are yours", "حصصك": "your lessons", "حصصه": "their lessons",
    "حصة في خطتك": "lessons in your plan", "حصة بلا بيانات": "Lesson with no data",
    "زياراتك": "Your visits", "بطاقتك": "your card",
    "تنتظر بطاقتك": "awaiting your card",
    "زيارةً مسنَدةً إليك": "visits assigned to you",
    "لا حصص مسنَدة إليك بعد.": "No lessons assigned to you yet.",
    "أتممتَ بطاقتها": "you completed its card",
    "حضّرتَها وأصدرتَها": "you planned and issued it",
    "جاهزةٌ بتحضيرٍ مُصدَر": "ready with an issued plan",
    "مؤشراً مرصوداً": "indicators observed",
    "أضعف مؤشر": "Weakest indicator", "أقوى مؤشر": "Strongest indicator",
    "أضعفُ مؤشراتك": "Your weakest indicators",
    "مرات الرصد": "Times observed", "مرات الإعلان": "Times declared",
    "عدد المقيّمين": "Observers", "استمارات رصدها": "rubrics recorded",
    "فرداً في المنظومة": "people in the system",
    "من الجدول والتحضير": "from the schedule and the plan",
    "من حذفها": "Deleted by", "ما حُذف معها": "Deleted with it",
    "ما جرى وما حُذف": "What happened and what was deleted",
    "آخر تغيير: ": "Last change: ", "تحديثٌ الآن": "Refreshing now",
    "يُحفظ…": "Saving…", "سيُحفظ…": "Will save…", "يُتحقَّق…": "Checking…",
    "حُفظ للجميع ✓": "Saved for everyone ✓",
    "الحفظ على هذا الجهاز فقط": "Saved on this device only",
    "على هذا الجهاز فقط": "on this device only",
    "غير متصلٍ بالمنظومة": "Not connected to the system",
    "متصلٌ بمخزن المنظومة": "Connected to the system store",
    "المخزن المشترك": "Shared store",
    "فُرّغت بيانات هذا الجهاز.": "This device's data has been wiped.",
    "أُلغي التفريغ.": "Wipe cancelled.",
    "بدايةٌ نظيفةٌ بعد التجربة": "A clean start after testing",
    "رقم غير صحيح.": "Invalid number.",
    "لا يطابق رقماً في الكشف": "No matching number in the roster",
    "لا جدول لتصديره.": "No schedule to export.",
    "لا عمليات بعد.": "No activity yet.",
    "لا عمليات مطابقة.": "No matching activity.",
    "اليومُ خارج أسابيع التقويم": "Today falls outside the assessment weeks",
    "✗ غير متطابق": "✗ Mismatch",
})

# ═════════ ٧) المجالاتُ الثمانيةُ ومؤشراتُها الخمسون ═════════
# ⚠️ أصلُ هذه النصوص **نصُّ ETEC المعتمد**، وهذه ترجمةُ عملٍ للتفاهم لا وثيقةٌ
#    رسمية. فتُوسم في الشاشة بذلك، ويبقى الأصلُ العربيُّ هو المرجعَ عند الخلاف.
EN.update({
    "التخطيط وتجهيز بيئة التعلم": "Planning and preparing the learning environment",
    "أهداف واضحة قابلة للقياس ومتنوعة (معرفي · مهاري · وجداني) معروضة للطلاب، وإستراتيجية متسقة معها ومع طبيعة المادة.":
        "Clear, measurable and varied objectives (cognitive · skills · affective) displayed to students, with a strategy consistent with them and with the nature of the subject.",
    "التخطيط يتضمّن إجراءات محددة للفئات الأولى بالرعاية، ولسريعي التعلم والموهوبين.":
        "The plan includes specific procedures for students needing priority care and for fast learners and the gifted.",
    "توزيع زمن الحصة على مراحلها بالدقائق (تهيئة · تنفيذ · تقويم · غلق)، وتناسب عدد الأنشطة معه.":
        "Lesson time distributed across its stages in minutes (warm-up · delivery · assessment · closure), with the number of activities proportionate to it.",
    "موافقة التنفيذ للتوزيع الزمني للمقرر، واستمرارية التخطيط وعدم انقطاعه.":
        "Delivery matches the course's time distribution, and planning is continuous without gaps.",
    "تجهيز بيئة التعلم: مصادر سمعية وبصرية وحسّية · داعم للقراءة والكتابة · داعم للحساب.":
        "Learning environment prepared: audio, visual and tactile resources · support for reading and writing · support for numeracy.",

    "العرض وإدارة الحصة": "Delivery and lesson management",
    "تهيئة حافزة مشوّقة مرتبطة بأهداف الدرس، تثير الفضول وحب الاستطلاع.":
        "A motivating, engaging warm-up linked to the lesson objectives that sparks curiosity and inquiry.",
    "تنفيذ إجراءات كل هدف بتسلسل منطقي، مع صحة المادة العلمية واكتمالها والقدرة على تبسيطها.":
        "Procedures for each objective delivered in logical sequence, with subject content accurate, complete and simplified appropriately.",
    "تطبيق إستراتيجيات تدريس متنوعة (استقصاء · تعاوني · مشروعات) تركّز على التعلم النشط.":
        "Varied teaching strategies applied (inquiry · cooperative · project-based) focused on active learning.",
    "إستراتيجيات وأنشطة تتسم بالشمول، وتلائم خصائص المرحلة العمرية للمتعلمين.":
        "Strategies and activities that are inclusive and suited to the learners' age-stage characteristics.",
    "إستراتيجيات وأنشطة تلائم قدرات المتعلمين وخبراتهم السابقة، وتراعي ميولهم واهتماماتهم.":
        "Strategies and activities suited to learners' abilities and prior experience, taking account of their inclinations and interests.",
    "ربط محتوى الدرس بتطبيقاته الحياتية الواقعية والجوانب الاجتماعية.":
        "Lesson content linked to real-life applications and social dimensions.",
    "أنشطة تعلم متنوعة ومبتكرة تشجّع على التجريب والبحث والاستقصاء.":
        "Varied, innovative learning activities that encourage experimentation, research and inquiry.",
    "تنويع الأسئلة الصفية وشمولها وصياغتها وعدالة توزيعها.":
        "Classroom questions varied, comprehensive, well phrased and fairly distributed.",
    "تشجيع المتعلمين على المشاركة في الأنشطة والمناقشة الصفية واستخدام مصادر التعلم.":
        "Learners encouraged to take part in activities and class discussion and to use learning resources.",
    "تنفيذ مهمة مكيَّفة للفئات الأولى بالرعاية، وتخصيص وقت كافٍ لها.":
        "An adapted task delivered for students needing priority care, with sufficient time allocated.",
    "تنفيذ مهمة إثرائية لسريعي التعلم والموهوبين، وتخصيص وقت كافٍ لها.":
        "An enrichment task delivered for fast learners and the gifted, with sufficient time allocated.",
    "أساليب تحفيز وتعزيز متنوعة تزيد الدافعية (إشادة · مكافآت · احتفاء بالمنجزات).":
        "Varied motivation and reinforcement methods that raise engagement (praise · rewards · celebrating achievement).",
    "ضبط الحصة وتنظيم الصف، واستثمار كامل الزمن، والالتزام بالبدء والانتهاء.":
        "Lesson control and classroom organisation, full use of time, and starting and ending on time.",

    "مشاركة المتعلمين واندماجهم  —  يُرصد على الطالب لا على المعلم":
        "Learner participation and engagement  —  observed on the student, not the teacher",
    "تكافؤ فرص المشاركة في الأنشطة والمناقشة واستخدام مصادر التعلم (يُوثَّق في مخطط عدالة التفاعل).":
        "Equal opportunity to take part in activities and discussion and to use learning resources (documented in the interaction-equity chart).",
    "مشاركة الطلاب في تنفيذ الأنشطة بإيجابية وحماس واستمتاع.":
        "Students take part in activities positively, enthusiastically and with enjoyment.",
    "ظهور الاندماج والرغبة في التعلم: انتباه · إنصات · تساؤل · فضول.":
        "Engagement and desire to learn are evident: attention · listening · questioning · curiosity.",
    "تعبير الطلاب عن آرائهم وأفكارهم بثقة ووضوح.":
        "Students express their views and ideas with confidence and clarity.",
    "العمل التعاوني والحوار الفعّال والمناقشة بين الطلاب.":
        "Cooperative work, effective dialogue and discussion among students.",
    "التعاطف والاحترام المتبادل: تقبّل الرأي · المبادرة بالدعم · ضبط الانفعالات.":
        "Empathy and mutual respect: accepting others' views · offering support · managing emotions.",

    "المهارات المستهدفة": "Targeted skills",
    "مصادر وأساليب وأنشطة تنمّي مهارات القراءة والكتابة.":
        "Resources, methods and activities that develop reading and writing skills.",
    "توظيف الطلاب أنفسهم للقراءة والكتابة في تنفيذ أنشطة التعلم.":
        "Students themselves use reading and writing to carry out learning activities.",
    "مصادر وأساليب وأنشطة تنمّي المهارات العددية (الحساب)، وتوظيف الطلاب لها في الأنشطة.":
        "Resources, methods and activities that develop numeracy, and students' use of them in activities.",
    "أنشطة تنمّي التفكير الناقد (التحليل · الاستنتاج · التقويم).":
        "Activities that develop critical thinking (analysis · inference · evaluation).",
    "أنشطة تنمّي التفكير الإبداعي (الطلاقة · المرونة · الأصالة).":
        "Activities that develop creative thinking (fluency · flexibility · originality).",
    "أنشطة تنمّي حل المشكلات (تحديد المشكلة · فهمها · اختيار الحل · تقويم الحلول).":
        "Activities that develop problem solving (defining the problem · understanding it · choosing a solution · evaluating solutions).",
    "أساليب وطرق متنوعة لتنمية التفكير، وأنشطة إثرائية متنوعة ومبتكرة.":
        "Varied methods for developing thinking, and varied, innovative enrichment activities.",

    "التقنية والتعلم الإلكتروني": "Technology and e-learning",
    "توظيف أدوات التعلم الإلكتروني والسبورة الذكية في دعم الموقف التدريسي وفق القواعد التربوية.":
        "E-learning tools and the smart board used to support teaching in line with sound pedagogy.",
    "محتوى إلكتروني مناسب لموضوع الدرس يلبي احتياجات جميع المتعلمين.":
        "Digital content suited to the lesson topic that meets the needs of all learners.",
    "توظيف الطلاب أنفسهم للتقنية (بحث · تنفيذ مهام · عروض · كتابة)، ومتابعة المعلم لإتقانهم.":
        "Students themselves use technology (research · carrying out tasks · presentations · writing), with the teacher monitoring their mastery.",
    "أنشطة مبتكرة تدمج التعلم الصفي بالإلكتروني، مع تقديم الدعم للطلاب أثناء الاستخدام.":
        "Innovative activities blending classroom and digital learning, with support provided to students while using it.",
    "التوجيه إلى المصادر الموثوقة والاستخدام الآمن، ومهمة مُسنَدة على المنصة الرقمية.":
        "Guidance towards trusted sources and safe use, with a task assigned on the digital platform.",

    "التقويم والتغذية الراجعة": "Assessment and feedback",
    "تقويم تشخيصي قبلي مناسب للتعلم.": "Suitable diagnostic pre-assessment of learning.",
    "تقويم بنائي (تكويني) أثناء الدرس للتأكد من تحقق كل هدف.":
        "Formative assessment during the lesson to confirm each objective is met.",
    "تقويم ختامي يشمل أهداف الدرس.": "Summative assessment covering the lesson objectives.",
    "تنوّع أدوات التقويم (ذاتي · أقران · مهام مفتوحة النهاية · مشروعات · مهام أدائية · ملف إنجاز).":
        "Varied assessment tools (self · peer · open-ended tasks · projects · performance tasks · portfolio).",
    "مراعاة أنماط تعلم الطلاب (سمعي · بصري · حركي · اجتماعي · شخصي) وتحقيق التمايز في الأداء.":
        "Students' learning styles taken into account (auditory · visual · kinaesthetic · social · individual), achieving differentiation in performance.",
    "تطبيق المتعلمين لأدوات التقويم الذاتي، ومشاركتهم في تقويم أقرانهم.":
        "Learners apply self-assessment tools and take part in assessing their peers.",
    "تغذية راجعة فورية محددة ومتنوعة تصل جميع الطلاب فردياً أو جماعياً.":
        "Immediate, specific and varied feedback reaching all students individually or as a group.",
    "ارتباط التغذية الراجعة بالموقف التعليمي، وتعزيزها للتعلم الذاتي لدى المتعلمين.":
        "Feedback tied to the teaching situation and reinforcing learners' self-directed learning.",
    "توظيف الطلاب للتغذية الراجعة في تحسين أدائهم، وسجل متابعة منظم ومكتمل.":
        "Students use feedback to improve their performance, with an organised and complete follow-up record.",

    "بناء شخصية الطالب": "Building the student's character",
    "تفعيل قيمة الأسبوع وربطها بالمحتوى العلمي للمادة خلال الحصة.":
        "The value of the week activated and linked to the subject content during the lesson.",
    "استخلاص الطالب للأفكار الرئيسة والفرعية وتدوينها بلغته الخاصة.":
        "The student extracts the main and subsidiary ideas and notes them in their own words.",
    "عرض الطالب أمام زملائه لما دوّنه، وطرح المعلم أسئلة للتحقق من فهمه.":
        "The student presents their notes to classmates, and the teacher asks questions to check understanding.",

    "مهارات المعلم وقدراته  —  خارج مشاهدات فريق التقويم الخارجي":
        "Teacher skills and capabilities  —  outside the external review team's observations",
    "استخدام اللغة العربية الفصحى تحدثاً وكتابة، وحثّ الطلاب على استخدامها.":
        "Use of standard Arabic in speech and writing, and encouraging students to use it.",
    "مهارات الاتصال والحضور: الحركة · مواجهة الطلاب · نبرة الصوت · التعامل بلطف وتوازن.":
        "Communication and presence: movement · facing the students · tone of voice · courteous and balanced manner.",

    "المجال ١": "Domain 1", "المجالان ٢ و٣": "Domains 2 & 3", "المجال ٤": "Domain 4",
    "المجال ٥": "Domain 5", "المجال ٦": "Domain 6", "المجال ٧": "Domain 7",
    "العرض وإدارة الحصة": "Delivery and lesson management",
    "التفكير الناقد والإبداعي": "Critical and creative thinking",
    "القراءة والكتابة": "Reading and writing",
    "المهارات العددية": "Numeracy",
    "التقنية والذكاء الاصطناعي": "Technology and artificial intelligence",
    "التمايز والربط بالحياة": "Differentiation and real-life links",
    "القيم وبناء الشخصية": "Values and character building",
    "التحفيز والمشاركة": "Motivation and participation",
    "متابعة أداء الطلاب": "Monitoring student performance",
    "ما تُقاس عليه الحصة": "What the lesson is measured against",
})

# ═════════ ٨) نموذجُ التحضير: حقولُه وتلميحاتُه ═════════
EN.update({
    "السؤال الأساسي": "Essential question",
    "السؤال الأساسي والأهداف": "Essential question and objectives",
    "تدرّجٌ يربط الدرس بالواقع: الأساسي مدخلٌ من الحياة، وسؤال الوحدة يصله بمحتوى الوحدة، وسؤال المحتوى يصل ذلك كلّه بدرس اليوم.":
        "A ladder linking the lesson to real life: the essential question opens from life, the unit question ties it to the unit content, and the content question ties all of that to today's lesson.",
    "أسئلة الوحدة": "Unit questions", "أسئلة المحتوى": "Content questions",
    "الهدف المعرفي": "Cognitive objective", "الهدف المهاري": "Skills objective",
    "الهدف الوجداني": "Affective objective",
    "فعلٌ سلوكي قابل للقياس (يحدد · يقارن · يكتب) لا «يعرف» ولا «يفهم»؛ ويُعرض على الطلاب لا يبقى في الدفتر.":
        "A measurable behavioural verb (identifies · compares · writes) — not “knows” or “understands”; and displayed to the students, not left in the notebook.",
    "الاتجاه التدريسي": "Teaching approach",
    "اتجاهٌ واحد تُقاس شواهده في الحصة، لا اتجاهات مجتمعة بلا أثر.":
        "One approach whose evidence is measured in the lesson — not several combined with no effect.",
    "عرض الأهداف": "Displaying objectives",
    "الإستراتيجية": "Strategy", "الاستراتيجية": "Strategy",
    "الإستراتيجية المعلنة": "Declared strategy",
    "الإستراتيجية والاتجاه": "Strategy and approach",
    "الاستراتيجية والاتجاه": "Strategy and approach",
    "الإستراتيجية المعلنة هي التي تُقاس ببطاقة التشخيص، ودرجتها تدخل في مؤشر م٢·٣.":
        "The declared strategy is the one measured by the diagnostic card, and its score feeds indicator D2·3.",
    "مصادر التعلم": "Learning resources", "داعمات البيئة": "Environment supports",
    "ضع ✓ لما سيُرى فعلاً في الصف: مصدر القراءة والكتابة، ومحسوس الحساب، والمقاعد المهيّأة.":
        "Tick what will actually be seen in the room: the reading and writing resource, the concrete numeracy aid, and the arranged seating.",
    "أوراق العمل": "Worksheets", "إعداد أوراق العمل": "Preparing worksheets",
    "خريطة الزمن": "Time map",
    "بالدقائق — ومجموعها يساوي زمن الحصة": "In minutes — totalling the lesson time",
    "وزّع الزمن حتى يساوي المجموعُ زمنَ الحصة، وخصّص زمناً للفئات الأولى بالرعاية وللموهوبين.":
        "Distribute the time so the total equals the lesson time, and allocate time for students needing priority care and for the gifted.",
    "وزّع الزمن على المراحل": "Distribute the time across the stages",
    "العرض وإدارة الحصة · مشاركة المتعلمين واندماجهم":
        "Delivery and lesson management · Learner participation and engagement",
    "التهيئة سؤالٌ أو موقفٌ مثير لا «درسنا اليوم عن…»، والغلق «علم بالقلم»: يكتب الطالب ما تعلّمه.":
        "The warm-up is a question or a striking situation, not “today's lesson is about…”; and the closure is “pen in hand”: the student writes what they learned.",
    "تابع: التمايز والتحفيز والربط بالحياة":
        "Continued: differentiation, motivation and real-life links",
    "المهمة المكيَّفة": "Adapted task", "المهمة الإثرائية": "Enrichment task",
    "لكلٍّ منهما مهمة مكتوبة وزمنٌ في الخريطة؛ فعبارة «مراعاة الفروق» بلا مهمة لا تُعدّ شاهداً.":
        "Each needs a written task and time on the map; “attending to differences” with no task is not evidence.",
    "توزيع الأدوار بالأسماء وأسئلةٌ لمن لم يشارك يصنعان عدالة التفاعل التي يرسمها الزائر.":
        "Assigning roles by name, plus questions for those who have not spoken, create the interaction equity the visitor charts.",
    "مثالٌ من حياة الطلاب أنفسهم في مدينتهم ومدرستهم.":
        "An example from the students' own lives, in their city and their school.",
    "تُمارَس في كل مادة: اكتب كيف سيقرأ الطالب أو يكتب أو يحسب في هذا الدرس.":
        "Practised in every subject: write how the student will read, write or calculate in this lesson.",
    "مهارات التفكير": "Thinking skills", "نشاط التفكير": "Thinking activity",
    "سؤالٌ أو مهمة بمستوى تحليل أو تقويم أو إبداع، لا سؤال استرجاع.":
        "A question or task at the analysis, evaluation or creation level — not a recall question.",
    "أدوات التقييم": "Assessment tools", "توظيف التقنية": "Use of technology",
    "الأداة بيد الطالب لا بيد المعلم وحده، ومهمةٌ على المنصة يؤديها الطالب.":
        "The tool is in the student's hands, not the teacher's alone, with a platform task the student completes.",
    "المهمة على المنصة": "Platform task",
    "التقويم التشخيصي": "Diagnostic assessment",
    "التشخيصي قبل الشرح، والبنائي بعد كل هدف بأداة محددة.":
        "Diagnostic before teaching, and formative after each objective with a defined tool.",
    "التقويم البنائي": "Formative assessment",
    "الذاتي والأقران": "Self and peer",
    "التغذية الراجعة": "Feedback",
    "اللحظة التي يوظّف فيها الطالب ملاحظتك فيعدّل عمله.":
        "The moment the student acts on your comment and revises their work.",
    "التقييم الختامي": "Summative assessment",
    "أسئلة مكتوبة نصاً تقيس أهداف المجال ١ نفسها.":
        "Questions written out in full that measure the same Domain 1 objectives.",
    "أسئلة تفكير عليا": "Higher-order questions",
    "أسئلة التفكير العليا": "Higher-order thinking questions",
    "لماذا؟ ماذا لو؟ قارن · اقترح… سؤالان على الأقل.":
        "Why? What if? Compare · Suggest… at least two questions.",
    "قيمة الأسبوع": "Value of the week",
    "تُربط بموقف من الدرس نفسه، والتلخيص والغلق يؤديهما الطالب.":
        "Linked to a situation from the lesson itself; the student does the summary and the closure.",
    "مهارة التلخيص": "Summarising skill", "مهارة الغلق": "Closure skill",
    "التلخيص واستخلاص النتائج": "Summarising and drawing conclusions",
    "التهيئة": "Warm-up", "التنفيذ": "Delivery", "التقويم": "Assessment", "الغلق": "Closure",
    "التهيئة · مدخل الحصة": "Warm-up · lesson opening",
    "الغلق · علم بالقلم": "Closure · pen in hand",
    "علم بالقلم: التلخيص والعرض": "Pen in hand: summarising and presenting",
    "النشاط الأول": "Activity 1", "النشاط الثاني": "Activity 2",
    "مراحل الحصة": "Lesson stages",
    "المجموع = زمن الحصة": "Total = lesson time", "زمن الحصة": "Lesson time",
    "زمن الأولى بالرعاية": "Priority-care time", "زمن الموهوبين": "Gifted time",
    "ومن زمن التنفيذ": "from the delivery time",
    "التهيئة والتمهيد للدرس": "Warm-up and lead-in",
    "التشويق": "Hook", "التلخيص": "Summary", "التفصيل": "Elaboration",
    "الملخص السبوري": "Board summary",
    "ما يفعله المعلم": "What the teacher does",
    "ما يفعله المتعلم — فعلٌ يُرى": "What the learner does — a visible action",
    "ما قاله الطلاب — يُسأل ثلاثة من مستويات مختلفة":
        "What the students said — ask three from different levels",
    "ماذا تتعلّم اليوم؟ وكيف عرفتَ ذلك؟": "What are you learning today? How do you know?",
    "كيف تعرف أنك أتقنتَ ما تعلّمته؟": "How do you know you have mastered it?",
    "ماذا تفعل إذا لم تفهم؟ وأرِني ملاحظات معلمك على عملك.":
        "What do you do if you don't understand? Show me your teacher's comments on your work.",
    "ما الذي شاهدتُه وأنوي تطبيقه؟": "What did I see that I intend to apply?",
    "كيف سأطبّقه في حصتي؟ وفي أي درس؟": "How will I apply it in my lesson, and in which lesson?",
    "ما الأثر الذي أتوقّعه على طلابي؟": "What impact do I expect on my students?",
    # مستوياتُ الأداء والتقويم
    "غير متحقق": "Not met", "متحقق جزئياً": "Partly met",
    "متحقق لحد كبير": "Largely met", "متحقق": "Met",
    "يحتاج لتحسين": "Needs improvement", "يحتاج تحسيناً": "Needs improvement",
    "مقبول": "Acceptable", "جيد": "Good", "جيد جداً": "Very good", "ممتاز": "Excellent",
    "ضعيف": "Weak", "قوي": "Strong", "متوسط": "Moderate", "علاجي": "Remedial",
    "لا ينطبق": "N/A", "طُبّق جزئياً": "Partly applied",
    "طُبّق ويُرى ثابتاً": "Applied and consistently seen", "لم يُطبَّق": "Not applied",
    "فردي": "Individual", "ثنائي": "Paired", "جماعي": "Group",
    "تقويم ذاتي": "Self-assessment", "تقويم أقران": "Peer assessment",
    "تقويم بنائي": "Formative assessment",
    "التقويم من أجل التعلم": "Assessment for learning",
    "٩٠٪ فأعلى ← ٤   ·   ٧٥ إلى أقل من ٩٠ ← ٣   ·   ٥٠ إلى أقل من ٧٥ ← ٢   ·   أقل من ٥٠ ← ١":
        "90% and above → 4   ·   75 to under 90 → 3   ·   50 to under 75 → 2   ·   under 50 → 1",
    "الدرجة": "Score", "النسبة": "Percentage", "المستوى": "Level", "الحكم": "Rating",
    "المؤشر": "Indicator", "الرمز": "Code", "الزمن": "Time", "البطاقة": "Card",
    "الرصد": "Observation", "التحضير": "Planning", "الاستمارة": "Rubric",
    "متوسط الدرجة": "Average score", "متوسط النسبة": "Average percentage",
    "درجة المؤشر": "Indicator score", "متوسط البطاقة من ١٠٠": "Card average out of 100",
    "متوسط نسبتك": "Your average", "متوسطك من ٤": "Your average out of 4",
    "نسبتك": "Your percentage", "الأقران": "Peers",
})

# ═════════ ٩) بنكُ الإستراتيجيات: ١٩ بطاقةً ومؤشراتُها ═════════
EN.update({
    "التفكير الناقد": "Critical thinking",
    "توزيع الطلاب في مجموعات مناسبة": "Grouping students appropriately",
    "طرح أسئلة تتناول التحليل والتركيب والتقويم":
        "Asking questions that address analysis, synthesis and evaluation",
    "تشجيع الطلاب على التعبير عن آرائهم": "Encouraging students to express their views",
    "ربط الموضوع بقضايا البيئة والمجتمع":
        "Linking the topic to environmental and social issues",
    "تشجيع الطلاب على التفكير التأملي": "Encouraging students to think reflectively",
    "استثمار الأفكار الناقدة للطلاب ومتابعة المجموعات":
        "Building on students' critical ideas and monitoring the groups",
    "مناقشة الأفكار المطروحة": "Discussing the ideas raised",
    "تعميم النتائج والخبرات": "Generalising the findings and experiences",

    "توزيع الطلاب في مجموعات": "Grouping the students",
    "مناسبة الزمن المخصص لكل نشاط": "Time allocated to each activity is appropriate",
    "التسلسل المنطقي لتنفيذ أوراق العمل": "Logical sequencing of the worksheets",
    "استخدام النشاطات الإثرائية عند الحاجة": "Using enrichment activities when needed",
    "تقديم أنشطة إثرائية للطلاب المتميزين":
        "Providing enrichment activities for high-achieving students",
    "متابعة عمل المجموعات وتقديم المساعدة عند الحاجة":
        "Monitoring group work and offering help when needed",
    "تقويم التعلم بعد تنفيذ كل معرفة جديدة":
        "Assessing learning after each new piece of knowledge",
    "الالتزام بالزمن": "Keeping to time",

    "جدول التعلم (KWL)": "KWL chart",
    "مناسبة تنظيم البيئة الصفية وطريقة جلوس الطلاب":
        "Classroom layout and seating arrangement are appropriate",
    "توزيع النموذج على الطلاب بداية الحصة":
        "Distributing the chart to students at the start of the lesson",
    "توضيح مهام كل مجموعة من الطلاب": "Clarifying each group's tasks",
    "تنشيط المعرفة السابقة عبر مناقشات صفية وعصف ذهني":
        "Activating prior knowledge through class discussion and brainstorming",
    "الأسئلة تثير دافعية الطلاب في (ماذا تريد أن تعرف ...)":
        "Questions spark students' motivation in “What do you want to know…”",
    "إتاحة مصادر للتعلم (شرح · فيديو · قراءة موجهة · بحث ...)":
        "Providing learning resources (explanation · video · guided reading · research…)",
    "تنظيم الطلاب للمعلومات التي تم الوصول إليها":
        "Students organise the information they have found",
    "عرض (ماذا تعلمت؟ ...) من المجموعات":
        "Groups present “What did I learn?…”",
    "مناسبة تطبيق مراحل الاستراتيجية حسب وقت الحصة":
        "The strategy's stages fit the lesson time",
    "مدى مشاركة الطلاب في تطبيق الاستراتيجية":
        "Extent of student participation in applying the strategy",

    "العصف الذهني": "Brainstorming",
    "تحديد المشكلة": "Defining the problem",
    "طرح الأسئلة وتسجيلها في مكان واضح":
        "Posing questions and recording them where all can see",
    "الإثارة والجاهزية للتفكير": "Arousal and readiness to think",
    "تحفيز المتعلم على الوصول لأفكار إبداعية":
        "Prompting the learner towards creative ideas",
    "إنتاج أفكار وآراء إبداعية": "Generating creative ideas and views",
    "تنقيح وتقييم الأفكار": "Refining and evaluating the ideas",
    "تحديد أغرب فكرة": "Identifying the most unusual idea",
    "احترام الرأي الآخر": "Respecting differing views",
    "الوصول لحل المشكلة": "Reaching a solution to the problem",
    "إعادة صياغة الموضوع": "Reframing the topic",

    "اللعب بالعرائس": "Puppet play",
    "مناسبة الموضوع": "Suitability of the topic",
    "مناسبة اللعبة": "Suitability of the game",
    "ابتكارية اللعبة": "Originality of the game",
    "تغطية عناصر الدرس": "Coverage of the lesson elements",
    "طريقة التقديم": "Manner of presentation",
    "إدارة الصف أثناء ممارسة اللعبة": "Classroom management during the game",
    "تنظيم الوقت بطريقة مناسبة": "Organising time appropriately",
    "دور الطالب في اللعبة": "The student's role in the game",

    "حل المشكلات": "Problem solving",
    "المشكلات مناسبة لمستوى الطلاب": "Problems suited to the students' level",
    "المشكلات ذات صلة بموضوع الدرس": "Problems relevant to the lesson topic",
    "المشكلات ذات صلة بحياة الطلاب": "Problems relevant to students' lives",
    "الابتعاد عن الإلقاء": "Avoiding lecturing",
    "حث الطلاب على القراءة الحرة والاطلاع":
        "Urging students towards free reading and wider study",
    "تشجيع الطلاب على الاستمرار والمثابرة وتحفيز التفكير":
        "Encouraging persistence and perseverance and prompting thinking",
    "تشجيع الأفكار المبتكرة": "Encouraging original ideas",
    "استخدام الأسلوب العلمي لحل المشكلات":
        "Using the scientific method to solve problems",
    "مناقشة الحلول وتقويمها": "Discussing and evaluating the solutions",
    "العمل الجماعي": "Group work",

    "جيكسو": "Jigsaw",
    "تقسيم الطلاب إلى مجموعات (٣–٥) غير متجانسة":
        "Dividing students into mixed-ability groups of 3–5",
    "تقسيم محتوى الدرس إلى (٥–٦) فقرات أو حسب الحاجة":
        "Dividing the lesson content into 5–6 segments, or as needed",
    "توزيع الفقرات على الطلاب في كل مجموعة":
        "Distributing the segments to students within each group",
    "إتاحة الوقت المناسب للقراءة وتنفيذ المهام":
        "Allowing adequate time for reading and completing the tasks",
    "تشجيع المعلم للطلاب على تبادل الأفكار حول كل فقرة":
        "The teacher encourages students to exchange ideas on each segment",
    "وضوح شخصية الطالب أثناء شرحه للمعلومة":
        "The student's presence is clear while explaining the information",
    "التنقل بين المجموعات ومتابعة المهام المنفذة":
        "Moving between groups and monitoring the tasks completed",
    "إجراء تقييم (اختبار قصير) كورقة عمل للمجموعات":
        "Running an assessment (short quiz) as a group worksheet",
    "ساعدت الاستراتيجية الطلاب على تنمية قدراتهم ومهاراتهم":
        "The strategy helped students develop their abilities and skills",
    "مستوى تفاعل الطلاب ودافعيتهم للتعلم":
        "Level of student engagement and motivation to learn",

    "خرائط المفاهيم": "Concept maps",
    "اختيار الموضوع (موضوع رئيس)": "Choosing the topic (a main topic)",
    "تحديد المفاهيم الفرعية": "Identifying the subsidiary concepts",
    "تحديد العلاقة بين المفاهيم من العام للخاص":
        "Establishing the relationship between concepts from general to specific",
    "ترتيب المفاهيم في شكل يبرز العلاقة بينها":
        "Arranging the concepts so the relationship between them stands out",
    "تحديد كلمات الربط بين المفاهيم على الأسهم":
        "Writing the linking words between concepts on the arrows",
    "استخدام الألوان والصور": "Using colour and images",
    "مشاركة الطلاب في بناء الخريطة": "Students take part in building the map",
    "متابعة عمل الطلاب أثناء تصميم الخرائط":
        "Monitoring students' work while they design the maps",
    "خرائط صنعها الطلاب": "Maps made by the students",
    "تلخيص المعلومات من خلال الطلاب": "Summarising the information through the students",

    "لعب الأدوار": "Role play",
    "تقديم الدرس في صورة مشكلة": "Presenting the lesson as a problem",
    "تحديد زمن تمثيل الدور": "Setting the time for acting the role",
    "تحديد الأدوار ووصفها": "Defining and describing the roles",
    "مناقشة المشكلة": "Discussing the problem",
    "تفاعل الطلاب مع الأدوار": "Students' engagement with the roles",
    "إيقاف لعب الأدوار في الوقت المناسب": "Stopping the role play at the right moment",
    "إعادة تمثيل الأدوار": "Re-enacting the roles",
    "تشجيع الطلاب على اقتراح سلوكيات بديلة":
        "Encouraging students to suggest alternative behaviours",
    "مشاركة الطلاب في بناء الخبرات وتعميمها":
        "Students take part in building the experience and generalising it",

    "نموذج فراير": "Frayer model",
    "تقسيم الطلاب إلى مجموعات عمل غير متجانسة":
        "Dividing students into mixed-ability working groups",
    "شرح خصائص النموذج للطلاب وتحديد أجزائه الأربعة":
        "Explaining the model's features to students and identifying its four parts",
    "رسم الشكل التخطيطي للنموذج من قبل الطلاب":
        "Students draw the model's diagram themselves",
    "مناقشة الطلاب في تعريف المفهوم وتحديد خصائصه من خلال العصف الذهني":
        "Discussing with students how to define the concept and identify its features through brainstorming",
    "مساعدة الطلاب على التفكير ووصف معنى المفهوم":
        "Helping students think about and describe the concept's meaning",
    "تشجيع الطلاب على المناقشة خلال صياغة التعريف":
        "Encouraging discussion while formulating the definition",
    "مناسبة وقت تطبيق الاستراتيجية من الحصة":
        "The time given to the strategy within the lesson is appropriate",
    "طريقة تحليل وتقويم اكتساب الطلاب للمفاهيم":
        "How students' concept acquisition is analysed and assessed",
    "الالتزام بمراحل تطبيق الاستراتيجية (تحليل المفهوم · تدريس المفهوم · قياس اكتساب المفهوم)":
        "Following the strategy's stages (analysing the concept · teaching the concept · measuring its acquisition)",
    "تناوب الطلاب في توضيح ما اكتسبوه من مفاهيم":
        "Students take turns explaining the concepts they have acquired",

    "التعلم التعاوني": "Cooperative learning",
    "تقسيم الطلاب إلى مجموعات غير متجانسة بحجم مناسب":
        "Dividing students into mixed-ability groups of a suitable size",
    "توزيع الأدوار داخل كل مجموعة (قائد · مسجّل · مقرّر · ضابط وقت)":
        "Assigning roles within each group (leader · recorder · reporter · timekeeper)",
    "وضوح المهمة والمنتج المطلوب من كل مجموعة":
        "The task and required output from each group are clear",
    "الاعتماد المتبادل: نجاح المجموعة يتوقف على إسهام كل فرد":
        "Interdependence: the group's success depends on every member's contribution",
    "المساءلة الفردية: لكل طالب ناتج يُسأل عنه":
        "Individual accountability: each student has an output they answer for",
    "التنقل بين المجموعات وتقديم الدعم في وقته":
        "Moving between groups and providing support at the right time",
    "إتاحة زمن كافٍ للحوار داخل المجموعة قبل العرض":
        "Allowing enough time for discussion within the group before presenting",
    "عرض المجموعات لنواتجها ومناقشتها": "Groups present and discuss their outputs",
    "تقويم العمل الجماعي والفردي معاً":
        "Assessing group and individual work together",
    "تأمل المجموعة في أدائها وتحديد ما تحسّنه":
        "The group reflects on its performance and identifies what to improve",

    "التدريس التبادلي": "Reciprocal teaching",
    "اختيار نصّ مناسب لمستوى الطلاب ومرتبط بهدف الدرس":
        "Choosing a text suited to the students' level and tied to the lesson objective",
    "شرح الأدوار الأربعة ونمذجتها أمام الطلاب قبل تسليمها لهم":
        "Explaining and modelling the four roles before handing them to the students",
    "تقسيم الطلاب إلى مجموعات وتوزيع الأدوار داخل كل مجموعة":
        "Dividing students into groups and assigning roles within each",
    "قراءة مقطع محدد ثم توقّف منظم عنده لا قراءة النص كاملاً":
        "Reading a defined passage then pausing in a structured way, rather than reading the whole text",
    "تلخيص الطالب للمقطع بلغته هو لا بلغة الكتاب":
        "The student summarises the passage in their own words, not the book's",
    "صياغة الطالب لسؤال عن المقطع وطرحه على مجموعته":
        "The student frames a question about the passage and puts it to the group",
    "توضيح ما غمض من كلمة أو فكرة، والرجوع إلى النص للتحقق":
        "Clarifying any unclear word or idea and returning to the text to check",
    "التنبؤ بما سيأتي في المقطع التالي وتبريره":
        "Predicting what comes in the next passage and justifying it",
    "تناوب الأدوار بين الطلاب في المقاطع اللاحقة":
        "Rotating the roles among students in the following passages",
    "متابعة المعلم للمجموعات وتدخّله عند تعثّر الدور":
        "The teacher monitors the groups and steps in when a role falters",

    "المحطات الرقمية والتعلم المقلوب": "Digital stations and flipped learning",
    "تحديد الهدف أولاً ثم اختيار الأداة الرقمية المناسبة له":
        "Setting the objective first, then choosing the digital tool that fits it",
    "تجهيز المحتوى الرقمي أو المقطع قبل الحصة والتحقق من عمله":
        "Preparing the digital content or clip before the lesson and checking it works",
    "وضوح مهمة كل محطة رقمية ومدتها ومخرجها":
        "Each digital station's task, duration and output are clear",
    "التقنية بيد الطالب: بحث · إنتاج · عرض · اختبار ذاتي":
        "Technology in the student's hands: research · creation · presentation · self-testing",
    "مهمة مُسنَدة على المنصة الرقمية ومتابعة تسليمها":
        "A task assigned on the digital platform, with submission monitored",
    "استثمار نتائج الأداة الرقمية في تحديد من يحتاج دعماً":
        "Using the tool's results to identify who needs support",
    "التوجيه إلى المصادر الموثوقة وقواعد الاستخدام الآمن":
        "Guidance towards trusted sources and safe-use rules",
    "بديل جاهز عند تعطّل الأداة أو ضعف الشبكة":
        "A ready fallback if the tool fails or the network is weak",
    "دمج ناتج المحطة الرقمية في خلاصة الحصة لا تركه منفصلاً":
        "Folding the digital station's output into the lesson summary rather than leaving it separate",
    "مستوى انضباط الطلاب وتفاعلهم أثناء استخدام الأجهزة":
        "Students' discipline and engagement while using the devices",

    "تحديد ما يُطلب تلخيصه بدقة: فكرة رئيسة · خطوات · قاعدة":
        "Defining precisely what is to be summarised: main idea · steps · rule",
    "نمذجة التلخيص أمام الطلاب مرة واحدة على الأقل":
        "Modelling the summary in front of the students at least once",
    "تخصيص زمن صامت للكتابة الفردية قبل العرض":
        "Allocating silent time for individual writing before presenting",
    "كتابة الطالب بلغته هو لا نسخ عبارة الكتاب":
        "The student writes in their own words rather than copying the book",
    "تدوين الأفكار الرئيسة والفرعية مرتبة":
        "Noting the main and subsidiary ideas in order",
    "اختيار طلاب من مستويات مختلفة للعرض لا المتطوعين وحدهم":
        "Choosing students of different levels to present, not just volunteers",
    "عرض الطالب أمام زملائه بصوت مسموع ووضوح":
        "The student presents to classmates audibly and clearly",
    "طرح المعلم أسئلة تحقق من فهم الطالب لما عرضه":
        "The teacher asks questions to check the student's understanding of what they presented",
    "تعليق الزملاء على العرض بلغة محددة لا بعبارات عامة":
        "Classmates comment on the presentation in specific terms, not generalities",
    "حفظ الملخصات في الدفتر أو ملف الإنجاز للرجوع إليها":
        "Keeping the summaries in the notebook or portfolio for later reference",

    "التدريس الصريح بالنمذجة المتدرجة": "Explicit teaching with graduated modelling",
    "مراجعة قصيرة للمتطلب السابق في بداية الحصة":
        "A short review of the prerequisite at the start of the lesson",
    "عرض المهارة في خطوات صغيرة متتابعة لا دفعة واحدة":
        "Presenting the skill in small successive steps rather than all at once",
    "نمذجة المعلم للمهارة أمام الطلاب مع التفكير بصوت مسموع":
        "The teacher models the skill for students while thinking aloud",
    "تقديم مثال محلول كامل قبل طلب الأداء المستقل":
        "Giving a fully worked example before asking for independent performance",
    "التطبيق الموجّه المشترك قبل التطبيق الفردي":
        "Shared guided practice before individual practice",
    "طرح أسئلة تحقُّق كثيرة تكشف فهم أغلب الطلاب لا المتطوعين":
        "Asking many checking questions that reveal most students' understanding, not just volunteers'",
    "تصحيح الخطأ فور ظهوره وإعادة النمذجة عند الحاجة":
        "Correcting an error as soon as it appears and re-modelling when needed",
    "الانتقال إلى الأداء المستقل بعد بلوغ نسبة نجاح عالية في الموجّه":
        "Moving to independent performance once a high success rate is reached in guided practice",
    "توفير سقالات (قوائم خطوات · منظمات بصرية) تُرفع تدريجياً":
        "Providing scaffolds (step lists · visual organisers) that are gradually withdrawn",
    "مراجعة ختامية تربط ما تعلّمه الطالب بالخطوة التالية":
        "A closing review linking what the student learned to the next step",

    "الاستدعاء النشط والممارسة المتباعدة": "Active recall and spaced practice",
    "بدء الحصة باسترجاع ما سبق دون الرجوع إلى الكتاب أو الدفتر":
        "Starting the lesson by recalling prior learning without the book or notebook",
    "أسئلة استرجاع قصيرة موزّعة على الحصة لا في آخرها فقط":
        "Short recall questions spread through the lesson, not only at the end",
    "تنويع صيغ الاسترجاع (شفهي · بطاقة · سبورة صغيرة · اختبار قصير)":
        "Varying the recall format (oral · flashcard · mini-whiteboard · short quiz)",
    "تضمين محتوى من دروس أو وحدات سابقة لا درس اليوم وحده":
        "Including content from earlier lessons or units, not just today's",
    "إتاحة زمن تفكير كافٍ قبل طلب الإجابة":
        "Allowing enough thinking time before asking for the answer",
    "استجابة كل الطلاب لا المتطوعين وحدهم":
        "All students respond, not just volunteers",
    "تصحيح فوري يبيّن الصواب وسبب الخطأ":
        "Immediate correction that shows the right answer and why the error occurred",
    "تسجيل نتائج الاسترجاع واستعمالها في تحديد ما يُعاد تدريسه":
        "Recording recall results and using them to decide what to reteach",
    "تكرار المحتوى الصعب في حصص لاحقة بمسافات زمنية متباعدة":
        "Revisiting difficult content in later lessons at spaced intervals",
    "تدريب الطلاب على استعمال الاسترجاع في مذاكرتهم الذاتية":
        "Training students to use recall in their own study",

    "فكّر — زاوج — شارك": "Think — Pair — Share",
    "طرح سؤال يستحق التفكير لا سؤال استرجاع مباشر":
        "Posing a question worth thinking about, not a direct recall question",
    "تحديد زمن التفكير الفردي وإلزام الصمت فيه":
        "Setting the individual thinking time and requiring silence during it",
    "مطالبة كل طالب بتدوين فكرته قبل الحوار":
        "Requiring every student to note their idea before the discussion",
    "تنظيم الأزواج بوضوح وتحديد من يبدأ":
        "Organising the pairs clearly and deciding who starts",
    "تحديد زمن الحوار الثنائي ومتابعته":
        "Setting and monitoring the time for the paired discussion",
    "التنقل بين الأزواج والاستماع لأفكارهم":
        "Moving between pairs and listening to their ideas",
    "اختيار المشاركين بالأسماء لا بالمتطوعين":
        "Choosing contributors by name rather than by volunteering",
    "مطالبة الطالب بعرض فكرة زميله أحياناً لا فكرته وحده":
        "Sometimes asking the student to present their partner's idea, not only their own",
    "ربط الأفكار المعروضة ببعضها وبناء الخلاصة منها":
        "Linking the presented ideas to one another and building the conclusion from them",
    "مشاركة أغلب طلاب الصف خلال الحصة":
        "Most of the class contribute during the lesson",

    "الاستقصاء بدورة الخمس (5E)": "Inquiry with the 5E cycle",
    "تهيئة تثير سؤالاً أو ظاهرة محيّرة تشدّ الطلاب للموضوع":
        "A warm-up raising a question or puzzling phenomenon that draws students into the topic",
    "إتاحة الاستكشاف العملي قبل تقديم التفسير من المعلم":
        "Allowing hands-on exploration before the teacher gives the explanation",
    "توافر الأدوات والمواد اللازمة لكل مجموعة":
        "The necessary tools and materials are available for each group",
    "تسجيل الطلاب لملاحظاتهم وبياناتهم أثناء الاستكشاف":
        "Students record their observations and data during the exploration",
    "بناء التفسير العلمي من ملاحظات الطلاب أنفسهم":
        "Building the scientific explanation from the students' own observations",
    "تصويب التصورات الخاطئة التي ظهرت أثناء الاستكشاف":
        "Correcting the misconceptions that surfaced during the exploration",
    "مهمة إثرائية تطبّق المفهوم في سياق جديد":
        "An enrichment task applying the concept in a new context",
    "التزام إجراءات السلامة في النشاط العملي":
        "Following safety procedures in the practical activity",
    "تقويم يقيس الفهم والعملية معاً لا الحفظ":
        "Assessment measuring understanding and process together, not memorisation",
    "إدارة زمن المراحل الخمس بما يناسب زمن الحصة":
        "Managing the five stages' timing to fit the lesson",

    "المحطات التعليمية ولوحة الاختيار": "Learning stations and choice board",
    "تصميم محطات (أو خيارات) تخدم هدف الحصة نفسه":
        "Designing stations (or choices) that serve the same lesson objective",
    "تمايز المحطات في المستوى أو نمط التعلم لا في الكم فقط":
        "Stations differentiated by level or learning style, not merely by quantity",
    "وضوح تعليمات كل محطة مكتوبة عند مكانها":
        "Each station's instructions written clearly at its place",
    "تحديد زمن كل محطة وإعلان إشارة الانتقال":
        "Setting each station's time and announcing the signal to move",
    "توزيع الطلاب على المحطات وفق بيانات مستواهم لا عشوائياً":
        "Assigning students to stations by their attainment data, not at random",
    "وجود محطة يشرف عليها المعلم مباشرة للفئة الأولى بالرعاية":
        "One station directly supervised by the teacher for students needing priority care",
    "توافر ناتج مكتوب أو منتج من كل طالب في كل محطة":
        "A written output or product from every student at every station",
    "انضباط الحركة والانتقال بين المحطات":
        "Orderly movement and transition between stations",
    "متابعة المعلم لكل المحطات وتقديم الدعم في وقته":
        "The teacher monitors every station and provides support in good time",
    "خلاصة ختامية تجمع نواتج المحطات في فهم مشترك":
        "A closing summary drawing the stations' outputs into shared understanding",
})

# ═════════ ١٠) شروحُ المراحل وأوصافُ الأدوار والتقارير ═════════
EN.update({
    "جدول الحصص الموحَّدة للتقويم الخارجي":
        "Unified lesson schedule for the external review",
    "المصفوفة الأولى — ومنها تبدأ كل حصة":
        "The first matrix — every lesson starts here",
    "هذه الشاشة هي جدولُ الحصص الموحَّدة للتقويم الخارجي داخل المنصة: لكل مجمعٍ ورقةٌ، وصفوفُها اليومُ في تخصص المعلم الزائر، وأعمدتُها الحصصُ بأوقات بدئها، وتحت كل حصةٍ خمسةُ حقول: المعلم · الإستراتيجية · الاتجاه التدريسي · الفصل · وقت البدء. فما يُكتب في الخلية يصير حصةً، ومن الخلية تبدأ الحصةُ بضخِّ بياناتها في التحضير.":
        "This screen is the unified lesson schedule for the external review inside the platform: one sheet per complex, with rows for the day by the peer teacher's subject, and columns for the periods with their start times. Under each period are five fields: teacher · strategy · teaching approach · class · start time. Whatever is entered in a cell becomes a lesson, and from that cell the lesson begins, its data flowing into the plan.",
    "البنيةُ نفسها: الأسبوع واليوم وتخصص الزائر صفوفاً، ومدارسُ المجمع وحصصُها أعمدة":
        "The same structure: week, day and peer subject as rows; the complex's schools and their periods as columns",
    "اختر القطاع والمجمع والمرحلة، واكتب اسم المدرسة — ثم تخصصك إن كنت معلماً.":
        "Choose the sector, complex and stage, and enter the school name — then your subject if you are a teacher.",
    "الأسبوع: اتركه «كل الأسابيع» لترى الفصل كلَّه كما في الإكسل، أو اختر أسبوعاً بعينه.":
        "Week: leave it on “All weeks” to see the whole term as in the spreadsheet, or pick one week.",
    "اكتب في خلية الحصة: اسم المعلم، والإستراتيجية من البنك، والاتجاه التدريسي، والفصل.":
        "In the lesson cell enter: the teacher's name, the strategy from the bank, the teaching approach, and the class.",
    "ومجموعةُ التخصص الزائرة لكل يوم تظهر في أول خلية من صفه وتُعدَّل منها.":
        "The visiting subject team for each day appears in the first cell of its row and is edited there.",
    "اضغط «ابدأ الحصة» في الخلية — تُفتح مرحلةُ التحضير وبياناتُها مضخوخةٌ فيها.":
        "Press “Start lesson” in the cell — the planning stage opens with its data already filled in.",
    "التحضير توأمُ الاستمارة: ستةٌ وأربعون مؤشراً من الخمسين له خانتُه هنا، ويراها الزائرُ تحت المؤشر وهو يرصد. وأربعةٌ لا تُحضَّر: ثلاثةُ أداءٍ يُشاهد في الحصة، وواحدٌ يُتحقَّق من سجلّ التخطيط. فما يُكتب هنا هو ما يُرى في الحصة — ولا يُصدَّر ناقصاً.":
        "The lesson plan is the twin of the observation form: forty-six of the fifty indicators have "
        "their field here, and the visitor sees it under the indicator while rating. Four are not "
        "planned: three are performance observed in the lesson, and one is verified against the "
        "planning record. What is written here is what is seen in the lesson — and it is not issued incomplete.",
    "التحضير توأمُ الاستمارة: كل خانةٍ فيه يقابلها مؤشرٌ يبحث عنه الزائر. فما يُكتب هنا هو ما يُرى في الحصة — ولا يُصدَّر ناقصاً.":
        "The plan is the rubric's twin: every field in it matches an indicator the visitor looks for. What is written here is what is seen in the lesson — and it is not issued incomplete.",
    "التحضير توأمُ الاستمارة: كل خانةٍ فيه يقابلها مؤشرٌ تبحث عن شاهده. ":
        "The plan is the rubric's twin: every field in it matches an indicator whose evidence you seek. ",
    "املأ خانات التحضير بترتيب مجالات الاستمارة، واستعن بزرّ «؟» في كل خانة.":
        "Fill the plan's fields in the order of the rubric's domains, using the “?” button on each field.",
    "وزّع خريطة الزمن حتى يساوي مجموع المراحل زمن الحصة.":
        "Distribute the time map so the stages total the lesson time.",
    "اكتب المهمة المكيَّفة والإثرائية — فعبارة «مراعاة الفروق» بلا مهمةٍ لا تُعدّ شاهداً.":
        "Write the adapted and enrichment tasks — “attending to differences” with no task is not evidence.",
    "اضغط «إصدار التحضير»: لا يعمل قبل اكتمال الخانات الإلزامية، ويقول لك بعدها كم مؤشراً تركتَه بلا شاهدٍ مخطَّط.":
        "Press “Issue the plan”: it does not work until the required fields are complete, and it then tells you how many indicators you left with no planned evidence.",
    "اضغط «إصدار التحضير»: لا يعمل قبل اكتمال كل خانةٍ يقابلها مؤشر.":
        "Press “Issue plan”: it will not work until every field matching an indicator is complete.",
    "ما يُعدّه المعلم قبل الحصة": "What the teacher prepares before the lesson",
    "ورقةُ التنفيذ — ما يُنفَّذ وما يُقرأ قبل الدخول":
        "The run sheet — what is delivered and what is read before entering",
    "بعد أن يكتمل التحضير، هذه ورقتُه جاهزةً للتنفيذ: خريطةُ الزمن ومراحلُ الحصة وبطاقةُ الإستراتيجية والمهمتان المكيَّفة والإثرائية — يُمسكها المعلم في الحصة، ويقرؤها الزائرُ قبل دخوله فيعرف ما يبحث عن شواهده.":
        "Once the plan is complete, this is the sheet ready for delivery: the time map, the lesson stages, the strategy card and the adapted and enrichment tasks — the teacher holds it during the lesson, and the visitor reads it before entering so they know what evidence to look for.",
    "اختر الحصة — وتظهر ورقةُ تنفيذها كاملةً في شاشةٍ واحدة.":
        "Choose the lesson — its full run sheet appears on a single screen.",
    "المعلم: نفّذ المراحل بأزمنتها، والورقةُ أمامك بلا تنقّل بين الشاشات.":
        "Teacher: deliver the stages to their times, with the sheet in front of you — no moving between screens.",
    "الزائر: اقرأها قبل الدخول — فالرصدُ قبل قراءة التحضير يُفقد الشواهد معناها.":
        "Visitor: read it before entering — observing before reading the plan drains the evidence of meaning.",
    "اطبعها إن شئت: تخرج في صفحةٍ أو صفحتين بلا أزرارٍ ولا زوائد.":
        "Print it if you wish: it comes out on one or two pages with no buttons or clutter.",
    "خلاصةُ التحضير في صفحة — تُقرأ قبل الدخول":
        "The plan in summary on one page — read before entering",
    "تقرؤه قبل الحصة — منه تعرف ما تبحث عن شواهده":
        "You read it before the lesson — from it you know what evidence to seek",
    "فاقرأه قبل أن تدخل — تدخل وأنت تعرف ما ينوي المعلمُ فعله، لا تكتشفه معه. ":
        "So read it before you enter — you go in knowing what the teacher intends, not discovering it alongside them. ",
    "وما لم يُكتب هنا لا يُفترض في الحصة.":
        "And what is not written here is not assumed in the lesson.",
    "افتح الحصة من الجدول أو من لوحتك.":
        "Open the lesson from the schedule or from your dashboard.",
    "اقرأ خريطة الزمن ومراحل الحصة وبطاقة الإستراتيجية.":
        "Read the time map, the lesson stages and the strategy card.",
    "ولا تُعدّل شيئاً هنا — التحضيرُ ملكُ صاحبه.":
        "And change nothing here — the plan belongs to its author.",
    "ورقةٌ مختصرةٌ تجمع ما سيُنفَّذ: خريطةُ الزمن ومراحلُ الحصة وبطاقةُ ":
        "A short sheet gathering what will be delivered: the time map, the lesson stages and the ",
    "الإستراتيجية والمهمتان المكيَّفة والإثرائية. يُمسكها المعلمُ في الحصة، ":
        "strategy card and the adapted and enrichment tasks. The teacher holds it during the lesson, ",
    "وتقرؤها أنت قبل دخولك فتعرف ما تبحث عن شواهده.":
        "and you read it before entering so you know what evidence to seek.",
    "افتح الحصة، ثم اقرأ الورقة كاملةً.": "Open the lesson, then read the whole sheet.",
    "اطبعها أو افتحها على جوالك لتكون بين يديك في الحصة.":
        "Print it or open it on your phone so it is at hand during the lesson.",
    "ورقةٌ مختصرةٌ فيها ما سيُنفَّذ في الحصة: خريطةُ الزمن ومراحلُها ":
        "A short sheet with what will be delivered in the lesson: the time map and its stages ",
    "وبطاقةُ الإستراتيجية. والدخولُ على علمٍ بما سيجري خيرٌ من اكتشافه فيها.":
        "and the strategy card. Going in informed is better than discovering it there.",
    "افتح الزيارة المسنَدة إليك، ثم اقرأ الورقة كاملةً.":
        "Open the visit assigned to you, then read the whole sheet.",
    "ما يُملأ أثناء الحصة ولها": "What is filled during and for the lesson",
    "المشرف المختص وحده يرصد الاستمارة وبطاقة الإستراتيجية — وما لا مشرف لتخصصه يرصده الفريق المعاون. ومعلمان زائران يملآن بطاقة الأقران. والشاهد يُرى لا يُفترض: ما لم يُرصد أثناء الحصة لا يُحتسب.":
        "The specialist supervisor alone completes the rubric and the strategy card — and where a subject has no supervisor, the supporting team does. Two peer teachers fill the peer card. Evidence is seen, not assumed: what is not recorded during the lesson does not count.",
    "افتح الحصة، واقرأ تحضير المعلم أولاً — فهو ما تبحث عن شواهده.":
        "Open the lesson and read the teacher's plan first — that is what you seek evidence for.",
    "ارصد الاستمارة مؤشراً مؤشراً، و«لا ينطبق» للاستثناء لا للهروب.":
        "Complete the rubric indicator by indicator; “N/A” is for genuine exceptions, not an escape.",
    "افتح بطاقة تشخيص الإستراتيجية التي أعلنها المعلم وقيّم مؤشراتها العشرة.":
        "Open the diagnostic card for the strategy the teacher declared and rate its ten indicators.",
    "المعلم الزائر يملأ بطاقة الأقران وينقل إجراءً واحداً لنفسه.":
        "The peer teacher fills the peer card and takes one action away for themselves.",
    "النتيجة وبطاقة الجسر والاعتماد": "Result, bridge card and approval",
    "تنتهي الحصة بدرجةٍ موثَّقة وإجراءٍ واحدٍ يُتابَع — لا بانطباعٍ عام. وبطاقة الجسر هي التي تنقل الأثر إلى الحصص اليومية.":
        "The lesson ends with a documented score and one action to follow up — not a general impression. The bridge card is what carries the impact into daily lessons.",
    "راجع الدرجة والنسبة والمستوى، ودرجة مؤشر الإستراتيجية.":
        "Review the score, the percentage and the level, and the strategy indicator's score.",
    "اكتب في بطاقة الجسر إجراءً واحداً محدداً يمكن رؤيته.":
        "Write in the bridge card one specific action that can be seen.",
    "اطبع تقرير الزيارة أو أرسله للمعلم عبر واتساب.":
        "Print the visit report or send it to the teacher on WhatsApp.",
    "وفي الزيارة التالية يُفتح الإجراء للتحقق من تنفيذه.":
        "At the next visit the action is opened to verify it was carried out.",
    "زيارتُك إفادةٌ لا درجة: لا استمارةَ مقيّمين عليك ولا مؤشراتٍ تُقيَّم، ":
        "Your visit is for learning, not a grade: no observer rubric falls to you and no indicators are rated, ",
    "بل وصفُ ما جرى في الحصة، وما أفادك منه، وما ستطبّقه. ":
        "only a description of what happened, what helped you, and what you will apply. ",
    "وما يُكتب بعد أيامٍ يذهب أكثرُه.": "And most of what is written days later is lost.",
    "اقرأ تحضير زميلك أولاً — فمنه تُعرف مواضعُ الانتباه.":
        "Read your colleague's plan first — it shows where to pay attention.",
    "املأ بطاقة الأقران أثناء الحصة أو بعدها مباشرةً.":
        "Fill the peer card during the lesson or straight afterwards.",
    "ولا درجةَ عليك: الدرجةُ للمشرفين وقيادة المدرسة.":
        "And no grade falls to you: grading is for the supervisors and school leadership.",
    "آخرُ خطوةٍ في زيارتك ليست حكماً على زميلك، بل التزامٌ على نفسك: ":
        "The last step of your visit is not a judgement on your colleague but a commitment to yourself: ",
    "إجراءٌ واحدٌ محدَّدٌ إلى حصتك القادمة. وهو ما يُتابَع معك أنت.":
        "one specific action for your next lesson. That is what is followed up with you.",
    "اكتب إجراءً واحداً محدَّداً يمكن رؤيته في حصتك.":
        "Write one specific action that can be seen in your lesson.",
    "وتظهر نتيجةُ الحصة إن رصدها المقيّمون — للاطّلاع لا للتعديل.":
        "The lesson result appears if the observers recorded it — to read, not to edit.",
    "تُملأ أثناء الحصة أو بعدها مباشرةً": "Filled during the lesson or straight afterwards",
    "ثمرةُ الزيارة — إجراءٌ واحدٌ إلى حصتك":
        "The fruit of the visit — one action for your lesson",
    "إجراءٌ واحد تنقله لنفسك": "One action you take for yourself",
    "ابدأ من هنا — ما أُسنِد إليك وما بقي":
        "Start here — what is assigned to you and what remains",
    # أوصافُ الأدوار
    "يحضّر حصته ويصدرها، ثم يرى نتيجتها وإجراء الجسر":
        "Plans and issues their lesson, then sees its result and bridge action",
    "يرى الزيارات المسنَدة إليه، ويقرأ التحضير ويملأ بطاقة الأقران":
        "Sees the visits assigned to them, reads the plan and fills the peer card",
    # ⚠️ دقَّ الوصفُ: الرصدُ للمدير والوكيل على ما لا مشرفَ لتخصصه وحدَه
    "يرى حصص مدرسته وحدها ويجدولها، ويرصد ما لا مشرفَ لتخصصه ويعتمد نتيجته":
        "Sees and schedules only their own school's lessons, and observes and approves "
        "those whose subject has no supervisor",
    "يجدول حصص مدرسته ويسنِد المعلمين الزائرين إليها، ويرصد ما لا مشرفَ لتخصصه":
        "Schedules their school's lessons, assigns peer teachers to them, and observes "
        "those whose subject has no supervisor",
    "يرى حصص تخصصه في المجمع الذي يزوره كل يوم، ويرصدها ويعتمدها":
        "Sees their subject's lessons in the complex they visit each day, observes and approves them",
    # التقارير
    "كل ما ينتجه التطبيق — للطباعة أو التصدير":
        "Everything the app produces — to print or export",
    "تقرير المدارس": "Schools report", "تقرير المعلمين": "Teachers report",
    "تقرير التخصصات": "Subjects report", "تقرير المؤشرات": "Indicators report",
    "تقرير الإستراتيجيات": "Strategies report", "تقرير الاتجاهات": "Approaches report",
    "تقرير التفعيل": "Activation report",
    "لكل مدرسة: كم حصة، وكم حُضِّر ورُصد، ومتوسط النسبة":
        "Per school: how many lessons, how many planned and observed, and the average percentage",
    "لكل معلم: عددُ الحصص والنسبةُ والمستوى وإجراءُ الجسر":
        "Per teacher: number of lessons, percentage, level and bridge action",
    "لكل مادة: عدد الحصص ومتوسط النسبة — لتُعرف المادة المتعثّرة":
        "Per subject: number of lessons and average percentage — to identify the struggling subject",
    "ترتيب المؤشرات الخمسين بمتوسط درجتها — مادة خطة التحسين":
        "The fifty indicators ranked by average score — the substance of the improvement plan",
    "أيُّ إستراتيجيةٍ تُطبَّق أكثر، وبأي درجة":
        "Which strategy is applied most, and at what level",
    "توزيع الاتجاهات التدريسية المعلنة": "Distribution of the declared teaching approaches",
    "مَن فعّل ومَن لم يفعّل: معلمون ومقيّمون وزائرون":
        "Who is active and who is not: teachers, observers and peers",
    "كشفُ المعلمين مقابلَ الجدول: من بلا حصةٍ مسجَّلةٍ بعد — بالاسم والرقم الوظيفي والمادة":
        "The teacher roster against the schedule: who still has no lesson recorded — by name, staff number and subject",
    "لا بيانات بعد — تظهر التقارير بعد جدولة الحصص ورصدها.":
        "No data yet — reports appear once lessons are scheduled and observed.",
    "حصصك ودرجاتُها وإجراءاتُ جسرك":
        "Your lessons, their scores and your bridge actions",
    "ثمانيةٌ ترتيباً — ابدأ بها في حصتك القادمة":
        "Eight in order — start with these in your next lesson",
    "سبعةُ تقاريرَ تُطبع وتُصدَّر": "Seven reports to print and export",
    "تهيئةُ الحصص وإسنادُ الزائرين ومتابعتُهما":
        "Setting up lessons, assigning peers and following both up",
    "حالُ التفعيل في سطرٍ واحد — وما يحتاج تدخّلك":
        "Activation status in one line — and what needs your attention",
    "المخزن · الدعوة · السجلّ · السلّة · النسخة · التفريغ":
        "Store · invite · log · trash · backup · wipe",
    "مرتَّبٌ بالأهمّ — وكلُّ بندٍ يفتح موضعَه":
        "Ordered by importance — each item opens its place",
    "من التخطيط إلى الدرجة: جدولٌ واحد · تحضيرٌ واحد · استمارةٌ واحدة · تقاريرُ تُصدر نفسها":
        "From planning to the score: one schedule · one plan · one rubric · reports that write themselves",
    "ما يفعله كلٌّ في كل مرحلة": "What each role does at each stage",
    "ما يُرى في الحصة لا ما يُقال": "What is seen in the lesson, not what is said",
})

# ═════════ ١١) الرسائلُ والتحذيراتُ وأدواتُ المخزن ═════════
EN.update({
    " · إستراتيجية · اتجاه · فصل · بدء": " · strategy · approach · class · start",
    "◄ السابق": "◄ Previous", "التالي ►": "Next ►",
    "الخادم": "Server", "السجلّ والاسترداد": "Log and restore",
    "النسخ والتفريغ": "Backup and wipe", "تحفيظ": "Memorisation",
    "التخصص الملغى": "Removed subject",
    "موضعُها": "Where it sits",
    "تُنقل إلى تخصصها الصحيح أو تُحذف — ولا تُترك.":
        "Move them to their correct subject or delete them — do not leave them.",
    "حصصٌ مسجَّلةٌ بتخصصٍ لم يبقَ في المنصة، فلا خليةَ لها في الجدول ولا تظهر فيه. ":
        "Lessons recorded under a subject no longer on the platform: they have no cell in the schedule and do not appear in it. ",
    "نمط العمل وتقويمه": "Working mode and its assessment",
    "تاريخ التطبيق المزمع": "Planned delivery date",
    "مثال: الأحد القادم — حصة الرابعة": "e.g. next Sunday — period 4",
    "رقم جوال المعلم (مثال 05xxxxxxxx):": "Teacher's mobile (e.g. 05xxxxxxxx):",
    "إنهاء ← بعد الحصة": "Finish → After the lesson",
    "التعليم المتمايز": "Differentiated instruction",
    # ⚠️ قُصِّر: «Problem- and project-based learning» يحتاج ١٧٨بك في خانةٍ
    #    متاحُها ١٤٢ فكان يُقتطع في القائمة. (أمسكه fitcheck ١ أكتوبر ٢٠٢٦)
    "حل المشكلات والمشاريع": "Problem & project learning",
    "خطة الاستعداد للزيارة": "Visit preparation plan",
    "خطة الزيارات": "Visit plan",
    "إجراء واحد محدد يمكن رؤيته — لا عبارة عامة":
        "One specific action that can be seen — not a general statement",
    "إجراءٌ واحد محدد يُنقل إلى الحصص اليومية ويُتحقق منه في الزيارة التالية":
        "One specific action carried into daily lessons and verified at the next visit",
    "بطاقة زيارة الأقران — شاهدتُ وأطبّق":
        "Peer visit card — what I saw and will apply",
    "مؤشراتُ تطبيقها العشرة — وهي ما يرصده الزائر:":
        "Its ten application indicators — what the visitor records:",
    "التحويل إلى درجة مؤشر الإستراتيجية: ":
        "Conversion to the strategy indicator's score: ",
    "بالدقائق — ومجموعُها زمنُ الحصة": "In minutes — totalling the lesson time",
    "التهيئةُ والغلقُ كما في الخريطة، والتنفيذُ والتقويمُ يُقسمان على النشاطين":
        "Warm-up and closure as on the map; delivery and assessment are split across the two activities",
    "مضخوخةٌ من خليّة الجدول — أكمل ما بقي":
        "Filled from the schedule cell — complete the rest",
    " — من دورك عند الدخول، ولا تُبدَّل هنا":
        " — from your role at sign-in; it is not changed here",
    "لكل حصةٍ زائران — يُسنَدان بالرقم الوظيفي فتظهر الحصةُ في حسابَيهما":
        "Two peers per lesson — assigned by staff number so the lesson appears in both their accounts",
    "والإسنادُ لا يكون على خانةٍ بلا معلم.":
        "And no assignment can be made on a cell with no teacher.",
    "هذه أسماءٌ بلا حصةٍ في الجدول. والجدولُ لا يكتمل قبلها، ":
        "These names have no lesson in the schedule. The schedule is not complete without them, ",
    "لا كشفَ معلمين في هذه المنصة، فلا سبيلَ إلى معرفة الناقص — ":
        "There is no teacher roster on this platform, so the missing cannot be identified — ",
    "وقياسُ الجدول على الكشف لا على نفسه.":
        "the schedule is measured against the roster, not against itself.",
    "كشفُ المعلمين تامُّ الإدخال: لكلِّ اسمٍ حصةٌ في الجدول.":
        "The teacher roster is fully entered: every name has a lesson in the schedule.",
    "كشفُ المعلمين تامُّ الإدخال (": "Teacher roster fully entered (",
    " — والجدولُ ناقصٌ حتى تُسجَّل. ": " — the schedule is incomplete until they are recorded. ",
    "كلُّ حصةٍ مجدولةٍ لها زائرُها": "Every scheduled lesson has its peer",
    "لا حصةَ مجدولةٌ بعد — والجدولُ أولُ الطريق":
        "No lesson scheduled yet — the schedule is the first step",
    "المخزن المشترك غيرُ مربوط — ما يُكتب يبقى على جهاز صاحبه":
        "The shared store is not linked — what is written stays on its author's device",
    "أعمدةُ مدرستك وحدها مفتوحةٌ لك — ولتغييرها اخرج وادخل بمدرسةٍ أخرى.":
        "Only your school's columns are open to you — to change them, sign out and sign in with another school.",
    "الأعمدةُ المفتوحةُ للإدخال: ": "Columns open for entry: ",
    "ترشيحُ الأعمدة بالمدرسة (اختياري):": "Filter columns by school (optional):",
    "لا مرحلةَ مختارةٌ بعد، فكلُّ الأعمدة مفتوحةٌ للإدخال.":
        "No stage chosen yet, so all columns are open for entry.",
    "وقتُ البدء يُكتب في الخانة — فقد تختلف مواعيدُ الحصص بين مدارس المجمع الواحد، ":
        "The start time is entered in the cell — period times can differ between schools in one complex, ",
    "والمكتوبُ في رأس العمود هو الغالبُ في الملف تذكيراً لا إلزاماً.":
        "and the value in the column header is the usual one in the file, as a reminder not a rule.",
    "الترتيبُ هو ترتيبُ يومك فعلاً: تبدأ بالابتدائية ثم المتوسطة ثم الثانوية بحسب أوقات الحصص. ":
        "The order is your actual day: primary first, then intermediate, then secondary, by period times. ",
    "و«افتح» تعرض ورقةَ تنفيذ الحصة — اقرأها قبل دخولك فهي ما تبحث عن شواهده.":
        "“Open” shows the lesson's run sheet — read it before you enter; it is what you seek evidence for.",
    "أيُّ فريقِ تخصّصٍ يزور المجمع في كل يومٍ من كل أسبوع":
        "Which subject team visits the complex on each day of each week",
    "إلى أي مجمعٍ يذهب فريقُ كل تخصصٍ في كل يومٍ من كل أسبوع":
        "Which complex each subject team goes to on each day of each week",
    "يضبط الأسبوعَ واليومَ والمجمعَ من تاريخ اليوم":
        "Sets the week, day and complex from today's date",
    " ليس يومَ زيارةٍ لفريقك — يُنتقل إلى أقرب يوم":
        " is not a visit day for your team — moving to the nearest day",
    "اختر تخصصك أعلاه لتُبنى خطةُ زياراتك.":
        "Choose your subject above to build your visit plan.",
    "اختر تخصصك لتظهر خطتك": "Choose your subject to see your plan",
    "اختر تخصصك — به تُعرف حصصك وزياراتك.":
        "Choose your subject — your lessons and visits are matched by it.",
    "اختر مدرستك — عليها يُبنى كلُّ ما تراه.":
        "Choose your school — everything you see is built on it.",
    " — تخصصُه «أخرى»، فاختره بنفسك.": " — their subject is “Other”, so choose it yourself.",
    "لا حصصَ مسجَّلةً لتخصصك في هذا المجمع بعد — راجع مسؤول الجدولة.":
        "No lessons recorded for your subject in this complex yet — check with the scheduler.",
    "لم تُسجَّل حصصٌ بعد في هذا المجمع.": "No lessons recorded in this complex yet.",
    "لا حصةَ باسمك بعد — سجّل نفسك في خانة حصتك من «جدولي».":
        "No lesson in your name yet — register yourself in your lesson's cell from “My schedule”.",
    "لا حصةَ تطابق الترشيح — وتُسنَد الزياراتُ بعد أن يُكتب اسمُ المعلم في خانتها.":
        "No lesson matches the filter — visits are assigned once the teacher's name is in the cell.",
    "لا صفَّ يطابق الترشيح — أزل البحث أو «المعبّأ فقط».":
        "No row matches the filter — clear the search or “Filled only”.",
    "لا زياراتٍ مسنَدةً إليك بعد": "No visits assigned to you yet",
    "لا زياراتٍ مسنَدةً إليك بعد.": "No visits assigned to you yet.",
    "يُسنِدها وكيلُ المدرسة التعليمي — راجعه إن تأخّرت.":
        "The school's academic deputy assigns them — check with them if they are late.",
    "اختر الحصة لعرض ورقة تنفيذها": "Choose the lesson to see its run sheet",
    "اختر الإستراتيجية في التحضير لتظهر بطاقتُها هنا.":
        "Choose the strategy in the plan for its card to appear here.",
    "اختر الإستراتيجية في جدول الحصص لتفتح بطاقتها.":
        "Choose the strategy in the schedule to open its card.",
    "لم تُعلَن إستراتيجيةٌ لهذه الحصة في الجدول":
        "No strategy has been declared for this lesson in the schedule",
    "تحضير هذه الحصة لم يُصدَر بعد — والرصد قبل قراءة التحضير يُفقد الشواهد معناها.":
        "This lesson's plan is not issued yet — observing before reading the plan drains the evidence of meaning.",
    "تحضيرُ هذه الحصة لم يُصدَر بعد، فورقةُ التنفيذ ناقصة.":
        "This lesson's plan is not issued yet, so the run sheet is incomplete.",
    "لا يُصدَّر التحضير قبل اكتمال ما يقابله مؤشرٌ في الاستمارة — الناقص:":
        "The plan is not issued until every field matching a rubric indicator is complete — missing:",
    "ظهر الآن للزائرين والمقيّمين في مرحلة أداء الحصة.":
        "It is now visible to peers and observers at the lesson-delivery stage.",
    "خريطة الزمن — المجموع ": "Time map — total ",
    "خريطة الزمن — اكتب «زمن الحصة» في بيانات الحصة أولاً":
        "Time map — enter the “lesson time” in the lesson data first",
    " — اضغط «وزّع الزمن على المراحل»": " — press “Distribute the time across the stages”",
    "زمنا الأولى بالرعاية والموهوبين أكبرُ من زمن التنفيذ — وهما داخله لا خارجه":
        "The priority-care and gifted times exceed the delivery time — they sit inside it, not outside",
    "سيُكتب فوق الأزمنة التي كتبتَها بنفسك في: ":
        "This will overwrite the times you entered yourself in: ",
    "\nوتُستبدل قيمُها بما في الجدول.\n\nأتُتابع؟":
        "\nTheir values will be replaced with those in the schedule.\n\nContinue?",
    "لم يرصد أحدٌ هذه الحصة بعد.": "No one has observed this lesson yet.",
    "لا تُعتمد حصةٌ لم يرصدها أحد.": "A lesson no one has observed cannot be approved.",
    "بعد الاعتماد تُقفل الحصة: لا يُعدَّل جدولُها ولا تحضيرُها ولا رصدُها.\n\nأتُتابع؟":
        "After approval the lesson is locked: its schedule, plan and observations cannot be changed.\n\nContinue?",
    "فكُّ الاعتماد يُعيد فتحَ الحصة للتعديل — ويُسجَّل باسمك.\n\nأتُتابع؟":
        "Unlocking reopens the lesson for editing — and is recorded in your name.\n\nContinue?",
    "هذه الحصة معتمدةٌ ومقفولة — رصدُها مغلقٌ للتعديل. ":
        "This lesson is approved and locked — its observations are closed to editing. ",
    "ولفكِّ الاعتماد: مرحلةُ «بعد الحصة».": "To unlock it: the “After the lesson” stage.",
    "◆ حصةٌ معتمدةٌ ومقفلة — اعتمدها ": "◆ Approved and locked lesson — approved by ",
    ". لا تُعدَّل بياناتُها ولا تحضيرُها ولا رصدُها.":
        ". Its data, plan and observations cannot be changed.",
    "لا حصةَ تنتظر الاعتماد": "No lesson awaits approval",
    "حُفظت بطاقتك — ويظهر إجراؤك في تقاريرك.":
        "Your card is saved — your action appears in your reports.",
    "حذف هذه الحصة وكل ما عُلِّق بها؟": "Delete this lesson and everything attached to it?",
    ".\nالمسحُ يحذفها وما عُلِّق بها. أتُتابع؟":
        ".\nClearing deletes it and everything attached. Continue?",
    "هذه الحصة فيها ": "This lesson has ",
    " حصة\n• التحضيراتُ والرصدُ وبطاقاتُ الأقران\n":
        " lessons\n• plans, observations and peer cards\n",
    "• سلّةُ المحذوفات وسجلُّ العمليات\n\nلا يُستردُّ شيءٌ بعده. أتُتابع؟":
        "• the trash and the activity log\n\nNothing can be restored afterwards. Continue?",
    "الاستردادُ يعيد الحصةَ وتحضيرَها ورصدَها وبطاقاتِ أقرانها معاً. ":
        "Restoring brings back the lesson with its plan, observations and peer cards together. ",
    "ويمتنع إن كانت خانتُها قد شُغِلت بحصةٍ أخرى بعد الحذف.":
        "It is refused if its cell has been taken by another lesson since the deletion.",
    "لا يمكن الاسترداد: خانةُ هذه الحصة شُغِلت بحصةٍ أخرى بعد حذفها.":
        "Cannot restore: this lesson's cell was taken by another lesson after it was deleted.",
    "لا محذوفات — وما يُحذف يظهر هنا ويُستردّ بنقرة.":
        "Nothing deleted — anything deleted appears here and is restored with one click.",
    "يُحفظ المحذوفُ ثلاثين يوماً ثم يُمحى نهائياً":
        "Deleted items are kept for thirty days then permanently erased",
    "يُحفظ المحذوفُ ثلاثين يوماً ويُستردُّ بنقرة":
        "Deleted items are kept for thirty days and restored with one click",
    "من فعل ماذا ومتى — آخر ٦٠٠ عملية": "Who did what and when — the last 600 entries",
    "يُسجَّل ما يغيّر الحقيقة: تسجيلُ حصةٍ وتعديلُ حقلٍ وحذفٌ واستردادٌ وإصدارُ تحضيرٍ ":
        "What changes the record is logged: registering a lesson, editing a field, deleting, restoring, issuing a plan, ",
    "وبدءُ رصدٍ وبطاقةُ أقرانٍ وتغييرُ دوران — ولا تُسجَّل القراءةُ ولا التنقّل.":
        "starting an observation, a peer card and a rota change — reading and navigation are not logged.",
    "ستُّ عملياتٍ — والسجلُّ كاملاً في أدوات المنصة":
        "Six entries — the full log is in the platform tools",
    "سحبُ ما كتبه غيرُك على أجهزتهم": "Pull what others have written on their devices",
    "تُنزَّل بياناتُ المنظومة كلُّها ملفاً على جهازك":
        "The system's entire data downloads as a file to your device",
    "نسخة-منصة-الحصة-الموحدة.json": "unified-lesson-platform-backup.json",
    "محوٌ كاملٌ على كل الأجهزة — بعد نسخةٍ وتأكيدٍ مكتوب":
        "Complete erase on all devices — after a backup and a typed confirmation",
    "محوٌ كاملٌ للمنظومة — بعد نسخةٍ احتياطيةٍ وتأكيدٍ مكتوب":
        "Complete erase of the system — after a backup and a typed confirmation",
    "محوٌ نهائيٌّ لا يُستردّ بعده. أتُتابع؟":
        "A permanent erase with no restore afterwards. Continue?",
    "تفريغٌ كاملٌ لبيانات المنظومة على كل الأجهزة:\n\n":
        "A complete wipe of the system's data on every device:\n\n",
    "ستُحفظ نسخةٌ احتياطيةٌ على جهازك أولاً.\n\n":
        "A backup will be saved to your device first.\n\n",
    "فُرّغت بيانات المنظومة على المخزن المشترك.\nوالنسخةُ الاحتياطيةُ على جهازك.":
        "The system's data on the shared store has been wiped.\nThe backup is on your device.",
    "⛔ لم يستجب الخادمُ للاستبدال.\n\n": "⛔ The server did not accept the replacement.\n\n",
    "الصق رابط المخزن المشترك ليرى كلُّ أفراد المنظومة البيانات نفسها،\n":
        "Paste the shared store link so everyone in the system sees the same data,\n",
    "أو اتركه فارغاً للعمل على هذا الجهاز وحده:\n\n":
        "or leave it empty to work on this device alone:\n\n",
    "وهو رابطُ الخادم الذي نشرتَه — ينتهي بـ.workers.dev أو بنطاقك.\n":
        "It is the server link you published — ending in .workers.dev or your own domain.\n",
    "⛔ الرابط لا يستجيب كما ينبغي:\n": "⛔ The link is not responding as it should:\n",
    "استجاب ولم يُرجع ما كُتب فيه — تأكّد أن المخزن KV مربوطٌ ":
        "It responded but did not return what was written — check the KV store is bound ",
    "باسم DB وأنك ألصقت الكود كاملاً.": "under the name DB and that you pasted the whole code.",
    "الكتابةُ تعمل. والقراءةُ تأخّرت ثوانيَ لأن مخزن الخادم يتّسق تدريجياً — وهذا طبيعي.":
        "Writing works. Reading lagged a few seconds because the server store is eventually consistent — which is normal.",
    "تعذّر التحقّق في هذا المتصفح.": "Verification failed in this browser.",
    "تعذّر الحفظ محلياً — تحقّق من مساحة المتصفح.":
        "Could not save locally — check the browser's storage space.",
    "نُسخ رابط الدعوة.\n\nأرسله لمن يعنيه — يفتحه فيُربط جهازه تلقائياً،\n":
        "Invite link copied.\n\nSend it to whoever needs it — opening it links their device automatically,\n",
    "ولا يُطلب منه لصقُ شيء.\n\n": "and they are not asked to paste anything.\n\n",
    "يُرسَل للمدرسة فيُربط جهازُ من يفتحه تلقائياً":
        "Sent to the school; whoever opens it has their device linked automatically",
    "المكتوبُ هنا لا يصل إلى بقية المنظومة، ولا يصل منها شيء — والعلاجُ ربطُ الخادم مرةً واحدة.":
        "What is written here does not reach the rest of the system, and nothing reaches it from them — the remedy is to link the server once.",
    "\n\nتأكّد أنه الرابطُ الذي سلَّمه مديرُ التخطيط والاعتماد المدرسي.":
        "\n\nMake sure it is the link provided by the Director of Planning and School Accreditation.",
    "راجع إدارة التخطيط والاعتماد لتزويدك برابط الدخول الصحيح.":
        "Contact the Planning and Accreditation Department for the correct access link.",
    "راجع مديرَ التخطيط والاعتماد المدرسي لترقيته ثم أعد المحاولة.":
        "Contact the Director of Planning and School Accreditation to upgrade it, then try again.",
    "والرابطُ يُطلب من مدير التخطيط والاعتماد المدرسي — ولا يُنشأ من الصفحة.":
        "The link is obtained from the Director of Planning and School Accreditation — it is not created from this page.",
    "بياناتك تُحفظ في هذا الجهاز، وتصل إلى المنظومة عبر الرابط الذي زُوّدت به.":
        "Your data is saved on this device and reaches the system through the link you were given.",
    "البريدُ وكلمةُ المرور — ولك وحدك أدواتُ المنظومة":
        "Email and password — the system tools are yours alone",
    "البريدُ أو كلمةُ المرور غيرُ صحيحة.": "The email or password is incorrect.",
    "محفوظٌ محلياً — بانتظار الشبكة": "Saved locally — waiting for the network",
    "لا عمليات بعد.": "No activity yet.",
    # أدلّةُ الاستخدام
    "دليلُ استخدام المنصة — المعلم القائم بالحصة":
        "Platform user guide — Teaching teacher",
    "دليلُ استخدام المنصة — المعلم الزائر": "Platform user guide — Peer teacher",
    "دليلُ استخدام المنصة — مدير المدرسة": "Platform user guide — School principal",
    "دليلُ استخدام المنصة — الوكيل التعليمي": "Platform user guide — Academic deputy",
    "دليلُ استخدام المنصة — المشرف التربوي": "Platform user guide — Subject supervisor",
    "نشرة آلية الحصص الموحَّدة": "Unified lesson programme briefing",
    "نشرة استخدام الاستمارة": "Rubric usage briefing",
    "نشرة استخدام نموذج التحضير": "Planning template usage briefing",
    "نشرات الاتجاهات التدريسية": "Teaching approach briefings",
    "نشرات الاتجاهات التدريسية الستة": "The six teaching approach briefings",
})

# ═════════ ١٢) خياراتُ الحقول وتلميحاتُها — آخرُ دفعة ═════════
EN.update({
    "الربط بالحياة": "Real-life links", "تحضيره": "their plan",
    "ورقةُ تنفيذٍ من تحضيرٍ صدر في ": "Run sheet from a plan issued on ",
    "إصدار ": "Build ", "اليوم \\ الأسبوع": "Day \\ Week",
    "علم بالقلم": "Pen in hand", "وربطها بمحتوى الدرس": "and linking it to the lesson content",
    "الهوية الوطنية": "National identity",
    "أدوات مادية": "Physical resources", "سبورة ذكية": "Smart board",
    "فيديو": "Video", "مختبر افتراضي": "Virtual lab",
    "محتوى إلكتروني للدرس": "Digital content for the lesson",
    "اسم المنصة والمهمة المُسنَدة": "Platform name and the assigned task",
    "الأداة بيد الطالب": "The tool in the student's hands",
    "الأداة أو المعيار": "Tool or criterion",
    "سمعي": "Auditory", "بصري": "Visual", "حسّي/محسوسات": "Tactile / concrete",
    "فردية": "Individual", "زوجية": "Paired",
    "مجموعات تعاونية": "Cooperative groups",
    "مستويات متدرّجة": "Graded levels", "منافسة/لعبة": "Competition / game",
    "تمثيل أدوار": "Role play", "حل مشكلات": "Problem solving",
    "تقييم أقران": "Peer assessment",
    "على السبورة": "On the board", "على الشاشة": "On the screen",
    "معلنة شفهياً في بداية الحصة": "Stated aloud at the start of the lesson",
    "مصدر للقراءة والكتابة في الصف": "A reading and writing resource in the room",
    "مصدر أو محسوس للحساب": "A numeracy resource or manipulative",
    "مقاعد مهيّأة للعمل التعاوني": "Seating arranged for cooperative work",
    "نص يقرؤه الطلاب": "A text the students read",
    "كتابة إجابة أو جملة": "Writing an answer or a sentence",
    "حساب ينفّذه الطلاب": "A calculation the students carry out",
    "قراءة بيانات": "Reading data",
    "ناقد: تحليل · استنتاج · تقويم": "Critical: analysis · inference · evaluation",
    "إبداعي: طلاقة · مرونة · أصالة": "Creative: fluency · flexibility · originality",
    "السؤال أو المهمة التي تنمّي التفكير":
        "The question or task that develops thinking",
    "سؤال أو نشاط قبلي يكشف المعرفة السابقة":
        "A prior question or activity that reveals existing knowledge",
    "بعد كل هدف — الأداة": "After each objective — the tool",
    "اللحظة التي يوظّف فيها الطالب الملاحظة لتحسين عمله":
        "The moment the student uses the comment to improve their work",
    "التلخيص الشفهي": "Oral summary",
    "التعبير أمام الزملاء": "Presenting to classmates",
    "نقاشات ختامية": "Closing discussions",
    "توزيع الأدوار بالأسماء": "Assigning roles by name",
    "أسئلة لمن لم يشارك": "Questions for those who have not spoken",
    "دعم من يتعثّر": "Support for those who struggle",
    "تعزيز لفظي محدد": "Specific verbal reinforcement",
    "احتفاء بالمنجز": "Celebrating the achievement",
    "مثال أو تطبيق من حياة الطلاب":
        "An example or application from the students' lives",
    "للفئات الأولى بالرعاية — ما هي، ولمن، ومتى تُسلَّم":
        "For students needing priority care — what it is, for whom, and when it is due",
    "لسريعي التعلم والموهوبين — تنمّي تفكيراً أعلى لا مزيداً من التمارين":
        "For fast learners and the gifted — developing higher-order thinking, not more exercises",
    # مفرداتُ فرق التخصص
    "لغتي + إسلامية": "Arabic + Islamic studies",
    "علوم + حاسب آلي": "Science + Computing",
    "رياضيات واجتماعيات": "Mathematics and social studies",
    # ⚠️ أسماءُ الأشخاص والجهات لا تُترجَم — وتُثبَّت هنا كي لا يطلبها الحارس
    "أ. أحمد صيام": "أ. أحمد صيام", "أ. محمود كامل": "أ. محمود كامل",
    "مدارس ابن خلدون": "Ibn Khaldun Schools",
    "مدير المجمع": "Complex Director", "مديرة المجمع": "Complex Director",
    "رياض الأطفال": "Kindergarten",   # مرحلةُ الروضة في نطاق المشرفة
    # ── سجلُّ الإشراف · الفريق المعاون · حارسُ التعارض (٣٠ سبتمبر ٢٠٢٦) ──
    "الفريق المعاون": "Supporting team",
    # ── صفحةُ الاستعداد والتحضير: أدواتُها وبطاقةُ إستراتيجيتها ومخرجُ الخانة الفارغة ──
    "أدوات التحضير": "Preparation tools",
    "لم تُرصد": "Not scored", "رُصدت": "Scored", "معتمدة": "Approved",
    # ── تقريرُ الحصص بلا مشرفٍ مختص (١ أكتوبر ٢٠٢٦) ──
    "حصصٌ بلا مشرفٍ مختص": "Lessons with no specialist supervisor",
    "التخصصاتُ التي لا مشرفَ لها في نطاقك: من يرصدها، وهل رُصدت بعد":
        "Subjects with no supervisor in your scope: who scores them, and whether they have been scored",
    "حصةً بلا مشرفٍ مختص": "lessons with no specialist supervisor",
    "تنتظر الرصد": "awaiting scoring",
    "لا حصةَ في نطاقك بلا مشرفٍ مختص — كلُّ تخصصٍ له مشرفُه.":
        "No lesson in your scope lacks a specialist supervisor — every subject has one.",
    "هذه حصصُ تخصصاتٍ لا مشرفَ مختصّاً لها، فرصدُها على الفريق المعاون: ":
        "These are lessons of subjects with no specialist supervisor, so the supporting team scores them: ",
    ". ولا يرصدها غيرُهم.": ". No one else scores them.",
    "المدرسة والمجمع": "School and complex",
    "الاعتماد": "Approval",
    "الموعد": "When",
    " ليس يومَ زيارةٍ لك — يُنتقل إلى أقرب يوم":
        " is not one of your visit days — jumping to the nearest one",
    "اليوم: ": "Today: ",
    # ── طريقةُ التحضير بالذكاء الاصطناعي (٣٠ سبتمبر ٢٠٢٦) ──
    "طريقة التحضير بالذكاء الاصطناعي": "Preparing with AI",
    "صفحات الدرس في الكتاب": "Lesson pages in the textbook",
    "كيف تعمل — أربع خطوات": "How it works — four steps",
    "تنسخ أمراً يحمل درسَك وإستراتيجيتَك واتجاهَك، ويكتب لك المساعدُ التحضيرَ ووسائلَه، فتُلصقه هنا فيملأ الخانات":
        "You copy a prompt carrying your lesson, strategy and approach; the assistant writes the preparation and its aids; you paste it back and the fields fill themselves",
    "**أكمل بيانات الحصة أعلاه** (عنوان الدرس وصفحاته في الكتاب وزمن الحصة) واختر الإستراتيجية والاتجاه — فمنها يُبنى الأمر.":
        "**Complete the lesson data above** (lesson title, its textbook pages, and lesson duration) and choose the strategy and approach — the prompt is built from them.",
    "**انسخ الأمر**: يحمل مادتك وصفَّك وعنوانَ درسك وصفحاته، ومؤشرات إستراتيجيتك العشرة، وشواهد اتجاهك الثلاثة، ونموذجَ التحضير بحقوله.":
        "**Copy the prompt**: it carries your subject, grade, lesson title and pages, your strategy\u2019s ten indicators, your approach\u2019s three evidences, and the preparation template with all its fields.",
    "**ألصقه في أي مساعدٍ ذكيّ** — ويطلب منه الأمرُ أيضاً أن يُصمّم وسائلَ الحصة جاهزةً للاستعمال لا أن يصفها.":
        "**Paste it into any AI assistant** — the prompt also asks it to design the lesson aids ready to use, not merely describe them.",
    "**ألصق جوابه هنا** (أو ارفع ملف وورد) ثم «وزّع على الخانات» — فتمتلئ الخاناتُ كلُّها، وتُراجعها وتُصدر تحضيرك.":
        "**Paste its answer here** (or upload a Word file) then \u00abDistribute to the fields\u00bb — every field fills, you review them and issue your preparation.",
    "اكتب أولاً ما شاهدتَه وتنوي تطبيقه — لا تُحفظ بطاقةٌ خاوية.":
        "First write what you saw and intend to apply — an empty card is not saved.",
    "تعذّرت هجرةُ البيانات — راجع إدارة التخطيط":
        "Data migration failed — contact the planning department",
    "افتح صفحة التحضير": "Open the preparation page",
    "لا حصةَ باسمك في الجدول بعد، فلا تقريرَ لك. وتقريرُك يُبنى وحدَه متى ":
        "No lesson under your name in the schedule yet, so there is no report. Your report builds itself once ",
    "سجّلتَ حصتك في الجدول وأصدرتَ تحضيرَها ورصدها المشرف.":
        "you record your lesson, issue its preparation, and the supervisor scores it.",
    "لا زيارةَ مسنَدةً إليك بعد. والزياراتُ يُسنِدها الوكيلُ التعليمي من ":
        "No visit assigned to you yet. Visits are assigned by the educational deputy from ",
    "شاشة «إسناد الزائرين» بالرقم الوظيفي — فإن لم تظهر زيارتُك فراجعه ":
        "the peer-assignment screen, by staff number — if your visit does not appear, check with them ",
    "وتأكّد أن رقمك المسجَّل هو الذي دخلتَ به.":
        "and make sure the number recorded is the one you signed in with.",
    "لكل زيارة: اقرأ تحضير المعلم قبل دخولك — فهو ما تبحث عن شواهده — ":
        "For each visit: read the teacher\u2019s preparation before you enter — it is what you look for evidence of — ",
    "ثم املأ بطاقة الأقران وانقل إجراءً واحداً لنفسك.":
        "then fill the peer card and carry one action over to yourself.",
    "النموذجُ ونشرتُه · بطاقاتُ الإستراتيجيات · نشراتُ الاتجاهات":
        "The template and its bulletin · strategy cards · approach bulletins",
    "بنك بطاقات الإستراتيجيات التسع عشرة": "The nineteen strategy cards",
    "بطاقة الإستراتيجية المعلنة": "The declared strategy card",
    "لم تُعلَن بعد": "not declared yet",
    "مؤشراتُ تطبيقها العشرة — وهي ما يرصده الزائر في حصتك:":
        "Its ten implementation indicators — what the visitor scores in your lesson:",
    "افتح بطاقة «": "Open the card for \u00ab",
    "اختر الإستراتيجية في خانة الجدول أو في التحضير، فتظهر مؤشراتُها العشرة هنا ":
        "Choose the strategy in the schedule cell or in the preparation, and its ten indicators appear here ",
    "ومعها رابطُ بطاقتها.": "with a link to its card.",
    "لا حصةَ باسمك في الجدول بعد. وسببُها أحدُ اثنين: إمّا أنك لم تسجّل حصتك ":
        "No lesson under your name in the schedule yet. One of two reasons: either you have not recorded your lesson ",
    "في جدول الحصص الموحَّدة، وإمّا أن اسمك أو رقمك الوظيفي كُتب في الجدول ":
        "in the unified lesson schedule, or your name or staff number was written in the schedule ",
    "على غير ما دخلتَ به.": "differently from how you signed in.",
    "اذهب إلى الجدول وسجّل حصتك": "Go to the schedule and record your lesson",
    "تدخل باسم: ": "You are signed in as: ",
    " · الرقم الوظيفي ": " · staff number ",
    " — واكتبه في خلية الجدول كما هو.": " — write it in the schedule cell exactly so.",
    "إشرافٌ بالمرحلة": "Stage-wide supervision",
    "المقيّم: ": "Scored by: ",
    ". والمديرُ يطّلع ويعلّق، والوكيلُ يتابع التعبئة.":
        ". The principal views and comments; the deputy follows completion.",
    "لا مشرفَ مختصٌّ لهذا التخصص في هذه المدرسة، ":
        "No specialist supervisor for this subject at this school, ",
    "فالتقييمُ للفريق المعاون: ": "so scoring falls to the supporting team: ",
    "لا حصصَ مسجَّلةً لموادك في هذا المجمع بعد — راجع مسؤول الجدولة.":
        "No lessons recorded for your subjects at this complex yet — check with the scheduler.",
    "اختر مجمعك — عليه يُبنى كلُّ ما تراه.":
        "Choose your complex — everything you see is built on it.",
    "هذا الرقمُ ليس في سجلّ الإشراف التربوي — راجع ":
        "This number is not on the supervision register — contact ",
    "هذا الرقمُ ليس في سجلّ الإشراف التربوي.":
        "This number is not on the supervision register.",
    "يومٌ فيه تعارض": "days with a clash",
    "تعارض: ": "Clash: ",
    "تعارض: مشرفُ هذه المادة (": "Clash: the supervisor of this subject (",
    "مشرفُ هذه المادة (": "The supervisor of this subject (",
    ") له حصةٌ في ": ") has a lesson at ",
    ") له حصةٌ مسجَّلةٌ في ": ") has a lesson recorded at ",
    " في اليوم نفسِه من هذا الأسبوع.": " on the same day of this week.",
    " في اليوم نفسِه من هذا الأسبوع، ": " on the same day of this week, ",
    "ولا يكون في مجمعين في يوم. انقل هذه الحصة إلى يومٍ أو أسبوعٍ آخر.":
        "and cannot be at two complexes in one day. Move this lesson to another day or week.",
    " — موادُّك في ": " — your subjects fall at ",
    ". والزيارةُ مجمعٌ واحدٌ في اليوم، ": ". A visit is one complex a day, ",
    "فاختر واحداً ونقِّل الباقي إلى أسبوعٍ آخر مع الوكيل.":
        "so pick one and move the rest to another week with the deputy.",
    "فريق متابعة التقويم الداخلي": "Internal Evaluation Follow-up Team",
    "يتابع مجمعه كلَّه، ويرصد الحصص التي لا مشرفَ لتخصصها":
        "Follows the whole complex, and scores lessons whose subject has no supervisor",
    "تتابع مجمعها كلَّه، وترصد الحصص التي لا مشرفةَ لتخصصها":
        "Follows the whole complex, and scores lessons whose subject has no supervisor",
    "اثنان من الإدارة العامة: يتابعان الحصص بلا مشرفٍ مختص ولا يرصدان":
        "Two from the general administration: they follow lessons with no specialist supervisor, without scoring",
    "اثنتان من الإدارة العامة: تتابعان الحصص بلا مشرفةٍ مختصة ولا ترصدان":
        "Two from the general administration: they follow lessons with no specialist supervisor, without scoring",
    "مدير التخطيط والاعتماد المدرسي": "Director of Planning and School Accreditation",
    "الابتدائية- المنار": "الابتدائية- المنار", "المتوسطة- المنار": "المتوسطة- المنار",
    "الثانوية- المنار": "الثانوية- المنار",
    "الابتدائية- الياسمين": "الابتدائية- الياسمين",
    "المتوسطة- الياسمين": "المتوسطة- الياسمين",
    "الثانوية- الياسمين": "الثانوية- الياسمين",
    "المتوسطة- عرقة": "المتوسطة- عرقة", "الثانوية- عرقة": "الثانوية- عرقة",
})

# ⚠️ **أسماءُ المشرفين لا تُترجَم** فتُخرَّج إلى نفسها — وتُقرأ من سجلّها آلياً،
#    فلا تُكتب بيدٍ ولا يسقط اسمٌ عند تحديث السجلّ.
import supdb as _SUPDB
for _g in ("f", "m"):
    for _r in _SUPDB.recs(_g):
        EN.setdefault(_r["name"], _r["name"])

EN["أخرى"] = "Other"    # تخصصٌ غيرُ مصنَّفٍ في الكشف — يختاره صاحبُه

# ═════════ ١٣) صيغٌ مؤنَّثةٌ كُتبت في المصدر لا بالمؤنِّث ═════════
# ⚠️ أكثرُ المؤنَّث يُشتقُّ آلياً في platform.py، وهذه كُتبت مؤنَّثةً بيدٍ في
#    `G("مذكَّر","مؤنَّث")` فلم يمرَّ عليها المؤنِّث — فلا سبيلَ إلى اشتقاقها.
EN.update({
    "المعلمة القائمة بالحصة": "Teaching teacher",
    "المشرفة التربوية المختصة": "Subject supervisor",
    "المشرفة التربوية": "Subject supervisor",
    "تحضّر حصتها وتصدرها، ثم ترى نتيجتها وإجراء الجسر":
        "Plans and issues their lesson, then sees its result and bridge action",
    "ترى الزيارات المسنَدة إليها، وتقرأ التحضير وتملأ بطاقة الأقران":
        "Sees the visits assigned to them, reads the plan and fills the peer card",
    # ⚠️ ونسخةُ البنات لها صياغتُها — ومعجمُها يُفحص ببنائها لا ببناء البنين
    "ترى حصص مدرستها وحدها وتجدولها، وترصد ما لا مشرفةَ لتخصصه وتعتمد نتيجته":
        "Sees and schedules only their own school's lessons, and observes and approves "
        "those whose subject has no supervisor",
    "تجدول حصص مدرستها وتسنِد المعلمات الزائرات إليها، وترصد ما لا مشرفةَ لتخصصه":
        "Schedules their school's lessons, assigns peer teachers to them, and observes "
        "those whose subject has no supervisor",
    "ترى حصص تخصصها في المجمع الذي تزوره كل يوم، وترصدها وتعتمدها":
        "Sees their subject's lessons in the complex they visit each day, observes and approves them",
    "دليلُ استخدام المنصة — المعلمة القائمة بالحصة":
        "Platform user guide — Teaching teacher",
    "دليلُ استخدام المنصة — المشرفة التربوية":
        "Platform user guide — Subject supervisor",
    # ⚠️ اسمُ علَمٍ — يُعرض كما هو
    "أ. هدى المشجري": "أ. هدى المشجري",
})

# ═════════ ١٤) ما كان الحارسُ الخاطئُ يحميه ═════════
# ⛔ ثلاثةٌ وأربعون نصّاً معروضاً حُسبت «مفاتيحَ» لأن نقطتَي الشرط الثلاثي
#    تشبهان نقطتَي مفتاح الكائن — فلم يطلبها الحارسُ وبقيت عربيةً.
EN.update({
    "عربي": "عربي",   # ⛔ تسميةُ زرِّ العودة — تبقى عربيةً ليقرأها صاحبُها
    "التبديل إلى العربية": "Switch to Arabic",
    "جدولي": "My schedule", "جدول مدرستي": "My school's schedule",
    "جدول المجمع (للاطّلاع)": "Complex schedule (view only)",
    "من يزورنا": "Who visits us", "من يزور مدرستنا": "Who visits our school",
    "خطواتُ زيارتك": "Your visit steps",
    "حصصك المسجَّلة": "Your recorded lessons",
    "اختر الحصة التي تزورها": "Choose the lesson you are visiting",
    "افتح الإسناد": "Open assignment",
    "مفعِّل": "Active", "مكتملة": "Complete", "متميّز": "Outstanding",
    "حُضِّر": "Planned", "صدر": "Issued", "يحتاج": "Needs", "راجع": "Contact",
    "التحضير مُصدَر": "Plan issued",
    "إخفاء التلميحات": "Hide hints", "إظهار الشريط": "Show the sidebar",
    "أتممتَ زياراتك كلَّها ✓": "You have completed all your visits ✓",
    "  ← فريقك": "  ← your team", "  ← مجمعك": "  ← your complex",
    " حصةً مجدولةً": " lessons scheduled",
    " حصةً لم يصدر تحضيرُها بعد": " lessons whose plan is not issued yet",
    " حصةً بلا معلمٍ زائرٍ مُسنَد": " lessons with no peer teacher assigned",
    " حصةً رُصدت ولم تُعتمد نتيجتُها": " lessons observed whose result is not approved",
    " زيارةً تنتظر بطاقتك": " visits awaiting your card",
    " — وسواها للقراءة.": " — the rest are read-only.",
    "مراحلُ التدريس — اختر واحدةً أو أكثر:": "Teaching stages — choose one or more:",
    "المخزن المشترك مربوط — ويرى الجميعُ البياناتِ نفسَها":
        "The shared store is linked — everyone sees the same data",
    "مربوطٌ — ويرى الجميعُ البياناتِ نفسَها":
        "Linked — everyone sees the same data",
    "تعذّر الحفظ المشترك — يُعاد قريباً":
        "Shared save failed — it will retry shortly",
    "✓ متطابق": "✓ Match",
    "لا يطابق رقماً في الكشف — اكتب اسمك يدوياً.":
        "No matching number in the roster — enter your name manually.",
    "لا حصةَ مسجَّلةٌ بعد — والتسجيل بزرّ «سجّلني هنا» في خانة الحصة التي ستُنفَّذ فيها.":
        "No lesson recorded yet — register with the “Register me here” button in the cell of the lesson you will teach.",
    "لا حصص باسمك في الجدول — تأكّد أن اسمك مكتوبٌ في الجدول كما هو مسجَّل.":
        "No lessons in your name in the schedule — check your name is written there exactly as registered.",
    "لم تُصدَر ورقةُ التحضير بعد — أكملها في مرحلة «الاستعداد والتحضير» ثم عد إلى هنا.":
        "The plan has not been issued yet — complete it at the “Preparation and planning” stage, then come back here.",
    "\n\nتأكّد أنه رابطُ الخادم الذي نشرتَه، بلا مسافةٍ ولا شَرطةٍ في آخره.":
        "\n\nMake sure it is the server link you published, with no trailing space or slash.",
    "خادمُك يعمل بشفرةٍ قديمةٍ لا تعرف الاستبدال — انشر النسخة الجديدة ثم أعد المحاولة.":
        "Your server is running old code that does not support replacement — publish the new version, then try again.",
    "كُتب واستُرجع بنجاح — البيانات ستُشارَك بين الأجهزة.":
        "Written and read back successfully — data will be shared between devices.",
    "وبعد الربط انسخ «رابط الدعوة» وأرسله للمدارس.":
        "Once linked, copy the “Invite link” and send it to the schools.",
})

# ⚠️ أسابيعُ التقويم الأولى — ظهرت مفاتيحَ في «rot» بعد أن صارت المفاتيحُ تُمسح
EN.update({
    "الأسبوع الأول": "Week 1", "الأسبوع الثاني": "Week 2",
    "الأسبوع الثالث": "Week 3", "الأسبوع الرابع": "Week 4",
    "الأسبوع الخامس": "Week 5",
    # وخياراتُ أدوات التقويم في نموذج التحضير
    "ملف إنجاز": "Portfolio", "مهام أدائية": "Performance tasks",
    "مهام مفتوحة النهاية": "Open-ended tasks", "مشروعات": "Projects",
    "ذاتي": "Self", "أقران": "Peer",
})

# ═════════ ١٥) بوّابةُ الدخول: رسائلُ التحقّق ═════════
EN.update({
    "اكتب رقمك الوظيفي — به تُعرف حصصك.":
        "Enter your staff number — your lessons are matched by it.",
    "الرقمُ الوظيفي ": "The staff number is ",
    " منازل — وهذا ": " digits — this one is ",
    " منازل)": " digits)",
    "الرقم الوظيفي (": "Staff number (",
    "هذا الرقمُ ليس في كشف المنسوبين — راجع ":
        "This number is not on the staff roster — contact ",
    "الاسمُ حروفٌ لا أرقام.": "The name is letters, not digits.",
    "اكتب الاسمَ الأولَ واسمَ العائلة على الأقل.":
        "Enter at least your first name and family name.",
    "الاسمُ قصيرٌ — اكتبه كما هو مسجَّل.":
        "The name is too short — write it as it is registered.",
    "الاسم الأول واسم العائلة": "First name and family name",
})

EN.update({
    " أو ": " or ",
    "إدارة التخطيط والاعتماد المدرسي": "the Planning and School Accreditation Department",
})

# ═════════ ١٦) استيرادُ تحضيرٍ جاهز ═════════
EN.update({
    "تحضيرٌ جاهز — بدل ملء الخانات واحدةً واحدة":
        "Ready-made plan — instead of filling the fields one by one",
    "اكتبه خارجاً ثم أدخله هنا دفعةً واحدة — والخاناتُ تبقى كما هي لأن لكلٍّ منها مؤشراً":
        "Write it outside, then bring it in at once — the fields stay as they are, because each one has an indicator",
    "١) انسخ الأمر   ٢) ألصقه في أي مساعدٍ ذكيّ   ٣) ألصق الجواب هنا أو ارفع ملف وورد":
        "1) Copy the prompt   2) Paste it into any AI assistant   3) Paste the answer here, or upload a Word file",
    "انسخ الأمر": "Copy the prompt", "انسخ الأمر:": "Copy the prompt:",
    "ارفع ملف وورد (.docx)": "Upload a Word file (.docx)",
    "وزّع على الخانات": "Distribute into the fields",
    "أدخِله": "Bring it in", "أدخِله واستبدل المكتوب": "Bring it in and replace what is written",
    "ألصق هنا جواب المساعد، أو نصَّ تحضيرك بصيغة ### اسم الحقل: القيمة":
        "Paste the assistant's answer here, or your plan in the form ### field name: value",
    "نُسخ الأمر.\n\nألصقه في المساعد، ثم أعد الجوابَ كاملاً إلى الصندوق أدناه.":
        "Prompt copied.\n\nPaste it into the assistant, then bring the whole answer back to the box below.",
    "سيُملأ ": "Will fill ", " خانةً": " fields", " خانة": " fields",
    "، ويُستبدل ما في ": ", and replace what is in ",
    " خانةً مكتوبةً": " fields already written",
    "ولم أعرف: ": "Not recognised: ",
    "سيُستبدل ما كتبتَه في ": "This will replace what you wrote in ",
    " خانة.\n\nأتُتابع؟": " fields.\n\nContinue?",
    "أُدخل ": "Brought in ",
    " خانة.\n\nراجعها ثم اضغط «إصدار التحضير».":
        " fields.\n\nReview them, then press “Issue plan”.",
    "لم أجد حقولاً بصيغة ### اسم الحقل: القيمة":
        "No fields found in the form ### field name: value",
    "تأكّد أن المساعد أجاب بالصيغة المطلوبة في الأمر، أو أعد نسخ الأمر.":
        "Check the assistant answered in the format the prompt asks for, or copy the prompt again.",
    "لم يطابق أيُّ حقلٍ أسماءَ الخانات — راجع الصيغة.":
        "No field matched the form's names — check the format.",
    "استيراد تحضير": "Plan import",
    # ── رسائلُ الملفّ ──
    "ملفُّ PDF لا يُقرأ هنا: نصُّ العربية فيه يخرج مشوَّهاً فيملأ الخاناتِ بخطأ.\n\n":
        "PDF is not read here: Arabic text comes out of it distorted and would fill the fields wrongly.\n\n",
    "احفظ تحضيرك بصيغة وورد (.docx) وأعد الرفع.":
        "Save your plan as a Word file (.docx) and upload again.",
    "تعذّرت قراءةُ الملف: ": "Could not read the file: ",
    "الملفُّ ليس مستندَ وورد (.docx)": "This is not a Word document (.docx)",
    "لم يُوجد نصُّ المستند داخل الملف": "The document's text was not found inside the file",
    "متصفّحُك لا يفكُّ ملفات وورد — حدّثه، أو الصق النصَّ في الصندوق بدل رفع الملف.":
        "Your browser cannot open Word files — update it, or paste the text into the box instead.",
    # ── نصُّ الأمر نفسُه ──
    "اكتب تحضير حصةٍ دراسيةٍ بالتفصيل، بحسب البيانات الآتية:":
        "Write a detailed lesson plan based on the following:",
    "المادة: ": "Subject: ", "الصف/الفصل: ": "Grade / class: ", "الدرس: ": "Lesson: ",
    "الإستراتيجية المعلنة: ": "Declared strategy: ",
    "الاتجاه التدريسي: ": "Teaching approach: ",
    "زمن الحصة بالدقائق: ": "Lesson time in minutes: ",
    "(اكتب اسم الدرس هنا)": "(write the lesson title here)",
    "⛔ أجب بهذه الصيغة حرفياً: سطرٌ لكل حقل يبدأ بـ### ثم اسمُ الحقل ثم نقطتان.":
        "⛔ Answer in exactly this format: one line per field, starting with ### then the field name then a colon.",
    "ولا تكتب مقدّمةً ولا خاتمةً ولا شرحاً خارج الأسطر.":
        "Do not write an introduction, a conclusion, or any commentary outside those lines.",
    "وما كان اختياراً من قائمةٍ فاكتب أحدَ خياراتها كما هو.":
        "Where a field offers a list, write one of its options exactly as given.",
    "  (اختر من: ": "  (choose from: ", "  (رقمٌ بالدقائق)": "  (a number in minutes)",
    "الزمن — ": "Time — ", " — نمط العمل ": " — working mode ",
})

# ═════════ ١٧) تقييدُ الإستراتيجية بالاتجاه · الأدوار الجديدة · مرشَّحو الزيارة ═════════
EN.update({
    "اختر الاتجاه التدريسي أولاً": "Choose the teaching approach first",
    "إسقاط إستراتيجية لا تناسب الاتجاه: «": "Dropped a strategy that does not fit the approach: “",
    "الاطّلاع والتعليق": "View and comment",
    "متابعةُ الحصة": "Lesson follow-up",
    "تتأكّد من تعبئة معلميك — والرصدُ للمشرف التربوي":
        "You check your teachers have filled in — observation belongs to the subject supervisor",
    "ترى ما رصده المشرفُ التربوي، وتكتب تعليقك":
        "You see what the subject supervisor recorded, and write your comment",
    "لم يرصد المشرفُ التربوي هذه الحصة بعد.":
        "The subject supervisor has not observed this lesson yet.",
    "إجراءُ الجسر: ": "Bridge action: ",
    "تعليقُ مدير المدرسة — يظهر في تقرير الحصة":
        "School principal's comment — appears in the lesson report",
    "ملاحظتك على الحصة — لا درجة": "Your note on the lesson — not a score",
    "حفظ التعليق": "Save comment",
    "حُفظ تعليقك — ويظهر في تقرير الحصة.":
        "Your comment is saved — it appears in the lesson report.",
    "تعليق مدير": "Principal comment",
    "الزائر ": "Peer ",
    " مرشَّحاً متفرِّغاً": " candidates free at this time",
    "لا مرشَّحَ من تخصصه متفرِّغٌ في هذا الوقت":
        "No candidate in this subject is free at this time",
})

EN.update({
    "اقرأ أولاً": "Read first",
    "اطوِ الشرح": "Collapse the guidance",
    "اعرض الشرح": "Show the guidance",
})
