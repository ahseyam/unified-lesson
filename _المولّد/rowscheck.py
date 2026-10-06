# -*- coding: utf-8 -*-
"""⛔ **التخزينُ صفّاً صفّاً يُجرَّب على SQL حقيقيٍّ لا بالقراءة.**

⚠️ والشفرةُ المقيسةُ هي **الخادمُ القائم** في مجلَّده الخاصّ خارج شجرة التسليم
   — لا نسخةٌ ثانيةٌ في المولّد. فنسختان تفترقان، والمقيسُ غيرُ المنشور لا
   يُثبت شيئاً. (القاعدةُ نفسُها التي يقوم عليها `srvcheck`.)

⛔ **ولماذا هذا الحارسُ أصلاً؟** في ٦ أكتوبر ٢٠٢٦ سقط الخادمُ ٥٠٣ لأن القاعدةَ
   كانت كتلةً واحدةً تُفكُّ وتُركَّب في كل عملية. فصار لكلِّ حصةٍ وتحضيرٍ صفُّه،
   والقراءةُ المتكرّرةُ تطلب **ما استجدَّ بعد ترقيمٍ تعرفه**. وهذا تغييرٌ في
   موضعِ بياناتِ معلمين يعملون الآن — فلا يُنشر بلا قياس.

⚠️ ويُشغَّل على **sqlite حقيقيٍّ** (`node:sqlite`) يحاكي واجهةَ D1: فالمقيسُ
   هو SQL نفسُه — `ON CONFLICT` و`IS NOT` والقراءةُ الفرعيّةُ في `VALUES` —
   لا شكلُ الشفرة. ومحاكٍ بخريطةٍ في الذاكرة كان سيُمرّر عبارةً لا تعمل.

⚠️ و**يُجرَّب الحارسُ على عيوبٍ مزروعةٍ في كل تشغيل**: خمسةَ عشرَ عيباً تُزرع
   واحداً واحداً في نسخةٍ من الخادم، ويُشترط أن يُسقط كلٌّ منها شاهدَه بعينه.
   فحارسٌ لم يُجرَّب على عيبٍ لا يُعتمد — وقد مرَّ عيبان في أول تجربةٍ لأن
   شاهدَيهما **لم يقيسا شيئاً**: السجلُّ مقصوصٌ على كلِّ حالٍ فنزعُ أرضيّتِه
   لا يُرى بالوجود (ويُرى بثمنِ الكتابة)، وقسمُ `obs` خاوٍ في القاعدة الحقيقية
   فإسقاطُه من القراءة لا يُكشف (فصار للأقسام الخمسة أرضيّةُ شواهد).
"""
import io
import json
import os
import random
import shutil
import subprocess
import sys

import probedir as PRB

HERE = os.path.dirname(os.path.abspath(__file__))
SRVDIR = os.path.expanduser("~/Desktop/خادم الحصة الموحَّدة (خاصّ — لا يُنشر)")
WORKER = os.path.join(SRVDIR, "worker.js")

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
TEST = r"""import worker from "./worker.js";
import { makeD1 } from "./d1mock.mjs";
import fs from "node:fs";

const KEY = "JOIN-TEST-000", ADM = "ADMIN-TEST-999";
let R = [], fails = 0;
const A = (t, ok, x) => { R.push([!!ok, t, x === undefined ? "" : String(x)]); if (!ok) fails++;
  console.log((ok ? "  \u2713 " : "  \u26d4 ") + t + (x === undefined ? "" : "   [" + String(x) + "]")); };

function mkEnv(blob) {
  const KV = new Map();
  if (blob) KV.set("platform:ikm_db", blob);
  const d1 = makeD1();
  return { STORE_KEY: KEY, ADMIN_KEY: ADM, D1: d1, _kv: KV,
    DB: { get: async (k) => (KV.has(k) ? KV.get(k) : null), put: async (k, v) => { KV.set(k, v); } } };
}
// ⚠️ env.D1 و env.DB معاً يُشغّل migrateOnce؛ وهو ما يجري في المضيف فعلاً.
// لكن طبقةَ store تُفضّل D1 — فالكتلةُ تسكن جدولَ store في D1 لا الـKV.
async function seedBlob(env, blob) {
  await env.D1.exec("CREATE TABLE IF NOT EXISTS store (k TEXT PRIMARY KEY, v TEXT, at TEXT)");
  env.D1._db.prepare("INSERT OR REPLACE INTO store (k,v,at) VALUES (?,?,?)")
    .run("platform:ikm_db", blob, new Date().toISOString());
}

const G = (env, q) => worker.fetch(new Request("http://x/?" + q), env);
const P = (env, o) => worker.fetch(new Request("http://x/", { method: "POST", body: JSON.stringify(Object.assign({ key: KEY }, o)) }), env);
const jj = async (r) => { const t = await r.text(); try { return JSON.parse(t); } catch (e) { return { __bad: t.slice(0, 300) }; } };

/* ═══ ① الهجرةُ على القاعدة الحقيقية، ثم مقابلةُ الصفوف بالكتلة ═══ */
const blob = JSON.parse(fs.readFileSync("fixture.json", "utf8")).data;
/* ⛔ **القاعدةُ الحقيقيةُ بلا `obs` ولا `peer`** — فإسقاطُ أحدِهما من القراءة
   الكاملة كان يمرُّ بلا كشف: الشاهدُ لم يقس شيئاً. فتُزرع في الأقسام الخمسةِ
   كلِّها سجلاتٌ، ويُشترط أن تكون كلُّها غيرَ خاوية قبل أن تُقبل المطابقة. */
const anchorL = (blob.sched || [])[0] || { id: "x0" };
blob.obs = Object.assign({}, blob.obs, { [anchorL.id + "|مشرف"]: { sc: { "م1": 3 }, by: "أ. المقيس" } });
blob.peer = Object.assign({}, blob.peer, { [anchorL.id + "|زائر"]: { note: "بطاقةُ قرين" } });
blob.rot = Object.assign({}, blob.rot, { "دورانُ القياس": ["أ", "ب"] });
const blobTxt = JSON.stringify(blob);
const env = mkEnv(null);
await seedBlob(env, blobTxt);

let calls = 0, wrote = 0, res;
for (;;) {
  res = await jj(await P(env, { kind: "platform", id: "ikm_db", __migrate: true, limit: 400 }));
  calls++; wrote += res.wrote || 0;
  if (res.done || calls > 40) break;
}
A("الهجرةُ تنتهي بأشواطٍ محدودة", res.done, calls + " شوطاً · " + wrote + " صفّاً من " + res.total);
/* ⚠️ ومسحةٌ ختاميةٌ: بها وحدَها يُعلَم أن الصفوفَ لحقت الكتلةَ، وبلا ذلك
   يُرفض التحويلُ — وهو المقصود. */
const swp = await jj(await P(env, { kind: "platform", id: "ikm_db", __migrate: true, limit: 9000, sweep: true }));
A("والمسحةُ الختاميةُ تتمّ", swp.ok && swp.done, (swp.wrote || 0) + " صفّاً أُلحق");

const st0 = await jj(await G(env, "kind=platform&id=ikm_db&stat=1&key=" + KEY));
A("وتُسجَّل الصفوفُ في الجدول", st0.ok && ((st0.stat||{}).parts||{}).sched, JSON.stringify(st0.stat && st0.stat.parts));
/* ⚠️ أرضيّةُ الشواهد: لا تُقبل مطابقةٌ وقسمٌ من الخمسة خاوٍ — فالخاوي لا يُقاس */
const P5 = ["sched", "prep", "obs", "peer", "rot"];
A("والأقسامُ الخمسةُ كلُّها فيها ما يُقاس",
  P5.every(p => (((st0.stat||{}).parts||{})[p]||{}).n > 0),
  P5.map(p => p + "=" + ((((st0.stat||{}).parts||{})[p]||{}).n || 0)).join(" · "));

/* المقابلة: الكاملةُ من الصفوف مقابلَ الكتلة، سجلاً سجلاً */
const rowsTxt = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
const rows = rowsTxt.data;
function cmp(a, b) {
  const miss = [], diff = [];
  const ai = {}; (a.sched || []).forEach(x => { if (x && x.id) ai[x.id] = x; });
  const bi = {}; (b.sched || []).forEach(x => { if (x && x.id) bi[x.id] = x; });
  Object.keys(ai).forEach(k => { if (!bi[k]) miss.push("sched:" + k); else if (JSON.stringify(ai[k]) !== JSON.stringify(bi[k])) diff.push("sched:" + k); });
  Object.keys(bi).forEach(k => { if (!ai[k]) miss.push("+sched:" + k); });
  ["prep", "obs", "peer", "rot"].forEach(p => {
    const x = a[p] || {}, y = b[p] || {};
    Object.keys(x).forEach(k => { if (!(k in y)) miss.push(p + ":" + k); else if (JSON.stringify(x[k]) !== JSON.stringify(y[k])) diff.push(p + ":" + k); });
    Object.keys(y).forEach(k => { if (!(k in x)) miss.push("+" + p + ":" + k); });
  });
  return { miss, diff };
}
const c = cmp(blob, rows);
A("والصفوفُ تُعيد الكتلةَ سجلاً بسجل — لا ناقصَ ولا مختلف",
  c.miss.length === 0 && c.diff.length === 0,
  "ناقص " + c.miss.length + " · مختلف " + c.diff.length +
  (c.miss.length ? " [" + c.miss.slice(0, 4).join(" ") + "]" : "") +
  (c.diff.length ? " {" + c.diff.slice(0, 4).join(" ") + "}" : ""));
A("والأعدادُ هي هي",
  (rows.sched || []).length === (blob.sched || []).length &&
  Object.keys(rows.prep || {}).length === Object.keys(blob.prep || {}).length,
  (rows.sched || []).length + "/" + (blob.sched || []).length + " حصة · " +
  Object.keys(rows.prep || {}).length + "/" + Object.keys(blob.prep || {}).length + " مفتاحَ prep");

/* ═══ ② تحويلُ النمط محروسٌ ═══ */
let r = await jj(await P(env, { kind: "platform", id: "ikm_db", __mode: "rows" }));
A("ولا يُحوَّل النمطُ بمفتاح الانضمام", r.ok === false, r.error);
r = await jj(await P(env, { kind: "platform", id: "ikm_db", __mode: "rows", admin: ADM }));
A("ويُحوَّل بمفتاح الإدارة", r.ok && r.mode === "rows", r.error || r.mode);

/* ═══ ③ القراءةُ الكاملةُ بعد التحويل تُطابق الكتلة ═══ */
const after = await jj(await G(env, "kind=platform&id=ikm_db&key=" + KEY));
A("والقراءةُ العاديةُ صارت من الصفوف", after.mode === "rows" && after.seq > 0, "seq=" + after.seq);
const c2 = cmp(blob, after.data);
A("وتُطابق الكتلةَ تماماً", c2.miss.length === 0 && c2.diff.length === 0,
  "ناقص " + c2.miss.length + " · مختلف " + c2.diff.length);

/* ═══ ④ الفارقة: دفعةٌ صغيرةٌ ثم «ما بعد الترقيم» ═══ */
const seq0 = after.seq;
r = await jj(await P(env, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: "NEW1", gk: "zz|1", teacher: "أ. جديد" }], prep: { NEW1: { goal: "هدف" } } } }));
A("والكتابةُ بالنسخة الثانية لا تُعيد القاعدة", r.ok && !r.data && r.seq > seq0, "seq=" + r.seq + " data=" + (r.data ? "نعم" : "لا"));
const inc = await jj(await G(env, "kind=platform&id=ikm_db&v=2&since=" + seq0 + "&key=" + KEY));
A("والفارقةُ تحمل المستجدَّ وحدَه", inc.inc === true && (inc.data.sched || []).length === 1 &&
  Object.keys(inc.data.prep || {}).length === 1,
  "حصص " + (inc.data.sched || []).length + " · prep " + Object.keys(inc.data.prep || {}).length);
A("وحجمُها جزءٌ من ألفٍ من الكاملة",
  JSON.stringify(inc).length * 300 < blobTxt.length,
  JSON.stringify(inc).length + " بايتاً مقابل " + blobTxt.length);

/* ═══ ⑤ منعُ ازدواج الخلية ═══ */
const taken = blob.sched[0];
r = await jj(await P(env, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: "DUP1", gk: taken.gk, teacher: "أ. المتطفّل" }] } }));
A("وخليةٌ محجوزةٌ تُردّ ولا تُقبل", r.ok && r.conflicts && r.conflicts.length === 1,
  JSON.stringify(r.conflicts || []).slice(0, 120));
A("ويُسمّى من سبق", (r.conflicts || [{}])[0].by === (taken.teacher || ""), (r.conflicts || [{}])[0].by);
const chk = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
A("ولا يدخل الصفوفَ", !(chk.data.sched || []).some(x => x.id === "DUP1"));
A("وصاحبُها القديمُ باقٍ", (chk.data.sched || []).some(x => x.id === taken.id));

/* وازدواجٌ داخل دفعةٍ واحدة */
r = await jj(await P(env, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: "T1", gk: "same|cell", teacher: "أ. الأول" }, { id: "T2", gk: "same|cell", teacher: "أ. الثاني" }] } }));
A("وازدواجٌ في الدفعة نفسِها يُردُّ أحدُهما", (r.conflicts || []).length === 1, JSON.stringify(r.conflicts || []));

/* ═══ ⑥ تعديلُ حصّةٍ قائمةٍ يُدمج حقولاً ولا يُعدُّ تصادماً ═══ */
r = await jj(await P(env, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: taken.id, note: "ملاحظةٌ مضافة" }] } }));
A("وتعديلُ حصّتي لا يُعدُّ تصادماً", (r.conflicts || []).length === 0);
const m2 = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
const got = (m2.data.sched || []).find(x => x.id === taken.id);
A("ويُدمج الحقلُ ولا يُستبدل السجلّ", got && got.note === "ملاحظةٌ مضافة" && got.teacher === taken.teacher,
  got ? Object.keys(got).length + " حقلاً" : "مفقود");

/* ═══ ⑦ الحذفُ شاهدٌ: يُذكر في gone ═══ */
const sq = (await jj(await G(env, "kind=platform&id=ikm_db&key=" + KEY))).seq;
r = await jj(await P(env, { kind: "platform", id: "ikm_db", v: 2, data: { __deleted: ["NEW1"] } }));
A("والحذفُ يُقبل", r.ok, r.error);
const g2 = await jj(await G(env, "kind=platform&id=ikm_db&v=2&since=" + sq + "&key=" + KEY));
A("ويصل الأجهزةَ في gone لا بالغياب", ((g2.gone||{}).sched || []).indexOf("NEW1") >= 0 && ((g2.gone||{}).prep || []).indexOf("NEW1") >= 0,
  JSON.stringify(g2.gone) + " inc=" + g2.inc + " seq=" + g2.seq);
const g3 = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
A("ولا يبقى في الكاملة", !(g3.data.sched || []).some(x => x.id === "NEW1") && !("NEW1" in (g3.data.prep || {})));

/* ═══ ⑧ حذفٌ جماعيٌّ يُردّ بلا مفتاح إدارة ═══ */
const many = (blob.sched || []).slice(0, 60).map(x => x.id);
r = await jj(await P(env, { kind: "platform", id: "ikm_db", v: 2, data: { __deleted: many } }));
A("وحذفُ ستّين حصةً يُردُّ بلا مفتاح إدارة", r.ok === false && /مفتاحَ الإدارة/.test(r.error || ""), r.error);
const g4 = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
A("ولا تُمَسُّ حصةٌ واحدة", (g4.data.sched || []).filter(x => many.indexOf(x.id) >= 0).length === many.length,
  (g4.data.sched || []).filter(x => many.indexOf(x.id) >= 0).length + "/" + many.length);

/* ═══ ⑨ دفعةٌ كاملةٌ لم تتغيّر: لا تكتب شيئاً ═══ */
const full = g4.data;
env.D1._reset();
await P(env, { kind: "platform", id: "ikm_db", v: 2, data: full });
const cost = env.D1._cost();
A("ودفعةٌ كاملةٌ بلا تغييرٍ لا تكتب إلا الترقيم", cost.writes <= 3,
  cost.writes + " صفّاً مكتوباً من " + ((full.sched || []).length + Object.keys(full.prep || {}).length) + " مُرسَل");

/* ═══ ⑩ العميلُ القديم: يأخذ القاعدةَ كاملةً في ردِّ الكتابة ═══ */
r = await jj(await P(env, { kind: "platform", id: "ikm_db", data: { rot: { probeOld: "1" } } }));
A("والعميلُ القديمُ يتلقّى القاعدةَ كما كان", r.ok && r.data && (r.data.sched || []).length > 300,
  r.data ? (r.data.sched || []).length + " حصة" : "لا data");
A("ولا تصل العميلَ القديمَ فارقةٌ أبداً",
  !(await jj(await G(env, "kind=platform&id=ikm_db&since=5&key=" + KEY))).inc);

/* ═══ ⑪ المفتاحُ يُفحص قبل كل شيء ═══ */
A("وقراءةٌ بمفتاحٍ خاطئٍ تُردّ ٤٠٣", (await G(env, "kind=platform&id=ikm_db&key=خطأ")).status === 403);
A("وهجرةٌ بمفتاحٍ خاطئٍ تُردّ",
  (await worker.fetch(new Request("http://x/", { method: "POST", body: JSON.stringify({ key: "خطأ", __migrate: true }) }), env)).status === 403);

/* ═══ ⑫ قصُّ السجلّ وأرضيّتُه ═══ */
const logs = {};
for (let i = 0; i < 300; i++) logs["~log~" + (2000000 + i).toString(36) + "|x" + i] = { a: i };
await P(env, { kind: "platform", id: "ikm_db", v: 2, data: { prep: logs } });
const st1 = await jj(await G(env, "kind=platform&id=ikm_db&stat=1&key=" + KEY));
A("والسجلُّ مقصوصٌ عند ألفَين", (st1.stat||{}).logs === 2000, (st1.stat||{}).logs + " مدخلاً");
A("وتُسجَّل أرضيّةٌ للقصّ", !!(st1.stat||{}).logfloor, (st1.stat||{}).logfloor);
/* ⛔ **الشاهدُ الأولُ هنا لم يقس شيئاً**: كان يتحقّق أن المدخلَ القديمَ ليس
   في القاعدة — وهو ليس فيها على كل حال، لأن القصَّ يجري بعد الكتابة فيحذفه.
   فمرَّ نزعُ الأرضيّةِ بلا كشف. والضررُ الحقيقيُّ **ثمنُ الكتابة**: جهازٌ
   قديمٌ يُعيد خمسَ مئةِ مدخلٍ فتُكتب كلُّها ثم تُحذف — ذبذبةٌ تستنفد حدَّ
   المئةِ ألفِ كتابةٍ يومياً. فيُقاس العددُ المكتوبُ لا الوجود. */
const stale = {};
for (let i = 0; i < 500; i++) stale["~log~0000" + i.toString(36).padStart(4, "0") + "|قديم"] = { a: i };
env.D1._reset();
await P(env, { kind: "platform", id: "ikm_db", v: 2, data: { prep: stale } });
const costStale = env.D1._cost();
A("ولا يُقيمُ جهازٌ قديمٌ ما قُصَّ — ولا يُكتب حرفٌ منه", costStale.writes <= 3,
  costStale.writes + " صفّاً مكتوباً من 500 مُرسَلٍ قديم");
const st2 = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
A("ولا يدخل القاعدةَ منه شيء",
  !Object.keys(st2.data.prep || {}).some(k => k.indexOf("~log~0000") === 0));
A("ويبقى السجلُّ الحديثُ كما هو",
  Object.keys(st2.data.prep || {}).filter(k => k.indexOf("~log~") === 0).length === 2000,
  Object.keys(st2.data.prep || {}).filter(k => k.indexOf("~log~") === 0).length + " مدخلاً");

/* ═══ ⑬ الرجوعُ إلى الكتلة بنقرة ═══ */
r = await jj(await P(env, { kind: "platform", id: "ikm_db", __mode: "blob", admin: ADM }));
A("والرجوعُ إلى الكتلة يُقبل", r.ok && r.mode === "blob");
const back = await jj(await G(env, "kind=platform&id=ikm_db&key=" + KEY));
A("وتُخدَم الكتلةُ المحفوظةُ كما كانت", back.mode === "blob" && (back.data.sched || []).length === (blob.sched || []).length,
  (back.data.sched || []).length + " حصة");

/* ═══ ⑭ ⛔ **الرجوعُ ثم العودةُ لا يُخفي ما كُتب بينهما** ═══
   من رجع إلى الكتلة فسجّل المعلمون فيها، ثم عاد إلى الصفوف — وجد الصفوفَ
   متخلّفةً فتُخدَم ناقصةً **بلا خطأ**، وترقيمُ الأجهزة صالحٌ فلا تطلب
   الكاملة. فيُمنع التحويلُ حتى تُعاد الهجرة. (الوضعُ الآن: كتلة) */
r = await jj(await P(env, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: "BLOBONLY", gk: "ب|١", teacher: "أ. كُتب في الكتلة" }] } }));
A("وكتابةٌ على الكتلة تُقبل", r.ok);
r = await jj(await P(env, { kind: "platform", id: "ikm_db", __mode: "rows", admin: ADM }));
A("ثم يُمنع العودُ إلى صفوفٍ متخلّفة", r.ok === false && /بعد آخر هجرة/.test(r.error || ""), r.error);
let s2;
for (;;) { s2 = await jj(await P(env, { kind: "platform", id: "ikm_db", __migrate: true, limit: 9000 })); if (s2.done || !s2.ok) break; }
await jj(await P(env, { kind: "platform", id: "ikm_db", __migrate: true, limit: 9000, sweep: true }));
r = await jj(await P(env, { kind: "platform", id: "ikm_db", __mode: "rows", admin: ADM }));
A("وبعد إعادة الهجرة يُقبل", r.ok && r.mode === "rows", r.error || r.mode);
const bo = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
A("وما كُتب في الكتلة صار في الصفوف", (bo.data.sched || []).some(x => x.id === "BLOBONLY"));

/* ═══ ⑮ ولا يُحوَّل النمطُ قبل الهجرة ═══ */
const e2 = mkEnv(null);
await seedBlob(e2, blobTxt);
r = await jj(await P(e2, { kind: "platform", id: "ikm_db", __mode: "rows", admin: ADM }));
A("ولا تحويلَ قبل الهجرة", r.ok === false, r.error);

/* ⚠️ أرضيّةُ الشواهد: فحصٌ انقطع في منتصفه يُعلن نجاحاً كاذباً */
const FLOOR = 40;
let w = R.filter(x => !x[0]).length;
if (R.length < FLOOR) { console.log("  ⛔ " + R.length + " شاهداً والأرضيّةُ " + FLOOR + " — فحصٌ لم يكتمل"); w++; }
console.log("\n  " + (w ? "⛔ سقط " + w + " من " + R.length : "✓ " + R.length + " شاهداً كلُّها تمرّ"));
process.exit(w ? 1 : 0);
"""

# ⚠️ عيوبٌ تُزرع، ولكلٍّ **شاهدُه بعينه**: لو سقط الحارسُ بشاهدٍ آخر لم يُقبل،
#    فالمقصودُ أن يكشف العيبَ المزروعَ لا أن يفشل لأي سبب.
FAULTS = [
    ("نزعُ شرطِ «ما لم يتغيّر لا يُكتب»",
     '"WHERE rec.v IS NOT excluded.v OR rec.del <> 0").bind(db, part, rk, v, gk || null, db);',
     '"").bind(db, part, rk, v, gk || null, db);', "دفعةٌ كاملةٌ بلا تغيير"),
    ("نزعُ منعِ ازدواج الخلية",
     "        if (own && own.rk !== x.id) {", "        if (false) {", "خليةٌ محجوزةٌ تُردّ"),
    ("نزعُ منعِ الازدواج داخل الدفعة",
     "        if (mine && mine !== x.id) {", "        if (false) {", "الدفعة نفسِها"),
    ("جعلُ الحذفِ محواً بلا شاهد",
     '"UPDATE rec SET del = 1, v = NULL, seq = " + SEQ +\n'
     '    " WHERE db = ? AND part = ? AND rk = ? AND del = 0").bind(db, db, part, rk);',
     '"DELETE FROM rec WHERE db = ? AND part = ? AND rk = ?").bind(db, part, rk);',
     "يصل الأجهزةَ في gone"),
    ("نزعُ أرضيّةِ السجلّ",
     'if (p === "prep" && k.indexOf(LOGP) === 0 && m.logfloor && k < m.logfloor) continue;',
     "if (false) continue;", "ولا يُكتب حرفٌ منه"),
    ("نزعُ قصِّ السجلّ كلِّه",
     "  await pruneLogs(d1, db);", "  // nope", "مقصوصٌ عند ألفَين"),
    ("إسقاطُ قسمٍ من القراءة الكاملة",
     "'},\"obs\":{' + g.obs.join(\",\") +", "'},\"obs\":{' + \"\" +", "سجلاً بسجل"),
    ("إسقاطُ قسمٍ من القراءة الفارقة",
     'if (x.part === "sched") data.sched.push(v); else data[x.part][x.rk] = v;',
     'if (x.part === "sched") data.sched.push(v);', "الفارقةُ تحمل المستجدَّ"),
    ("نزعُ حارسِ تحويل النمط",
     'if (!adm) return denyAdmin("تحويلُ نمطِ التخزين");',
     'if (false) return denyAdmin("تحويلُ نمطِ التخزين");', "لا يُحوَّل النمطُ بمفتاح الانضمام"),
    ("نزعُ حارسِ الحذف الجماعي",
     "&& !admin) {\n      return { deny:", "&& false) {\n      return { deny:", "ستّين حصةً يُردُّ"),
    ("نزعُ دمجِ الحقول في الحصة",
     "      const merged = Object.assign({}, old || {}, x);",
     "      const merged = Object.assign({}, x);", "يُدمج الحقلُ"),
    ("جعلُ الفارقةِ تُخدَم عميلاً قديماً",
     'url.searchParams.get("v") === "2" && since > 0', "since > 0", "فارقةٌ أبداً"),
    ("نزعُ مصادقةِ القراءة",
     "if (!authOK(env, url, null)) return deny();   /* ⛔ قبل أي قراءة */",
     "{}", "بمفتاحٍ خاطئٍ تُردّ ٤٠٣"),
    ("نزعُ تمييزِ النسخة الثانية في الردّ",
     '          if (body.v === 2) {\n            return json({ ok: true, store: s.kind, mode: "rows", seq: w.seq,',
     '          if (false) {\n            return json({ ok: true, store: s.kind, mode: "rows", seq: w.seq,',
     "لا تُعيد القاعدة"),
    ("نزعُ حارسِ الصفوف المتخلّفة",
     'if ((m.blobw || 0) !== (m.swept === undefined ? -1 : m.swept)) {',
     "if (false) {", "صفوفٍ متخلّفة"),
    ("نزعُ عدّادِ كتاباتِ الكتلة",
     '"INSERT INTO meta (db, blobw) VALUES (?, 1) ON CONFLICT(db) DO UPDATE SET blobw = meta.blobw + 1")',
     '"INSERT INTO meta (db, blobw) VALUES (?, 0) ON CONFLICT(db) DO UPDATE SET blobw = meta.blobw")',
     "صفوفٍ متخلّفة"),
    ("نزعُ تسجيلِ المسحةِ الختامية",
     "    await d1.prepare(\"UPDATE meta SET swept = blobw WHERE db = ?\").bind(db).run();",
     "    void 0;", "ويُحوَّل بمفتاح الإدارة"),
    ("جعلُ الترقيمِ ثابتاً لا يُزاد",
     'ON CONFLICT(db) DO UPDATE SET seq = meta.seq + 1")\n    .bind(db));',
     'ON CONFLICT(db) DO UPDATE SET seq = meta.seq")\n    .bind(db));', "المستجدَّ وحدَه"),
]


def fixture():
    """قاعدةٌ على قدِّ الحقيقية: ٤٠٠ حصةٍ وتحضيراتٍ وسلّةٍ وسجلٍّ ألفَين.

    ⚠️ وبِذرةٌ ثابتةٌ: حارسٌ يختلف جوابُه من تشغيلٍ لآخر لا يُحتجُّ به.
    """
    rnd = random.Random(1448)
    body = "نصٌّ تجريبيٌّ للقياس " * 12
    sched, prep = [], {}
    days = ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس"]
    subs = ["رياضيات", "علوم", "عربي", "إسلامية", "E"]
    for i in range(400):
        lid = "L%04d" % i
        gk = "|".join(["وطني", "الياسمين", "الابتدائية- الياسمين",
                       "الحصة %d" % (1 + i % 7), "الأسبوع العاشر",
                       days[i % 5], subs[i % 5]])
        sched.append({"id": lid, "gk": gk, "teacher": "أ. معلّمُ %d" % i,
                      "stage": "ابتدائي", "spec": subs[i % 5], "day": days[i % 5],
                      "week": "الأسبوع العاشر", "note": body[:60]})
        if i % 3 == 0:
            prep[lid] = {"goal": body, "steps": [body[:80]] * 4, "tools": body[:50]}
    for i in range(136):
        prep["~trash~%08x" % rnd.getrandbits(32)] = {"L": {"id": "Z%d" % i}, "by": "أ. الحاذف"}
    for i in range(2000):
        prep["~log~%s-%04d-x" % (format(1700000000 + i, "x"), i)] = \
            {"a": "تسجيلُ حصة", "d": body[:40], "by": "أ. فاعل"}
    for i in range(5):
        prep["~note~L%04d|أ. المدير" % i] = {"t": body[:70], "at": 1}
    return {"sched": sched, "prep": prep, "obs": {}, "peer": {}, "rot": {}}


def main():
    if not os.path.exists(WORKER):
        print("  ⛔ لا خادمَ في مجلَّده الخاصّ:\n      %s" % WORKER)
        return 1
    d = PRB.probe("rows")
    os.makedirs(d, exist_ok=True)
    shutil.copy(WORKER, os.path.join(d, "worker.js"))
    io.open(os.path.join(d, "d1mock.mjs"), "w", encoding="utf-8").write(D1MOCK)
    io.open(os.path.join(d, "t.mjs"), "w", encoding="utf-8").write(TEST)
    io.open(os.path.join(d, "fixture.json"), "w", encoding="utf-8").write(
        json.dumps({"data": fixture()}, ensure_ascii=False))
    io.open(os.path.join(d, "package.json"), "w", encoding="utf-8").write('{"type":"module"}')

    env = dict(os.environ)
    env["NODE_NO_WARNINGS"] = "1"
    r = subprocess.run([sys.executable and "node", "t.mjs"], cwd=d, env=env,
                       capture_output=True, text=True)
    for ln in r.stdout.rstrip().splitlines():
        print(ln)
    if r.returncode != 0:
        if r.stderr.strip():
            print("  " + r.stderr.strip().splitlines()[0][:160])
        print("\n  ⛔ لا يُنشر")
        return 1

    # ── وتجربةُ الحارس على عيوبٍ نعلمها ──
    print("\n  ── الكاشفُ على عيوبٍ مزروعة ──")
    good = io.open(os.path.join(d, "worker.js"), encoding="utf-8").read()
    bad = 0
    for name, old, new, expect in FAULTS:
        if old not in good:
            print("  ⛔ %-38s — المرساةُ غيرُ موجودةٍ في الشفرة" % name)
            bad += 1
            continue
        io.open(os.path.join(d, "worker.js"), "w", encoding="utf-8").write(good.replace(old, new, 1))
        q = subprocess.run(["node", "t.mjs"], cwd=d, env=env, capture_output=True, text=True)
        fell = [ln.strip() for ln in q.stdout.splitlines() if ln.strip().startswith("⛔")]
        if q.returncode != 0 and any(expect in ln for ln in fell):
            print("  ✓ %-38s → أسقط شاهدَه" % name)
        elif q.returncode != 0:
            print("  ⚠ %-38s → سقط بشاهدٍ آخر: %s" % (name, (fell + [""])[0][:52]))
            bad += 1
        else:
            print("  ⛔ %-38s → **مرَّ بلا كشف**" % name)
            bad += 1
    io.open(os.path.join(d, "worker.js"), "w", encoding="utf-8").write(good)

    print("\n  %s" % ("✓ التخزينُ صفّاً صفّاً يفي بعقد المنصة — و%d عيباً مزروعاً كُشفت"
                      % len(FAULTS) if not bad else "⛔ الكاشفُ لا يُعتمد"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
