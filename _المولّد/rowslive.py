# -*- coding: utf-8 -*-
"""⛔ **المزامنةُ الفارقةُ تُجرَّب بدوالِّ المنصة نفسِها على خادمٍ بالصفوف.**

`rowscheck` يقيس **الخادمَ**: SQL والدمجَ والترقيم. وهذا يقيس **العميلَ**:
`pullNow` و`pushNow` و`dropGone` و`seqOf` — وهي الشفرةُ الجديدةُ الخطِرة،
لأن بياناتَ معلّمين يعملون الآن تمرُّ بها.

⛔ **ولماذا لا يكفي `synccheck`؟** خادمُه المزيَّفُ يردُّ بالعقد القديم، فلا
   يسلك العميلُ طريقَ الفارقةِ أبداً — فيمرُّ الحارسُ على شفرةٍ **لم تُنفَّذ**.
   فهنا يُشغَّل `worker.js` الحقيقيُّ على sqlite حقيقيٍّ، وتُحوَّل القاعدةُ
   إلى الصفوف، ثم تُنادى دوالُّ الصفحةِ المبنيّةِ كما ينادِيها المستخدم.

⚠️ و**الربحُ يُقاس بالبايتات لا بالدعوى**: الخادمُ يسجّل حجمَ كل ردّ، ويُشترط
   أن تكون السحبةُ المتكرّرةُ أصغرَ من الكاملة بمئةِ ضعفٍ على الأقلّ. فقولُ
   «خفَّت المزامنة» بلا رقمٍ ليس شاهداً.
"""
import html as H
import json
import os
import re
import shutil
import socketserver
import subprocess
import sys

import probedir as PRB

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRVDIR = os.path.expanduser("~/Desktop/خادم الحصة الموحَّدة (خاصّ — لا يُنشر)")
WORKER = os.path.join(SRVDIR, "worker.js")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRC = os.path.join(ROOT, "٨ - النموذج الرقمي (تجربة)",
                   "منصة الحصة الموحَّدة — ابن خلدون.html")
KEY = "MFTH-TAJRIBA-1234567890ab"
AKEY = "IDARA-TAJRIBA-0987654321zz"
FLOOR = 20                 # أرضيّةُ الشواهد: فحصٌ أقلُّ منها لم يكتمل

SHIM = r"""
import worker from "./worker.js";
import { makeD1 } from "./d1mock.mjs";
import http from "node:http";
import fs from "node:fs";
const KV = new Map();
/* ⚠️ D1 حقيقيّةٌ (sqlite) لا خريطةٌ في الذاكرة: المقيسُ هو SQL نفسُه */
const env = { STORE_KEY: process.env.STORE_KEY || "", ADMIN_KEY: process.env.ADMIN_KEY || "",
  D1: makeD1(),
  DB: { get: async (k) => (KV.has(k) ? KV.get(k) : null), put: async (k, v) => { KV.set(k, v); } } };
const LOG = [];
http.createServer(async (q, s) => {
  const chunks = [];
  for await (const c of q) chunks.push(c);
  const body = Buffer.concat(chunks).toString("utf8");
  if (q.url.indexOf("/__log") === 0) {
    s.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
    s.end(JSON.stringify(LOG)); return;
  }
  const req = new Request("http://x" + q.url, { method: q.method, headers: q.headers,
    body: (q.method === "GET" || q.method === "HEAD") ? undefined : body });
  const r = await worker.fetch(req, env);
  const t = await r.text();
  /* ⚠️ يُسجَّل حجمُ الردّ ونوعُ الطلب: به يُقاس الربحُ بالبايتات */
  let tag = q.method;
  if (q.method === "GET") tag += /[?&]since=/.test(q.url) ? ":فارقة" : ":كاملة";
  else { try { const b = JSON.parse(body); tag += b.__migrate ? ":هجرة" : (b.__mode ? ":تحويل" : ":دفعة"); } catch (e) {} }
  LOG.push([tag, t.length, r.status]);
  const h = {}; r.headers.forEach((v, k) => { h[k] = v; });
  s.writeHead(r.status, h); s.end(t);
}).listen(Number(process.env.PORT), "127.0.0.1", () => console.log("UP " + process.env.PORT));
"""

BOOT = r"""
<script>
const _AK = "__AKEY__", _U = "__URL__";
function post(o){ return fetch(_U, {method:"POST", headers:{"Content-Type":"text/plain;charset=utf-8"},
  body: JSON.stringify(Object.assign({key:"__KEY__"}, o))}).then(r=>r.json()); }
setTimeout(async function(){
 var R = [];
 function A(t, ok, x){ R.push(x===undefined ? [t, !!ok] : [t, !!ok, String(x)]); }
 try{
  localStorage.clear(); load();
  localStorage.setItem(API, _U);
  localStorage.setItem(SKEY, "__KEY__");
  ME = {role:"admin", name:"أ. القياس", emp:""};

  /* ⛔ **قاعدةٌ على قدِّ الحقيقية أولاً** — وإلّا كان شاهدُ البايتات فارغاً:
     ثلاثُ حصصٍ تجعل القراءةَ الكاملةَ ٢٩١ بايتاً، فنسبتُها إلى الفارقةِ
     واحدٌ، فيسقط الشاهدُ أو يمرُّ بلا معنى. فأربعُ مئةِ حصةٍ ومئةٌ وثلاثون
     تحضيراً كما في مدارس ابن خلدون في ٦ أكتوبر ٢٠٢٦. */
  var body = "نصٌّ على قدِّ التحضير الحقيقي ".repeat(14);
  DB.sched = []; DB.prep = {};
  for(var i = 0; i < 400; i++){
    DB.sched.push({id:"S" + i, gk:"ح|" + i, teacher:"أ. معلّمُ " + i,
                   stage:"ابتدائي", spec:"رياضيات", note: body.slice(0, 60)});
    if(i % 3 === 0) DB.prep["S" + i] = {goal: body, steps:[body.slice(0,80)], tools: body.slice(0,50)};
  }
  pending = true; lastSent = "";
  A("زرعُ قاعدةٍ على قدِّ الحقيقية", await pushNow(),
    DB.sched.length + " حصة · " + Object.keys(DB.prep).length + " تحضيراً");

  /* ① جهازٌ أوّلُ يكتب حصّتَين وتحضيراً — والخادمُ ما زال بالكتلة */
  DB.sched = DB.sched.concat([{id:"A1", gk:"ق|١", teacher:"أ. الأول"}, {id:"A2", gk:"ق|٢", teacher:"أ. الأول"}]);
  DB.prep["A1"] = {goal:"هدفُ الأولى"};
  pending = true; lastSent = "";
  A("دفعةُ الكتلة نجحت", await pushNow());
  A("والترقيمُ صفرٌ في نمط الكتلة", seqOf() === 0, seqOf());

  /* ② هجرةٌ ثم مسحةٌ ختاميةٌ ثم تحويل */
  var g1 = await post({kind:"platform", id:SID, __migrate:true, limit:400});
  var g2 = {ok:true};
  /* ⚠️ والهجرةُ أشواطٌ: أربعُ مئةٍ في الشوط، فقاعدةُ ٥٣٥ صفّاً شوطان */
  while(g1.ok && !g1.done) g1 = await post({kind:"platform", id:SID, __migrate:true, limit:400});
  A("الهجرةُ تمّت بأشواط", g1.ok && g1.done && g2.ok, (g1.total||0) + " صفّاً جملةً");
  /* ومسحةٌ ختاميةٌ: ما كُتب وقتَ الهجرة يُلحَق، وما لم يتغيّر لا يُكتب */
  var sw = await post({kind:"platform", id:SID, __migrate:true, limit:4000, sweep:true});
  A("والمسحةُ الختاميةُ تمرُّ", sw.ok && sw.done, (sw.wrote||0) + " صفّاً أُلحق");
  var md = await post({kind:"platform", id:SID, __mode:"rows", admin:_AK});
  A("وتحوّل التخزينُ إلى الصفوف", md.ok && md.mode === "rows", md.error || md.mode);

  /* ③ أولُ سحبةٍ كاملةٌ وتُعطي ترقيماً */
  setSeq(0);
  A("وأولُ سحبةٍ تنجح", await pullNow());
  A("وتُعطي ترقيماً", seqOf() > 0, seqOf());
  A("ولا تُفقد الحصتان", DB.sched.length === 402 && !!DB.prep["A1"], DB.sched.length + " حصة");

  /* ④ سحبةٌ فارقةٌ بلا جديد: تُعيد «لا جديد» فلا يُعاد الرسم */
  A("وسحبةٌ بلا جديدٍ تُعيد «لا جديد»", (await pullNow()) === false);

  /* ⑤ الجهازُ يكتب ثالثةً فيتقدّم الترقيم */
  var sq1 = seqOf();
  DB.sched.push({id:"A3", gk:"ق|٣", teacher:"أ. الأول"});
  DB.prep["A3"] = {goal:"هدفُ الثالثة"};
  pending = true;
  await pushNow();
  A("والترقيمُ يتقدّم بعد الدفعة", seqOf() > sq1, sq1 + "→" + seqOf());

  /* ⑥ جهازٌ ثانٍ (قاعدةٌ خاويةٌ وترقيمٌ صفرٌ) يرى الثلاثةَ */
  var keep = JSON.stringify(DB);
  DB = {sched:[], prep:{}, obs:{}, peer:{}, rot:{}, __seq:0}; lastSent = ""; pending = false;
  await pullNow();
  A("وجهازٌ جديدٌ يرى القاعدةَ كلَّها", DB.sched.length === 403, DB.sched.length + " حصة");
  A("ويرى تحضيراتِها", !!DB.prep["A1"] && !!DB.prep["A3"]);

  /* ⑦ وخليةٌ محجوزةٌ تُردُّ عليه ويُزال ما كتبه */
  DB.sched.push({id:"X9", gk:"ق|١", teacher:"أ. المتطفّل"});
  DB.prep["X9"] = {goal:"لن يُحفظ"};
  pending = true; lastSent = "";
  await pushNow();
  await new Promise(r=>setTimeout(r, 400));
  A("وخليةٌ محجوزةٌ تُزال من الجهاز", !DB.sched.some(x=>x.id === "X9") && DB.sched.length === 403, DB.sched.length + " حصة");

  /* ⑧ الجهازُ الثاني يحذف A2 حذفاً صريحاً */
  DB.__deleted = ["A2"];
  DB.sched = DB.sched.filter(x=>x.id !== "A2");
  delete DB.prep["A2"];
  pending = true; lastSent = "";
  await pushNow();
  delete DB.__deleted;
  A("والحذفُ يُقبل", !DB.sched.some(x=>x.id === "A2"));

  /* ⑨ والجهازُ الأولُ يعود بترقيمه القديم: الفارقةُ تُسقط المحذوف */
  DB = JSON.parse(keep); lastSent = dbSnapshot(); pending = false;
  A("وللأول ترقيمٌ سابقٌ محفوظٌ مع قاعدته", seqOf() > 0, seqOf());
  A("وسحبتُه الفارقةُ تأتي بجديد", await pullNow());
  A("والمحذوفُ يسقط عنده بـgone لا بالغياب", !DB.sched.some(x=>x.id === "A2"), DB.sched.length + " حصة");
  A("ويسقط تحضيرُه معه", !DB.prep["A2"]);
  A("ولا يسقط غيرُه", DB.sched.length === 402 && !!DB.prep["A1"] && !!DB.prep["A3"],
    DB.sched.length + " حصة");

  /* ⑩ ⛔ **والترقيمُ ليس بياناً**: لو دخل في لقطةِ القاعدة لرأى `pushNow`
     أن القاعدةَ تغيّرت بعد كلِّ سحبةٍ (والسحبةُ تُحدّث الترقيمَ دائماً)،
     فدفع فارقةً خاويةً، فزاد الخادمُ الترقيمَ، فتغيّرت اللقطةُ من جديد —
     **حلقةُ طلبٍ لا تنتهي، كلَّ اثنتي عشرةَ ثانيةً من كلِّ جهاز**. وهذا
     العيبُ مرَّ على الحارس في أول تجربةٍ له، فصار له شاهدٌ يقيسه. */
  lastSent = dbSnapshot();
  setSeq(seqOf() + 5);
  A("والترقيمُ لا يُحسب تغييراً في القاعدة", dbSnapshot() === lastSent,
    "لقطتان " + (dbSnapshot() === lastSent ? "متساويتان" : "مختلفتان"));
  setSeq(seqOf() - 5);

  /* ⑪ والرجوعُ إلى الكتلة لا يُفقد ما كان فيها */
  var bk = await post({kind:"platform", id:SID, __mode:"blob", admin:_AK});
  setSeq(0);
  await pullNow();
  A("والرجوعُ إلى الكتلة يُخدَم", bk.ok && DB.sched.length >= 400, DB.sched.length + " حصة");

  window.__LOG = JSON.stringify(await (await fetch(_U.replace(/\/$/, "") + "/__log")).json());
  localStorage.clear();
  document.title = "DONE"; window.__OUT = JSON.stringify(R);
 }catch(e){ document.title = "ERR|" + e.message; window.__OUT = JSON.stringify(R); }
}, 500);
</script>
<script>setTimeout(function(){
 var d=document.createElement("pre"); d.id="dump"; d.textContent=window.__OUT||""; document.body.appendChild(d);
 var l=document.createElement("pre"); l.id="net"; l.textContent=window.__LOG||""; document.body.appendChild(l);
}, 15000);</script>
"""

D1MOCK = r"""/* محاكي D1 على sqlite حقيقيّ — فالسؤالُ المقيسُ هو SQL نفسُه لا شكلُه */
import { DatabaseSync } from "node:sqlite";

export function makeD1(path = ":memory:") {
  const db = new DatabaseSync(path);
  let writes = 0, reads = 0, stmts = 0;
  const run1 = (sql, args) => {
    stmts++;
    const s = db.prepare(sql);
    const up = /^\s*(insert|update|delete|replace)/i.test(sql);
    if (up) { const r = s.run(...args); writes += Number(r.changes || 0); return { success: true, meta: { changes: Number(r.changes || 0) } }; }
    const rows = s.all(...args); reads += rows.length;
    return { success: true, results: rows, meta: {} };
  };
  const mkStmt = (sql, args = []) => ({
    sql, args,
    bind: (...a) => mkStmt(sql, a),
    first: async (col) => {
      const r = run1(sql, args);
      const x = (r.results || [])[0];
      if (!x) return null;
      return col === undefined ? x : x[col];
    },
    all: async () => run1(sql, args),
    run: async () => run1(sql, args),
  });
  return {
    _db: db,
    _cost: () => ({ writes, reads, stmts }),
    _reset: () => { writes = 0; reads = 0; stmts = 0; },
    exec: async (sql) => { db.exec(sql); return { count: 1 }; },
    prepare: (sql) => mkStmt(sql),
    batch: async (list) => {
      db.exec("BEGIN");
      try {
        const out = [];
        for (const st of list) out.push(run1(st.sql, st.args));
        db.exec("COMMIT");
        return out;
      } catch (e) { db.exec("ROLLBACK"); throw e; }
    },
  };
}
"""


def free_port():
    with socketserver.TCPServer(("127.0.0.1", 0), None) as s:
        return s.server_address[1]


def main():
    if not os.path.exists(WORKER):
        print("  ⛔ لا خادمَ في مجلَّده الخاصّ:\n      %s" % WORKER)
        return 1
    if not os.path.exists(SRC):
        print("  ⛔ لم تُبنَ المنصةُ بعد — ولا يُفحص ما لم يُبنَ.")
        return 1
    port = free_port()
    shim = PRB.probe("rl_shim.mjs")
    d = os.path.dirname(shim)
    open(shim, "w", encoding="utf-8").write(SHIM)
    open(os.path.join(d, "d1mock.mjs"), "w", encoding="utf-8").write(D1MOCK)
    open(os.path.join(d, "package.json"), "w", encoding="utf-8").write('{"type":"module"}')
    shutil.copy(WORKER, os.path.join(d, "worker.js"))
    env = dict(os.environ, PORT=str(port), STORE_KEY=KEY, ADMIN_KEY=AKEY, NODE_NO_WARNINGS="1")
    srv = subprocess.Popen(["node", shim], env=env, cwd=d,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for _ in range(80):
        ln = srv.stdout.readline()
        if ln.startswith("UP"):
            break
        if srv.poll() is not None:
            print("  ⛔ لم يقم الخادم:\n" + ln + srv.stdout.read())
            return 1
    else:
        srv.kill()
        print("  ⛔ لم يُعلن الخادمُ قيامَه")
        return 1
    url = "http://127.0.0.1:%d/" % port
    try:
        p = PRB.probe("rl_probe.html")
        open(p, "w", encoding="utf-8").write(
            open(SRC, encoding="utf-8").read()
            + BOOT.replace("__URL__", url).replace("__KEY__", KEY).replace("__AKEY__", AKEY))
        out = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--allow-file-access-from-files", "--virtual-time-budget=30000",
             "--dump-dom", "file://" + p], capture_output=True, text=True).stdout
    finally:
        srv.kill()

    m = re.search(r'<pre id="dump">(.*?)</pre>', out, re.S)
    nt = re.search(r'<pre id="net">(.*?)</pre>', out, re.S)
    t = re.search(r"<title>(.*?)</title>", out, re.S)
    rows = json.loads(H.unescape(m.group(1))) if (m and m.group(1).strip()) else []
    ok = True
    for r in rows:
        g = bool(r[1])
        ok &= g
        print("  %s %s%s" % ("✓" if g else "⛔", r[0],
                             ("   [" + str(r[2]) + "]") if len(r) > 2 else ""))
    if t and H.unescape(t.group(1)).startswith("ERR"):
        print("  ⛔", H.unescape(t.group(1)))
        ok = False
    if len(rows) < FLOOR:
        print("  ⛔ %d شاهداً والأرضيّةُ %d — فحصٌ لم يكتمل" % (len(rows), FLOOR))
        ok = False

    # ── والربحُ بالبايتات: لا دعوى بلا رقم ──
    log = json.loads(H.unescape(nt.group(1))) if (nt and nt.group(1).strip()) else []
    if not log:
        print("  ⛔ لم يُسجَّل شيءٌ من حركة الشبكة — فحصٌ لم يَقِس شيئاً")
        return 1
    # ⛔ **ولا تُقاس إلا الحركةُ في نمط الصفوف**: الدفعةُ الأولى جرت والخادمُ
    #    بالكتلة، فردُّها حمل القاعدةَ (١٤٢ ك.ب) — وهو الصحيحُ هناك. فكان
    #    الشاهدُ يسقط على سلوكٍ سليم. فتُقتطع النافذةُ بين التحويلَين.
    sw = [i for i, (tg, b, st) in enumerate(log) if tg == "POST:تحويل"]
    if len(sw) < 2:
        print("  ⛔ لم يُسجَّل تحويلا النمط — فلا نافذةَ تُقاس")
        return 1
    win = log[sw[0] + 1:sw[-1]]
    full = [b for (tg, b, st) in win if tg == "GET:كاملة"]
    diff = [b for (tg, b, st) in win if tg == "GET:فارقة"]
    push = [b for (tg, b, st) in win if tg == "POST:دفعة"]
    print("\n  ── حركةُ الشبكة في نمط الصفوف (%d طلباً من %d) ──" % (len(win), len(log)))
    print("     قراءةٌ كاملةٌ  %d مرةً · أكبرُها %s بايتاً" % (len(full), max(full) if full else 0))
    print("     قراءةٌ فارقةٌ  %d مرةً · أكبرُها %s بايتاً" % (len(diff), max(diff) if diff else 0))
    print("     ردُّ الدفعة    %d مرةً · أكبرُها %s بايتاً" % (len(push), max(push) if push else 0))
    if not diff:
        print("  ⛔ لم تجرِ سحبةٌ فارقةٌ واحدةٌ — فالشفرةُ الجديدةُ لم تُنفَّذ")
        ok = False
    elif not full:
        print("  ⛔ لم تجرِ سحبةٌ كاملةٌ — فلا أساسَ للمقارنة")
        ok = False
    elif max(full) < 100000:
        # ⛔ **ولا نسبةٌ على قاعدةٍ صغيرة**: ثلاثُ حصصٍ تجعل الكاملةَ ٢٩١ بايتاً
        #    فتكون النسبةُ واحداً — فالشاهدُ يسقط أو يمرُّ ولم يَقِس شيئاً.
        print("  ⛔ الكاملةُ %d بايتاً فقط — القاعدةُ أصغرُ من أن تُقاس (الأرضيّةُ ١٠٠ ك.ب)" % max(full))
        ok = False
    else:
        r = max(full) / max(1, max(diff))
        g = r >= 100
        print("  %s والفارقةُ أخفُّ من الكاملة %d ضعفاً (المطلوب ١٠٠)" % ("✓" if g else "⛔", r))
        ok &= g
    if push:
        g = max(push) < 400
        print("  %s وردُّ الدفعةِ لا يحمل القاعدةَ (%d بايتاً)" % ("✓" if g else "⛔", max(push)))
        ok &= g
    print("\n  %s" % ("✓ المزامنةُ الفارقةُ تفي بعقد المنصة" if ok else "⛔ لا يُنشر"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
