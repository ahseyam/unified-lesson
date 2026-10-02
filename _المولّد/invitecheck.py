# -*- coding: utf-8 -*-
"""⛔ **رابطُ الدعوة يُقاس وهو يُفتح عبر http لا عبر الملف.**

كان ٤٦٨ حرفاً لأنه يحمل مسارَ الصفحة بأسمائها العربية مرمَّزة، فيُكسر في
واتساب. وصار يستعمل الرابطَ القصيرَ في الجذر (`m.html` · `f.html`) — ١٥٥
حرفاً. ⚠️ والجذرُ يُحسب بحذف آخر جزأين من المسار، وحسابٌ خاطئٌ يُنتج رابطاً
ميّتاً **يُوزَّع على المدارس** ولا يُكتشف إلا عندهم.

ولا تكفي المسابرُ القائمةُ: كلُّها تفتح الصفحةَ من `file://`، والدالّةُ تردّ
الطويلَ هناك قصداً. فهنا تُخدَم شجرةٌ مطابقةٌ للمنشور عبر http، ويُنادى
`inviteURL()` الحقيقيّ. (٢ أكتوبر ٢٠٢٦)
"""
import html as H
import http.server
import json
import os
import re
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D8 = "٨ - النموذج الرقمي (تجربة)"
PAGES = [("m", "منصة الحصة الموحَّدة — ابن خلدون.html", "m.html"),
         ("f", "منصة الحصة الموحَّدة — ابن خلدون (بنات).html", "f.html")]
FLOOR = 6

BOOT = r"""
<script>
setTimeout(function(){
 var R = [];
 function A(t, ok, x){ R.push(x === undefined ? [t, !!ok] : [t, !!ok, String(x)]); }
 try{
  localStorage.setItem(API, "https://srv.example/");
  localStorage.setItem(SKEY, "K123456789012345678901234");
  inviteURL().then(function(u){
    A("الرابطُ قصيرٌ لا يحمل مسارَ الصفحة", u.indexOf("__SHORT__") >= 0, u.slice(0, 80));
    A("ولا يحمل اسمَ المجلّد العربيَّ مرمَّزاً", u.indexOf("%D9%A8") < 0);
    A("ويحمل عنوانَ الخادم", u.indexOf("srv.example") >= 0);
    A("ويحمل المفتاح", u.indexOf("K1234567890") >= 0);
    A("وفي جزء التجزئة لا في الاستعلام",
      u.indexOf("#srv=") > 0 && u.indexOf("?srv=") < 0);
    A("وأقصرُ من المسار الطويل بكثير", u.length < 220, u.length + " حرفاً");
    document.title = "DONE"; window.__OUT = JSON.stringify(R);
  });
 }catch(e){ document.title = "ERR|" + e.message; window.__OUT = JSON.stringify(R); }
}, 500);
</script>
<script>setTimeout(function(){var d=document.createElement("pre");d.id="dump";
 d.textContent=window.__OUT||"";document.body.appendChild(d);}, 8000);</script>
"""


def free_port():
    with socketserver.TCPServer(("127.0.0.1", 0), None) as s:
        return s.server_address[1]


def main():
    ok = True
    for gender, page, short in PAGES:
        src = os.path.join(ROOT, D8, page)
        if not os.path.exists(src):
            print("  ⛔ لا صفحةَ مبنيّة: %s" % page)
            return 1
        tmp = tempfile.mkdtemp(prefix="inv_")
        try:
            os.makedirs(os.path.join(tmp, D8))
            dst = os.path.join(tmp, D8, page)
            open(dst, "w", encoding="utf-8").write(
                open(src, encoding="utf-8").read()
                + BOOT.replace("__SHORT__", "/" + short))
            # ⚠️ الروابطُ القصيرةُ كما في المنشور — ووجودُها شرطُ اختصار الرابط
            for _g, _p, sh in PAGES:
                open(os.path.join(tmp, sh), "w", encoding="utf-8").write("<!doctype html>")
            port = free_port()
            hd = http.server.SimpleHTTPRequestHandler
            srv = socketserver.TCPServer(("127.0.0.1", port),
                                         lambda *a, **k: hd(*a, directory=tmp, **k))
            th = threading.Thread(target=srv.serve_forever, daemon=True)
            th.start()
            try:
                import urllib.parse as up
                url = "http://127.0.0.1:%d/%s/%s" % (port, up.quote(D8), up.quote(page))
                out = subprocess.run(
                    [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                     "--virtual-time-budget=14000", "--dump-dom", url],
                    capture_output=True, text=True).stdout
            finally:
                srv.shutdown()
            m = re.search(r'<pre id="dump">(.*?)</pre>', out, re.S)
            t = re.search(r"<title>(.*?)</title>", out, re.S)
            rows = json.loads(H.unescape(m.group(1))) if (m and m.group(1).strip()) else []
            print("── %s ──" % ("بنين" if gender == "m" else "بنات"))
            for r in rows:
                g = bool(r[1]); ok &= g
                print("  %s %s%s" % ("✓" if g else "⛔", r[0],
                                     ("   [" + str(r[2]) + "]") if len(r) > 2 else ""))
            if t and H.unescape(t.group(1)).startswith("ERR"):
                print("  ⛔", H.unescape(t.group(1))); ok = False
            if len(rows) < FLOOR:
                print("  ⛔ %d شاهداً والأرضيّةُ %d" % (len(rows), FLOOR)); ok = False
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    print("\n  %s" % ("✓ رابطُ الدعوة قصيرٌ وحيّ" if ok else "⛔ لا يُوزَّع"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
