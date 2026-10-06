# -*- coding: utf-8 -*-
"""⛔ **بوّابةُ الرفع: تُفحص الحزمةُ التي ستُرفع، لحظةَ رفعها.**

⛔ **لماذا؟** حارسُ التسرّب في `hub.py` يمسح الشجرةَ **أثناء البناء** — فما
   ظهر بعده يمرُّ من الحرّاس كلِّهم. وفي ٦ أكتوبر ٢٠٢٦ نسخت مصيدةُ صَدَفةٍ
   (`trap … EXIT`) شفرةَ الخادم إلى `_المولّد/worker.js` بعد انتهاء التدقيق،
   فوصلت إلى مرحلة الرفع ولم يمسكها إلا النظرُ في قائمة `git status`.
   والمستودعُ **عامّ**، وفي الملف عقدُ التخزين كلُّه.

⚠️ **والمقيسُ ما يراه جِت لا ما في القرص**: `git ls-files -co --exclude-standard`
   — المتعقَّبُ وغيرُ المتعقَّب معاً، منقوصاً منه ما في `.gitignore`. فهذا
   هو ما سيصير في المستودع العامّ بعد `git add -A` بعينه.

وما يُفحص:
  ① مفرداتُ التسرّب في كل ملفٍ نصيّ (`leakwords.LEAK_WORDS`).
  ② واسمُ شخصٍ في **خصائص** الملفات الثنائية — لا في متنها.
  ③ وملفٌّ يحمل بصمةَ شفرة الخادم ولو بلا كلمةٍ محروسة.

الاستعمال: `python3 pubcheck.py` — يُنادى قبل كل رفعٍ ويردُّ ١ عند أول تسرّب.
"""
import hashlib
import io
import os
import re
import subprocess
import sys
import zipfile

from leakwords import LEAK_WORDS, LEAK_OK, LEAK_OK_WORDS, META_NAMES, META_RX

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRVDIR = os.path.expanduser("~/Desktop/خادم الحصة الموحَّدة (خاصّ — لا يُنشر)")
TEXT = (".html", ".js", ".py", ".md", ".json", ".txt", ".gs", ".css", ".mjs", ".svg")
ZIPPED = (".docx", ".xlsx", ".pptx")


def tracked():
    """ما سيصير في المستودع العامّ: المتعقَّبُ وغيرُه، بلا المُستثنى."""
    r = subprocess.run(["git", "ls-files", "-co", "--exclude-standard", "-z"],
                       cwd=ROOT, capture_output=True, text=True)
    return [p for p in r.stdout.split("\0") if p]


def srv_fingerprints():
    """بصماتُ ملفات الخادم الخاصّ — فما طابق إحداها نسخةٌ منها ولو تغيّر اسمُه."""
    out = {}
    if not os.path.isdir(SRVDIR):
        return out
    for dp, dns, fns in os.walk(SRVDIR):
        for fn in fns:
            fp = os.path.join(dp, fn)
            try:
                out[hashlib.sha256(open(fp, "rb").read()).hexdigest()] = fn
            except Exception:
                pass
    return out


def main():
    files = tracked()
    if not files:
        print("  ⛔ لم يُعدّ جِت ملفاً واحداً — فحصٌ لم يَقِس شيئاً")
        return 1
    fps = srv_fingerprints()
    if not fps:
        print("  ⛔ لا مجلدَ خادمٍ خاصّ — فلا بصماتٍ تُقارَن، والفحصُ ناقص")
        return 1

    bad, scanned = [], 0
    for rp in files:
        fp = os.path.join(ROOT, rp)
        if not os.path.isfile(fp):
            continue
        low = rp.lower()
        try:
            raw = open(fp, "rb").read()
        except Exception:
            continue
        # ③ بصمةٌ مطابقةٌ لملفٍ من مجلد الخادم الخاصّ
        h = hashlib.sha256(raw).hexdigest()
        if h in fps:
            bad.append((rp, "نسخةٌ طبقُ الأصل من «%s» في مجلد الخادم الخاصّ" % fps[h]))
            continue
        if low.endswith(TEXT):
            scanned += 1
            txt = raw.decode("utf-8", "ignore")
            for w in LEAK_WORDS:
                if w.lower() in txt.lower():
                    if rp in LEAK_OK and w in LEAK_OK_WORDS:
                        continue
                    bad.append((rp, "مفردةٌ محروسة: «%s»" % w))
        elif low.endswith(ZIPPED):
            scanned += 1
            try:
                with zipfile.ZipFile(fp) as z:
                    meta = "".join(z.read(n).decode("utf-8", "ignore")
                                   for n in z.namelist() if n.startswith("docProps/"))
            except Exception:
                continue
            for ln in meta.splitlines():
                if any(re.search(rx, ln) for rx in META_RX) and \
                   any(nm.lower() in ln.lower() for nm in META_NAMES):
                    bad.append((rp, "اسمُ شخصٍ في خصائص الملف"))
                    break

    if scanned < 50:
        print("  ⛔ %d ملفاً نصّياً فقط فُحصت — أرضيّةُ الفحص ٥٠، فلم يَقِس شيئاً" % scanned)
        return 1
    print("  فُحص %d ملفاً من %d سيُرفع · وقُوبلت %d بصمةٍ من مجلد الخادم"
          % (scanned, len(files), len(fps)))
    if bad:
        for rp, why in bad[:25]:
            print("  ⛔ %s ← %s" % (rp, why))
        print("\n  ⛔ **لا يُرفع**. وملفُّ الخادم أو دليلُه موضعُه «خادم الحصة\n"
              "     الموحَّدة (خاصّ — لا يُنشر)» على سطح المكتب، لا مجلدُ التسليم\n"
              "     — فالمجلدُ نفسُه هو المستودعُ العامّ.")
        return 1
    print("  ✓ لا تسرّبَ فيما سيُرفع")
    return 0


if __name__ == "__main__":
    sys.exit(main())
