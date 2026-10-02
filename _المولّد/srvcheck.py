# -*- coding: utf-8 -*-
"""⛔ **خادمُ المخزن يُجرَّب بالمنصة نفسِها لا بالقراءة.**

⚠️ والشفرةُ المقيسةُ هي **الخادمُ القائم** في مجلَّده الخاصّ خارج شجرة التسليم
   (`~/Desktop/خادم الحصة الموحَّدة (خاصّ — لا يُنشر)/worker.js`) — لا نسخةٌ
   ثانيةٌ في المولّد. فنسختان تفترقان، والمقيسُ غيرُ المنشور لا يُثبت شيئاً.

⛔ وبه كُشف أن الخادمَ بقي **بلا مصادقةٍ** ثلاثةَ أيام: كُتب علاجُها في
   `srv_auth.md` ولم يُضف إلى الملف — فالدليلُ ليس تنفيذاً. (٢ أكتوبر ٢٠٢٦)

تُشغَّل شفرةُ `worker.js` في Node بخادمٍ محليٍّ صغيرٍ يحاكي KV بخريطةٍ في
الذاكرة — **والشفرةُ هي هي بلا تعديل** — ثم تُفتح الصفحةُ المبنيّةُ في كروم
وتُنادى دوالُّها الحقيقية: `testSrv` و`pushNow` و`pullNow` و`rosterPull`.

وما يُقاس:
  ١) فحصُ الخادم الذي تعرضه المنصة يمرّ (كتابةٌ ثم استرجاع).
  ٢) الكتابةُ تُدمج: جهازان يكتبان حصّتَين فيراهما كلاهما.
  ٣) و`__replace` يستبدل — فكشفُ المنسوبين لا يُمحى بالدمج.
  ٤) والمفتاحُ يُفحص: طلبٌ بمفتاحٍ خاطئ يُردّ ٤٠٣.
  ٥) ومفتاحٌ غيرُ مضبوطٍ يعمل بلا فحص — فالنشرُ آمنٌ قبل ضبطه.
"""
import http.server
import json
import os
import re
import socketserver
import subprocess
import sys
import threading

import probedir as PRB

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRVDIR = os.path.expanduser("~/Desktop/خادم الحصة الموحَّدة (خاصّ — لا يُنشر)")
WORKER = os.path.join(SRVDIR, "worker.js")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRC = os.path.join(ROOT, "٨ - النموذج الرقمي (تجربة)",
                   "منصة الحصة الموحَّدة — ابن خلدون.html")
KEY = "MFTH-TAJRIBA-1234567890ab"

# ⚠️ المحاكاةُ لا تُعيد كتابةَ منطق الخادم: تستورد الوحدةَ كما هي وتُمرّر لها
#    الطلبَ وبيئةً فيها `DB` بواجهة get/put.
SHIM = r"""
import worker from "./worker.js";
import http from "node:http";
const KV = new Map();
const env = { STORE_KEY: process.env.STORE_KEY || "",
  /* ⚠️ الخادمُ القائم يعمل على D1 أو KV؛ وتُوفَّر هنا KV وحدَها باسم `DB`
     — وهو ما يرتبط به في المضيف حين لا تُربط D1. */
  DB: { get: async (k) => (KV.has(k) ? KV.get(k) : null),
        put: async (k, v) => { KV.set(k, v); } } };
http.createServer(async (q, s) => {
  const chunks = [];
  for await (const c of q) chunks.push(c);
  const body = Buffer.concat(chunks).toString("utf8");
  const req = new Request("http://x" + q.url, {
    method: q.method,
    headers: q.headers,
    body: (q.method === "GET" || q.method === "HEAD") ? undefined : body });
  const r = await worker.fetch(req, env);
  const t = await r.text();
  const h = {};
  r.headers.forEach((v, k) => { h[k] = v; });
  s.writeHead(r.status, h);
  s.end(t);
}).listen(Number(process.env.PORT), "127.0.0.1",
  () => console.log("UP " + process.env.PORT));
"""

BOOT = r"""
<script>
function wait(ms){ return new Promise(r=>setTimeout(r, ms)); }
setTimeout(async function(){
 var R = [];
 function A(t, ok, x){ R.push(x===undefined ? [t, !!ok] : [t, !!ok, String(x)]); }
 try{
  localStorage.clear(); load();
  localStorage.setItem(API, "__URL__");
  localStorage.setItem(SKEY, "__KEY__");

  var t1 = await testSrv("__URL__");
  A("فحصُ الخادم الذي تعرضه المنصة يمرّ", t1.ok, t1.why || t1.note);

  ME = {role:"admin", name:"أ. القياس", emp:""};
  DB.sched = [{id:"s1", gk:"a|b|c|1|w|d|sp", teacher:"أ. نموذج الأول"}];
  DB.prep = {"s1": {goal:"هدفُ الأول"}};
  pending = true; lastSent = "";
  var p1 = await pushNow();
  A("الدفعةُ الأولى نجحت", p1);

  /* جهازٌ ثانٍ: قاعدةٌ فارغةٌ يكتب حصةً أخرى ثم يدفع */
  DB.sched = [{id:"s2", gk:"a|b|c|2|w|d|sp", teacher:"أ. نموذج الثاني"}];
  DB.prep = {"s2": {goal:"هدفُ الثاني"}};
  pending = true; lastSent = "";
  var p2 = await pushNow();
  A("والدفعةُ الثانية من «جهازٍ آخر»", p2);
  A("ويرى الثاني حصةَ الأول (دمجٌ لا استبدال)",
    DB.sched.some(x=>x.id==="s1") && DB.sched.some(x=>x.id==="s2"),
    DB.sched.map(x=>x.id).join("+"));
  A("ويُدمج التحضيرُ بالمفاتيح",
    !!(DB.prep["s1"] && DB.prep["s2"]), Object.keys(DB.prep).join("+"));

  /* ⛔ ‏`~trash~` داخل prep — المفتاحُ المستحدَثُ يضيع، وهذا هو السبب */
  DB.prep["~trash~zz"] = {L:{id:"zz"}, by:"أ. القياس"};
  pending = true; lastSent = "";
  await pushNow();
  DB.prep = {}; 
  await pullNow();
  A("وسلّةُ المحذوفات تَعبر المزامنة", !!DB.prep["~trash~zz"]);

  /* ⚠️ ومفتاحٌ مستحدَثٌ خارجَ الخمسة **يُتجاهَل** — وعليه بُنيت المنصة */
  var r0 = await fetch(api(), {method:"POST",
    headers:{"Content-Type":"text/plain;charset=utf-8"},
    body: apiBody({kind:"platform", id:SID, data:{zzNew:{a:1}}})}).then(r=>r.json());
  A("ومفتاحٌ خارجَ الخمسة يُتجاهَل", !(r0.data && r0.data.zzNew));

  /* ③ الاستبدال: كشفُ المنسوبين */
  var rid = NS + "_roster";
  await fetch(api(), {method:"POST", headers:{"Content-Type":"text/plain;charset=utf-8"},
    body: apiBody({kind:"platform", id:rid, data:{"11111":{n:"أ. نموذج"}}, __replace:true})});
  var g1 = await fetch(apiGet("platform", rid)).then(r=>r.json());
  A("والكشفُ يُخزَّن كما هو بـ__replace", !!(g1.data && g1.data["11111"]),
    JSON.stringify(g1.data).slice(0,60));
  await fetch(api(), {method:"POST", headers:{"Content-Type":"text/plain;charset=utf-8"},
    body: apiBody({kind:"platform", id:rid, data:{"22222":{n:"أ. ثانٍ"}}, __replace:true})});
  var g2 = await fetch(apiGet("platform", rid)).then(r=>r.json());
  A("ويستبدله ضخٌّ تالٍ ولا يدمجه",
    !!(g2.data && g2.data["22222"]) && !(g2.data && g2.data["11111"]));

  /* ④ المفتاحُ يُفحص */
  var bad = await fetch("__URL__?kind=platform&id=" + encodeURIComponent(SID) + "&key=ghalat")
            .then(r=>({s:r.status}));
  A("ومفتاحٌ خاطئٌ يُردّ ٤٠٣", bad.s === 403, bad.s);
  var none = await fetch("__URL__?kind=platform&id=" + encodeURIComponent(SID))
            .then(r=>({s:r.status}));
  A("وبلا مفتاحٍ أصلاً يُردّ", none.s === 403, none.s);

  localStorage.clear();
  document.title = "DONE"; window.__OUT = JSON.stringify(R);
 }catch(e){ document.title = "ERR|" + e.message; window.__OUT = JSON.stringify(R); }
}, 500);
</script>
<script>setTimeout(function(){var d=document.createElement("pre");d.id="dump";
 d.textContent=window.__OUT||"";document.body.appendChild(d);}, 9000);</script>
"""

FLOOR = 11


def free_port():
    with socketserver.TCPServer(("127.0.0.1", 0), None) as s:
        return s.server_address[1]


def main():
    port = free_port()
    shim = PRB.probe("srv_shim.mjs")
    open(shim, "w", encoding="utf-8").write(SHIM)
    # ⚠️ الوحدةُ تُستورد بالمسار النسبي، فتُنسخ بجوار الـshim كما هي
    import shutil
    if not os.path.exists(WORKER):
        print("  ⛔ لا خادمَ في مجلَّده الخاصّ:\n      %s" % WORKER)
        return 1
    shutil.copy(WORKER, os.path.join(os.path.dirname(shim), "worker.js"))
    env = dict(os.environ, PORT=str(port), STORE_KEY=KEY)
    srv = subprocess.Popen([ "node", shim], env=env, cwd=os.path.dirname(shim),
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    up = False
    for _ in range(80):
        ln = srv.stdout.readline()
        if ln.startswith("UP"):
            up = True
            break
        if srv.poll() is not None:
            print("  ⛔ لم يقم الخادم:\n" + ln + srv.stdout.read())
            return 1
    if not up:
        srv.kill()
        print("  ⛔ لم يُعلن الخادمُ قيامَه")
        return 1
    url = "http://127.0.0.1:%d/" % port
    try:
        p = PRB.probe("srv_probe.html")
        open(p, "w", encoding="utf-8").write(
            open(SRC, encoding="utf-8").read()
            + BOOT.replace("__URL__", url).replace("__KEY__", KEY))
        out = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--allow-file-access-from-files", "--virtual-time-budget=22000",
             "--dump-dom", "file://" + p], capture_output=True, text=True).stdout
    finally:
        srv.kill()
    import html as H
    m = re.search(r'<pre id="dump">(.*?)</pre>', out, re.S)
    t = re.search(r"<title>(.*?)</title>", out, re.S)
    rows = json.loads(H.unescape(m.group(1))) if (m and m.group(1).strip()) else []
    ok = True
    for r in rows:
        g = bool(r[1]); ok &= g
        print("  %s %s%s" % ("✓" if g else "⛔", r[0],
                             ("   [" + str(r[2]) + "]") if len(r) > 2 else ""))
    if t and H.unescape(t.group(1)).startswith("ERR"):
        print("  ⛔", H.unescape(t.group(1))); ok = False
    if len(rows) < FLOOR:
        print("  ⛔ %d شاهداً والأرضيّةُ %d — فحصٌ لم يكتمل" % (len(rows), FLOOR))
        ok = False
    print("\n  %s" % ("✓ الخادمُ يفي بعقد المنصة" if ok else "⛔ لا يُنشر"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
