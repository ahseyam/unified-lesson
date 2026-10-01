# -*- coding: utf-8 -*-
"""⛔ أربعةُ تغييراتٍ تُقاس في متصفّحٍ لا تُصدَّق من الشفرة:
   ١. الإستراتيجيةُ مقيَّدةٌ باتجاهها، ومقفولةٌ قبل اختياره.
   ٢. الجدولُ لا يُعدَّل إلا من المعلم القائم بالحصة (والمستشار).
   ٣. الرصدُ والاعتمادُ للمشرف وحدَه؛ والمديرُ يطّلع ويعلّق.
   ٤. مرشَّحو الزيارة: من التخصص أو القريب، وبلا تعارضٍ في الوقت."""
import html as H, json, os, re, subprocess, sys
import probedir as PRB   # نسخُ الفحص خارج شجرة التسليم
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRC="/Users/ahmadseyam/Desktop/نموذج تحضير الدرس - بطاقة الملاحظة الصفية/٨ - النموذج الرقمي (تجربة)/منصة الحصة الموحَّدة — ابن خلدون.html"
BOOT = r"""
<script>
setTimeout(function(){
 var R = [];
 function T(n, g, w){ R.push([(String(g)===String(w)?"✓ ":"⛔ ")+n,
    String(g)===String(w) ? "" : ("وجد "+g+" · المنتظَر "+w)]); }
 try{
  localStorage.clear();
  var SEC=D.sectors[0], CX=D.complexlist[0], bands=D.bands[CX]||[], b=bands[0];
  var wk=D.weeks[0], day=D.days[0];
  /* ⛔ **الكشفُ لم يعد في الصفحة** (نُزع ١ أكتوبر ٢٠٢٦: كان أربعُمئةٍ وستون
     اسماً ورقماً وظيفياً يقرأها كلُّ من يفتح المصدر). فكان هذا الفحصُ يقرأ
     كشفاً خالياً فيسقط بـTypeError **ويَخرج صفراً مُعلناً النجاح** — ولولا
     أرضيّةُ الشواهد لمرّ. فيُزرع كشفٌ مُختبَريٌّ بأسماءٍ ليست لأحد. */
  var _sub = Object.keys(D.specmap||{}).find(function(k){ return (D.specmap||{})[k]; });
  D.roster = {"90001": {n:"معلمُ الفحص الأول", s:_sub, c:CX, g:b.stage, k:SEC},
              "90002": {n:"معلمُ الفحص الثاني", s:_sub, c:CX, g:b.stage, k:SEC},
              "90003": {n:"معلمُ الفحص الثالث", s:_sub, c:CX, g:b.stage, k:SEC}};
  var ids=Object.keys(D.roster);
  /* معلمٌ ومادتُه */
  var meK = ids.find(function(k){ return (D.specmap||{})[D.roster[k].s]; });
  if(!meK) throw new Error("لا مادةَ في specmap — تعذّر زرعُ الكشف");
  var meSp = (D.specmap||{})[D.roster[meK].s];
  var L={id:"r1", gk:[SEC,CX,b.stage,b.per,wk,day,meSp].join("|"),
    sector:SEC,complex:CX,stage:b.stage,school:b.stage,week:wk,day:day,
    period:b.per.replace(/\D/g,""),time:b.time,teacher:D.roster[meK].n,teacherNo:meK,
    subject:meSp,spec:meSp,klass:"5/A",strategy:"",approach:"",
    peer1:"",peer2:"",peer1e:"",peer2e:"",ev1:"",ev2:"",ev3:""};
  DB.sched.push(L); save();

  /* ── ١) الربطُ ── */
  var AS = D.appstrat || {};
  T("لكل اتجاهٍ إستراتيجياتُه", Object.keys(AS).length, D.approaches.length);
  var all = []; Object.keys(AS).forEach(function(k){ all = all.concat(AS[k]); });
  T("كلُّ إستراتيجيةٍ لها اتجاه",
    D.bank.filter(function(x){ return all.indexOf(x.name) < 0; }).length, 0);
  var a0 = D.approaches[0];
  T("قائمةُ «"+a0+"» أقصرُ من ١٩", AS[a0].length < 19, true);

  /* ── ٢) صلاحيةُ الجدول ── */
  var ctx = {stages:[], complex:CX, sector:SEC};
  function editable(role){
    ME = {role:role, name:D.roster[meK].n, emp:meK, spec:meSp,
          sector:SEC, complex:CX, school:b.stage};
    return canEdit(ctx, b, L);
  }
  T("المعلمُ صاحبُ الحصة يعدّل", editable("teacher"), true);
  T("المشرفُ لا يعدّل", editable("supervisor"), false);
  T("المديرُ لا يعدّل", editable("principal"), false);
  T("الوكيلُ لا يعدّل", editable("deputy"), false);
  T("الزائرُ لا يعدّل", editable("peer"), false);
  T("المستشارُ يعدّل (طريقُ إصلاح)", editable("admin"), true);
  /* معلمٌ آخرُ لا يملك خانةَ غيره */
  ME = {role:"teacher", name:"معلمٌ آخر", emp:ids.find(function(k){return k!==meK;}), spec:meSp};
  T("معلمٌ آخرُ لا يعدّل خانةَ غيره", canEdit(ctx, b, L), false);

  /* ── ٣) من يرصد ويعتمد ── */
  /* ⛔ الرصدُ صار مربوطاً بسجلّ الإشراف: المشرفُ يرصد **حصةَ مادته** برقمه،
     لا كلَّ حصة. والحالاتُ المفصَّلةُ في `supcheck.py`؛ وهنا الأصلُ وحدَه.
     و`myEvalSlot` حُذفت لأنها لم تكن تُنادى — والصفةُ تُشتقّ في evalForms. */
  var _sup = (D.sups||[]).filter(function(r){
      return supCovers(r, L.sector, L.complex, L.stage, L.spec); })[0];
  T("لحصة التجربة مشرفُها في السجلّ", !!_sup, true);
  ME={role:"supervisor",name:_sup?_sup.name:"x",emp:_sup?_sup.emp:""};
  T("المشرفُ يرصد حصةَ مادته", canScore(L), true);
  ME={role:"supervisor",name:"x",emp:"00000"};
  T("ومن ليس في السجلّ لا يرصد", canScore(L), false);
  ME={role:"principal",name:"x",emp:"",sector:L.sector,complex:L.complex,school:L.stage};
  T("المديرُ لا يرصد حصةً لها مشرفُها", canScore(L), false);
  ME={role:"deputy",name:"x",emp:"",sector:L.sector,complex:L.complex,school:L.stage};
  T("والوكيلُ كذلك", canScore(L), false);
  ME={role:"teacher",name:"x",emp:""}; T("والمعلمُ لا يرصد", canScore(L), false);

  /* ── ٤) مرشَّحو الزيارة ── */
  /* معلمٌ من التخصص نفسِه وعنده حصةٌ في الوقت نفسِه */
  var busyK = ids.find(function(k){
    return k!==meK && ((D.specmap||{})[D.roster[k].s] === meSp); });
  DB.sched.push({id:"r2", gk:[SEC,CX,b.stage,b.per,wk,day,meSp].join("|")+"#2",
    sector:SEC,complex:CX,stage:b.stage,school:b.stage,week:wk,day:day,
    period:b.per.replace(/\D/g,""),time:b.time,teacher:D.roster[busyK].n,
    teacherNo:busyK,subject:meSp,spec:meSp,klass:"6/B",
    peer1:"",peer2:"",peer1e:"",peer2e:"",ev1:"",ev2:"",ev3:""});
  save();
  ME={role:"deputy",name:"وكيل",emp:"",sector:SEC,complex:CX,school:b.stage};
  GS=null; PH=1; shell(); setctx("tab","assign"); shell();
  var txt = (document.body.innerText||"").replace(/\s+/g," ");
  T("شاشةُ الإسناد ظهرت", txt.indexOf("إسناد المعلمين الزائرين")>=0, true);
  T("تعرض عددَ المرشَّحين المتفرِّغين", /مرشَّحاً متفرِّغاً/.test(txt), true);
  /* ⚠️ الشاهدُ في **قائمة المرشَّحين** لا في نصِّ الصفحة: المشغولُ يظهر
     بصفته معلمَ حصةٍ أخرى في الجدول — وذاك صواب. */
  var opts = [];
  [].slice.call(document.querySelectorAll("select.cin")).forEach(function(s2){
    [].slice.call(s2.options).forEach(function(o2){ opts.push(o2.text); });
  });
  T("قوائمُ المرشَّحين معروضة", opts.length > 0, true);
  T("⛔ لا يُعرض المشغولُ مرشَّحاً",
    opts.filter(function(x){ return x.indexOf("(" + busyK + ")") >= 0; }).length, 0);
  T("ويُعرض متفرِّغٌ من تخصصه",
    opts.filter(function(x){ return x.indexOf(" — " + meSp + " (") >= 0; }).length > 0, true);

  /* ── ٥) اسمُ المعلم: فرقُ مسافةٍ أو تشكيلٍ لا يقتل صفحتَه ──
     ⛔ بعد نزع الكشف صار الاسمُ يُكتب مرتين (الجدولُ والدخول)، وكان التطابقُ
        حرفياً تامّاً — فمسافةٌ لاحقةٌ تُقفل الصفحةَ كلَّها بلا كلمةٍ تُقال:
        لا لوحةَ ذكاءٍ ولا خانةً تُكتب. (شكا منه المستشارُ ١ أكتوبر ٢٠٢٦) */
  var MT = D.roster[meK].n;
  ME = {role:"teacher", name:MT, emp:"", spec:meSp, sector:SEC, complex:CX, stages:[b.stage]};
  var LN = {id:"nm1", teacher:MT, teacherNo:""};
  T("الاسمُ نفسُه حصتُه", isMine(LN), true);
  LN.teacher = MT + " ";
  T("ومسافةٌ لاحقةٌ لا تسلبها", isMine(LN), true);
  LN.teacher = " " + MT.replace(/َ|ُ|ِ/g, "") ;
  T("ولا تشكيلٌ ولا مسافةٌ سابقة", isMine(LN), true);
  LN.teacher = MT.replace(/ا/, "أ");
  T("ولا همزةُ ألفٍ مختلفة", isMine(LN), true);
  LN.teacher = "معلمٌ آخرُ تماماً";
  T("واسمٌ آخرُ ليست حصتَه", isMine(LN), false);
  T("ويُقال السببُ نصّاً", (notMineWhy(LN) || "").indexOf("مسجَّلةٌ باسم") >= 0, true);
  LN.teacher = ""; LN.teacherNo = "";
  T("وخانةٌ فارغةٌ يُقال فيها ذلك",
    (notMineWhy(LN) || "").indexOf("فارغة") >= 0, true);
  ME.emp = "11111"; LN.teacher = MT; LN.teacherNo = "22222";
  T("والرقمُ يغلب الاسمَ عند اختلافه", isMine(LN), false);
  T("ويُقال بالرقمين", (notMineWhy(LN) || "").indexOf("الرقم") >= 0, true);

  /* ── ٦) خليةُ الحصة: لا تكرارَ ولا أرقامَ تُقلب ──
     ⛔ «الحصة الحصة 1» — لأن `L.period` نصُّه «الحصة 1» لا «1». عولج في
        الرأس ٣٠ سبتمبر **في موضعه وحدَه**، وبقي في خانة التحضير وجدول
        الزيارات. و«الأحد · ٤ أكتوبر» تُقرأ «الأحد ٤٠ أكتوبر» لأن النقطةَ
        محايدةُ الاتجاه. (شكا منهما المستشارُ بلقطةٍ ١ أكتوبر ٢٠٢٦) */
  var cc = D.cal[0], ddx = cc.days[D.days[0]] || {};
  var LC = {id:"c9", sector:SEC, complex:CX, stage:b.stage, school:b.stage,
            week:cc.w, day:D.days[0], period:b.per, time:b.time,
            datetxt:ddx.gt, hijri:ddx.ht, teacher:"فاحص", spec:meSp};
  var PC = {}; inject(LC, PC);
  T("خانةُ «الحصة» بلا تكرار", (PC.i_period.match(/الحصة/g)||[]).length, 1);
  T("ورقمُها عربيٌّ لا لاتيني", /[0-9]/.test(PC.i_period), false);
  T("ومعها زمنُها", PC.i_period.indexOf(b.time) >= 0, true);
  T("والتاريخُ محميٌّ بعلامة الاتجاه", PC.i_date.indexOf("‏") >= 0, true);
  T("ولا «الحصة الحصة» في الرأس", lessonSub(LC).indexOf("الحصة الحصة") < 0, true);
  /* ── ٧) الأرقامُ الهنديةُ تُقرأ كاللاتينية ──
     ⛔ كان `replace(/\D/g,"")` يمحو «٢٨٣٣٣» عن آخرها فلا يدخل صاحبُها. */
  T("٢٨٣٣٣ تُقرأ رقماً", latnum("٢٨٣٣٣"), "28333");
  T("والفارسيةُ ۲۸۳۳۳ كذلك", latnum("۲۸۳۳۳"), "28333");
  T("ومختلطةٌ تُوحَّد", latnum("٢8٣3٣"), "28333");
  var sup0 = (D.sups || [])[0];
  if(sup0){
    var arEmp = String(sup0.emp).replace(/[0-9]/g, function(c){
      return String.fromCharCode(0x0660 + (+c)); });
    T("ومشرفٌ يدخل برقمه الهندي", !!supByEmp(arEmp), true);
    T("ولا يُردُّ بخطأ", empError(arEmp, "supervisor"), "");
  }

  /* ── ٨) بوّابةُ الدخول تُفتح بلوحة المفاتيح وقارئِ الشاشة ──
     ⛔ كانت البطاقاتُ `div` بمستمعِ نقرٍ وحدَه: لا تُركَّز بـTab، ولا تُفتح
        بالمسافة، ولا يعلم قارئُ الشاشة أنها خيار — فمن لا يستعمل الفأرةَ
        **لا يدخل المنصةَ أصلاً**. (أمسكه وكيلُ الوصول ١ أكتوبر ٢٠٢٦) */
  ME = null; login();
  var kcards = [].slice.call(document.querySelectorAll("div.role"));
  T("بطاقاتُ الأدوار كلُّها", kcards.length, D.roles.length);
  T("وكلُّها تُركَّز بـTab",
    kcards.filter(function(c){ return c.tabIndex === 0; }).length, kcards.length);
  T("ولكلٍّ دورُ اختيارٍ معلَن",
    kcards.filter(function(c){ return c.getAttribute("role") === "radio"; }).length, kcards.length);
  T("ولكلٍّ تسميةٌ تُنطق",
    kcards.filter(function(c){ return (c.getAttribute("aria-label") || "").length > 10; }).length,
    kcards.length);
  T("والمجموعةُ معرَّفةٌ لقارئ الشاشة",
    document.querySelector(".roles").getAttribute("role"), "radiogroup");
  kcards[0].focus();
  T("والتركيزُ يقع عليها", document.activeElement === kcards[0], true);
  kcards[0].dispatchEvent(new KeyboardEvent("keydown", {key:" ", bubbles:true, cancelable:true}));
  T("والمسافةُ تختار", kcards[0].classList.contains("on"), true);
  T("ويُعلَن الاختيار", kcards[0].getAttribute("aria-checked"), "true");
  kcards[0].dispatchEvent(new KeyboardEvent("keydown", {key:"ArrowDown", bubbles:true, cancelable:true}));
  T("والسهمُ ينتقل", document.activeElement === kcards[1], true);
  kcards[1].dispatchEvent(new KeyboardEvent("keydown", {key:"Enter", bubbles:true, cancelable:true}));
  T("وEnter تختار", kcards[1].classList.contains("on"), true);
  T("ولا يبقى الأولُ مختاراً", kcards[0].getAttribute("aria-checked"), "false");

  /* ── ٩) نطاقُ الوكيل: الحذفُ والتقريرُ وما يقع عليه ──
     ⛔ كان الوكيلُ يحذف حصصَ المجمع كلِّه — ومنها **المعتمدةُ المقفولةُ
        لمدرسةٍ أخرى** — ويمحو من السلّة محواً نهائياً بلا رجعة. والقاعدةُ
        محروسةٌ في التعديل ومكشوفةٌ في الحذف.
     ⚠️ وتُعطَّل النوافذُ الأصليةُ هنا: `alert` توقف كروم بلا رأسٍ فلا يُقاس شيء. */
  var _al = window.alert, _cf = window.confirm;
  window.alert = function(){}; window.confirm = function(){ return true; };
  var CXB2 = D.complexlist[1] || CX, bB2 = (D.bands[CXB2] || [])[0] || b;
  function _mkL(id, cx, bb){
    return {id:id, gk:[SEC, cx, bb.stage, bb.per, wk, day, meSp].join("|"),
            sector:SEC, complex:cx, stage:bb.stage, school:bb.stage, week:wk, day:day,
            period:bb.per, time:bb.time, teacher:"ف", teacherNo:"", subject:meSp,
            spec:meSp, klass:"5/A"};
  }
  var Lmine = _mkL("dp1", CX, b), Lother = _mkL("dp2", CXB2, bB2);
  var Lappr = _mkL("dp3", CX, b); Lappr.approved = {by:"س", at:"2026-10-01"};
  DB.sched = [Lmine, Lother, Lappr]; save();
  ME = {role:"deputy", name:"وكيلُ الفحص", emp:"", spec:meSp,
        sector:SEC, complex:CX, school:b.stage, stages:[b.stage]};
  T("الوكيلُ يحذف حصةَ مدرسته", canDrop(Lmine), true);
  T("ولا يحذف حصةَ مدرسةٍ أخرى", canDrop(Lother), false);
  T("ويُقال له السبب", (dropWhy(Lother)||"").indexOf("نطاقك") >= 0, true);
  T("ولا يحذف معتمدةً مقفولة", canDrop(Lappr), false);
  T("ويُقال سببُ القفل", (dropWhy(Lappr)||"").indexOf("معتمدة") >= 0, true);
  var _n0 = DB.sched.length;
  dropLesson(Lother.id);
  T("والنداءُ المباشرُ لا يمرّ", DB.sched.length, _n0);
  /* وما يقع عليه يُعرَّف */
  T("isMyGap تعمل", typeof isMyGap, "function");
  T("وعدّادُ ما عليه رقم", typeof myGapCount(), "number");
  /* وتقريرُ الإدخال على نطاقه */
  D.roster = {"90001": {n:"معلمُ مدرستي", s:_sub, c:CX, g:b.stage.split("- ")[0], k:SEC},
              "90002": {n:"معلمُ مدرسةٍ أخرى", s:_sub, c:CXB2, g:bB2.stage.split("- ")[0], k:SEC},
              "90003": {n:"إداريٌّ لا يُدرّس", s:"أخرى", c:CX, g:b.stage.split("- ")[0], k:SEC}};
  var _pe = pendingEntry();
  T("الكشفُ يُرشَّح بنطاق الداخل", _pe.total, 1);
  T("والنطاقُ يُعلَن في التقرير", (_pe.scope||"").length > 0, true);
  T("ولا يُعدُّ من لا تخصصَ تعليميَّ له",
    _pe.left.filter(function(x){ return x[0].indexOf("إداريّ") >= 0; }).length, 0);
  window.alert = _al; window.confirm = _cf;

  document.title="DONE"; window.__OUT = JSON.stringify(R);
 }catch(e){ document.title="ERR|"+e.message+" @ "+(e.stack||"").split("\n")[1];
            window.__OUT = JSON.stringify(R); }
}, 350);
</script>
<script>setTimeout(function(){var d=document.createElement("pre");d.id="dump";
 d.textContent=window.__OUT||"";document.body.appendChild(d);},1600);</script>
"""
p = PRB.probe("roles_probe.html")
open(p,"w",encoding="utf-8").write(open(SRC,encoding="utf-8").read()+BOOT)
out = subprocess.run([CHROME,"--headless=new","--disable-gpu","--no-sandbox",
     "--virtual-time-budget=12000","--dump-dom","file://"+p],capture_output=True,text=True).stdout
t = re.search(r"<title>(.*?)</title>", out, re.S)
m = re.search(r'<pre id="dump">(.*?)</pre>', out, re.S)
rows = json.loads(H.unescape(m.group(1))) if (m and m.group(1).strip()) else []
for line, extra in rows: print("  " + line + ("   [" + extra + "]" if extra else ""))
ttl = H.unescape(t.group(1)) if t else "?"
if ttl.startswith("ERR"): print("  ⛔ " + ttl)
bad = [1 for l,_ in rows if l.startswith("⛔")]
# ⛔ **فحصٌ لم يَقِس شيئاً فاشلٌ لا ناجح.** كان الحارسُ يَخرج صفراً إن عاد
#    الصندوقُ خالياً — لا شاهدٌ ولا عنوانُ خطأ — فيُعلن «✓ الأربعةُ منفَّذة»
#    وقد لم يفحص واحداً. وأُثبت تجريبياً: أُفسد نصُّ الإقلاع فمرّ الحارس.
#    (أمسكه وكيلُ مراجعة الحرّاس ١ أكتوبر ٢٠٢٦)
FLOOR = 61
short = len(rows) < FLOOR
if short:
    print("  ⛔ %d شاهداً فقط — والأرضيّةُ %d. لم يُقَس ما يكفي، فالحكمُ فشل."
          % (len(rows), FLOOR))
print("\n  %s — %d/%d شاهداً"
      % ("✓ الأربعةُ منفَّذة" if not bad and not short and not ttl.startswith("ERR") else "⛔ فيها خلل",
         len(rows)-len(bad), len(rows)))
sys.exit(1 if (bad or short or ttl.startswith("ERR")) else 0)
