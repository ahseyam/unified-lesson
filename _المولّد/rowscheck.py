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
  let logscans = 0, logrows = 0;
  const run1 = (sql, args) => {
    stmts++;
    /* ⛔ **ثمنُ القراءة يُقاس**: D1 يحسب كلَّ صفٍّ **يُمسح** لا كلَّ صفٍّ يُرجَع.
       و`COUNT(*)` على `rk LIKE '~log~%'` لا فهرسَ له فيمسح القاعدةَ كلَّها.
       فيُعَدُّ هنا عددُ هذه المسحات وكم صفّاً كانت ستقرأ في كل مرة. */
    if (/COUNT\(\*\)[\s\S]*LIKE '~log~%'/.test(sql)) {
      logscans++;
      try { logrows += Number(db.prepare("SELECT COUNT(*) AS n FROM rec").get().n) || 0; } catch (e) {}
    }
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
    _cost: () => ({ writes, reads, stmts, logscans, logrows }),
    _reset: () => { writes = 0; reads = 0; stmts = 0; logscans = 0; logrows = 0; },
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
/* ⚠️ `arch=1`: المقابلةُ بالكتلة تطلب الأرشيفَ معها، وإلّا حُسب إقصاءُ السجلِّ
   والسلّةِ عن القراءة العامّة **نقصاً** وهو تصميمٌ مقصود. */
const rowsTxt = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&arch=1&key=" + KEY));
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
const after = await jj(await G(env, "kind=platform&id=ikm_db&arch=1&key=" + KEY));
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

/* ═══ ⑦ب ختمُ الوقت: الجهازُ القديمُ لا يُحيي محذوفاً ولا يغلب تعديلاً ═══
   ⛔ شكوى أ. إيهاب عباس (٧ أكتوبر ٢٠٢٦): «لا تُحذف نهائياً ولا يحدث التعديل،
      ويبقى القديم والحديث». وأُثبتت بالقياس: ١٦٩ خليةً حُذفت فعاد منها ١١٣.
   ⚠️ والسببُ أن الجهازَ يدفع نسختَه **كاملةً** فيكتب القديمُ فوق الجديد. */
r = await jj(await P(env, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: "NEW1", gk: "زومبي|خلية", teacher: "أ. العائدُ من القبر", mt: 1000 }] } }));
const z1 = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
A("ولا يُحيي المحذوفَ جهازٌ قديمٌ يدفع نسختَه",
  !(z1.data.sched || []).some(x => x.id === "NEW1"),
  (z1.data.sched || []).filter(x => x.id === "NEW1").length + " عائداً");
const zq = (await jj(await G(env, "kind=platform&id=ikm_db&key=" + KEY))).seq;
r = await jj(await P(env, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: taken.id, note: "الأحدث", mt: Date.now() + 5000 }] } }));
r = await jj(await P(env, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: taken.id, note: "الأقدم", mt: 1000 }] } }));
const z2 = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
const zt = (z2.data.sched || []).find(x => x.id === taken.id);
A("والأقدمُ لا يغلب الأحدث", zt && zt.note === "الأحدث", zt ? zt.note : "مفقود");
/* ⚠️ والسجلّاتُ التي لا ختمَ لها — ما كُتب قبل اليوم — تبقى تُدمج كما كانت،
      وإلّا جمَّدنا قاعدةً كاملةً بلا ختمٍ عن كلِّ تعديل. */
const unst = (blob.sched || [])[3];
r = await jj(await P(env, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: unst.id, note: "بلا ختم" }] } }));
const z3 = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
const zu = (z3.data.sched || []).find(x => x.id === unst.id);
A("وسجلٌّ بلا ختمٍ يبقى يُدمج كما كان", zu && zu.note === "بلا ختم", zu ? zu.note : "مفقود");
const z4 = await jj(await G(env, "kind=platform&id=ikm_db&v=2&since=" + zq + "&key=" + KEY));
A("ولا يُذكر المردودُ في الفارقة", !((z4.sched || []).some(x => x.id === "NEW1")),
  "فارقةٌ فيها " + ((z4.sched || []).length) + " حصة");

/* ═══ ⑦ج ⛔ **والقبرُ لا يُفتح بختمٍ أحدثَ من دفنه** ═══
   شكوى المستشار ٨ أكتوبر ٢٠٢٦: «أيُّ حصصٍ يحذفها الوكيلُ التعليميُّ تعود
   بالجدول». وقِيس على القاعدتين الحيَّتين: **٢٧٤ حذفاً عاد منه ١٠١**.
   ⚠️ والشاهدُ أعلاه كان يدفع ختماً **أقدمَ** (١٠٠٠) فيمرّ — وهو ليس الحالَ
      الواقعة. فالحالُ ختمٌ **بالآن**: `deltaOf` في الصفحة يختم كلَّ ما خالف
      أساسَه بوقت الدفع، وما حذفه الخادمُ مخالفٌ لأساسه؛ و`touchL` يختم
      حصةَ معلمٍ يُعدّلها اللحظةَ التي حذفها وكيلُه فيها. */
r = await jj(await P(env, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: "NEW1", gk: "زومبي|خلية", teacher: "أ. العائدُ بختمٍ أحدث",
                    mt: Date.now() + 9000 }] } }));
const y1 = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
A("ولا يُحيي الحصةَ المحذوفةَ ختمٌ أحدثُ من دفنها",
  !(y1.data.sched || []).some(x => x.id === "NEW1"),
  (y1.data.sched || []).filter(x => x.id === "NEW1").length + " عائداً");
A("ويُخبَر الجهازُ بقبرها ليَدفن نسختَه",
  (r.buried || []).some(b => b.part === "sched" && b.rk === "NEW1"),
  JSON.stringify(r.buried || []));
/* وتحضيرُها كذلك — وهو **الأكثرُ وقوعاً**: ٨١ من ١٠١ عادت من باب التحضير */
r = await jj(await P(env, { kind: "platform", id: "ikm_db", v: 2,
  data: { prep: { NEW1: { i_topic: "درسٌ عاد من القبر", mt: Date.now() + 9000 } } } }));
const y2 = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
A("ولا يعود تحضيرُ المحذوفةِ بختمٍ أحدث", !("NEW1" in (y2.data.prep || {})),
  JSON.stringify((y2.data.prep || {}).NEW1 || "").slice(0, 60));
A("ويُخبَر بقبر التحضير",
  (r.buried || []).some(b => b.part === "prep" && b.rk === "NEW1"),
  JSON.stringify(r.buried || []));
/* ⛔ **والقبرُ لا يحجز خانةً على حصةٍ جديدة**: جهازٌ قديمٌ يدفع المحذوفةَ،
   ومعلمٌ آخرُ يسجّل في خانتها في الدفعة نفسِها — فلو مرَّ القبرُ على حارس
   التصادم لحجز الخانةَ على التسجيل الصحيح. */
r = await jj(await P(env, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: "NEW1", gk: "زومبي|خلية", teacher: "أ. العائد", mt: Date.now() + 9000 },
                  { id: "HEIR1", gk: "زومبي|خلية", teacher: "أ. الوارثُ للخانة",
                    mt: Date.now() }] } }));
const y4 = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
A("ولا يحجز القبرُ خانتَه على تسجيلٍ جديد",
  (y4.data.sched || []).some(x => x.id === "HEIR1") && (r.conflicts || []).length === 0,
  JSON.stringify(r.conflicts || []) + " · وارثٌ " +
  (y4.data.sched || []).filter(x => x.id === "HEIR1").length);
A("ولا يعود العائدُ معه", !(y4.data.sched || []).some(x => x.id === "NEW1"));
await P(env, { kind: "platform", id: "ikm_db", v: 2, data: { __deleted: ["HEIR1"] } });
/* ⚠️ **والاستردادُ وحدَه يُحيي** (`raw`): قرارٌ صريحٌ بمفتاح الإدارة لا دفعةُ
      جهازٍ قديم. ولولا إعفاؤه لعاد المخزنُ ناقصاً بعد كلِّ استردادٍ — وقد
      قِيس: ٣٦ حصةً من ٤٠١. وشاهدُه في ⑦هـ: «ويعود ما حُذف بعد النسخة». */

/* ═══ ⑦ج ⛔ **لا تُحجز خانةٌ بلا صاحب** — في الخادم لا في الصفحة وحدَها ═══
   قِيس ٧ أكتوبر ٢٠٢٦: ١٤٨ خليةً بلا اسمٍ البتّة في المخزن الحيّ. والحارسُ كان
   في الصفحة، فطلبٌ مباشرٌ أو جهازٌ بشفرةٍ قديمةٍ يُنشئ صفّاً يحجز الخلية. */
r = await jj(await P(env, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: "NONAME", gk: "بلا|صاحب", teacher: "" }] } }));
const nn = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
A("وحصةٌ بلا اسمٍ تُردُّ ولا تُحجز", !(nn.data.sched || []).some(x => x.id === "NONAME"),
  JSON.stringify(r.refused || []).slice(0, 80));
A("ويُسمّى سببُ الردّ", ((r.refused || [])[0] || {}).id === "NONAME", (r.refused || []).length + " مردوداً");
r = await jj(await P(env, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: "ZERO1", gk: "صفر|خانة", teacher: "٠" }] } }));
const z0 = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
A("و«٠» ليست اسماً", !(z0.data.sched || []).some(x => x.id === "ZERO1"));
/* ⚠️ والتعديلُ على صفٍّ قائمٍ يمرُّ — وإلّا رُدَّ تصحيحُ حصةٍ قديمةٍ ناقصة */
r = await jj(await P(env, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: taken.id, note: "تعديلٌ على قائم" }] } }));
const z9 = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
A("وتعديلُ صفٍّ قائمٍ يمرُّ ولو نقص", (r.refused || []).length === 0 &&
  ((z9.data.sched || []).find(x => x.id === taken.id) || {}).note === "تعديلٌ على قائم");

/* ═══ ⑦د ⛔ **الأرشيفُ لا يُحمَّل على كل جهاز** ═══
   قِيس على الحيّ: ٢٧٠٠ صفٍّ في كل فتحةِ صفحة، منها ٢٠٠٠ سجلٌّ و٤٠٣ سلّة. */
const arcTr = {}, arcLg = {};
for (let i = 0; i < 40; i++) arcTr["~trash~T" + i] = { L: { id: "T" + i }, at: "x" };
for (let i = 0; i < 40; i++) arcLg["~log~" + (9100000 + i).toString(36) + "|a"] = { a: i };
await P(env, { kind: "platform", id: "ikm_db", v: 2, data: { prep: Object.assign({}, arcTr, arcLg) } });
const plain = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
const withA = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&arch=1&key=" + KEY));
const nTrP = Object.keys(plain.data.prep || {}).filter(k => k.indexOf("~trash~") === 0).length;
const nTrA = Object.keys(withA.data.prep || {}).filter(k => k.indexOf("~trash~") === 0).length;
const nLgP = Object.keys(plain.data.prep || {}).filter(k => k.indexOf("~log~") === 0).length;
const nLgA = Object.keys(withA.data.prep || {}).filter(k => k.indexOf("~log~") === 0).length;
A("والسلّةُ لا تُحمَّل في القراءة العامّة", nTrP === 0, nTrP + " مقابل " + nTrA + " عند الطلب");
A("ويبقى منها كلُّها عند طلب الأرشيف", nTrA >= 40, nTrA);
/* ⛔ **والبلاغاتُ أرشيفٌ ثالثٌ**: تُجمع من كل جهازٍ ولا تُبثُّ على أحد */
const nEr = {};
for (let i = 0; i < 7; i++) nEr["~err~E" + i] = { k: "خطأ", m: "س" + i, t: new Date().toISOString() };
await P(env, { kind: "platform", id: "ikm_db", v: 2, data: { prep: nEr } });
const pl2 = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
const ar2 = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&arch=1&key=" + KEY));
A("والبلاغاتُ لا تُحمَّل في القراءة العامّة",
  Object.keys(pl2.data.prep || {}).filter(k => k.indexOf("~err~") === 0).length === 0);
A("وتصل المستشارَ عند طلب الأرشيف",
  Object.keys(ar2.data.prep || {}).filter(k => k.indexOf("~err~") === 0).length === 7,
  Object.keys(ar2.data.prep || {}).filter(k => k.indexOf("~err~") === 0).length + " بلاغاً");
A("ومن السجلِّ آخرُه وحدَه", nLgP <= 300 && nLgP > 0, nLgP + " مقابل " + nLgA + " عند الطلب");
A("ويبقى السجلُّ كلُّه عند الطلب", nLgA > nLgP, nLgA);
/* ⚠️ والتحضيراتُ الحقيقيةُ لا تُمَسُّ بهذا الإقصاء */
A("ولا يُنقص التحضيرُ الحقيقيُّ شيئاً",
  Object.keys(plain.data.prep || {}).filter(k => k.indexOf("~") !== 0).length ===
  Object.keys(withA.data.prep || {}).filter(k => k.indexOf("~") !== 0).length,
  Object.keys(plain.data.prep || {}).filter(k => k.indexOf("~") !== 0).length + " تحضيراً");
/* ⚠️ والسلّةُ لا تُبثُّ في الفارقة أيضاً */
const sqA = (await jj(await G(env, "kind=platform&id=ikm_db&key=" + KEY))).seq;
await P(env, { kind: "platform", id: "ikm_db", v: 2, data: { prep: { "~trash~TX": { L: { id: "TX" }, at: "x" } } } });
const incA = await jj(await G(env, "kind=platform&id=ikm_db&v=2&since=" + sqA + "&key=" + KEY));
A("ولا تُبثُّ السلّةُ في الفارقة", !("~trash~TX" in ((incA.data || {}).prep || {})),
  Object.keys((incA.data || {}).prep || {}).length + " مدخلاً في الفارقة");

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

/* ═══ ⑫ قصُّ السجلّ وأرضيّتُه ═══
   ⚠️ **والأعدادُ تُؤخذ من الخادم نفسِه** لا تُكتب هنا: رُفع السقفُ من ألفَين
      إلى عشرين ألفاً (أثرُ عشرةِ أيامٍ بدل سبعَ عشرةَ ساعة) فسقطت أربعةُ
      شواهدَ مكتوبةٍ بالرقم — والعيبُ في الشاهد لا في المقيس. */
const WSRC = fs.readFileSync("worker.js", "utf8");
const KEEP = Number((WSRC.match(/const LOG_KEEP = (\d+)/) || [])[1] || 0);
const SLACK = Number((WSRC.match(/const LOG_SLACK = (\d+)/) || [])[1] || 0);
const HEAD = Number((WSRC.match(/const LOG_HEAD = (\d+)/) || [])[1] || 0);
A("وثوابتُ السجلِّ مقروءةٌ من الخادم", KEEP > 0 && SLACK > 0 && HEAD > 0,
  "سقف " + KEEP + " · هامش " + SLACK + " · رأس " + HEAD);
const already = Object.keys(blob.prep || {}).filter(k => k.indexOf("~log~") === 0).length;
/* ⚠️ ويُبذَر **تحت بوّابة القصِّ بقليل**: فالحالُ المقصودةُ «سجلٌّ قاربَ حدَّه»
   ثم تعبره دفعةٌ فيُقَصّ. ولو بُذر فوقها قُصَّ قبل أن يُقاس شيء. */
const push = Math.max(300, KEEP + SLACK - 100 - already);
/* ⚠️ **وتُبذَر بـSQL لا بالدفع**: المقصودُ «سجلٌّ فوق حدِّه» لا مسارُ الكتابة
   (وهو مقيسٌ في شواهدَ أخرى). ودفعُ ثمانيةِ آلافٍ عبر المسار أبطأ الكاشفَ
   خمسةَ أضعافٍ بلا شاهدٍ يزيد — والعدّادُ يُضبط كما تضبطه المسحةُ والترقية. */
const insLogs = env.D1._db.prepare(
  "INSERT OR REPLACE INTO rec (db,part,rk,v,gk,del,seq,mt) VALUES ('platform:ikm_db','prep',?,?,NULL,0,1,0)");
for (let i = 0; i < push; i++)
  insLogs.run("~log~" + (2000000 + i).toString(36) + "|x" + i, JSON.stringify({ a: i }));
env.D1._db.prepare("UPDATE meta SET logn = ? WHERE db = 'platform:ikm_db'").run(push + already);
const st1 = await jj(await G(env, "kind=platform&id=ikm_db&stat=1&key=" + KEY));
/* ⚠️ والعقدُ صار: لا يتجاوز السجلُّ حدَّه **وهامشَ قصِّه** — والهامشُ ثمنُ
   ألّا تُمسح القاعدةُ في كل حفظة. ثم يُقَصُّ إلى الحدِّ عند تجاوزه. */
A("والسجلُّ لا يتجاوز حدَّه وهامشَه", (st1.stat||{}).logs <= KEEP + SLACK,
  (st1.stat||{}).logs + " من " + (KEEP + SLACK));
/* ⛔ **وحدُّ القراءةِ اليوميُّ نفد في ٧ أكتوبر ٢٠٢٦ فسقطت المنصةُ للجميع**:
   كان القصُّ يمسح القاعدةَ كلَّها في **كل حفظة** بحثاً عن عدد السجلّ. فمئةُ
   معلّمٍ يحفظون = ملايينُ الصفوف المقروءة في ساعات. فصار العدُّ محفوظاً. */
env.D1._reset();
for (let i = 0; i < 12; i++) {
  await P(env, { kind: "platform", id: "ikm_db", v: 2,
    data: { sched: [{ id: (blob.sched || [])[i].id, note: "حفظةٌ " + i }] } });
}
const c12 = env.D1._cost();
A("واثنتا عشرةَ حفظةً لا تمسح السجلَّ مرةً",
  c12.logscans === 0, c12.logscans + " مسحةً · ثمنُها كان " + c12.logrows + " صفّاً");
/* وعند تجاوز الحدِّ بهامشه تُمسح مرةً واحدةً ويُقَصُّ السجلّ */
env.D1._reset();
const logs2 = {};
for (let i = 0; i < SLACK + 100; i++) logs2["~log~" + (2100000 + i).toString(36) + "|y" + i] = { a: i };
await P(env, { kind: "platform", id: "ikm_db", v: 2, data: { prep: logs2 } });
const c13 = env.D1._cost();
A("وتُمسح مرةً واحدةً عند تجاوز الحدّ", c13.logscans === 1, c13.logscans + " مسحةً");
const st1b = await jj(await G(env, "kind=platform&id=ikm_db&stat=1&key=" + KEY));
A("ويبقى السجلُّ عند حدّه بعدها", (st1b.stat||{}).logs === KEEP, (st1b.stat||{}).logs + " مدخلاً");
A("وتُسجَّل أرضيّةٌ للقصّ", !!(st1b.stat||{}).logfloor, (st1b.stat||{}).logfloor);
/* ⛔ **والقاعدةُ الحيّةُ هاجرت قبل أن يوجد العدّاد**، فلو بقي صفراً لما قُصَّ
   سجلُّها حتى يبلغ ألفَين وثلاثَ مئةٍ فوق ألفَيها. فيُهيَّأ بعدٍّ حقيقيٍّ
   مرةً واحدةً عند الترقية — وهو ما يجري على القاعدتين الحيّتين بعد النشر. */
const eLg = mkEnv(null);
await eLg.D1.exec("CREATE TABLE IF NOT EXISTS rec (db TEXT NOT NULL, part TEXT NOT NULL, rk TEXT NOT NULL, v TEXT, gk TEXT, del INTEGER NOT NULL DEFAULT 0, seq INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (db, part, rk))");
await eLg.D1.exec("CREATE TABLE IF NOT EXISTS meta (db TEXT PRIMARY KEY, seq INTEGER NOT NULL DEFAULT 0, mode TEXT NOT NULL DEFAULT 'blob', logfloor TEXT NOT NULL DEFAULT '', mig TEXT NOT NULL DEFAULT '', blobw INTEGER NOT NULL DEFAULT 0, swept INTEGER NOT NULL DEFAULT -1)");
eLg.D1._db.exec("INSERT INTO meta (db, seq, mode) VALUES ('platform:ikm_db', 5, 'rows')");
const insLg = eLg.D1._db.prepare("INSERT INTO rec (db,part,rk,v,seq) VALUES ('platform:ikm_db','prep',?,?,1)");
for (let i = 0; i < KEEP + 500; i++) insLg.run("~log~" + (3000000 + i).toString(36) + "|z" + i, '{"a":1}');
await P(eLg, { kind: "platform", id: "ikm_db", v: 2, data: { prep: { "~log~zzzzz|1": { a: 1 } } } });
const sLg = await jj(await G(eLg, "kind=platform&id=ikm_db&stat=1&key=" + KEY));
A("وقاعدةٌ هاجرت قبل العدّادِ تُقَصُّ من أول حفظة", (sLg.stat||{}).logs === KEEP,
  (sLg.stat||{}).logs + " مدخلاً");
/* ⚠️ **وقاعدةٌ تُهاجَر اليوم** لا تمرُّ بالترقية: صفوفُها تدخل بالهجرة لا
   بالحفظ، فعدّادُها يُضبط عند **ختام المسحة** بعدٍّ حقيقيٍّ واحد. ولولاه
   لنما سجلُّها ضعفَ حدِّه قبل أن يُقَصَّ أولَ مرة. */
const eSw = mkEnv(null);
const bSw = { sched: [{ id: "S1", gk: "a|b", teacher: "أ. واحد" }], prep: {}, obs: {}, peer: {}, rot: {} };
for (let i = 0; i < KEEP + 400; i++) bSw.prep["~log~" + (4000000 + i).toString(36) + "|w" + i] = { a: i };
await seedBlob(eSw, JSON.stringify(bSw));
for (;;) { const q = await jj(await P(eSw, { kind: "platform", id: "ikm_db", __migrate: true, limit: 9000 })); if (q.done || !q.ok) break; }
/* ⚠️ والمسحةُ مُصفَّحةٌ كالهجرة: قاعدةٌ فيها عشرون ألفَ مدخلٍ تحتاج أشواطاً،
   فشوطٌ واحدٌ لا يبلغ آخرَها فلا تُسجَّل تامّةً ولا يُضبط عدّادُها. */
for (;;) { const q = await jj(await P(eSw, { kind: "platform", id: "ikm_db", __migrate: true, limit: 9000, sweep: true })); if (q.done || !q.ok) break; }
await jj(await P(eSw, { kind: "platform", id: "ikm_db", __mode: "rows", admin: ADM }));
/* حفظةٌ واحدةٌ بمدخلِ سجلٍّ واحد — ولا دفعةَ عميلٍ كاملةٍ تُصحّح العدّاد */
await P(eSw, { kind: "platform", id: "ikm_db", v: 2, data: { prep: { "~log~zzzzzz|1": { a: 1 } } } });
const sSw = await jj(await G(eSw, "kind=platform&id=ikm_db&stat=1&key=" + KEY));
const mSw = eSw.D1._db.prepare("SELECT logn, seq, swept, blobw FROM meta WHERE db='platform:ikm_db'").get();
A("وقاعدةٌ هاجرت بسجلٍّ فوق الحدِّ تُقَصُّ من أول حفظة", (sSw.stat||{}).logs === KEEP,
  (sSw.stat||{}).logs + " مدخلاً · meta=" + JSON.stringify(mSw));
/* ═══ ⑫ج ⛔ **المخططُ يُتحقَّق ولا يُفترض** ═══
   «no such column: logn» أسقطت المنصةَ بعد ترقية الحساب (٧ أكتوبر ٢٠٢٦):
   كانت الأعمدةُ المستجدّةُ تُضاف بـ`try{ALTER}catch{}` **ثم يُعلَّم المخططُ
   تامّاً على كل حال**. فحين أفشل حدُّ القراءةِ اليوميُّ ذلك `ALTER`، بقيت
   النسخةُ تردُّ كلَّ طلبٍ بعمودٍ لا وجودَ له حتى تموت وتُحيا غيرُها. */
const eHl = mkEnv(null);
await eHl.D1.exec("CREATE TABLE rec (db TEXT NOT NULL, part TEXT NOT NULL, rk TEXT NOT NULL, v TEXT, gk TEXT, del INTEGER NOT NULL DEFAULT 0, seq INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (db, part, rk))");
await eHl.D1.exec("CREATE TABLE meta (db TEXT PRIMARY KEY, seq INTEGER NOT NULL DEFAULT 0, mode TEXT NOT NULL DEFAULT 'blob', logfloor TEXT NOT NULL DEFAULT '', mig TEXT NOT NULL DEFAULT '')");
const execOk = eHl.D1.exec;
eHl.D1.exec = async (sql) => { if (/ALTER TABLE/i.test(sql)) throw new Error("limit"); return execOk(sql); };
const h1 = await jj(await G(eHl, "kind=platform&id=ikm_db&stat=1&key=" + KEY));
A("وعمودٌ لم يُضَفْ يُردُّ برسالةٍ مفهومة",
  h1.ok === false && /ترقي/.test(h1.error || ""), String(h1.error || "").slice(0, 60));
eHl.D1.exec = execOk;
const h2 = await jj(await G(eHl, "kind=platform&id=ikm_db&stat=1&key=" + KEY));
A("ثم يشفى الطلبُ التاليُ من نفسه بلا نشرٍ جديد", h2.ok === true, h2.error || "تمّ");
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
const st2 = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&arch=1&key=" + KEY));
A("ولا يدخل القاعدةَ منه شيء",
  !Object.keys(st2.data.prep || {}).some(k => k.indexOf("~log~0000") === 0));
/* ⛔ **والسلّةُ تُنظَّف في الخادم**: كان الجهازُ يمحو ما مضى عليه ثلاثون يوماً،
   ولمّا صارت لا تصل الجهازَ إلا بطلبٍ لم يبقَ من ينفّذ وعدَ «ثلاثين يوماً». */
const oldAt = new Date(Date.now() - 40 * 86400000).toISOString();
const newAt = new Date().toISOString();
const insTr = env.D1._db.prepare(
  "INSERT OR REPLACE INTO rec (db,part,rk,v,gk,del,seq,mt) VALUES ('platform:ikm_db','prep',?,?,NULL,0,1,0)");
for (let i = 0; i < 12; i++)
  insTr.run("~trash~OLD" + i, JSON.stringify({ L: { id: "OLD" + i }, at: oldAt }));
for (let i = 0; i < 5; i++)
  insTr.run("~trash~NEW" + i, JSON.stringify({ L: { id: "NEW" + i }, at: newAt }));
env.D1._db.prepare("UPDATE meta SET logn = ? WHERE db = 'platform:ikm_db'").run(KEEP + SLACK + 10);
await P(env, { kind: "platform", id: "ikm_db", v: 2, data: { rot: { tr: "1" } } });
const trA = await jj(await G(env, "kind=platform&id=ikm_db&from=rows&arch=1&key=" + KEY));
const trKeys = Object.keys(trA.data.prep || {});
A("ويُمحى من السلّة ما جاوز ثلاثين يوماً",
  !trKeys.some(k => k.indexOf("~trash~OLD") === 0),
  trKeys.filter(k => k.indexOf("~trash~OLD") === 0).length + " قديماً باقياً");
A("ويبقى حديثُها", trKeys.filter(k => k.indexOf("~trash~NEW") === 0).length === 5,
  trKeys.filter(k => k.indexOf("~trash~NEW") === 0).length + " من ٥");

A("ويبقى السجلُّ الحديثُ كما هو",
  Object.keys(st2.data.prep || {}).filter(k => k.indexOf("~log~") === 0).length === KEEP,
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

/* ═══ ⑯ ⛔ **المسحةُ مطابقةٌ تامّةٌ لا إضافة** ═══
   كشفته المقابلةُ على القاعدة الحيّة قبل التحويل: خمسُ حصصٍ حذفها المعلمون
   **أثناء** الهجرة بقيت حيّةً في الصفوف وهي في سلّة محذوفات الكتلة — ولو
   حُوِّل النمطُ لعادت، ولحجزت خلاياها على غيرهم. */
const e3 = mkEnv(null);
await seedBlob(e3, blobTxt);
let q3;
for (;;) { q3 = await jj(await P(e3, { kind: "platform", id: "ikm_db", __migrate: true, limit: 9000 })); if (q3.done || !q3.ok) break; }
A("هاجرت الكتلةُ إلى بيئةٍ نظيفة", q3.ok && q3.done, (q3.total || 0) + " صفّاً");
/* معلّمٌ يحذف حصّةً **بعد** أن هاجرت */
const b3 = JSON.parse(blobTxt);
/* ⚠️ وتُختار حصةٌ **لها تحضيرٌ**: ليست كلُّ حصةٍ محضَّرةً، فاختيارُ واحدةٍ
   بلا تحضيرٍ يجعل الشاهدَ يقيس سجلاً واحداً ويظنُّ العطلَ في الشفرة. */
const victim = (b3.sched.find((x) => x && x.id && (b3.prep || {})[x.id]) || b3.sched[3]).id;
b3.sched = b3.sched.filter((x) => x.id !== victim);
delete b3.prep[victim];
await seedBlob(e3, JSON.stringify(b3));
const sw3 = await jj(await P(e3, { kind: "platform", id: "ikm_db", __migrate: true, limit: 9000, sweep: true }));
A("والمسحةُ تُشاهد ما خرج من الكتلة محذوفاً", sw3.ok && sw3.stray === 2,
  "شواهدُ حذفٍ " + sw3.stray + " (المنتظَر ٢: الحصةُ وتحضيرُها)");
const f3 = await jj(await G(e3, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
A("فلا يعود المحذوفُ في الصفوف", !(f3.data.sched || []).some((x) => x.id === victim), victim);
A("ولا يبقى تحضيرُه", !(victim in (f3.data.prep || {})));
A("ويبقى سواه", (f3.data.sched || []).length === b3.sched.length,
  (f3.data.sched || []).length + "/" + b3.sched.length);
r = await jj(await P(e3, { kind: "platform", id: "ikm_db", __mode: "rows", admin: ADM }));
A("ويُقبل التحويلُ بعد مسحةٍ تامّة", r.ok && r.mode === "rows", r.error || r.mode);
/* ⚠️ وقبرُ المسحةِ يُختم كقبرِ الحذف: بلا ختمٍ يبقى صفراً فيُحييه أيُّ جهازٍ
      قديمٍ يدفع نسختَه (صفرٌ ≥ صفر)، فيعود المحذوفُ من بابٍ آخر. */
await P(e3, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: victim, gk: "زومبي|مسحة", teacher: "أ. العائد", mt: 1000 }] } });
const f3z = await jj(await G(e3, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
A("ولا يُعيد محذوفَ المسحةِ جهازٌ قديم",
  !(f3z.data.sched || []).some((x) => x.id === victim), victim);

/* ═══ ⑯ب ⛔ **سجلٌّ متقادمٌ لا يُحسب في السقف** ═══
   مدخلاتُ `~log~` تدور: تُقصُّ من الكتلة فتبقى في الصفوف. وقِيس على القاعدة
   الحيّة ٧ أكتوبر ٢٠٢٦: **٢٠٣٥ من ٢٠٣٧** صفٍّ «خارج الكتلة» كانت سجلّاً —
   فرفض السقفُ مسحةً صحيحةً، ومُنع التحويلُ والخادمُ يسقط على المعلمين. */
const e5 = mkEnv(null);
await seedBlob(e5, blobTxt);
let q5;
for (;;) { q5 = await jj(await P(e5, { kind: "platform", id: "ikm_db", __migrate: true, limit: 9000 })); if (q5.done || !q5.ok) break; }
await jj(await P(e5, { kind: "platform", id: "ikm_db", __migrate: true, limit: 9000, sweep: true }));
/* الكتلةُ تقصُّ سجلَّها (كما يفعل الخادمُ مع كل كتابة)، وتفقد حصةً محذوفة */
const b5 = JSON.parse(blobTxt);
const logs5 = Object.keys(b5.prep).filter((k) => k.indexOf("~log~") === 0).sort();
logs5.slice(0, logs5.length - 60).forEach((k) => { delete b5.prep[k]; });
const gone5 = b5.sched[7].id;
b5.sched = b5.sched.filter((x) => x.id !== gone5);
await seedBlob(e5, JSON.stringify(b5));
const sw5 = await jj(await P(e5, { kind: "platform", id: "ikm_db", __migrate: true, limit: 9000, sweep: true }));
A("ومسحةٌ فيها سجلٌّ متقادمٌ كثيرٌ تمرُّ", sw5.ok && sw5.done && !sw5.why,
  "خارجُ الكتلة " + (sw5.stray || 0) + " · منها بيانات " + (sw5.hard || 0) + " · السقف " + sw5.strayCap);
A("ويُشاهَد السجلُّ المتقادمُ محذوفاً", (sw5.stray || 0) > 1000, sw5.stray);
A("والحصةُ المحذوفةُ معه", (sw5.hard || 0) >= 1, sw5.hard);
r = await jj(await P(e5, { kind: "platform", id: "ikm_db", __mode: "rows", admin: ADM }));
A("ويُقبل التحويلُ بعدها", r.ok && r.mode === "rows", r.error || r.mode);

/* ═══ ⑰ وسقفٌ يمنع كارثة: كتلةٌ نقصت نصفَها لا تُشاهِد القاعدةَ محذوفةً ═══ */
const e4 = mkEnv(null);
await seedBlob(e4, blobTxt);
let q4;
for (;;) { q4 = await jj(await P(e4, { kind: "platform", id: "ikm_db", __migrate: true, limit: 9000 })); if (q4.done || !q4.ok) break; }
const b4 = JSON.parse(blobTxt);
b4.sched = b4.sched.slice(0, 40);                 /* ٣٥٧ حصةً تختفي فجأة */
await seedBlob(e4, JSON.stringify(b4));           /* ⛔ ولولا الزرعُ لم يُقَس شيء */
const sw4 = await jj(await P(e4, { kind: "platform", id: "ikm_db", __migrate: true, limit: 9000, sweep: true }));
A("وكتلةٌ نقصت فجأةً تُبلِّغ ولا تُشاهِد شيئاً محذوفاً",
  sw4.ok && sw4.stray > sw4.strayCap && !!sw4.why,
  "خارجُ الكتلة " + (sw4.stray || 0) + " · السقف " + sw4.strayCap + " · " + (sw4.why || "بلا سبب"));
const f4 = await jj(await G(e4, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
A("فتبقى الحصصُ كلُّها في الصفوف", (f4.data.sched || []).length === (blob.sched || []).length,
  (f4.data.sched || []).length + "/" + (blob.sched || []).length);
r = await jj(await P(e4, { kind: "platform", id: "ikm_db", __mode: "rows", admin: ADM }));
A("ويُمنع التحويلُ حتى تُراجَع", r.ok === false && /مسحةٌ ختاميةٌ/.test(r.error || ""), r.error);

/* ═══ ⑰ ⛔ **النسخُ الاحتياطية — في بيئةٍ خاصّةٍ بها** ═══
   ⚠️ والاستردادُ يُعيد الحالَ إلى ما كان، فلو جرى في البيئة العامّة أفسد ما
      بعده من شواهد — وقد جرى ذلك فعلاً فسقطت ثلاثةٌ لا ذنبَ لها. */
const eBk = mkEnv(null);
await seedBlob(eBk, blobTxt);
for (;;) { const q = await jj(await P(eBk, { kind: "platform", id: "ikm_db", __migrate: true, limit: 9000 })); if (q.done || !q.ok) break; }
await jj(await P(eBk, { kind: "platform", id: "ikm_db", __migrate: true, limit: 9000, sweep: true }));
await jj(await P(eBk, { kind: "platform", id: "ikm_db", __mode: "rows", admin: ADM }));
await P(eBk, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: "BK1", gk: "نسخ|خانة", teacher: "أ. نسخة" }] } });
/* ═══ ⑦هـ ⛔ **نسخةٌ احتياطيةٌ يوميةٌ تلقائية** — ولم تكن ثَمَّ نسخةٌ البتّة ═══ */
const bk1 = await jj(await P(eBk, { kind: "platform", id: "ikm_db", __backups: true, admin: ADM }));
A("وتُؤخذ نسخةٌ من تلقائها", (bk1.baks || []).length >= 1,
  JSON.stringify((bk1.baks || []).map(b => b.day)).slice(0, 60));
A("وفيها الأرشيفُ كلُّه", ((bk1.baks || [])[0] || {}).bytes > 1000, ((bk1.baks || [])[0] || {}).bytes);
A("ولا تُعدَّد النسخُ بلا مفتاح إدارة",
  (await jj(await P(eBk, { kind: "platform", id: "ikm_db", __backups: true }))).ok === false);
/* ⚠️ والاستردادُ يُعيد ما كان، ويأخذ نسخةً قبله */
const before = ((await jj(await G(eBk, "kind=platform&id=ikm_db&from=rows&key=" + KEY))).data.sched || []).length;
const day0 = ((bk1.baks || [])[0] || {}).day;
await P(eBk, { kind: "platform", id: "ikm_db", v: 2, data: { __deleted: [(blob.sched || [])[9].id] } });
const rs = await jj(await P(eBk, { kind: "platform", id: "ikm_db", __restore: day0, admin: ADM }));
A("والاستردادُ يُقبل بمفتاح الإدارة", rs.ok === true && rs.restored === day0,
  (rs.error || rs.restored) + " · في النسخة " + rs.sched + " حصة");
const aft = ((await jj(await G(eBk, "kind=platform&id=ikm_db&from=rows&key=" + KEY))).data.sched || []).length;
/* ⚠️ وهذا **شاهدُ إعفاءِ الاسترداد** من حارس القبور (⑦ج): الصفُّ مدفونٌ قبل
      الاسترداد، فلو مُنع الإحياءُ على الاسترداد أيضاً لنقص المخزنُ بعده. */
A("ويعود ما حُذف بعد النسخة — فالاستردادُ يفتح القبر", aft === before, aft + " مقابل " + before);
const bk2 = await jj(await P(eBk, { kind: "platform", id: "ikm_db", __backups: true, admin: ADM }));
A("وتُحفظ نسخةٌ قبل الاسترداد نفسِه",
  (bk2.baks || []).some(b => String(b.day).indexOf("before-restore") >= 0),
  JSON.stringify((bk2.baks || []).map(b => b.day)).slice(0, 90));
A("ولا استردادَ بلا مفتاح إدارة",
  (await jj(await P(eBk, { kind: "platform", id: "ikm_db", __restore: day0 }))).ok === false);
A("ولا استردادَ من تاريخٍ لا نسخةَ له",
  (await jj(await P(eBk, { kind: "platform", id: "ikm_db", __restore: "1999-01-01", admin: ADM }))).ok === false);

/* ═══ ⑰ب ⛔ **النجدة: القاعدةُ تسقط فلا تسقط المنصة** ═══
   قِيس يومَ نفد حدُّ القراءة (٧ أكتوبر ٢٠٢٦): كلُّ طلبٍ مردود، فمن يفتح
   المنصةَ يرى جدولاً خاوياً ويحجز خانةً محجوزة. فصارت تُخدَم آخرُ نسخةٍ
   **من مخزنٍ آخرَ غير القاعدة** للقراءة وحدَها.
   ⚠️ **والنسخةُ لا تسكن داخلَ ما تحميه**: لو بقيت في جدول `store` داخل D1
      لذهبت معها — فهي في KV، ويُقاس ذلك بإسقاط D1 كلِّها. */
const kvBak = new Map();
eBk.DB = {
  get: async (k)=>(kvBak.has(k) ? kvBak.get(k) : null),
  put: async (k, v)=>{ kvBak.set(k, v); },
  list: async ({ prefix })=>({ keys: [...kvBak.keys()].filter(k=>k.indexOf(prefix) === 0)
    .sort().reverse().map(k=>({ name: k })) }),
  delete: async (k)=>{ kvBak.delete(k); },
};
/* نسخةٌ تُؤخذ والقاعدةُ سليمةٌ — وتُكتب في المخزنَين */
await P(eBk, { kind: "platform", id: "ikm_db", __snap: true, admin: ADM });
A("والنسخةُ تُكتب في مخزنٍ غير القاعدة", kvBak.size >= 1, kvBak.size + " مفتاحاً في KV");
/* ثم تسقط القاعدةُ سقوطاً تامّاً */
const d1good = eBk.D1;
const d1dead = { prepare: ()=>{ throw new Error("D1_ERROR: down"); },
                 exec: async ()=>{ throw new Error("D1_ERROR: down"); },
                 batch: async ()=>{ throw new Error("D1_ERROR: down"); } };
eBk.D1 = d1dead;
const dg = await jj(await G(eBk, "kind=platform&id=ikm_db&key=" + KEY));
A("وتُخدَم آخرُ نسخةٍ عند سقوطها", dg.ok === true && dg.degraded === true,
  (dg.error || "") + " · يوم " + (dg.bakday || "—"));
A("وفيها الحصصُ كما كانت", ((dg.data || {}).sched || []).length > 300,
  ((dg.data || {}).sched || []).length + " حصة");
A("ويُسمّى سببُ السقوط", /D1_ERROR/.test(dg.why || ""), (dg.why || "").slice(0, 40));
/* ⛔ ولا تُخدَم نجدةٌ لكتابة: الكتابةُ تفشل ظاهراً فيحتفظ الجهازُ بعمله */
/* ⚠️ ويُرسَل المفتاحُ في المسار أيضاً، وإلّا لم يجد مسارُ النجدة قاعدةً
   يبحث عن نسختها فسقط لسببٍ آخر — فيمرُّ العيبُ المزروعُ بلا كشف. */
const wr = await jj(await worker.fetch(new Request(
  "http://x/?kind=platform&id=ikm_db&key=" + KEY,
  { method: "POST", body: JSON.stringify({ key: KEY, kind: "platform", id: "ikm_db", v: 2,
    data: { sched: [{ id: "DEG1", gk: "نجدة|خانة", teacher: "أ. نجدة" }] } }) }), eBk));
A("ولا تُخدَم نجدةٌ لطلب كتابة", wr.ok === false, JSON.stringify(wr).slice(0, 70));
/* ثم تعود القاعدةُ فتعود الخدمةُ كاملةً بلا علامة نجدة */
eBk.D1 = d1good;
const bk = await jj(await G(eBk, "kind=platform&id=ikm_db&key=" + KEY));
A("وتعود الخدمةُ كاملةً بعودتها", bk.ok === true && !bk.degraded && bk.seq > 0, "seq=" + bk.seq);
/* ⚠️ والتحضيرُ مثلُها: كان ختمُه **وقتَ وصوله** فيغلب القديمُ الواصلُ أخيراً */
const pk = (blob.sched || [])[5].id;
await P(eBk, { kind: "platform", id: "ikm_db", v: 2,
  data: { prep: { [pk]: { t: "تحضيرٌ أحدث", mt: Date.now() + 5000 } } } });
await P(eBk, { kind: "platform", id: "ikm_db", v: 2,
  data: { prep: { [pk]: { t: "تحضيرٌ أقدم", mt: 1000 } } } });
const z5 = await jj(await G(eBk, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
A("وتحضيرٌ أقدمُ لا يغلب أحدثَ منه", ((z5.data.prep || {})[pk] || {}).t === "تحضيرٌ أحدث",
  ((z5.data.prep || {})[pk] || {}).t);
/* ⚠️ وساعةٌ متقدّمةٌ لا تُخلّد سجلاً: الختمُ مسقوفٌ بساعةِ الخادم */
const ck = (blob.sched || [])[6].id;
await P(eBk, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: ck, note: "من ساعةٍ متقدّمةٍ سنة", mt: Date.now() + 31536000000 }] } });
await P(eBk, { kind: "platform", id: "ikm_db", v: 2,
  data: { sched: [{ id: ck, note: "من ساعةٍ سليمة", mt: Date.now() }] } });
const z6 = await jj(await G(eBk, "kind=platform&id=ikm_db&from=rows&key=" + KEY));
A("ولا تُخلّد ساعةٌ متقدّمةٌ سجلَّها",
  ((z6.data.sched || []).find(x => x.id === ck) || {}).note === "من ساعةٍ سليمة",
  ((z6.data.sched || []).find(x => x.id === ck) || {}).note);
/* ⚠️ وساعةُ الخادمِ تُردّ في كل ردّ، وبها يُصحّح الجهازُ المتأخّرُ ختمَه */
const z7 = await jj(await P(eBk, { kind: "platform", id: "ikm_db", v: 2, data: { sched: [] } }));
A("وردُّ الكتابةِ يحمل ساعةَ الخادم", Number(z7.now) > 1.7e12, z7.now);
const z8 = await jj(await G(eBk, "kind=platform&id=ikm_db&key=" + KEY));
A("وردُّ القراءةِ كذلك", Number(z8.now) > 1.7e12, z8.now);


/* ═══ ⑱ ⛔ **الخادمُ يُقدّم الصفحةَ بنفسه** ═══
   قِيس ٨ أكتوبر ٢٠٢٦ أن مضيفَ الاستضافة لا تكتمل معه مصافحةُ TLS من شبكاتٍ
   تُرشِّح بالاسم — فلا تُفتح الصفحةُ أصلاً. فيجلبها الخادمُ من شبكته ويُقدّمها،
   فيصير مضيفٌ واحدٌ للصفحة والبيانات.
   ⚠️ ويُقاس بجلبٍ مزيَّفٍ لا بالشبكة: المقصودُ **المسارُ والترويسةُ وبوّابةُ
      المفتاح**، لا أن جِت هب يعمل. */
const realFetch = globalThis.fetch;
let asked = [];
globalThis.fetch = async (u, o) => {
  const s0 = String(u);
  if (s0.indexOf("ahseyam.github.io") >= 0) {
    asked.push(s0);
    return new Response("<!doctype html><title>صفحةٌ مزيَّفة</title>", { status: 200 });
  }
  return realFetch(u, o);
};
const pg = await worker.fetch(new Request("http://x/m"), env);
A("ويُقدَّم جدولُ البنين على /m", pg.status === 200, pg.status);
A("بترويسة HTML", (pg.headers.get("content-type") || "").indexOf("text/html") === 0,
  pg.headers.get("content-type"));
A("ويُجلب من الاستضافة لا من القرص", asked.length === 1 && asked[0].indexOf("github.io") > 0,
  (asked[0] || "").slice(0, 60));
A("ويحمل جسداً", (await pg.text()).indexOf("صفحةٌ مزيَّفة") >= 0);
asked = [];
const pf = await worker.fetch(new Request("http://x/f"), env);
A("وجدولُ البنات على /f", pf.status === 200 && asked.length === 1 &&
  asked[0].indexOf("%D8%A8%D9%86%D8%A7%D8%AA") > 0, (asked[0] || "").slice(-30));
asked = [];
const vj = await worker.fetch(new Request("http://x/ver.json"), env);
A("وملفُّ الختم يُمرَّر بلا تخبئة", vj.status === 200 &&
  (vj.headers.get("cache-control") || "").indexOf("no-store") >= 0,
  vj.headers.get("cache-control"));
/* ⛔ **ولا تُطلب الصفحةُ بمفتاح**: لو حُرست بالمفتاح لما فُتحت أصلاً — وهو
   الطريقُ المسدودُ عينُه الذي نهرب منه. */
A("ولا يُطلب مفتاحٌ للصفحة", pg.status === 200 && pf.status === 200);
/* ⚠️ وما سوى المسارات المعروفة يبقى على عقده: البيانات بمفتاحها */
A("وسائرُ الطرق تبقى محروسة",
  (await worker.fetch(new Request("http://x/?kind=platform&id=ikm_db&key=خطأ"), env)).status === 403);
globalThis.fetch = realFetch;

/* ⚠️ أرضيّةُ الشواهد: فحصٌ انقطع في منتصفه يُعلن نجاحاً كاذباً */
const FLOOR = 106;
let w = R.filter(x => !x[0]).length;
if (R.length < FLOOR) { console.log("  ⛔ " + R.length + " شاهداً والأرضيّةُ " + FLOOR + " — فحصٌ لم يكتمل"); w++; }
console.log("\n  " + (w ? "⛔ سقط " + w + " من " + R.length : "✓ " + R.length + " شاهداً كلُّها تمرّ"));
process.exit(w ? 1 : 0);
"""

# ⚠️ عيوبٌ تُزرع، ولكلٍّ **شاهدُه بعينه**: لو سقط الحارسُ بشاهدٍ آخر لم يُقبل،
#    فالمقصودُ أن يكشف العيبَ المزروعَ لا أن يفشل لأي سبب.
FAULTS = [
    ("نزعُ شرطِ «ما لم يتغيّر لا يُكتب»",
     '"WHERE (rec.v IS NOT excluded.v OR rec.del <> 0) AND excluded.mt >= rec.mt" +',
     '"WHERE excluded.mt >= rec.mt" +', "دفعةٌ كاملةٌ بلا تغيير"),
    ("نزعُ منعِ ازدواج الخلية",
     "        if (own && own.rk !== x.id) {", "        if (false) {", "خليةٌ محجوزةٌ تُردّ"),
    ("نزعُ منعِ الازدواج داخل الدفعة",
     "        if (mine && mine !== x.id && !raw) {", "        if (false) {", "الدفعة نفسِها"),
    ("جعلُ الحذفِ محواً بلا شاهد",
     '"UPDATE rec SET del = 1, v = NULL, seq = " + SEQ + ", mt = ?" +\n'
     '    " WHERE db = ? AND part = ? AND rk = ? AND del = 0").bind(db, MT, db, part, rk);',
     '"DELETE FROM rec WHERE db = ? AND part = ? AND rk = ?").bind(db, part, rk);',
     "يصل الأجهزةَ في gone"),
    ("إعادةُ عدِّ السجلِّ في كل حفظة",
     "if ((Number(m.logn) || 0) + nlog > LOG_KEEP + LOG_SLACK) {",
     "if (true) {", "واثنتا عشرةَ حفظةً لا تمسح السجلَّ مرةً"),
    ("نزعُ تهيئةِ العدّادِ عند الترقية",
     'await d1.exec("UPDATE meta SET logn = (SELECT COUNT(*) FROM rec r WHERE r.db = meta.db"',
     'if (0) await d1.exec("UPDATE meta SET logn = (SELECT COUNT(*) FROM rec r WHERE r.db = meta.db"',
     "وقاعدةٌ هاجرت قبل العدّادِ تُقَصُّ من أول حفظة"),
    ("نزعُ ضبطِ العدّادِ عند ختام المسحة",
     '"ON CONFLICT(db) DO UPDATE SET logn = excluded.logn").bind(db, (lc && lc.n) || 0).run();',
     '"ON CONFLICT(db) DO UPDATE SET logn = excluded.logn").bind(db, 0).run();',
     "وقاعدةٌ هاجرت بسجلٍّ فوق الحدِّ تُقَصُّ من أول حفظة"),
    ("تعليمُ المخططِ تامّاً ولو نقص عمود",
     '      if (!have.has(c.split(" ")[0]))\n        throw new Error("لم تكتمل ترقيةُ مخزن البيانات — أعد المحاولة بعد لحظة");',
     '      if (false) throw new Error("x");', "ثم يشفى الطلبُ التاليُ من نفسه بلا نشرٍ جديد"),
    ("نزعُ حارسِ «لا خانةَ بلا صاحب»",
     "if (!old && !raw && !realName(x.teacher)) {", "if (false) {",
     "وحصةٌ بلا اسمٍ تُردُّ ولا تُحجز"),
    ("جعلِ الحارسِ يردُّ تعديلَ القائم أيضاً",
     "if (!old && !raw && !realName(x.teacher)) {", "if (!raw && !realName(x.teacher)) {",
     "وتعديلُ صفٍّ قائمٍ يمرُّ ولو نقص"),
    ("نزعُ إقصاءِ السلّة والبلاغات عن القراءة العامّة",
     'if (x.rk.indexOf(TRASHP) === 0 || x.rk.indexOf(ERRP) === 0) continue;',
     "if (false) continue;", "والسلّةُ لا تُحمَّل في القراءة العامّة"),
    ("نزعُ قصرِ السجلِّ على آخرِه",
     'if (x.rk.indexOf(LOGP) === 0 && floor && x.rk < floor) continue;', "if (false) continue;",
     "ومن السجلِّ آخرُه وحدَه"),
    ("نزعُ إقصاءِ السلّة عن الفارقة",
     'if (x.part === "prep" && !arch &&\n        (x.rk.indexOf(TRASHP) === 0 || x.rk.indexOf(ERRP) === 0)) continue;',
     "if (false) continue;", "ولا تُبثُّ السلّةُ في الفارقة"),
    ("نزعُ النسخةِ اليوميةِ التلقائية",
     "try { await bakMaybe(env, s, k, await metaGet(env.D1, k)); } catch (e) {}",
     "/* nope */", "وتُؤخذ نسخةٌ من تلقائها"),
    ("جعلِ الاستردادِ كتابةَ حجزٍ لا استعادة",
     "await rowsWrite(env.D1, k, dat, true, true);",
     "await rowsWrite(env.D1, k, dat, true, false);", "ويعود ما حُذف بعد النسخة"),
    ("نزعُ النسخةِ قبل الاسترداد",
     'await bakWrite(env, s, k, now0, (await bakDay()) + "-before-restore");',
     "/* nope */", "وتُحفظ نسخةٌ قبل الاسترداد نفسِه"),
    ("فتحُ الاستردادِ بلا مفتاح إدارة",
     'if (!adm) return denyAdmin("استردادُ نسخة");', "if (false) return null;",
     "ولا استردادَ بلا مفتاح إدارة"),
    ("نزعُ تنظيفِ السلّة في الخادم",
     "    await pruneTrash(d1, db);", "    /* nope */",
     "ويُمحى من السلّة ما جاوز ثلاثين يوماً"),
    ("جعلِ التنظيفِ يمحو الحديثَ أيضاً",
     "if (at && at < cut) old.push(x.rk);", "old.push(x.rk);", "ويبقى حديثُها"),
    ("نزعُ نجدةِ القراءة عند سقوط القاعدة",
     "      const kv0 = bakStore(env);\n      if (request.method === \"GET\" && kv0) {",
     "      const kv0 = null;\n      if (false) {", "وتُخدَم آخرُ نسخةٍ عند سقوطها"),
    ("جعلِ النجدةِ تخدم الكتابةَ أيضاً",
     'if (request.method === "GET" && kv0) {', "if (kv0) {", "ولا تُخدَم نجدةٌ لطلب كتابة"),
    ("إبقاءِ النسخةِ داخلَ القاعدة وحدَها",
     "  if (kv) { try { await kv.put(key + \":bak:\" + name, txt); } catch (e) {} }",
     "  /* nope */", "والنسخةُ تُكتب في مخزنٍ غير القاعدة"),
    ("حراسةُ الصفحةِ بالمفتاح",
     'if (request.method === "GET" && Object.prototype.hasOwnProperty.call(PATHS, url.pathname)) {',
     "if (false) {", "ويُقدَّم جدولُ البنين على /m"),
    ("تخبئةُ ملفِّ الختم",
     'h.set("cache-control", url.pathname === "/ver.json" ? "no-store" : "max-age=300");',
     'h.set("cache-control", "max-age=300");', "وملفُّ الختم يُمرَّر بلا تخبئة"),
    ("نزعُ سقفِ الختمِ بساعة الخادم",
     "const capMT = (x) => Math.min(Number(x) || 0, MT);",
     "const capMT = (x) => Number(x) || 0;", "ولا تُخلّد ساعةٌ متقدّمةٌ سجلَّها"),
    ("جعلُ ختمِ التحضيرِ وقتَ وصوله",
     '(vo && typeof vo === "object" && vo.mt) ? vo.mt : 0, raw));',
     "MT, raw));", "وتحضيرٌ أقدمُ لا يغلب أحدثَ منه"),
    ("كتمُ ساعةِ الخادمِ عن العميل",
     "mode: \"rows\", seq: w.seq, now: Date.now(),", 'mode: "rows", seq: w.seq,',
     "وردُّ الكتابةِ يحمل ساعةَ الخادم"),
    ("نزعُ رفضِ الأقدم في الكتابة",
     "AND excluded.mt >= rec.mt", "AND 1 = 1", "والأقدمُ لا يغلب الأحدث"),
    # ⚠️ وعطبا «القبرُ بلا ختمِ وقت» نُزعا (٨ أكتوبر ٢٠٢٦): كانا يكشفان حارسَ
    #    الختم، وقد حلَّ محلَّه حارسٌ أقوى — `rec.del = 0` في شرط الإدخال —
    #    فنزعُ ختمِ القبر لم يُعِد المحذوفَ، فمرّا بلا كشف. وعطبٌ لا يُعطب
    #    ليس عطباً: يُستبدل بما يكشف القاعدةَ القائمة.
    # ⚠️ وشاهدُه **التحضيرُ** لا الحصة: الحصةُ يحجزها التخطّي قبل SQL، أمّا
    #    الخرائطُ فتُترك للشرط — فهو موضعُ قياسِ هذه الطبقة.
    ("فتحُ القبرِ لكلِّ كتابة",
     '(revive ? "" : " AND rec.del = 0"))', '(revive ? "" : ""))',
     "ولا يعود تحضيرُ المحذوفةِ بختمٍ أحدث"),
    ("إعفاءُ كلِّ كتابةٍ من حارس القبور",
     "  if (!raw) {\n    const byPart = new Map();", "  if (false) {\n    const byPart = new Map();",
     "ويُخبَر الجهازُ بقبرها ليَدفن نسختَه"),
    ("كتمُ القبورِ عن الجهاز",
     "          buried.push({ part: p, rk: x.rk });",
     "          if (false) buried.push({ part: p, rk: x.rk });",
     "ويُخبَر بقبر التحضير"),
    ("جعلُ القبرِ يمرُّ على حارس التصادم",
     '      if (!old && isGrave("sched", x.id)) continue;', "",
     "ولا يحجز القبرُ خانتَه على تسجيلٍ جديد"),
    ("نزعُ أرضيّةِ السجلّ",
     'if (p === "prep" && k.indexOf(LOGP) === 0 && m.logfloor && k < m.logfloor) continue;',
     "if (false) continue;", "ولا يُكتب حرفٌ منه"),
    ("نزعُ قصِّ السجلّ كلِّه",
     "    await pruneLogs(d1, db);\n    await pruneTrash(d1, db);",
     "    await pruneTrash(d1, db);", "ويبقى السجلُّ عند حدّه بعدها"),
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
     '          if (body.v === 2) {\n            /* ⚠️ `now` ساعةُ الخادم',
     '          if (false) {\n            /* ⚠️ `now` ساعةُ الخادم',
     "لا تُعيد القاعدة"),
    ("نزعُ حارسِ الصفوف المتخلّفة",
     "            if ((m.blobw || 0) !== sw) {",
     "            if (false) {", "صفوفٍ متخلّفة"),
    ("نزعُ عدّادِ كتاباتِ الكتلة",
     '"INSERT INTO meta (db, blobw) VALUES (?, 1) ON CONFLICT(db) DO UPDATE SET blobw = meta.blobw + 1")',
     '"INSERT INTO meta (db, blobw) VALUES (?, 0) ON CONFLICT(db) DO UPDATE SET blobw = meta.blobw")',
     "صفوفٍ متخلّفة"),
    ("نزعُ تسجيلِ المسحةِ الختامية",
     "    await d1.prepare(\"UPDATE meta SET swept = blobw WHERE db = ?\").bind(db).run();",
     "    void 0;", "ويُحوَّل بمفتاح الإدارة"),
    ("نزعُ مطابقةِ الحذف من المسحة",
     "      for (const part of chunk(tx, 50)) await d1.batch(part);\n      stray = live.length;",
     "      stray = live.length;", "فلا يعود المحذوفُ"),
    ("نزعُ سقفِ المطابقة",
     "if (live.length && hard.length <= strayCap) {", "if (live.length) {",
     "تُبلِّغ ولا تُشاهِد"),
    # ⛔ والسجلُّ لا يُحسب في السقف: ٢٠٣٥ مدخلَ سجلٍّ منعت مسحةً صحيحةً على
    #    القاعدة الحيّة في ٧ أكتوبر، والخادمُ يسقط. فإن عاد حسابُه رُدَّت.
    ("جعلِ السقف يحسب السجلَّ أيضاً",
     "    const hard = live.filter((x) => !(x.part === \"prep\" && x.rk.indexOf(LOGP) === 0));",
     "    const hard = live;", "سجلٌّ متقادم"),
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
