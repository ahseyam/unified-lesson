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
    /* ⚠️ **نُقضت قاعدةُ «المشرفُ وحدَه»** (٤ أكتوبر ٢٠٢٦): المقيّمون خمسةٌ،
       لكلٍّ استمارتُه، والمعتمَدُ متوسّطُ من رصد. فصار الشاهدُ عكسَ ما كان:
       يرصد فريقُ المتابعة، ويرصد المديرُ ولو كان للحصة مشرفُها. */
    A("ويرصدها فريقُ متابعة التقويم الداخلي", canScore(gap));
    ME={role:"principal", name:"أ. المدير", emp:"22222",
        sector:L1.sector, complex:L1.complex, school:L1.stage};
    A("ويرصد المديرُ حصةً لها مشرفُها — في مدرسته", canScore(L1));
    ME={role:"principal", name:"أ. مديرٌ آخر", emp:"22299",
        sector:L1.sector, complex:L1.complex, school:"__لا مدرسة__"};
    A("ولا يرصد مديرُ مدرسةٍ أخرى — النطاقُ باقٍ", !canScore(L1));
  }

  /* ── الرقمُ الوظيفي: السجلُّ لا الكشف ── */
  A("رقمُ المشرف يُقبل", empError(one.emp, "supervisor") === "", empError(one.emp,"supervisor"));
  A("ورقمٌ ليس فيه يُردّ برسالته", empError("99999999", "supervisor").indexOf("سجلّ الإشراف") >= 0,
    empError("99999999","supervisor"));


  /* ── بوّابةُ الرقم الوظيفي: لكلِّ دورٍ مَرجعُه ──
     ⛔ الكشفُ كشفُ معلمين، فكانت القياداتُ الأربعُ تُحجب عن الدخول متى حُمِّل.
     ⚠️ ويُغرَس كشفٌ هنا: الكشفُ المنشورُ فارغٌ، والفارغُ يُسقط التحقّقَ كلَّه
        فيمرُّ الفحصُ وهو لم يقس شيئاً. */
  var ROLD = D.roster, ELEN = D.emplen;
  D.roster = {"11141": {n:"أ. معلمٌ في الكشف", s:"لغتي", c:(D.complexes[D.sectors[0]]||[])[0],
                        g:"الابتدائية", k:D.sectors[0]}};
  D.emplen = 5;
  A("معلمٌ في الكشف يدخل", empError("11141", "teacher") === "", empError("11141","teacher"));
  A("ومعلمٌ ليس فيه يُردّ", empError("98765", "teacher").indexOf("كشف المنسوبين") >= 0,
    empError("98765","teacher"));
  A("والزائرُ معلمٌ فيُقاس على الكشف", empError("98765", "peer").indexOf("كشف المنسوبين") >= 0);
  ["principal","deputy","cxmgr","intqa"].forEach(function(r){
    A("و" + r + " يدخل بلا عضويةِ كشفِ المعلمين", empError("98765", r) === "",
      empError("98765", r));
  });
  A("وقاعدةُ المنازل تبقى على القيادات", empError("12", "cxmgr").indexOf("منازل") >= 0,
    empError("12","cxmgr"));
  D.roster = ROLD; D.emplen = ELEN;

  /* ── المشرفُ المعان: له مشرفٌ قد لا يحضر ── */
  /* ⚠️ والعلمُ على مشرفةِ رياض الأطفال العالمي وحدَها، فنسخةُ البنين لا
     مشرفَ معاناً فيها — فلا يُطالَب بما ليس فيه، **ويُشترط** أن تكون إحدى
     النسختين قد مرَّت على الفرع فعلاً (أرضيّةُ بايثون أدناه)، وإلا مرَّ
     الحارسُ وهو لم يقس شيئاً. */
  var hs = SUPS.filter(function(r){ return !!r.schoolhelp; })[0];
  if(!hs) A("لا مشرفَ معاناً في هذه النسخة — والدالّةُ تنفيه", !isAssisted(L1));
  if(hs){
    A("شُحن علمُ «تساعدها المدرسة» في السجلّ", true, hs.name);
    var hcx = hs.complexes[0];
    var hb = (D.bands[hcx]||[]).filter(function(b){
      return hs.stages.some(function(st){ return b.stage.indexOf(st) === 0; }); })[0];
    A("ولمرحلته أعمدةٌ في مجمعه", !!hb, hb && hb.stage);
    if(hb){
      var LH = mkL({sector:hs.sectors[0], cx:hcx, stage:hb.stage, per:hb.per,
                    wk:D.weeks[0], day:D.days[0], spec:(D.specs||[])[0]});
      A("حصتُه ليست فجوةً — لها مشرف", !isGap(LH));
      A("وهي «معانةٌ»", isAssisted(LH));
      ME={role:"principal", name:"أ. المدير", emp:"22222",
          sector:LH.sector, complex:LH.complex, school:LH.stage};
      A("فيرصدها مديرُ مدرستها", canScore(LH));
      A("وتُعدُّ عليه بشارتها", isMyGap(LH));
      ME={role:"deputy", name:"أ. الوكيل", emp:"11111",
          sector:LH.sector, complex:LH.complex, school:LH.stage};
      A("ويرصدها وكيلُها", canScore(LH));
      ME={role:"cxmgr", name:"أ. مدير المجمع", emp:"33333",
          sector:LH.sector, complex:LH.complex};
      A("ويرصدها مديرُ المجمع — مجمعُه", canScore(LH));
      ME={role:"cxmgr", name:"أ. مديرُ مجمعٍ آخر", emp:"33399",
          sector:LH.sector, complex:"__لا مجمع__"};
      A("ولا مديرُ مجمعٍ آخر", !canScore(LH));
      ME={role:"intqa", name:"أ. فريق المتابعة", emp:"44444"};
      A("ويرصدها فريقُ المتابعة", canScore(LH));
      ME={role:"principal", name:"أ. المدير", emp:"22222",
          sector:LH.sector, complex:LH.complex, school:"__لا مدرسة__"};
      A("ولا مديرُ مدرسةٍ أخرى", !canScore(LH));
    }
  }

  /* ── الحذفُ والمحوُ والاستردادُ: فريقُ المتابعة يتابع ولا يُتلف ── */
  if(gap){
    var LD = mkL({sector:gap.sector, cx:gap.complex, stage:gap.stage, per:gap.per,
                  wk:D.weeks[0], day:D.days[0], spec:gap.spec});
    ME={role:"intqa", name:"أ. فريق المتابعة", emp:"44444"};
    A("فريقُ المتابعة لا يحذف", !canDrop(LD));
    A("ويُقال له لماذا", (dropWhy(LD)||"").indexOf("متابعةٌ لا حذف") >= 0, dropWhy(LD));
    A("ولا يمحو نهائياً", !canPurge(LD));
    A("ولا يستردّ", !canRestore(LD));
    ME={role:"deputy", name:"أ. الوكيل", emp:"11111",
        sector:LD.sector, complex:LD.complex, school:LD.stage};
    A("والوكيلُ في مدرستها يحذف", canDrop(LD));
    A("ويمحو", canPurge(LD));
    A("ويستردّ", canRestore(LD));
    ME={role:"deputy", name:"أ. الوكيل", emp:"11111",
        sector:LD.sector, complex:LD.complex, school:"__لا مدرسة__"};
    A("ووكيلُ غيرِها لا يمحو", !canPurge(LD));
    /* ⛔ وللسلّةِ حقيقةٌ واحدةٌ: كان العدّادُ يُرشِّح بقاعدةٍ والعرضُ بأخرى */
    DB.prep = {}; DB.prep[trashKey("zz1")] = {L: LD, by: "أ. غيري", at: new Date().toISOString()};
    ME={role:"intqa", name:"أ. فريق المتابعة", emp:"44444"};
    A("ولا يرى فريقُ المتابعة محذوفَ غيره", trashList().length === 0, trashList().length);
    ME={role:"deputy", name:"أ. الوكيل", emp:"11111",
        sector:LD.sector, complex:LD.complex, school:LD.stage};
    A("ويراه وكيلُ مدرستها", trashList().length === 1, trashList().length);
    ME={role:"deputy", name:"أ. الوكيل", emp:"11111",
        sector:LD.sector, complex:LD.complex, school:"__لا مدرسة__"};
    A("ولا يراه وكيلُ غيرِها", trashList().length === 0, trashList().length);
    DB.prep = {};
  }

  /* ── تأنيثُ نصوصِ الشارات: كُتبت في الشفرة فبقيت مذكَّرةً في البنات ──
     ⛔ «عليك — لا مشرفَ لتخصصها» و«مشرفٌ مختصٌّ لا يحضر» و«ووكيلها» بلا تاء:
        `fem()` لا تمسح نصوصَ الشفرة إلا بقائمةٍ جزئية. فصارت في `D` بـ`g()`،
        **ويُقاس الناتجُ لا المصدر**. */
  var FEM = (D.roles||[]).some(function(r){ return r.k==="intqa" && /تتابعان/.test(r.d||""); });
  A("عُرفت لغةُ النسخة من وصف الأدوار", true, FEM ? "بنات" : "بنين");
  ["gaptag","gaptip","asstag","asstip","intqanodel"].forEach(function(k){
    A("نصُّ " + k + " مشحونٌ في الصفحة", !!(D[k] && D[k].length > 3), D[k]);
  });
  if(FEM){
    A("شارةُ الفجوة مؤنَّثة", /مشرفةَ/.test(D.gaptag), D.gaptag);
    A("وشرحُها مؤنَّث", /مشرفةَ مختصةً/.test(D.gaptip) && /وأنتِ/.test(D.gaptip));
    A("وشارةُ المعان مؤنَّثة", /مشرفتُها قد لا تحضر/.test(D.asstag), D.asstag);
    A("وشرحُها يؤنِّث المديرةَ والوكيلة",
      /مديرة المدرسة ووكيلتها/.test(D.asstip), D.asstip);
  } else {
    A("شارةُ الفجوة مذكَّرة", /مشرفَ/.test(D.gaptag) && !/مشرفةَ/.test(D.gaptag), D.gaptag);
    A("وشرحُ المعان يذكِّر المديرَ والوكيل",
      /مدير المدرسة ووكيله/.test(D.asstip), D.asstip);
  }
  /* ⚠️ ولا فعلَ في نصِّ المنع: فاعلُه «الفريقُ» مذكَّرٌ في النسختين */
  A("ونصُّ منعِ الفريق بلا فعلٍ يُقلَب",
    !/تتابع|يتابع|تحذف/.test(D.intqanodel), D.intqanodel);

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
    ok = len(rows) >= 52
    if len(rows) < 52: print("  ⛔ عددُ الشواهد أقلُّ من المتوقَّع — فحصٌ لم يكتمل")
    # ⛔ **أرضيّةٌ تمنع المرورَ بالفراغ**: فرعُ «المشرفِ المعان» لا يوجد في
    #    نسخة البنين، فلو لم تمرَّ عليه نسخةُ البنات لم يُقَس القرارُ أصلاً.
    if lbl == "بنات" and not any(u"معانةٌ" in r[0] for r in rows):
        print("  ⛔ لم يُقَس فرعُ «المشرفِ المعان» — فحصٌ لم يقس شيئاً"); ok = False
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
