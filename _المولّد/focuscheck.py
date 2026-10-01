# -*- coding: utf-8 -*-
"""⛔ يُكتب اسمٌ حرفاً حرفاً كما يفعل المستخدم، ويُسأل بعد كل حرف:
   أما زال المؤشّرُ في الصندوق؟ وأما زال ما كُتب كاملاً؟"""
import html as H, json, os, re, subprocess, sys
import probedir as PRB   # نسخُ الفحص خارج شجرة التسليم
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRC="/Users/ahmadseyam/Desktop/نموذج تحضير الدرس - بطاقة الملاحظة الصفية/٨ - النموذج الرقمي (تجربة)/منصة الحصة الموحَّدة — ابن خلدون.html"
BOOT = r"""
<script>
function wait(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
setTimeout(async function(){
 var R=[];
 try{
  localStorage.clear();
  var SEC=D.sectors[0], CX=D.complexlist[0], b=(D.bands[CX]||[])[0];
  ME={role:"teacher",name:"أ. نموذج",emp:"",spec:D.specs[0]};
  localStorage.setItem(KEY+"_me", JSON.stringify(ME));
  GS=null; PH=1; shell(); setctx("tab","fill"); shell();
  var box=document.querySelector('[data-refocus="q"]');
  R.push(["صندوقُ البحث موجود", !!box]);
  if(box){
    box.focus();
    var word="أحمد صيام", lost=0, wrong=0;
    for(var i=0;i<word.length;i++){
      box = document.querySelector('[data-refocus="q"]');
      if(!box){ lost++; break; }
      box.focus();
      box.value = word.slice(0, i+1);
      box.dispatchEvent(new Event("input", {bubbles:true}));
      await wait(320);                       /* أطولُ من التأخير */
      var now = document.querySelector('[data-refocus="q"]');
      if(!now || document.activeElement !== now) lost++;
      if(!now || now.value !== word.slice(0, i+1)) wrong++;
    }
    R.push(["المؤشّرُ لم يخرج مع أي حرف", lost === 0, "خرج " + lost + " مرّة"]);
    R.push(["والنصُّ كاملٌ بعد كل حرف", wrong === 0, "اختلّ " + wrong + " مرّة"]);
    var fin = document.querySelector('[data-refocus="q"]');
    R.push(["النصُّ النهائيُّ صحيح", fin && fin.value === word, fin ? fin.value : "—"]);
  }
  document.title="DONE"; window.__OUT=JSON.stringify(R);
 }catch(e){ document.title="ERR|"+e.message; window.__OUT=JSON.stringify(R); }
}, 400);
</script>
<script>setTimeout(function(){var d=document.createElement("pre");d.id="dump";
 d.textContent=window.__OUT||"";document.body.appendChild(d);},7000);</script>
"""
p=PRB.probe("focus_probe.html")
open(p,"w",encoding="utf-8").write(open(SRC,encoding="utf-8").read()+BOOT)
out=subprocess.run([CHROME,"--headless=new","--disable-gpu","--no-sandbox",
   "--virtual-time-budget=20000","--dump-dom","file://"+p],capture_output=True,text=True).stdout
m=re.search(r'<pre id="dump">(.*?)</pre>',out,re.S)
t=re.search(r"<title>(.*?)</title>",out,re.S)
rows=json.loads(H.unescape(m.group(1))) if (m and m.group(1).strip()) else []
ok=True
for r in rows:
    g=bool(r[1]); ok&=g
    print("  %s %s%s" % ("✓" if g else "⛔", r[0], ("   ["+str(r[2])+"]") if len(r)>2 and not g else ""))
if t and H.unescape(t.group(1)).startswith("ERR"):
    print("  ⛔", H.unescape(t.group(1))); ok=False
print("\n  %s" % ("✓ الكتابةُ متّصلة" if ok and rows else "⛔ ما زال يخرج"))
sys.exit(0 if (ok and rows) else 1)
