# -*- coding: utf-8 -*-
"""⛔ **بابُ النشرات الواحد**: يبني الإحدى والعشرين ويُصدّر PDFها ثم يفحصها.

كان لكلِّ نشرةٍ نداءٌ يدويٌّ بمفتاحها ومسارها (`nshbuild.py <key> <out>`)،
فإذا تغيّرت المنصةُ لم يُعد بناؤها أحد — وبقيت لقطاتُها تُري المستخدمَ شاشةً
لا وجودَ لها، ونصُّها يأمره بما لا يستطيع. (قِيس ٢ أكتوبر ٢٠٢٦: سبعَ عشرةَ
لقطةً من ثلاثٍ وثلاثين تخالف المنصة، منها خطوةٌ تقول «واكتب اسم المدرسة».)

⚠️ والمساراتُ تُشتقُّ من **الموجود على القرص** لا من صياغةٍ في الذهن: يُطابَق
   اسمُ الملفّ بـ`FILENAME` لكلِّ مفتاح، فإن لم يوجد ملفٌّ لمفتاحٍ قيل ذلك
   ولم يُخترع له اسم.

الاستعمال: python3 nshall.py [--shots] [--no-pdf]
  --shots  يُعيد تصوير اللقطات التسع والتسعين أولاً (بطيء)
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE = os.path.join(ROOT, "١٠ - أدلّة استخدام المنصة")
# (مجلَّد، الجنس، اللغة، بانيها)
TARGETS = [("بنين", "m", "ar", "nshbuild.py"),
           ("بنات", "f", "ar", "nshbuild.py"),
           ("English", "m", "en", "nshbuild_en.py")]
FLOOR = 21


def names(gender, lang):
    """FILENAME لكلِّ مفتاح — تُقرأ من وحدة المحتوى بجنسها لا تُصاغ هنا."""
    env = dict(os.environ, CLS_GENDER=gender, CLS_LANG=lang)
    mod = "nshcontent_en" if lang == "en" else "nshcontent"
    code = ("import %s as C, json;"
            "print(json.dumps({'order': C.ORDER,"
            " 'file': getattr(C, 'FILENAME', {})}, ensure_ascii=False))" % mod)
    r = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env,
                       capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-600:])
        return None
    import json
    return json.loads(r.stdout)


def main():
    do_shots = "--shots" in sys.argv
    do_pdf = "--no-pdf" not in sys.argv
    ok, built, pdfs = True, 0, 0

    if do_shots:
        for _d, g, l, _b in TARGETS:
            r = subprocess.run([sys.executable, "nshshots.py"], cwd=HERE,
                               env=dict(os.environ, CLS_GENDER=g, CLS_LANG=l),
                               capture_output=True, text=True)
            bad = [x for x in r.stdout.splitlines() if "⛔" in x]
            print("  لقطات %-8s %s" % (_d, "✓" if not bad and not r.returncode
                                       else "⛔ " + " · ".join(bad[:2])))
            ok &= not bad and not r.returncode

    for d, g, l, builder in TARGETS:
        out_dir = os.path.join(BASE, d)
        have = {f for f in os.listdir(out_dir) if f.endswith(".docx")}
        meta = names(g, l)
        if not meta:
            print("  ⛔ تعذّر قراءةُ أسماء %s" % d)
            ok = False
            continue
        for key in meta["order"]:
            stem = meta["file"].get(key)
            # ⚠️ الإنجليزيةُ لا FILENAME لها، فيُطابَق بالمفتاح على ما في المجلَّد
            cand = [f for f in have
                    if (stem and f.startswith(stem)) or (not stem and False)]
            if not cand and l == "en":
                cand = [f for f in have if _en_match(key, f)]
            if len(cand) != 1:
                print("  ⛔ %s/%s — %d ملفاً مطابقاً، فلا يُخترع اسم"
                      % (d, key, len(cand)))
                ok = False
                continue
            dst = os.path.join(out_dir, cand[0])
            r = subprocess.run([sys.executable, builder, key, dst], cwd=HERE,
                               env=dict(os.environ, CLS_GENDER=g, CLS_LANG=l),
                               capture_output=True, text=True)
            if r.returncode:
                print("  ⛔ %s/%s — %s" % (d, key, (r.stderr or "").strip()[-200:]))
                ok = False
                continue
            built += 1
            if do_pdf:
                import export_pdf
                pdf = dst[:-5] + ".pdf"
                if export_pdf.export(dst, pdf):
                    pdfs += 1
                else:
                    print("  ⛔ %s — تعذّر تصديرُ PDF" % cand[0])
                    ok = False
    print("\n  بُنيت %d نشرةً · صُدّرت %d" % (built, pdfs))
    if built < FLOOR:
        print("  ⛔ المبنيُّ %d والأرضيّةُ %d" % (built, FLOOR))
        ok = False
    return 0 if ok else 1


_EN = {"teacher": "Teaching Teacher", "peer": "Peer Teacher",
       "principal": "School Principal", "deputy": "Academic Deputy",
       "supervisor": "Subject Supervisor", "cxmgr": "Complex Manager",
       "intqa": "Internal Evaluation Follow-up Team"}


def _en_match(key, fname):
    return _EN[key] in fname


if __name__ == "__main__":
    sys.exit(main())
