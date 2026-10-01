# -*- coding: utf-8 -*-
"""⛔ سجلُّ الإشراف: من يرصد كلَّ حصة، ومن لا يرصد، ومتى يُعلَن التعارض.
   والحالاتُ مختارةٌ نعلم جوابها سلفاً: مشرفُ رياضيات يرصد رياضياته ولا يرصد
   إنجليزيّةَ غيره · وتخصصٌ بلا مشرفٍ يرصده الفريق المعاون · ورقمٌ ليس في
   السجلّ يُردّ · ومجمعان في يومٍ واحدٍ يُصرخ بهما."""
import html as H, json, os, re, subprocess, sys
import probedir as PRB   # نسخُ الفحص خارج شجرة التسليم
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BASE = "/Users/ahmadseyam/Desktop/نموذج تحضير الدرس - بطاقة الملاحظة الصفية/٨ - النموذج الرقمي (تجربة)/"
SRC = {"بنين": BASE + "منصة الحصة الموحَّدة — ابن خلدون.html",
       "بنات": BASE + "منصة الحصة الموحَّدة — ابن خلدون (بنات).html"}

BOOT = r"""
<script>
setTimeout(function(){
 var R=[];
 function A(t,ok,x){ R.push(x===undefined?[t,!!ok]:[t,!!ok,String(x)]); }
 function mkL(o){ var L={id:o.id||("x"+Math.random()), sector:o.sector, complex:o.cx,
   stage:o.stage, school:o.stage, period:o.per, week:o.wk, day:o.day, spec:o.spec,
   teacher:o.teacher||"أ. تجربة", teacherNo:"30888", klass:"١/أ"};
   L.gk=[L.sector,L.complex,L.stage,L.period,L.week,L.day,L.spec].join("|"); return L; }
 try{
  localStorage.clear(); load();
  var SUPS = D.sups||[];
  A("السجلُّ مشحونٌ في الصفحة", SUPS.length > 0, SUPS.length);
  A("ولكلِّ مشرفٍ رقمٌ ومادةٌ أو إشرافٌ بالمرحلة",
    SUPS.every(function(r){ return r.emp && (r.allsubj || (r.subjects||[]).length); }));
  A("ولا رقمَ مكرَّر",
    new Set(SUPS.map(function(r){return r.emp;})).size === SUPS.length);
  A("والدوران الجديدان في الأدوار",
    D.roles.some(function(r){return r.k==="cxmgr";}) && D.roles.some(function(r){return r.k==="intqa";}));
  A("ورصدُ الفجوة لثلاثة لا غير",
    JSON.stringify(D.gapscore) === JSON.stringify(["deputy","principal","cxmgr"]),
    JSON.stringify(D.gapscore));

  /* ── نختار مشرفاً بمادةٍ واحدةٍ نعرفها، وحصةً في نطاقه ── */
  var one = SUPS.filter(function(r){ return !r.allsubj && r.subjects.length === 1; })[0];
  A("وُجد مشرفٌ بمادةٍ واحدةٍ للاختبار", !!one, one && one.name);
  var SEC = one.sectors[0], CX = one.complexes[0],
      BS = (D.bands[CX]||[]).filter(function(b){ return b.stage.indexOf(one.stages[0])===0; }),
      B  = BS[0] || (D.bands[CX]||[])[0];
  var L1 = mkL({sector:SEC, cx:CX, stage:B.stage, per:B.per, wk:D.weeks[0], day:D.days[0],
                spec:one.subjects[0]});
  A("حصةُ مادته يعرفها السجلُّ باسمه",
    supsFor(L1).some(function(r){ return r.emp === one.emp; }),
    supsFor(L1).map(function(r){return r.name;}).join("·"));
  A("وليست فجوة", !isGap(L1));

  /* ── الرصد: له هو لا لغيره ── */
  ME={role:"supervisor", name:one.name, emp:one.emp}; 
  A("يرصد حصةَ مادته", canScore(L1));
  var other = SUPS.filter(function(r){ return !r.allsubj && r.emp !== one.emp
      && r.subjects.indexOf(one.subjects[0]) < 0; })[0];
  if(other){
    var L2 = mkL({sector:other.sectors[0], cx:other.complexes[0],
                  stage:(D.bands[other.complexes[0]]||[])[0].stage,
                  per:(D.bands[other.complexes[0]]||[])[0].per,
                  wk:D.weeks[0], day:D.days[0], spec:other.subjects[0]});
    A("ولا يرصد حصةَ مشرفٍ آخر", !canScore(L2), other.name+"/"+other.subjects[0]);
  }

  /* ── الفجوة: تخصصٌ لا مشرفَ له ── */
  var gap=null;
  (D.sectors||[]).forEach(function(sec){
    ((D.complexes||{})[sec]||[]).forEach(function(cx){
      (D.bands[cx]||[]).forEach(function(b){
        (D.specs||[]).forEach(function(sp){
          if(gap) return;
          if(supsForCell(sec,cx,b.stage,sp).length===0)
            gap = mkL({sector:sec, cx:cx, stage:b.stage, per:b.per,
                       wk:D.weeks[0], day:D.days[0], spec:sp});
        });
      });
    });
  });
  A("وُجدت خليةٌ بلا مشرفٍ مختص", !!gap, gap && (gap.spec+" · "+gap.complex+" · "+gap.stage));
  if(gap){
    ME={role:"supervisor", name:one.name, emp:one.emp};
    A("لا يرصدها مشرفٌ ليست من نطاقه", !canScore(gap));
    ME={role:"deputy", name:"أ. الوكيل", emp:"11111",
        sector:gap.sector, complex:gap.complex, school:gap.stage};
    A("ويرصدها الوكيلُ التعليمي في مدرستها", canScore(gap));
    ME={role:"deputy", name:"أ. الوكيل", emp:"11111",
        sector:gap.sector, complex:gap.complex, school:"لا مدرسة"};
    A("ولا يرصدها وكيلُ مدرسةٍ أخرى", !canScore(gap));
    ME={role:"principal", name:"أ. المدير", emp:"22222",
        sector:gap.sector, complex:gap.complex, school:gap.stage};
    A("ويرصدها مديرُ المدرسة", canScore(gap));
    ME={role:"cxmgr", name:"أ. مدير المجمع", emp:"33333",
        sector:gap.sector, complex:gap.complex};
    A("ويرصدها مديرُ المجمع", canScore(gap));
    ME={role:"cxmgr", name:"أ. مدير المجمع", emp:"33333",
        sector:gap.sector, complex:"__لا مجمع__"};
    A("ولا يرصدها مديرُ مجمعٍ آخر", !canScore(gap));
    ME={role:"intqa", name:"أ. فريق المتابعة", emp:"44444"};
    A("ولا يرصدها فريقُ المتابعة — يتابع ولا يرصد", !canScore(gap));
    ME={role:"principal", name:"أ. المدير", emp:"22222",
        sector:L1.sector, complex:L1.complex, school:L1.stage};
    A("ولا يرصد المديرُ حصةً لها مشرفُها", !canScore(L1));
  }

  /* ── الرقمُ الوظيفي: السجلُّ لا الكشف ── */
  A("رقمُ المشرف يُقبل", empError(one.emp, "supervisor") === "", empError(one.emp,"supervisor"));
  A("ورقمٌ ليس فيه يُردّ برسالته", empError("99999999", "supervisor").indexOf("سجلّ الإشراف") >= 0,
    empError("99999999","supervisor"));

  /* ── حارسُ التعارض: مجمعان في يومٍ واحد ── */
  var two = one.complexes.length > 1 ? one : SUPS.filter(function(r){
      return !r.allsubj && r.complexes.length > 1; })[0];
  if(two){
    var s2=two.sectors[0], cA=two.complexes[0], cB=two.complexes[1], sp2=two.subjects[0];
    /* ⛔ المرحلةُ تُختار من مراحله هو: أولُ أعمدة المجمع في نسخة البنات
       رياضُ الأطفال، وليست من مراحل كل مشرفة — فكان الفحصُ يغرس خارج نطاقها. */
    function bandOf(cx){
      var bs=(D.bands[cx]||[]).filter(function(b){
        return two.stages.some(function(st){ return b.stage.indexOf(st)===0; }); });
      return bs[0] || (D.bands[cx]||[])[0];
    }
    var bA=bandOf(cA), bB=bandOf(cB);
    var La=mkL({id:"ca", sector:s2, cx:cA, stage:bA.stage, per:bA.per,
                wk:D.weeks[0], day:D.days[0], spec:sp2});
    var Lb=mkL({id:"cb", sector:s2, cx:cB, stage:bB.stage, per:bB.per,
                wk:D.weeks[0], day:D.days[0], spec:sp2});
    DB.sched=[La,Lb]; save();
    var cf=supConflict(La);
    A("مجمعان في اليوم نفسِه ⇒ تعارضٌ مُعلَن", !!cf, cf && cf.other.join("+"));
    A("والتعارضُ باسم مشرفه", !!cf && cf.name === two.name, cf && cf.name);
    DB.sched=[La]; save();
    A("ومجمعٌ واحدٌ ⇒ لا تعارض", !supConflict(La));
    /* ويومٌ آخرُ لا يتعارض */
    Lb.day = D.days[1]; Lb.gk=[Lb.sector,Lb.complex,Lb.stage,Lb.period,Lb.week,Lb.day,Lb.spec].join("|");
    DB.sched=[La,Lb]; save();
    A("ويومان مختلفان ⇒ لا تعارض", !supConflict(La));
  }
  localStorage.clear();
  document.title="DONE"; window.__OUT=JSON.stringify(R);
 }catch(e){ document.title="ERR|"+e.message; window.__OUT=JSON.stringify(R); }
}, 500);
</script>
<script>setTimeout(function(){var d=document.createElement("pre");d.id="dump";
 d.textContent=window.__OUT||"";document.body.appendChild(d);},7000);</script>
"""

allok = True
for lbl, src in SRC.items():
    p = PRB.probe("sup_probe.html")
    open(p, "w", encoding="utf-8").write(open(src, encoding="utf-8").read() + BOOT)
    out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                          "--virtual-time-budget=20000", "--dump-dom", "file://" + p],
                         capture_output=True, text=True).stdout
    m = re.search(r'<pre id="dump">(.*?)</pre>', out, re.S)
    t = re.search(r"<title>(.*?)</title>", out, re.S)
    rows = json.loads(H.unescape(m.group(1))) if (m and m.group(1).strip()) else []
    print("\n── %s ── (%d شاهداً)" % (lbl, len(rows)))
    ok = len(rows) >= 18
    if len(rows) < 18: print("  ⛔ عددُ الشواهد أقلُّ من المتوقَّع — فحصٌ لم يكتمل")
    for r in rows:
        g = bool(r[1]); ok &= g
        print("  %s %s%s" % ("✓" if g else "⛔", r[0],
              ("   [" + str(r[2]) + "]") if len(r) > 2 else ""))
    if t and H.unescape(t.group(1)).startswith("ERR"):
        print("  ⛔", H.unescape(t.group(1))); ok = False
    allok &= ok
    os.remove(p)
print("\n%s" % ("✓ سجلُّ الإشراف يحكم الرصدَ والتعارض" if allok else "⛔ لا يُعتمد"))
sys.exit(0 if allok else 1)
