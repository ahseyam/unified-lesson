# -*- coding: utf-8 -*-
"""⛔ **ربطُ الخادم يُشترك داخل المدرسة ولا يَعبر إلى مدرسةٍ أخرى.**

كان منسوباً إلى النسخة (`ikm` · `ikf`)، فمن ربط البنين وجد البنات تقول «الحفظ
على هذا الجهاز فقط» — ويُربط الجهازُ مرّتين، ويُوزَّع رابطان يُنسى أحدُهما
فيبقى نصفُ المنظومة بلا مخزن. (بلاغُ المستشار ٢ أكتوبر ٢٠٢٦.)

⚠️ ولا يُنقض الفصلُ بين المدارس: حادثةُ ٢٩ سبتمبر كانت منصتَي **مدرستين** على
   نطاقٍ واحدٍ تقرأ إحداهما بياناتِ الأخرى. فالنطاقُ صار **المدرسةَ** لا
   النسخة، والبياناتُ تبقى منفصلةً بمفتاحها.

ويُقاس على **أصلٍ واحدٍ عبر http** — فـ`localStorage` يخصُّ النطاق، ولا تظهر
المشاركةُ أصلاً إن فُتحت الصفحتان من ملفَّين.
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
import urllib.parse as up

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D8 = "٨ - النموذج الرقمي (تجربة)"
BOYS = "منصة الحصة الموحَّدة — ابن خلدون.html"
GIRLS = "منصة الحصة الموحَّدة — ابن خلدون (بنات).html"
SRV, SK = "https://srv.example/", "K-shared-0123456789"
FLOOR = 7

# ⚠️ **تشغيلةٌ واحدةٌ تنتقل من صفحةٍ إلى أخرى** — لا ملفَّ متصفّحٍ دائماً:
#    كروم بـ`--user-data-dir` لا يخرج فيعلّق الفحص. والانتقالُ يبقي السياقَ
#    والأصلَ نفسَهما، وهو ما يُقاس عليه `localStorage` أصلاً.
SET = r"""
<script>
setTimeout(function(){
  var R = [];
  try{
    localStorage.clear();
    /* ⚠️ يُربط كما يربط المستخدمُ: بالمفاتيح التي تقرؤها الصفحةُ نفسُها */
    localStorage.setItem(API, "__SRV__");
    localStorage.setItem(SKEY, "__SK__");
    R.push(["نسخةُ البنين رُبطت", api() === "__SRV__" && skey() === "__SK__", api()]);
    R.push(["ومعرّفُ نطاقها هو المدرسة", ORG === "ik", ORG]);
    R.push(["وقاعدتُها باسم نسختها", SID === "ikm_db", SID]);
    sessionStorage.setItem("__hand", JSON.stringify(R));   /* يُسلَّم للصفحة التالية */
    location.replace("__NEXT__");
  }catch(e){ document.title = "ERR|" + e.message; }
}, 400);
</script>"""

SEE = r"""
<script>
setTimeout(function(){
  var R = [];
  try{
    try{ R = JSON.parse(sessionStorage.getItem("__hand") || "[]"); }catch(e){ R = []; }
    R.push(["ونسختُ البنات ترث الربطَ بلا إعادة", api() === "__SRV__", api() || "(لا شيء)"]);
    R.push(["وترث المفتاحَ معه", skey() === "__SK__", skey() ? "موجود" : "(لا شيء)"]);
    R.push(["ونطاقُها المدرسةُ نفسُها", ORG === "ik", ORG]);
    /* ⛔ وقاعدتُها غيرُ قاعدتهم — الفصلُ باقٍ */
    R.push(["وقاعدتُها منفصلةٌ عن البنين", SID === "ikf_db" && KEY.indexOf("ikf") === 0,
            SID + " · " + KEY]);
    document.title = "DONE"; window.__OUT = JSON.stringify(R);
  }catch(e){ document.title = "ERR|" + e.message; window.__OUT = JSON.stringify(R); }
}, 400);
</script>
<script>setTimeout(function(){var d=document.createElement("pre");d.id="dump";
 d.textContent=window.__OUT||"";document.body.appendChild(d);}, 5000);</script>
"""


def run(url, prof):
    out = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
         "--virtual-time-budget=14000", "--dump-dom", url],
        capture_output=True, text=True, timeout=120).stdout
    m = re.search(r'<pre id="dump">(.*?)</pre>', out, re.S)
    t = re.search(r"<title>(.*?)</title>", out, re.S)
    rows = json.loads(H.unescape(m.group(1))) if (m and m.group(1).strip()) else []
    err = t and H.unescape(t.group(1)).startswith("ERR")
    return rows, (H.unescape(t.group(1)) if err else None)


def main():
    tmp = tempfile.mkdtemp(prefix="share_")
    prof = tempfile.mkdtemp(prefix="prof_")     # ⚠️ ملفٌّ واحدٌ للمتصفّح، وإلّا لم يُشارَك شيء
    ok = True
    try:
        os.makedirs(os.path.join(tmp, D8))
        for page, boot in ((BOYS, SET), (GIRLS, SEE)):
            src = os.path.join(ROOT, D8, page)
            if not os.path.exists(src):
                print("  ⛔ لا صفحةَ مبنيّة: %s" % page)
                return 1
            open(os.path.join(tmp, D8, page), "w", encoding="utf-8").write(
                open(src, encoding="utf-8").read()
                + boot.replace("__SRV__", SRV).replace("__SK__", SK)
                      .replace("__NEXT__", up.quote(GIRLS)))
        port = None
        with socketserver.TCPServer(("127.0.0.1", 0), None) as s:
            port = s.server_address[1]
        hd = http.server.SimpleHTTPRequestHandler
        srv = socketserver.TCPServer(("127.0.0.1", port),
                                     lambda *a, **k: hd(*a, directory=tmp, **k))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            base = "http://127.0.0.1:%d/%s/" % (port, up.quote(D8))
            rows, e = run(base + up.quote(BOYS), prof)
            if e:
                print("  ⛔", e); ok = False
        finally:
            srv.shutdown()
        for r in rows:
            g = bool(r[1]); ok &= g
            print("  %s %s%s" % ("✓" if g else "⛔", r[0],
                                 ("   [" + str(r[2]) + "]") if len(r) > 2 else ""))
        if len(rows) < FLOOR:
            print("  ⛔ %d شاهداً والأرضيّةُ %d" % (len(rows), FLOOR)); ok = False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(prof, ignore_errors=True)
    print("\n  %s" % ("✓ الربطُ مشتركٌ في المدرسة · والبياناتُ منفصلة"
                      if ok else "⛔ لا يُعتمد"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
