# -*- coding: utf-8 -*-
"""⛔ «وُزِّع ٤٠ خانة» ليست «وُضعت في الخانة الصحيحة»: يُولَّد جوابٌ بصيغة
   الأمر، ويُوزَّع، **ثم تُقرأ كلُّ خانةٍ من التخزين ويُقارن بما أُرسل إليها**.

⚠️ ويُجرَّب على حالٍ يُعرف جوابُها: الاختياراتُ من قوائمها، والأرقامُ أرقام،
   والنصوصُ موسومةٌ بمفتاحها فيُكشف أيُّ خلطٍ بين حقلين."""
import html as H, json, os, re, subprocess, sys
import probedir as PRB   # نسخُ الفحص خارج شجرة التسليم
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRC="/Users/ahmadseyam/Desktop/نموذج تحضير الدرس - بطاقة الملاحظة الصفية/٨ - النموذج الرقمي (تجربة)/منصة الحصة الموحَّدة — ابن خلدون.html"
BOOT = r"""
<script>
setTimeout(function(){
 try{
  localStorage.clear();
  var SEC=D.sectors[0], CX=D.complexlist[0], b=(D.bands[CX]||[])[0];
  var wk=D.weeks[0], day=D.days[0], sp=D.specs[0];
  var L={id:"imp1", gk:[SEC,CX,b.stage,b.per,wk,day,sp].join("|"),
    sector:SEC,complex:CX,stage:b.stage,school:b.stage,week:wk,day:day,
    period:b.per.replace(/\D/g,""),time:b.time,teacher:"أ. نموذج",teacherNo:"",
    subject:sp,spec:sp,klass:"5/A",strategy:(D.bank[0]||{}).name,approach:D.approaches[0],
    peer1:"",peer2:"",peer1e:"",peer2e:"",ev1:"",ev2:"",ev3:""};
  DB.sched.push(L); var P = DB.prep["imp1"] = {}; save();
  ME={role:"teacher",name:"أ. نموذج",emp:"",spec:sp};

  var F = planFields();
  /* جوابٌ مُصطنعٌ: لكل حقلٍ قيمةٌ تحمل مفتاحَه فيُكشف الخلط */
  var lines = [], want = {};
  F.forEach(function(f, i){
    var v;
    if(f.kind === "ticks")      v = (f.items||[])[0] || "";
    else if(f.kind === "select")v = (f.items||[])[1] || (f.items||[])[0] || "";
    else if(f.kind === "num")   v = String(5 + (i % 20));
    else                        v = "قيمة#" + f.key;
    if(!v) return;
    lines.push("### " + f.lab + ": " + v);
    want[f.key] = {kind: f.kind, val: v, items: f.items || null};
  });
  var map = planParse(lines.join("\n"));
  var plan = planPlan(P, map);
  var n = planApply(P, plan.fill.concat(plan.over));

  /* ⛔ **واللصقُ كان يفشل إذا أجاب المساعدُ بالإنجليزية** (بلاغُ أ. محمد أبو
     نار عبر وكيل عرقة عالمي — ٦ أكتوبر ٢٠٢٦): التوزيعُ كان يُطابق الاسمَ
     العربيَّ وحدَه، فضاعت **٢٨ خانةً من ٧٦ صامتةً** — ولم تفشل فشلاً بيّناً
     بل امتلأت ناقصةً. فصارت للتوزيع ثلاثُ مراسٍ، وتُقاس الثلاثُ هنا. */
  var en = [], tr = [], noc = [];
  F.forEach(function(f, i){
    var v = f.kind === "ticks" ? ((f.items||[])[0]||"")
          : f.kind === "select" ? ((f.items||[])[1]||(f.items||[])[0]||"")
          : f.kind === "num" ? String(5 + (i % 20)) : "قيمة#" + f.key;
    if(!v) return;
    en.push("### " + ((typeof I18N !== "undefined" && I18N[f.lab]) || f.lab) + " [" + f.key + "]: " + v);
    tr.push("### Lesson plan item number " + (i+1) + " [" + f.key + "]: " + v);
    noc.push("### Lesson plan item number " + (i+1) + ": " + v);
  });
  function fills(txt){ var Q = {}; var pl = planPlan(Q, planParse(txt)); return pl.fill.length; }
  var SENT = Object.keys(want).length;
  var lang = {sent: SENT, en: fills(en.join("\n")), code: fills(tr.join("\n")),
              none: fills(noc.join("\n"))};

  /* ── المقارنة: ما وصل إلى كل مفتاح؟ ── */
  var bad = [], okn = 0;
  Object.keys(want).forEach(function(k){
    var w = want[k];
    if(w.kind === "ticks"){
      var i0 = (w.items||[]).indexOf(w.val);
      if(P[k + "#" + i0] === true) okn++; else bad.push([k, "لم يُعلَّم", w.val]);
      return;
    }
    var got = P[k];
    if(w.kind === "num"){ if(String(got) === String(w.val)) okn++; else bad.push([k, got, w.val]); return; }
    if(w.kind === "select"){ if(got === w.val) okn++; else bad.push([k, got, w.val]); return; }
    if(got === w.val) okn++; else bad.push([k, got, w.val]);
  });
  /* ولا تُكتب قيمةٌ في مفتاحٍ لم يُرسَل إليه شيء */
  var stray = Object.keys(P).filter(function(k){
    return !(k in want) && !/#\d+$/.test(k) && P[k] && !/^__/.test(k); });
  document.title = "OK";
  window.__OUT = JSON.stringify({fields: F.length, sent: Object.keys(want).length,
    applied: n, ok: okn, bad: bad.slice(0,8), unknown: plan.unknown.slice(0,5),
    stray: stray.slice(0,8), lang: lang});
 }catch(e){ document.title = "ERR|" + e.message + " @ " + (e.stack||"").split("\n")[1]; }
}, 300);
</script>
<script>setTimeout(function(){var d=document.createElement("pre");d.id="dump";
 d.textContent=window.__OUT||"";document.body.appendChild(d);},1400);</script>
"""
p = PRB.probe("import_probe.html")
open(p,"w",encoding="utf-8").write(open(SRC,encoding="utf-8").read()+BOOT)
out = subprocess.run([CHROME,"--headless=new","--disable-gpu","--no-sandbox",
     "--virtual-time-budget=10000","--dump-dom","file://"+p],capture_output=True,text=True).stdout
m = re.search(r'<pre id="dump">(.*?)</pre>', out, re.S)
if not m or not m.group(1).strip():
    t = re.search(r"<title>(.*?)</title>", out, re.S)
    print("  ⛔", H.unescape(t.group(1)) if t else "?"); sys.exit(1)
r = json.loads(H.unescape(m.group(1)))
print("  حقولُ النموذج: %d · أُرسل: %d · وُزِّع: %d · وصل صحيحاً: %d"
      % (r["fields"], r["sent"], r["applied"], r["ok"]))
for k, got, wanted in r["bad"]:
    print("    ⛔ %-18s وصل %r · المنتظَر %r" % (k, got, wanted))
if r["unknown"]: print("    ⛔ لم تُفهم:", r["unknown"])
if r["stray"]:   print("    ⛔ كُتب في مفتاحٍ لم يُرسَل إليه:", r["stray"])
good = r["ok"] == r["sent"] and not r["bad"] and not r["unknown"] and not r["stray"]

# ── ولغةُ الجواب لا تُسقط خانة ──
L = r.get("lang") or {}
sent = L.get("sent", 0)
print("\n  ── جوابُ المساعد بالإنجليزية (بلاغُ أ. محمد أبو نار ٦ أكتوبر) ──")
rows = [("أسماءٌ إنجليزيةٌ من المعجم", L.get("en"), sent),
        ("ترجمةٌ غريبةٌ والرمزُ باقٍ", L.get("code"), sent)]
for lab, got, want in rows:
    ok = got == want
    good &= ok
    print("    %s %-28s %s من %s" % ("✓" if ok else "⛔", lab, got, want))
# ⚠️ وحالةٌ تُقاس لتبقى مفهومة: بلا رمزٍ وبلا اسمٍ معروفٍ لا يُطابق شيء —
#    وهي مستحيلةٌ بالأمر الجديد (فهو يحمل الرموز)، وتُذكر لئلّا يُظنَّ أن
#    التوزيع يُخمّن. ورسالةُ المنصة تقول للمعلم: أعد نسخَ الأمر.
print("    ⓘ %-28s %s من %s (بلا رمزٍ ولا اسمٍ معروف — تُردّ برسالةٍ تشرح)"
      % ("ترجمةٌ غريبةٌ بلا رمز", L.get("none"), sent))
if not sent:
    print("    ⛔ لم يُقَس شيءٌ من اللغات — فحصٌ ناقص"); good = False
print("\n  %s" % ("✓ كلُّ قيمةٍ في خانتها، أيّاً كانت لغةُ الجواب" if good else "⛔ فيه خلط"))
sys.exit(0 if good else 1)
