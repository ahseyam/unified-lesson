# -*- coding: utf-8 -*-
"""⛔ **طبقةُ الحفظ والمزامنة لم يكن يفحصها شيء** — وفيها وقعت ثلاثةُ أعطالِ
فقدِ بياناتٍ في يومين (٢٩–٣٠ سبتمبر ٢٠٢٦):

  ١. `setSyn` حُذف تعريفُه وبقيت نداءاتُه السبعة — فكان كلُّ `save()` يسقط
     بعد الكتابة المحلية وقبل الإرسال: المنصةُ تحفظ على الجهاز ولا تُزامن.
  ٢. المزامنةُ تستبدل شجرةَ البيانات (`DB = r.data`) — والشاشةُ المفتوحةُ
     تُمسك مرجعاً إلى السجلّ، فما يُكتب بعدها يُكتب في كائنٍ منبتٍّ.
  ٣. السحبُ يضبط `lastSent` — فيرى الدفعُ أن لا جديدَ ويُعلن نجاحاً كاذباً،
     فما كُتب بين دفعةٍ وسحبٍ لا يُدفع أبداً.

وكلُّها تمرُّ من كل فحصٍ قائمٍ: الشاشةُ تُرسَم، والنصُّ يُترجَم، ولا شيءَ
يُفقد إلا البيانات. فهذا حارسُها — بخادمٍ مزيَّفٍ في المتصفّح (`fetch`
مُستبدَلةٌ) تُقاس به الحقائقُ لا تُصدَّق من الشفرة.

⚠️ ولا يُفحص بـ`grep` على المصدر: وجودُ السطر ليس وقوعَ الأثر.
"""
import html as H
import json
import os
import re
import subprocess
import sys

import probedir as PRB   # نسخُ الفحص خارج شجرة التسليم

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D8 = os.path.join(ROOT, "٨ - النموذج الرقمي (تجربة)")

BOOT = r"""
<script>
setTimeout(function(){
 var R = [];
 function T(n, g, w){ R.push([(String(g)===String(w)?"✓ ":"⛔ ")+n,
    String(g)===String(w) ? "" : ("وجد "+g+" · المنتظَر "+w)]); }
 function done(){ document.title="DONE"; window.__OUT = JSON.stringify(R); }
 try{
  /* ═════ خادمٌ مزيَّف: يحفظ ما يُكتب ويُعيده كما يفعل الحقيقي ═════ */
  var SRV = {}, POSTS = [], GETS = [], KEYS = [];
  window.fetch = function(u, o){
    var body = (o && o.body) ? JSON.parse(o.body) : null;
    if(body){                                   /* كتابة */
      POSTS.push(body); KEYS.push(body.key || "");
      var k = body.kind + "|" + body.id;
      if(body.__replace) SRV[k] = body.data;
      else {
        SRV[k] = SRV[k] || {};
        /* الدمجُ كما في الخادم المنشور: المفاتيحُ الخمسةُ وحدَها */
        ["sched","prep","obs","peer","rot"].forEach(function(f){
          if(!(f in body.data)) return;
          if(f === "sched"){ SRV[k].sched = body.data.sched; return; }
          SRV[k][f] = SRV[k][f] || {};
          Object.keys(body.data[f]).forEach(function(x){ SRV[k][f][x] = body.data[f][x]; });
        });
      }
      return Promise.resolve({status:200, json:function(){
        return Promise.resolve({ok:true, replaced: !!body.__replace, data: SRV[k]}); }});
    }
    var m = /kind=([^&]+)&id=([^&]+)/.exec(String(u));   /* قراءة */
    var key = m ? (decodeURIComponent(m[1]) + "|" + decodeURIComponent(m[2])) : "?";
    GETS.push(key);
    var mk = /[?&]key=([^&]+)/.exec(String(u));
    KEYS.push(mk ? decodeURIComponent(mk[1]) : "");
    return Promise.resolve({status:200, json:function(){
      return Promise.resolve({ok:true, data: SRV[key] || null}); }});
  };
  localStorage.setItem(API, "https://خادمٌ-مزيَّف/");
  /* ⛔ **المفتاحُ يُرسَل مع كل طلبٍ — قراءةً وكتابة.** كان العقدُ بلا مصادقةٍ
     البتّة، فمن ملك عنوانَ الخادم ملك القاعدةَ قراءةً وكتابةً ومحواً. ولا
     يكفي أن يُكتب في التخزين: يُقاس أنه **وصل في الطلب**. (١ أكتوبر ٢٠٢٦) */
  localStorage.setItem(SKEY, "مفتاحُ-الفحص-الطويل-جداً-٢٤");

  /* ═════ ١· مفتاحُ المخزن خاصٌّ بالمدرسة ═════ */
  T("مفتاحُ الخادم يحمل اسمَ المدرسة", SID, NS + "_db");
  T("وليس «db» المشتركَ", SID === "db", false);

  /* ═════ ٢· `dbSnapshot` يُخرج `__schema` ═════ */
  DB.__schema = 3;
  T("الحمولةُ بلا «__schema»", dbSnapshot().indexOf("__schema") < 0, true);

  /* ═════ ٣· `save()` يكتب محلياً فعلاً ═════ */
  var L = {id:"sy1", gk:"g", sector:D.sectors[0], complex:D.complexlist[0],
           stage:"س", school:"س", week:D.weeks[0], day:D.days[0], period:"1",
           teacher:"فاحص", subject:D.specs[0], spec:D.specs[0]};
  DB.sched.push(L);
  DB.prep[L.id] = {f_q_main:"سؤالُ الفحص"};
  save();
  var onDisk = JSON.parse(localStorage.getItem(KEY) || "{}");
  T("save يكتب الحصةَ على الجهاز",
    (onDisk.sched || []).filter(function(x){ return x.id === "sy1"; }).length, 1);
  T("save يكتب التحضيرَ على الجهاز",
    ((onDisk.prep || {})["sy1"] || {}).f_q_main, "سؤالُ الفحص");

  /* ═════ ٤· الدفعُ يُرسل ما كُتب ═════ */
  pushNow().then(function(ok1){
   T("الدفعُ نجح", ok1, true);
   T("الحمولةُ ذهبت إلى مفتاح المدرسة", POSTS.length ? POSTS[0].id : "—", NS + "_db");

   /* ═════ ٥· الدمجُ يحفظ هويّةَ الكائن ═════
      الشاشةُ المفتوحةُ تُمسك مرجعاً — فإن استُبدلت الشجرةُ كُتب في المنبتّ. */
   var held = DB.prep["sy1"];                 /* مرجعٌ كما تُمسكه الشاشة */
   SRV["platform|" + NS + "_db"].prep["sy1"] = {f_q_main:"سؤالُ الفحص", f_life:"من الخادم"};
   return pullNow().then(function(){
    T("السحبُ أتى بحقلِ الخادم", (DB.prep["sy1"]||{}).f_life, "من الخادم");
    T("والمرجعُ الذي تُمسكه الشاشةُ هو نفسُه", DB.prep["sy1"] === held, true);
    held.f_fb = "كُتب بعد السحب";
    T("فالكتابةُ بعد السحب تصل القاعدة",
      (DB.prep["sy1"]||{}).f_fb, "كُتب بعد السحب");

    /* ═════ ٦· `lastSent` لا يضبطه السحب ═════
       ⚠️ **الترتيبُ هو الشاهد**: لو كتبنا بعد السحب لتغيَّرت البصمةُ
       فدُفعت ولو كان `lastSent` مغلوطاً — فيمرُّ العطلُ من الفحص (جرّبتُه
       مزروعاً فمرّ). والعطلُ الحقيقيُّ يضيع به ما كُتب **بين** دفعةٍ وسحب:
       كتابةٌ ← دفعٌ ← كتابةٌ ثانيةٌ ← سحبٌ (يضبط `lastSent` خطأً) ← دفعٌ
       يرى أن لا جديدَ فيُعلن نجاحاً كاذباً. فهذا تَرتيبُه. */
    return pushNow().then(function(){
      DB.prep["sy1"].f_higher = "كُتب بين دفعةٍ وسحب";   /* ولا يُدفَع بعده */
      var n0 = POSTS.length;
      return pullNow().then(function(){
        return pushNow().then(function(){
          T("ما كُتب بين دفعةٍ وسحبٍ يُدفَع",  POSTS.length > n0, true);
          T("ووصل إلى الخادم فعلاً",
            ((SRV["platform|" + NS + "_db"].prep["sy1"]) || {}).f_higher,
            "كُتب بين دفعةٍ وسحب");
      /* ═════ ٧· الحصصُ تُدمج بالمعرّف لا تُستبدل ═════ */
      var mine = DB.sched.filter(function(x){ return x.id === "sy1"; });
      T("لا تُكرَّر الحصةُ بعد دفعةٍ وسحب", mine.length, 1);

      /* ═════ ٨· كشفُ المعلمين يُقرأ من المخزن ويُخزَّن ═════ */
      SRV["platform|" + NS + "_roster"] = {"90009": {n:"معلمُ الكشف", s:D.specs[0]}};
      return rosterPull().then(function(got){
        T("الكشفُ يُحمَّل من المخزن", got, true);
        T("ويدخل D.roster", ((D.roster||{})["90009"]||{}).n, "معلمُ الكشف");
        T("ويُحفظ على الجهاز للعمل بلا شبكة",
          (JSON.parse(localStorage.getItem(RKEY)||"{}")["90009"]||{}).n, "معلمُ الكشف");
        T("وطُلب بمفتاح المدرسة", GETS.indexOf("platform|" + NS + "_roster") >= 0, true);

        /* ═════ ٩· حارسُ الرفع يرفض ما لا تعرفه المنصة ═════ */
        T("يُرفض كشفٌ بمادةٍ مجهولة",
          rosterCheck({"1": {n:"س", s:"مادةٌ لا وجودَ لها"}}) !== "", true);
        T("يُرفض مفتاحٌ غيرُ رقمي", rosterCheck({"abc": {n:"س", s:D.specs[0]}}) !== "", true);
        T("يُرفض سطرٌ بلا اسم", rosterCheck({"5": {s:D.specs[0]}}) !== "", true);
        var good = {}; good["7"] = {n:"س", s:Object.keys(D.specmap||{})[0]};
        T("ويُقبل الكشفُ السليم", rosterCheck(good), "");
        /* ═════ ١٠· المصادقة: المفتاحُ في كل طلبٍ بلا استثناء ═════ */
        T("طُلبت المصادقةُ في كل نداء", KEYS.length > 4, true);
        T("ولا نداءَ بلا مفتاح",
          KEYS.filter(function(x){ return !x; }).length, 0);
        T("وهو المفتاحُ المضبوط",
          KEYS.filter(function(x){ return x !== skey(); }).length, 0);
        T("والدعوةُ تحمله في جزء التجزئة",
          (location.origin + location.pathname + "#srv=x&k=" + encodeURIComponent(skey()))
            .indexOf("#srv=") > 0, true);
        done();
      });
        });
      });
    });
   });
  }).catch(function(e){ T("سقط أثناء المزامنة: " + e.message, 1, 0); done(); });
 }catch(e){ document.title="ERR|"+e.message+" @ "+(e.stack||"").split("\n")[1];
            window.__OUT = JSON.stringify(R); }
}, 400);
</script>
<script>setTimeout(function(){var d=document.createElement("pre");d.id="dump";
 d.textContent=window.__OUT||"";document.body.appendChild(d);},2600);</script>
"""

FLOOR = 24


def run(tag, fn):
    src = os.path.join(D8, fn)
    p = PRB.probe("sync_%s.html" % tag)
    open(p, "w", encoding="utf-8").write(open(src, encoding="utf-8").read() + BOOT)
    out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                          "--virtual-time-budget=15000", "--dump-dom", "file://" + p],
                         capture_output=True, text=True).stdout
    t = re.search(r"<title>(.*?)</title>", out, re.S)
    ttl = H.unescape(t.group(1)) if t else "?"
    m = re.search(r'<pre id="dump">(.*?)</pre>', out, re.S)
    rows = json.loads(H.unescape(m.group(1))) if (m and m.group(1).strip()) else []
    for line, extra in rows:
        print("  " + line + ("   [" + extra + "]" if extra else ""))
    if ttl.startswith("ERR"):
        print("  ⛔ " + ttl)
    bad = [1 for l, _ in rows if l.startswith("⛔")]
    short = len(rows) < FLOOR
    if short:
        print("  ⛔ %d شاهداً فقط — والأرضيّةُ %d. الفحصُ لم يَقِس." % (len(rows), FLOOR))
    ok = not bad and not short and not ttl.startswith("ERR")
    print("  %s %s — %d/%d شاهداً"
          % ("✓" if ok else "⛔", tag, len(rows) - len(bad), len(rows)))
    return ok


if __name__ == "__main__":
    ok = True
    for tag, fn in (("بنين", "منصة الحصة الموحَّدة — ابن خلدون.html"),
                    ("بنات", "منصة الحصة الموحَّدة — ابن خلدون (بنات).html")):
        ok &= run(tag, fn)
    print("\n  " + ("✓ الحفظُ والمزامنةُ والكشفُ تعمل" if ok else "⛔ فيها خلل"))
    sys.exit(0 if ok else 1)
