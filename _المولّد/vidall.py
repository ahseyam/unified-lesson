# -*- coding: utf-8 -*-
"""بابُ سيناريوهات الفيديو: يبني الأربعةَ عشرَ ويُصدّر PDFها.

الاستعمال: python3 vidall.py [--no-pdf]
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "١١ - سيناريوهات فيديو الاستخدام")
FLOOR = 14


def main():
    do_pdf = "--no-pdf" not in sys.argv
    built = pdfs = 0
    bad = []
    for g, sub in (("m", "بنين"), ("f", "بنات")):
        env = dict(os.environ, CLS_GENDER=g, CLS_FONTSET="js")
        r = subprocess.run([sys.executable, "-c",
                            "import vidcontent as V, nshcontent as C;"
                            "print('\\n'.join('%s\\t%s' % (k, V.NAME[k]) for k in C.ORDER))"],
                           cwd=HERE, env=env, capture_output=True, text=True)
        if r.returncode:
            print(r.stderr[-400:])
            return 1
        for line in r.stdout.strip().splitlines():
            key, name = line.split("\t")
            dst = os.path.join(OUT, sub, name + " — ابن خلدون" +
                               (" (بنات)" if g == "f" else "") + ".docx")
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            rr = subprocess.run([sys.executable, "vidbuild.py", key, dst],
                                cwd=HERE, env=env, capture_output=True, text=True)
            if rr.returncode:
                bad.append((key + "/" + sub, (rr.stderr or "").strip()[-160:]))
                continue
            built += 1
            if do_pdf:
                import export_pdf
                pdf = dst[:-5] + " (للعرض والطباعة).pdf"
                if export_pdf.export(dst, pdf):
                    pdfs += 1
                else:
                    bad.append((os.path.basename(dst)[:40], "تعذّر PDF"))
    for n, e in bad:
        print("  ⛔ %-44s %s" % (n, e))
    print("  بُني %d سيناريو · صُدّر %d" % (built, pdfs))
    if built < FLOOR:
        print("  ⛔ المبنيُّ %d والأرضيّةُ %d" % (built, FLOOR))
        return 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
