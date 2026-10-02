# -*- coding: utf-8 -*-
"""⛔ **لقطةٌ متخلِّفةٌ تُري المستخدمَ شاشةً لا وجودَ لها.**

نشراتُ الاستخدام تَعِد قارئَها: «لقطةٌ من المنصة نفسِها». فإن تغيّرت المنصةُ
ولم تُعد اللقطاتُ، صار الوعدُ كذباً — ويقرأ المستخدمُ خطوةً تأمره بما لا
يستطيع. وقِيس ٢ أكتوبر ٢٠٢٦: **سبعَ عشرةَ لقطةً من ثلاثٍ وثلاثين** تخالف
المنصةَ، منها خطوةٌ تقول «واكتب اسم المدرسة» ولا حقلَ لها.

وهذا الحارسُ يُصوّر من **البناء الحالي** في مجلَّدٍ مؤقّت (`CLS_SHOTDIR`) ثم
يقارن بالمنشور بالبكسل. ويفحص بعدها أن **الصورةَ المضمَّنةَ في المستند** هي
اللقطةُ نفسُها ببصمتها — فلقطةٌ طازجةٌ على القرص لا تنفع إن بقي المستندُ
يحمل القديمة.

⚠️ وختمُ البناء يُخفى عند التصوير (`nshshots`)، وإلّا اختلفت كلُّ لقطةٍ مع
   كلِّ بناءٍ ولو لم يتغيّر في الشاشة حرف — فلا يُعرف المتخلِّفُ من الطازج.

الاستعمال: python3 shotsync.py            (بطيء: تسعٌ وتسعون لقطة)
           python3 shotsync.py --docx     (المضمَّنُ وحدَه — سريع)
"""
import hashlib
import os
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE = os.path.join(ROOT, "١٠ - أدلّة استخدام المنصة")
PUB = os.path.join(BASE, "صور")
TMP = os.path.join(os.environ.get(
    "TMPDIR", "/tmp"), "shotsync_%d" % os.getpid())
TARGETS = [("بنين", "m", "ar"), ("بنات", "f", "ar"), ("English", "m", "en")]
FLOOR_SHOTS = 99        # ⛔ أرضيّةٌ: ثلاثٌ وثلاثون لكلِّ مجلَّد
FLOOR_DOCS = 21         # ⛔ وأرضيّةُ المستندات: سبعٌ لكلِّ لغة
# ⛔ **لا تُحتمل لقطةٌ متخلِّفةٌ واحدة**: كانت القاعدةُ «مجموعٌ فوق أرضيّة»
#    فغرستُ لقطةً قديمةً فمرَّت (١٠١ بدل ١٠٢). وقِيس هيكلُ الصور فإذا في كلِّ
#    مستندٍ صورةٌ واحدةٌ غيرُ مطابقةٍ **ببصمةٍ واحدةٍ في الواحد والعشرين** —
#    وهي الكليشة. فالقاعدةُ: ما عدا الكليشةَ، **كلُّ** صورةٍ مضمَّنةٍ لها
#    لقطةٌ على القرص. (٢ أكتوبر ٢٠٢٦)
MAX_FIXED = 1           # الكليشةُ وحدَها يُسمح لها ألّا تطابق لقطة


def embedded():
    """هل الصورةُ داخلَ كلِّ مستندٍ هي اللقطةُ التي على القرص؟"""
    ok, tot, hit, docs = True, 0, 0, 0
    fixed = {}            # بصماتُ ما لا يطابق لقطةً — يجب أن تكون واحدةً
    for d, _g, _l in TARGETS:
        sd = os.path.join(PUB, d)
        if not os.path.isdir(sd):
            print("  ⛔ لا مجلَّد لقطات: %s" % d)
            return False, 0
        disk = {}
        for f in os.listdir(sd):
            if f.endswith(".png"):
                disk[hashlib.sha256(
                    open(os.path.join(sd, f), "rb").read()).hexdigest()] = f
        for g in sorted(os.listdir(os.path.join(BASE, d))):
            if not g.endswith(".docx") or g.startswith("~$"):
                continue
            z = zipfile.ZipFile(os.path.join(BASE, d, g))
            docs += 1
            n_here, odd = 0, []
            for n in z.namelist():
                if not n.startswith("word/media/"):
                    continue
                tot += 1
                h = hashlib.sha256(z.read(n)).hexdigest()
                if h in disk:
                    hit += 1
                    n_here += 1
                else:
                    odd.append(h)
                    fixed[h] = fixed.get(h, 0) + 1
            # ⚠️ ويُقاس **لكلِّ مستند**: مجموعٌ كبيرٌ يُخفي مستنداً متخلِّفاً
            if n_here < 4:
                print("  ⛔ %s — %d لقطةً طازجةً فقط فيه" % (g, n_here))
                ok = False
            if len(odd) > MAX_FIXED:
                print("  ⛔ %s — %d صورةً لا لقطةَ لها على القرص "
                      "(المسموحُ الكليشةُ وحدَها)" % (g, len(odd)))
                ok = False
    print("  صورٌ مضمَّنةٌ تطابق اللقطاتِ على القرص: %d من %d · مستندات %d"
          % (hit, tot, docs))
    # ⛔ وغيرُ المطابق يجب أن يكون **بصمةً واحدةً** تتكرّر في كل مستند
    if len(fixed) != 1 or list(fixed.values())[0] != docs:
        print("  ⛔ غيرُ المطابق %d بصمةً بتكرار %s — والمتوقَّع بصمةُ الكليشة "
              "وحدَها في كل مستند" % (len(fixed), sorted(fixed.values())))
        ok = False
    if docs < FLOOR_DOCS:
        print("  ⛔ المستنداتُ %d والأرضيّةُ %d" % (docs, FLOOR_DOCS))
        ok = False
    return ok, hit


def _bbox(ia, ib):
    """صندوقُ الاختلاف، أو None إن تطابقتا (ويُردُّ صندوقٌ عند اختلاف القياس)."""
    from PIL import ImageChops
    if ia.size != ib.size:
        return ("قياسان", ia.size, ib.size)
    return ImageChops.difference(ia, ib).convert("L") \
        .point(lambda v: 255 if v > 8 else 0).getbbox()


def rendered():
    """هل اللقطاتُ على القرص هي ما يُخرجه البناءُ الحالي؟"""
    from PIL import Image
    os.makedirs(TMP, exist_ok=True)
    ok, same, diff, n, retried = True, 0, 0, 0, 0
    try:
        for d, g, l in TARGETS:
            r = subprocess.run([sys.executable, "nshshots.py"], cwd=HERE,
                               env=dict(os.environ, CLS_GENDER=g, CLS_LANG=l,
                                        CLS_SHOTDIR=TMP),
                               capture_output=True, text=True)
            if r.returncode or "⛔" in r.stdout:
                print("  ⛔ تعذَّر تصويرُ %s" % d)
                for ln in r.stdout.splitlines():
                    if "⛔" in ln:
                        print("      " + ln.strip())
                ok = False
                continue
            for f in sorted(os.listdir(os.path.join(PUB, d))):
                if not f.endswith(".png"):
                    continue
                a = os.path.join(PUB, d, f)
                b = os.path.join(TMP, d, f)
                n += 1
                if not os.path.exists(b):
                    print("  ⛔ %s/%s — لم تُصوَّر" % (d, f))
                    ok = False
                    continue
                ia = Image.open(a).convert("RGB")
                ib = Image.open(b).convert("RGB")
                if ia.size != ib.size:
                    print("  ⛔ %s/%s — قياسٌ مختلف %s ↔ %s"
                          % (d, f, ia.size, ib.size))
                    diff += 1
                    ok = False
                    continue
                bb = _bbox(ia, ib)
                if bb is None:
                    same += 1
                    continue
                # ⛔ **المشكوكُ فيه يُعاد تصويرُه قبل أن يُتَّهم.** قِيس ٢ أكتوبر
                #    ٢٠٢٦: أربعُ لقطاتِ جداولَ من تسعٍ وتسعين خالفت في شريطها
                #    السفليّ، ثم طابقت **صفرَ بكسلٍ** حين أُعيد تصويرُها
                #    منفردة — فالفارقُ اضطرابُ تخطيطٍ لحظةَ الالتقاط تحت
                #    الحِمل، لا تخلُّفَ لقطة. وحارسٌ يصرخ من وهمٍ يُهمَل.
                r2 = subprocess.run([sys.executable, "nshshots.py", f[:-4]],
                                    cwd=HERE,
                                    env=dict(os.environ, CLS_GENDER=g,
                                             CLS_LANG=l, CLS_SHOTDIR=TMP),
                                    capture_output=True, text=True)
                bb2 = None if r2.returncode else _bbox(
                    ia, Image.open(b).convert("RGB"))
                if bb2 is None and not r2.returncode:
                    same += 1
                    retried += 1
                    continue
                print("  ⛔ %s/%s — تخالف البناءَ الحالي بعد إعادتين · %s"
                      % (d, f, bb2 or bb))
                diff += 1
                ok = False
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("  لقطاتٌ مطابقةٌ للبناء: %d · مخالفة: %d%s"
          % (same, diff,
             (" · طابقت بعد إعادة: %d" % retried) if retried else ""))
    if n < FLOOR_SHOTS:
        print("  ⛔ المقيسُ %d والأرضيّةُ %d — فحصٌ لم يقس ما يجب"
              % (n, FLOOR_SHOTS))
        ok = False
    return ok


def main():
    ok, _ = embedded()
    if "--docx" not in sys.argv:
        ok &= rendered()
    print("  %s" % ("✓ اللقطاتُ تطابق المنصةَ والمستندات"
                    if ok else "⛔ لقطاتٌ متخلِّفة — أعد `nshall.py --shots`"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
