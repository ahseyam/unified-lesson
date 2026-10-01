# -*- coding: utf-8 -*-
"""⛔ مسحٌ للمنظومة كلِّها لا لشاشةٍ شُكي منها: لكلِّ دورٍ كلُّ مراحله وتبويباتها،
   في حالتين — **بلا بيانات** (أولُ ما يراه الداخل) و**ببيانات**. ويُفشِل:
     · شاشةً خاويةً (نصُّها أقلُّ من حدٍّ معقول)،
     · وشاشةً مسدودةً: لا زرَّ فيها ولا رابطَ ولا حقل — فالقارئُ لا يجد مخرجاً،
     · وشاشةً تسقط برسالة خطأ.
   وهذا هو الفحصُ الذي يُمسك «الصفحةُ لا تحوي شيئاً» قبل أن يراها المستشار."""
import html as H, json, os, re, subprocess, sys
import probedir as PRB   # نسخُ الفحص خارج شجرة التسليم
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BASE = "/Users/ahmadseyam/Desktop/نموذج تحضير الدرس - بطاقة الملاحظة الصفية/٨ - النموذج الرقمي (تجربة)/"
SRC = {"بنين": BASE + "منصة الحصة الموحَّدة — ابن خلدون.html",
       "بنات": BASE + "منصة الحصة الموحَّدة — ابن خلدون (بنات).html"}
MIN_CHARS = 260          # أقلُّ من ذلك شاشةٌ خاوية
MIN_ACTS  = 1            # زرٌّ أو رابطٌ أو حقلٌ واحدٌ على الأقل

BOOT = r"""
<script>
setTimeout(function(){
 var R=[];
 try{
  localStorage.clear(); load();
  var SEC=D.sectors[0], CX=D.complexlist[0];
  var bands=(D.bands[CX]||[]), wk=D.weeks[0], day=D.days[0];
  var gp=((D.rot[CX]||{})[wk]||{})[day]||Object.keys(D.pairs)[0];
  var sp=(D.pairs[gp]||D.specs)[0];
  /* مرحلةٌ لها مشرفُها — فالحالةُ العامّةُ لا حالةُ الفجوة */
  var b=bands.filter(function(x){return supsForCell(SEC,CX,x.stage,sp).length>0;})[0]||bands[0];
  var SUP=(D.sups||[]).filter(function(r){return !r.allsubj && r.subjects.length===1;})[0];

  function seed(){
    var L={id:"w1", sector:SEC, complex:CX, stage:b.stage, school:b.stage, period:b.per,
      week:wk, day:day, spec:sp, teacher:"معلمُ المسح", teacherNo:"30888", klass:"١/أ",
      time:b.time, strategy:(D.bank[0]||{}).name, approach:D.approaches[0],
      peer1:"زائرُ المسح", peer1e:"30999", peer2:"", peer2e:"",
      ev1:"",ev2:"",ev3:"",ev4:""};
    L.gk=[L.sector,L.complex,L.stage,L.period,L.week,L.day,L.spec].join("|");
    DB.sched=[L];
    DB.prep["w1"]={__issued:"٣٠ سبتمبر", i_teacher:"معلمُ المسح", f_strat:L.strategy};
    save(); return L;
  }
  function me(role){
    var m={role:role, name:(role==="teacher"?"معلمُ المسح":
            role==="peer"?"زائرُ المسح":"مستخدمُ المسح"), emp:"30888", spec:sp};
    if(role==="supervisor" && SUP){ m.name=SUP.name; m.emp=SUP.emp; }
    if(role==="principal"||role==="deputy"||role==="admin"){
      m.sector=SEC; m.complex=CX; m.school=b.stage; }
    if(role==="cxmgr"){ m.sector=SEC; m.complex=CX; }
    if(role==="peer"){ m.emp="30999"; }
    return m;
  }
  function look(role, ph, tab, state){
    ME=me(role); localStorage.setItem(KEY+"_me", JSON.stringify(ME));
    try{ localStorage.removeItem(KEY+"_ctx"); }catch(e){}
    GS=null; PH=ph; CUR=(state==="ببيانات") ? "w1" : null;
    if(["pending","active","ind","teacher","school","spec","strat","appr"].indexOf(tab)>=0) RPT=tab;
    var err="";
    try{
      shell();
      if(tab && ["fill","assign","log","visits","sup","school"].indexOf(tab)>=0){ setctx("tab",tab); shell(); }
    }catch(e){ err=e.message; }
    var main=document.querySelector("main")||document.body;
    var txt=(main.innerText||"").replace(/\s+/g," ").trim();
    var acts=main.querySelectorAll("button,a[href],input,select,textarea").length;
    R.push([role+" · "+ph+(tab?"/"+tab:"")+" · "+state, txt.length, acts, err, txt.slice(0,90)]);
  }
  /* ⚠️ تبويباتُ التقارير للقيادة وحدَها: المعلمُ والزائرُ لهما تقريرُهما
     الخاصُّ لا تبويبات — فلو سُئلا عنها تكرّرت الشاشةُ ستَّ مرّاتٍ بلا فائدة. */
  var TABS={1:["fill","visits","sup","assign","school"], 5:["school","teacher","spec","ind","active","pending"]};
  var OWNRPT={teacher:1, peer:1};
  ["teacher","peer","principal","deputy","supervisor","cxmgr","intqa","admin"].forEach(function(role){
    ME=me(role);
    var items;
    try{ items=navItems(); }catch(e){ items=[]; }
    items.forEach(function(it){
      var tabs=(it.id===5 && OWNRPT[role]) ? [null] : (TABS[it.id]||[null]);
      tabs.forEach(function(tb){
        ["بلا بيانات","ببيانات"].forEach(function(st){
          if(st==="ببيانات") seed(); else { DB.sched=[]; DB.prep={}; save(); }
          look(role, it.id, tb, st);
        });
      });
    });
  });
  localStorage.clear();
  document.title="DONE"; window.__OUT=JSON.stringify(R);
 }catch(e){ document.title="ERR|"+e.message; window.__OUT=JSON.stringify(R); }
}, 500);
</script>
<script>setTimeout(function(){var d=document.createElement("pre");d.id="dump";
 d.textContent=window.__OUT||"";document.body.appendChild(d);},12000);</script>
"""

allok = True
for lbl, src in SRC.items():
    p = PRB.probe("sweep_probe.html")
    open(p, "w", encoding="utf-8").write(open(src, encoding="utf-8").read() + BOOT)
    out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                          "--virtual-time-budget=40000", "--dump-dom", "file://" + p],
                         capture_output=True, text=True).stdout
    m = re.search(r'<pre id="dump">(.*?)</pre>', out, re.S)
    t = re.search(r"<title>(.*?)</title>", out, re.S)
    rows = json.loads(H.unescape(m.group(1))) if (m and m.group(1).strip()) else []
    bad = [r for r in rows if r[3] or r[1] < MIN_CHARS or r[2] < MIN_ACTS]
    print("\n── %s ── %d شاشةً مُسحت · %d معيبة" % (lbl, len(rows), len(bad)))
    if not rows:
        print("  ⛔ لم يُقَس شيء — عمًى لا نجاح"); allok = False
    for r in bad:
        why = ("سقطت: " + r[3]) if r[3] else ("خاوية: %d حرفاً" % r[1] if r[1] < MIN_CHARS
               else "مسدودة: لا زرَّ ولا حقل")
        print("  ⛔ %-42s %s\n       «%s»" % (r[0], why, r[4]))
    if t and H.unescape(t.group(1)).startswith("ERR"):
        print("  ⛔", H.unescape(t.group(1))); allok = False
    allok &= (len(bad) == 0 and len(rows) > 0)
    os.remove(p)
print("\n%s" % ("✓ لا شاشةَ خاويةً ولا مسدودةً ولا ساقطة" if allok else "⛔ في المنظومة شاشاتٌ لا تُسلَّم"))
sys.exit(0 if allok else 1)
