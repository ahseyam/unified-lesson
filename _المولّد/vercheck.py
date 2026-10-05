# -*- coding: utf-8 -*-
"""حارسُ التحديث الذاتي — صفحةٌ قديمةٌ مفتوحةٌ تُحدِّث نفسَها عند نشر أحدث.

⛔ **لا يُطلب من المعلّم إصلاحُ عطلٍ ليس له**: بعد نشر منع الحجز المزدوج قلتُ
   للمستشار «أرسل لهم: أغلقوا التبويبَ وافتحوه»، فردّ: «لن أستطيع — فهذا
   يزيد تشككهم بالمنصة. قم أنت بهذا الحل بنفسك». (٥ أكتوبر ٢٠٢٦)

⚠️ ويُقاس على **صفحةٍ تُخدَم عبر http** لا من القرص، لأن `fetch` النسبيَّ
   لا يعمل على `file:` — فالفحصُ من القرص يمرُّ بلا أن يقيس شيئاً.
⚠️ وثلاثةُ شواهدَ لا واحد: أن تُعيد عند اختلاف الختم · وألّا تُعيد عند
   تطابقه · وألّا تُعيد مرّتين للختم نفسِه (وإلّا دار المتصفّحُ أبداً).
"""
import http.server
import json
import os
import re
import shutil
import socketserver
import subprocess
import sys
import threading

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "٨ - النموذج الرقمي (تجربة)",
                   "منصة الحصة الموحَّدة — ابن خلدون.html")
# ⛔ **اعتراضُ `location.reload` لا ينفع**: الإسنادُ إليه قد لا ينفذ، فتُعاد
#    الصفحةُ فعلاً ويُصفَّر عدّادٌ في `window` معها — فيبدو أن شيئاً لم يقع.
#    فيُعدُّ التحميلُ بما ينجو من الإعادة: `sessionStorage` يبقى في التبويب.
PROBE = r"""
<script>
(function(){
  var n = 0;
  try{ n = parseInt(sessionStorage.getItem("__loads") || "0", 10) || 0; }catch(e){}
  n++;
  try{ sessionStorage.setItem("__loads", String(n)); }catch(e){}
  window.__LOADS = n;
})();
setTimeout(function(){
  try{ localStorage.clear(); }catch(e){}
  verCheck();
  setTimeout(function(){ verCheck(); setTimeout(function(){
    var d=document.createElement("pre"); d.id="dump";
    d.textContent = JSON.stringify({n: (window.__LOADS||0) - 1, build: D.build, url: D.verurl});
    document.body.appendChild(d);
  }, 1100); }, 1100);
}, 700);
</script>
"""


def serve(d, port=0):
    """⚠️ **منفذٌ ثابتٌ يسقط عند التشغيل المتوازي** («Address already in use»)،
    فيبدو العطلُ في المنصة وهو في الحارس. فيُطلب منفذٌ حرٌّ من النظام."""
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k): super().__init__(*a, directory=d, **k)
        def log_message(self, *a): pass
    socketserver.TCPServer.allow_reuse_address = True
    s = socketserver.TCPServer(("127.0.0.1", port), H)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, s.server_address[1]


def run(port, label):
    out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                          "--virtual-time-budget=9000", "--dump-dom",
                          "http://127.0.0.1:%d/p/page.html" % port],
                         capture_output=True, text=True).stdout
    m = re.search(r'<pre id="dump">(.*?)</pre>', out, re.S)
    import html as H2
    return json.loads(H2.unescape(m.group(1))) if (m and m.group(1).strip()) else {}


def main():
    import tempfile
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "p"))
    page = open(SRC, encoding="utf-8").read()
    mb = re.search(r'"build":\s*"([^"]+)"', page)
    if not mb:
        print("⛔ لا ختمَ في الصفحة"); return 1
    build = mb.group(1)
    open(os.path.join(tmp, "p", "page.html"), "w", encoding="utf-8").write(page + PROBE)
    srv, port = serve(tmp)
    bad = 0

    def ver(v):
        json.dump(v, open(os.path.join(tmp, "ver.json"), "w"), ensure_ascii=False)

    # ① ختمٌ مطابق ⇒ لا إعادة
    ver({"ikm": build, "ikf": build})
    r = run(port, "مطابق")
    ok = r.get("n") == 0
    print("  %s ختمٌ مطابقٌ ⇒ لا إعادة   (إعادات=%s)" % ("✓" if ok else "⛔", r.get("n")))
    bad += 0 if ok else 1

    # ② ختمٌ أحدثُ ⇒ إعادةٌ واحدةٌ لا أكثر
    ver({"ikm": build + "-NEW", "ikf": build})
    r = run(port, "مختلف")
    ok = r.get("n") == 1
    print("  %s ختمٌ أحدثُ ⇒ إعادةٌ واحدة (إعادات=%s)" % ("✓" if ok else "⛔", r.get("n")))
    bad += 0 if ok else 1

    # ③ ملفٌّ مفقود ⇒ لا إعادة ولا سقوط
    os.remove(os.path.join(tmp, "ver.json"))
    r = run(port, "مفقود")
    ok = r.get("n") == 0 and r.get("build")
    print("  %s ملفُّ الختم مفقودٌ ⇒ لا إعادة ولا سقوط" % ("✓" if ok else "⛔"))
    bad += 0 if ok else 1

    srv.shutdown(); shutil.rmtree(tmp, ignore_errors=True)
    print("\n  " + ("✓ الصفحةُ تُحدِّث نفسَها ولا تدور" if not bad else "⛔ التحديثُ الذاتيُّ لا يُعتمد"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
