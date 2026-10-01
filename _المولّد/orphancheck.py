# -*- coding: utf-8 -*-
"""⛔ يُجرَّب الكاشفُ على مخرَجٍ نعلم عيبه: تُزرع حصةٌ بتخصص «تحفيظ» (وقد حُذف)،
   فإن لم يصرخ التقريرُ بها فهي ضائعةٌ صامتة. ثم تُنزع فيُشترط سكوتُه."""
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
 function body(){ var e=document.getElementById("rptbody"); return e?e.textContent:""; }
 function open_(){ ME={role:"admin",name:"أ. المستشار",emp:"",spec:""};
   localStorage.setItem(KEY+"_me", JSON.stringify(ME));
   GS=null; PH=5; RPT="pending"; shell(); }
 try{
  localStorage.clear(); load();
  R.push(["«تحفيظ» ليس في تخصصات المنصة", (D.specs||[]).indexOf("تحفيظ") < 0,
          (D.specs||[]).join("·")]);
  R.push(["ولا في مجموعات الدوران", JSON.stringify(D.pairs).indexOf("تحفيظ") < 0]);

  /* ① نظيفٌ: لا صرخة */
  DB.sched = []; save(); open_();
  R.push(["بلا حصةٍ يتيمةٍ: لا تحذير", body().indexOf("تخصصٍ لم يبقَ") < 0]);

  /* ② مزروعٌ بعيبٍ نعلمه: لا بدَّ أن يصرخ */
  var CX=D.complexlist[0], b=(D.bands[CX]||[])[0], w=D.weeks[0], dy=D.days[0];
  DB.sched = [{id:"orph1",
    gk:[D.sectors[0],CX,b.stage,b.per,w,dy,"تحفيظ"].join("|"),
    sector:D.sectors[0], complex:CX, stage:b.stage, school:b.stage,
    period:b.per, week:w, day:dy, spec:"تحفيظ",
    teacher:"أ. المزروع", teacherNo:"30888", klass:"١/أ"}];
  save(); open_();
  var t = body();
  R.push(["الحصةُ بتخصصٍ ملغى صُرخ بها", t.indexOf("تخصصٍ لم يبقَ") >= 0]);
  R.push(["وباسم معلمها", t.indexOf("أ. المزروع") >= 0]);
  R.push(["وباسم التخصص الملغى", t.indexOf("تحفيظ") >= 0]);
  R.push(["وبموضعها في الجدول", t.indexOf(w) >= 0 && t.indexOf(CX) >= 0]);

  /* ③ ولا تظهر في الجدول نفسِه — فالصرخةُ هي سبيلُها الوحيد */
  PH=1; setctx("tab","fill"); setctx("sector",D.sectors[0]); setctx("complex",CX);
  shell();
  /* ⛔ ادّعاءٌ صحَّحه الفحص: قائمةُ حصص المجمع تُرشِّح بالمجمع لا بالتخصص،
     فاليتيمةُ ظاهرةٌ فيها — وذاك صوابٌ لا عطل: به تُفتح فتُصلَح. */
  var heads=[].map.call(document.querySelectorAll("table th"), function(x){ return x.textContent; });
  R.push(["لا عمودَ «تحفيظ» في مصفوفة الجدولة", heads.indexOf("تحفيظ") < 0]);
  R.push(["وتبقى في قائمة حصص المجمع فتُصلَح",
          document.body.textContent.indexOf("أ. المزروع") >= 0]);

  /* ④ وبالإنجليزية تُصرخ كذلك */
  LANG="en"; try{ localStorage.setItem(KEY+"_lang","en"); }catch(e){}
  open_(); var te = body();
  R.push(["وبالإنجليزية أيضاً", te.indexOf("no longer on the platform") >= 0]);
  /* ⛔ وادّعاءٌ ثانٍ صحَّحه الفحص: صفوفُ الجدول قيمٌ مخزونةٌ عربيةٌ بحكم بنية
     المنصة فلا تُترجَم — فيُقاس التحذيرُ والترويسُ وحدَهما. */
  var mb = document.querySelector("#rptbody .msg.bad"), mt = mb ? mb.textContent : "";
  R.push(["ونصُّ التحذير بلا حرفٍ عربيّ", !!mt && !/[ء-ي]/.test(mt), mt.slice(0,70)]);
  var hd = [].map.call(document.querySelectorAll("#rptbody th"), function(x){ return x.textContent; });
  R.push(["وترويسُ جدوله مترجَمة", hd.length > 0 &&
          !hd.some(function(x){ return /[ء-ي]/.test(x); }), hd.join("·")]);

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
    p = PRB.probe("orph_probe.html")
    open(p, "w", encoding="utf-8").write(open(src, encoding="utf-8").read() + BOOT)
    out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                          "--virtual-time-budget=20000", "--dump-dom", "file://" + p],
                         capture_output=True, text=True).stdout
    m = re.search(r'<pre id="dump">(.*?)</pre>', out, re.S)
    t = re.search(r"<title>(.*?)</title>", out, re.S)
    rows = json.loads(H.unescape(m.group(1))) if (m and m.group(1).strip()) else []
    print("\n── %s ──" % lbl)
    ok = bool(rows)
    for r in rows:
        g = bool(r[1]); ok &= g
        print("  %s %s%s" % ("✓" if g else "⛔", r[0],
              ("   [" + str(r[2]) + "]") if len(r) > 2 and not g else ""))
    if t and H.unescape(t.group(1)).startswith("ERR"):
        print("  ⛔", H.unescape(t.group(1))); ok = False
    if not rows: print("  ⛔ لم يُقَس شيء — وهذا عمًى لا نجاح")
    allok &= ok
    os.remove(p)
print("\n%s" % ("✓ الكاشفُ يصرخ بالمزروع ويسكت عن النظيف" if allok else "⛔ الكاشفُ لا يُعتمد"))
sys.exit(0 if allok else 1)
