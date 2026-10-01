# -*- coding: utf-8 -*-
"""ترقيع نصّي مباشر على ملفات DOCX مسلَّمة ضاع مولّدها.

⚠️ النصّ في وورد مقطّع بين runs، فالاستبدال يجري على مستوى الفقرة: تُجمع مقاطعها، ويُستبدل،
ثم يوضع الناتج في أول مقطع ويُفرَّغ الباقي — مع الحفاظ على تنسيق المقطع الأول.
الاستعمال: python3 patch_docx.py <ملف> "قديم=>جديد" ["قديم=>جديد" ...]
"""
import sys, re, zipfile, shutil, os


def patch(path, pairs):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        data = {n: z.read(n) for n in names}
    total = 0
    for n in [x for x in names if x.startswith('word/') and x.endswith('.xml')]:
        x = data[n].decode('utf-8')
        out = []
        last = 0
        for m in re.finditer(r'<w:p[ >].*?</w:p>', x, re.S):
            seg = m.group(0)
            texts = re.findall(r'(<w:t[^>]*>)([^<]*)(</w:t>)', seg)
            joined = "".join(t[1] for t in texts)
            new = joined
            for old, rep in pairs:
                new = new.replace(old, rep)
            if new != joined and texts:
                total += 1
                first = True
                def sub(mm):
                    nonlocal first
                    if first:
                        first = False
                        return mm.group(1) + new + mm.group(3)
                    return mm.group(1) + "" + mm.group(3)
                seg = re.sub(r'(<w:t[^>]*>)([^<]*)(</w:t>)', sub, seg)
            out.append(x[last:m.start()]); out.append(seg); last = m.end()
        out.append(x[last:])
        data[n] = "".join(out).encode('utf-8')
    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        for n in names:
            z.writestr(n, data[n])
    shutil.move(tmp, path)
    return total


if __name__ == "__main__":
    f = sys.argv[1]
    pairs = [tuple(a.split("=>")) for a in sys.argv[2:]]
    print("فقرات مُعدَّلة:", patch(f, pairs), "|", os.path.basename(f)[:50])
