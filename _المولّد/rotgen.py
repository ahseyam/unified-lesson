# -*- coding: utf-8 -*-
"""توليدُ جدول الدوران داخل الخادم — آلياً من `scheddata` لا بيد.

⛔ **ولماذا في الخادم؟** أجهزةٌ لم تأخذ النسخةَ الجديدة بعدُ ما زالت تعرض
   الجدولَ قبل إعادة التجميع، فتُسجَّل الحصصُ في أيامها القديمة. نظّفتُ ٧٢ ثم
   عادت ٥٤ في ساعة. فالمنعُ في الخادم وحدَه يوقف النزيفَ ولو بقي جهازٌ بلا
   تحديثٍ شهراً. (٨ أكتوبر ٢٠٢٦)

⚠️ **ولا يُكتب بيد**: نسختان تفترقان، والمقيسُ غيرُ المنشور لا يُثبت شيئاً.
   فيُولَّد من المصدر، ويقارنه `rowscheck` بما في `scheddata` — فلو تغيّر
   الدورانُ ولم يُنشر الخادمُ سقط الشاهدُ وأُنبِّه.

يُشغَّل: python3 rotgen.py        (يكتب المقطعَ في worker.js بين علامتيه)
"""
import io
import json
import os
import re
import sys

import scheddata as SD

SRV = os.path.expanduser("~/Desktop/خادم الحصة الموحَّدة (خاصّ — لا يُنشر)/worker.js")
BEG = "/* ROT-BEGIN — مولَّدٌ بـrotgen.py، لا يُحرَّر بيد */"
END = "/* ROT-END */"


def payload():
    spec2grp = {}
    for g, subs in SD.PAIRS.items():
        for s in subs:
            spec2grp[s] = g
    return {"g": spec2grp, "r": SD.ROT6}


def block():
    p = payload()
    return (BEG + "\nconst ROTSPEC = " + json.dumps(p["g"], ensure_ascii=False)
            + ";\nconst ROTDAY = " + json.dumps(p["r"], ensure_ascii=False) + ";\n" + END)


def main():
    if not os.path.exists(SRV):
        print("  ⛔ لا خادمَ في مجلَّده الخاصّ"); return 1
    s = io.open(SRV, encoding="utf-8").read()
    nb = block()
    if BEG in s and END in s:
        s = re.sub(re.escape(BEG) + r"[\s\S]*?" + re.escape(END), lambda _m: nb, s, count=1)
    else:
        anchor = "const LOCKP = \"~lock~\";"
        if anchor not in s:
            print("  ⛔ لا مرساةَ للإدراج"); return 1
        s = s.replace(anchor, nb + "\n" + anchor, 1)
    io.open(SRV, "w", encoding="utf-8").write(s)
    p = payload()
    print("  ✓ جدولُ الدوران في الخادم: %d مادةً · %d مجمعاً · %d أسبوعاً"
          % (len(p["g"]), len(p["r"]), len(next(iter(p["r"].values())))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
