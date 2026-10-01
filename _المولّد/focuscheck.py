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

  /* ── منطقةُ الإعلان: الحفظُ والخطأُ كانا صامتَين على القارئ الآلي ──
     ⚠️ ويُقاس على العنصر المحقون في الصفحة لا على نصِّ الشفرة. */
  R.push(["لا منطقةَ إعلانٍ قبل أول رسالة", !document.getElementById("toast")]);
  toast("حُفظ للجميع ✓", "ok");
  var tz = document.getElementById("toast");
  R.push(["نشأت منطقةُ الإعلان", !!tz]);
  if(tz){
    R.push(["وهي منطقةٌ حيّةٌ معلَنة", tz.getAttribute("role")==="status"
      && tz.getAttribute("aria-live")==="polite"
      && tz.getAttribute("aria-atomic")==="true",
      tz.getAttribute("role")+"|"+tz.getAttribute("aria-live")]);
    await wait(90);
    R.push(["ونصُّ النتيجةِ وصل إليها", (tz.textContent||"").indexOf("حُفظ")>=0, tz.textContent]);
    /* ⛔ منطقةٌ مخفيّةٌ بـdisplay:none لا يُعلنها قارئٌ — فتُقاس وهي ساكنة */
    tz.className = "toast ok";
    var cs = getComputedStyle(tz);
    R.push(["ولا تُخفى بـdisplay/visibility وهي ساكنة",
      cs.display !== "none" && cs.visibility !== "hidden", cs.display+"|"+cs.visibility]);
    toast("تعذَّر الإرسال", "warn");
    R.push(["والنتيجةُ الرادعةُ تُعلَن حازمة", tz.getAttribute("aria-live")==="assertive",
      tz.getAttribute("aria-live")]);
    toast("يُحفظ…", "wait");
    R.push(["ورسالةُ الطريقِ مؤدَّبةٌ لا تقطع", tz.getAttribute("aria-live")==="polite",
      tz.getAttribute("aria-live")]);
    await wait(90);
    toast("حُفظ للجميع ✓", "ok"); await wait(90);
    var once = tz.textContent;
    tz.__probe = 1;
    toast("حُفظ للجميع ✓", "ok");
    R.push(["ونصٌّ مكرَّرٌ يُفرَّغ ثم يُعاد فيُعلَن", tz.textContent === "", "«"+tz.textContent+"»"]);
    await wait(90);
    R.push(["ثم يعود", tz.textContent === once, tz.textContent]);
  }

  /* ── النافذةُ الموحَّدةُ تُشير إلى نصِّها ── */
  var btn = document.createElement("button"); btn.id="pv"; document.body.appendChild(btn); btn.focus();
  uiDialog("رسالةُ تجربةٍ للقارئ", "bad");
  var bx = document.querySelector("#udlg .udlgbox");
  R.push(["نافذةٌ موحَّدةٌ مفتوحة", !!bx]);
  if(bx){
    var dsc = bx.getAttribute("aria-describedby");
    var tgt = dsc && document.getElementById(dsc);
    R.push(["تُشير إلى نصِّها بـaria-describedby", !!tgt, dsc]);
    R.push(["والنصُّ المُشارُ إليه غيرُ فارغ",
      !!tgt && (tgt.textContent||"").indexOf("رسالةُ تجربة")>=0, tgt && tgt.textContent]);
    R.push(["وهي حاجزةٌ معلَنة", bx.getAttribute("role")==="alertdialog"
      && bx.getAttribute("aria-modal")==="true"]);
    document.getElementById("udlg").dispatchEvent(
      new KeyboardEvent("keydown",{key:"Escape",bubbles:true}));
    await wait(60);
    R.push(["وEscape يُغلقها", !document.getElementById("udlg")]);
    R.push(["ويعود التركيزُ إلى موضعه", document.activeElement === btn,
      document.activeElement && document.activeElement.id]);
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
# ⛔ أرضيّةُ شواهد: فحصٌ لم يقس شيئاً فاشلٌ لا ناجح
FLOOR = 17
if len(rows) < FLOOR:
    print("  ⛔ %d شاهداً فقط — والأرضيّةُ %d" % (len(rows), FLOOR)); ok = False
print("\n  %s" % ("✓ الكتابةُ متّصلةٌ والإعلانُ مسموع" if ok and rows else "⛔ ما زال يخرج"))
sys.exit(0 if (ok and rows) else 1)
