# -*- coding: utf-8 -*-
"""⛔ الترجمةُ لا تُسلَّم قبل إثبات أن **العربيةَ لم تتأذَّ**: لُفَّ ستُّمئة نصٍّ
   في TR، وغُيِّرت أربعون موضعَ عرضٍ، وصار ثابتُ شروح المراحل دالّةً. فأيُّ
   خللٍ في ذلك يُفسد الشاشةَ العربيةَ — وهي التي يعمل عليها الناسُ اليوم.

الشاهدُ ثلاثيّ: (١) كلُّ شاشةٍ ترسم بلا خطأ، (٢) وفيها شواهدُها العربية،
(٣) ولا يتسرّب إليها مصطلحٌ إنجليزيٌّ من المعجم."""
import html as H, json, os, re, subprocess, sys
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = os.path.dirname(os.path.abspath(__file__))
D8 = "/Users/ahmadseyam/Desktop/نموذج تحضير الدرس - بطاقة الملاحظة الصفية/٨ - النموذج الرقمي (تجربة)"
import i18ncheck_en as T   # ⛔ كان «test_en» باسمه القديم، فكان الفحصُ لا يعمل أصلاً

# شواهدُ عربيةٌ لكل شاشة — وجودُها يعني أن العربيةَ سليمة
import scheddata as _SD
_W0 = _SD.CAL[0]["w"]

WANT = {
 # ⚠️ أولُ أسبوعٍ في الجدول — ويتغيّر بتغيّر الرزنامة، فيُقرأ منها لا يُكتب.
 "teacher/1/fill": ["جدول الحصص الموحَّدة", "جدولي", "الحصة 1", _W0],
 "teacher/2/-":    ["الاستعداد والتحضير", "خريطة الزمن", "السؤال الأساسي"],
 "teacher/6/-":    ["تنفيذ الحصة", "ورقة التنفيذ"],
 "teacher/5/-":    ["تقريري"],
 "peer/5/-":       ["زياراتي المسنَدة", "خطواتُ زيارتك"],
 "peer/6/-":       ["تحضيرُ زميلك"],
 "peer/3/-":       ["بطاقةُ الزيارة"],
 "peer/4/-":       ["إجراؤك أنت"],
 "principal/1/fill": ["جدول مدرستي"],
 "principal/2/-":  ["تحضيرُ المعلم"],
 # ⛔ تغيّر بقصد: المديرُ لم يعد يملأ الاستمارة — يطّلع ويعلّق (قرارُ الاجتماع)
 # ⚠️ المديرُ صار يرصد حصصَ مدرسته (٤ أكتوبر ٢٠٢٦)، فلم يعد يمرُّ بشاشة
 #    الاطّلاع — ويبقى له صندوقُ التعليق بجانب الاستمارة.
 "principal/3/-":  ["رصد الحصة", "تعليقُ مدير المدرسة", "بطاقة تشخيص الإستراتيجية"],
 "principal/4/-":  ["بعد الحصة", "بطاقة الجسر"],
 "principal/5/school": ["تقرير المدارس"],
 "principal/5/pending": ["الإدخالُ الناقص", "الرقم الوظيفي"],
 "deputy/1/assign":["إسناد الزائرين"],
 "deputy/1/fill":  ["جدول مدرستي"],
 "deputy/5/active":["تقرير التفعيل"],
 "supervisor/1/fill": ["تخصص المعلم الزائر"],
 "supervisor/1/visits": ["خطة زياراتي"],
 "supervisor/1/sup": ["أين أزور"],
 "supervisor/3/-": ["رصد الحصة"],
 "supervisor/5/ind": ["تقرير المؤشرات"],
 "admin/7/-":      ["لوحةُ المنظومة", "حالُ المنظومة"],
 "admin/8/-":      ["أدواتُ المنصة", "المخزن المشترك"],
 "admin/1/log":    ["سجلّ العمليات"],
 "admin/5/teacher":["تقرير المعلمين"],
 "login/-/-":      ["اختر دورك", "منصة الحصة الموحَّدة"],
}
# ⛔ مصطلحاتٌ إنجليزيةٌ لا يجوز ظهورُها في شاشةٍ عربية
LEAK = ["Unified Lesson", "Programme stages", "Sign out", "Reports",
        "Time map", "Essential question", "Visit card", "Not met",
        "Teacher roster", "Platform tools", "Choose your role"]


# ⚠️ بناءُ البنات مؤنَّث، فالشاهدُ المذكَّرُ لا يوجد فيه: «تحضيرُ زميلتك» و
#    «إسناد الزائرات» و«اختاري دورك». فيُقبل الشاهدُ بصيغتيه — ولا يُرخَّص
#    الشاهدُ حتى يسقط، فتُذكر الصيغتان صريحتين.
FEM = {
 "تحضيرُ زميلك": "تحضيرُ زميلتك",
 "إسناد الزائرين": "إسناد الزائرات",
 "تخصص المعلم الزائر": "تخصص المعلمة الزائرة",
 "تقرير المعلمين": "تقرير المعلمات",
 "اختر دورك": "اختاري دورك",
 "جدولي": "جدولي",
 "تعليقُ مدير المدرسة": "تعليقُ مديرة المدرسة",
}


def run(src, tag):
    boot = (T.BOOT.replace("__VIEWS__", json.dumps(T.VIEWS))
                  .replace('setLang("en")', 'setLang("ar")')
                  .replace("__T__", "أ. نموذج الغامدي").replace("__P__", "أ. نموذج القحطاني")
                  .replace("__A__", "المستشار"))
    p = os.path.join(HERE, "ar2_%s.html" % tag)
    open(p, "w", encoding="utf-8").write(
        open(src, encoding="utf-8").read() + boot
        + '<script>setTimeout(function(){var d=document.createElement("pre");'
          'd.id="dump";d.textContent=window.__OUT||"";document.body.appendChild(d);},900);</script>')
    out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                          "--virtual-time-budget=12000", "--dump-dom", "file://" + p],
                         capture_output=True, text=True).stdout
    ttl = re.search(r"<title>(.*?)</title>", out, re.S)
    ttl = H.unescape(ttl.group(1)) if ttl else "?"
    if ttl.startswith("ERR"):
        print("  ⛔ " + ttl); return False
    m = re.search(r'<pre id="dump">(.*?)</pre>', out, re.S)
    rows = dict(json.loads(H.unescape(m.group(1))))
    ok = True
    for name, want in WANT.items():
        txt = rows.get(name, "")
        miss = [w for w in want
                if w not in txt and (tag != "بنات" or FEM.get(w, w) not in txt)]
        leak = [w for w in LEAK if w in txt]
        good = txt and not miss and not leak
        ok &= bool(good)
        print("  %s %-22s %s%s" % ("✓" if good else "⛔", name,
              ("ناقص: " + "، ".join(miss)) if miss else "",
              ("  ⛔إنجليزيٌّ متسرّب: " + "، ".join(leak)) if leak else ""))
    return ok


good = True
for tag, fn in (("بنين", "منصة الحصة الموحَّدة — ابن خلدون.html"),
                ("بنات", "منصة الحصة الموحَّدة — ابن خلدون (بنات).html")):
    print("══════ %s — الوضعُ العربي ══════" % tag)
    good &= run(os.path.join(D8, fn), tag)
    print()
sys.exit(0 if good else 1)
