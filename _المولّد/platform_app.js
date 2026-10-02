const D = __DATA__, LOGO = "__LOGO__";
/* ⛔ مفاتيحُ التخزين المحلي تُنسَب إلى المدرسة. الحادثة (٢٩ سبتمبر ٢٠٢٦):
   منصتان على نطاقٍ واحد (ahseyam.github.io) بمسارين مختلفين — و`localStorage`
   يخصُّ **النطاق لا المسار**. فقرأت منصةُ مدرسةٍ بياناتِ الأخرى من الجهاز نفسِه،
   وظهر في سجلِّ عملياتها حذفُ حصةٍ في مجمعٍ لا يتبعها. وأخطرُ منه أن مفتاحَ
   عنوان الخادم مشتركٌ أيضاً: فربطُ خادمٍ في إحداهما يُحوّل الأخرى إليه.
   ⚠️ والافتراضُ يبقى «ik» لمن لا dbid له — فلا تضيع بياناتُ من يستعملها اليوم. */
const NS = (typeof D !== "undefined" && D.dbid) ? D.dbid : "ik";
const KEY = NS + "_platform_v1", API = NS + "_api_v1";
/* ⛔ **ومفتاحُ المخزن المشترك كان `db` في النسختين** — أي أن البنين والبنات
   يكتبون في سجلٍّ واحدٍ على الخادم ولو فُصلت مفاتيحُ الجهاز. فصلُ الجهاز
   وحدَه لا يفصل شيئاً ما بقي الخادمُ واحداً. (١ أكتوبر ٢٠٢٦) */
const SID = NS + "_db";
/* هجرةٌ تقع مرةً واحدة: ما كان تحت «ik» على الجهاز يُنقل إلى مفتاح المدرسة،
   ولا يُمَسُّ القديمُ (أماناً)، ولا يُعاد النقلُ بعد أول مرةٍ — وإلّا عاد
   المحذوفُ إلى الحياة. ⚠️ ولا تجري إلا لنسخة البنين: «ik» كان مخزنَها. */
(function migrateNS(){
  if(NS !== "ikm") return;
  try{
    if(localStorage.getItem(NS + "_moved_from_ik")) return;
    ["_platform_v1", "_api_v1", "_platform_v1_lang"].forEach(sfx=>{
      const old = localStorage.getItem("ik" + sfx);
      if(old !== null && localStorage.getItem(NS + sfx) === null)
        localStorage.setItem(NS + sfx, old);
    });
    localStorage.setItem(NS + "_moved_from_ik", "1");
  }catch(e){}
})();
const $ = s => document.querySelector(s);
/* ═════════ اللغة: عربيٌّ افتراضاً، والإنجليزيةُ طبقةُ عرضٍ ═════════
   ⛔ المخزنُ عربيٌّ إلى الأبد: مفتاحُ الحصة
      «القطاع|المجمع|المرحلة|الحصة|الأسبوع|اليوم|التخصص» قيمٌ عربية. فلو
      تُرجمت لانفصلت كلُّ حصةٍ عن سجلّها وصارت المنصةُ منصتين. فالترجمةُ
      عند **العرض** وحدَه، والقيمةُ المحفوظةُ لا تُمَسّ. (٣٠ سبتمبر ٢٠٢٦)
   ⚠️ والافتراضُ عربيٌّ لكل من يفتح، فلا يتغيّر شيءٌ على من يعمل اليوم. */
const LANGK = KEY + "_lang";
let LANG = (function(){ try{ return localStorage.getItem(LANGK) || "ar"; }catch(e){ return "ar"; } })();
const T_EN = (typeof I18N !== "undefined") ? I18N : {};
/* ⛔ الأرقامُ والتواريخُ ورموزُ المؤشرات **قاعدةٌ لا معجم**: لو أُدرجت في
   المعجم لاحتاجت تسعين مدخلاً لكل تقويمٍ جديد — وبقيت الساعاتُ والتواريخُ
   بالهندية في شاشةٍ إنجليزية عند أول تغييرٍ في التقويم. */
const AR_DIG = {"٠":"0","١":"1","٢":"2","٣":"3","٤":"4","٥":"5","٦":"6","٧":"7","٨":"8","٩":"9"};
const AR_MONTH = {
  "يناير":"January","فبراير":"February","مارس":"March","أبريل":"April","مايو":"May",
  "يونيو":"June","يوليو":"July","أغسطس":"August","سبتمبر":"September",
  "أكتوبر":"October","نوفمبر":"November","ديسمبر":"December",
  "محرم":"Muharram","صفر":"Safar","ربيع الأول":"Rabi\u2019 I","ربيع الآخر":"Rabi\u2019 II",
  "جمادى الأولى":"Jumada I","جمادى الآخرة":"Jumada II","رجب":"Rajab","شعبان":"Sha\u2019ban",
  "رمضان":"Ramadan","شوال":"Shawwal","ذو القعدة":"Dhu al-Qi\u2019dah","ذو الحجة":"Dhu al-Hijjah",
};
const MONTH_RX = new RegExp(Object.keys(AR_MONTH)
  .sort((a,b)=>b.length-a.length).join("|"), "g");
function enNum(x){
  let s = String(x).replace(/[٠-٩]/g, c=>AR_DIG[c]);
  s = s.replace(MONTH_RX, m=>AR_MONTH[m]).replace(/\s*هـ/g, " AH");
  /* رمزُ المؤشر: «م٢·٣» ← «D2·3» — وقد صارت أرقامُه غربيةً قبل هذا السطر */
  /* ختمُ الإصدار نمطٌ لا نصٌّ مفرَد: يتغيّر مع كل بناء */
  /* ⛔ «٢٠٢٦م» علامةُ الميلادي — تُحذف بعد سنةٍ رقمية، وإلا بقي حرفٌ
     عربيٌّ وحيدٌ في ستّ شاشات ولم يُفهم مصدرُه إلا بقراءة الشاشة. */
  s = s.replace(/(\d)\s*م(?![\u0600-\u06ff])/g, "$1");
  s = s.replace(/^إصدار\s/, "Build ");
  return s.replace(/(^|[\s·])م(?=\d)/g, "$1D");
}
/* ⚠️ TR مُتَراكِمةٌ آمنة: TR(TR(s)) = TR(s) — فلا يضرُّ لفٌّ مزدوج
   ⛔ واسمُها TR لا t: «t» متغيِّرٌ محليٌّ في ثلاثين موضعاً من هذا الملف
      (جداولُ وعناصرُ)، فيحجبها ويسقط الرسمُ في منطقة التهيئة الميتة. */
/* ⛔ الفواصلُ **مرتَّبةٌ بالأولوية** ويُقسَم بواحدٍ في كل مستوى، ويُجرَّب
   المفتاحُ الكاملُ قبل القسمة في كل مرة. وبلا هذا الترتيب قُسِم عنوانُ
   المجال الثالث «مشاركة المتعلمين واندماجهم  —  يُرصد على الطالب…» على
   شَرطته الداخلية فلم يطابق شِقّاه مفتاحاً — **وكان له مفتاحٌ كاملٌ سليم**.
   فالقسمةُ الجائرةُ أفسدت ما كان يعمل. (٣٠ سبتمبر ٢٠٢٦) */
const TR_SEPS = [" · ", "  ·  ", " + ", " \\ "];
function TR1(k){
  if(Object.prototype.hasOwnProperty.call(T_EN, k)) return T_EN[k];
  return /[٠-٩]|هـ|^إصدار/.test(k) ? enNum(k) : k;
}
function TR(s){
  if(LANG !== "en" || s == null) return s;
  const k = String(s);
  if(Object.prototype.hasOwnProperty.call(T_EN, k)) return T_EN[k];
  /* ⛔ **الوصلُ هو العلّةُ الكبرى**: «المجال ١ · التخطيط وتجهيز بيئة التعلم»
     و«الأسبوع السادس · الأحد · ٧:٠٠» لا مدخلَ لهما، وأجزاؤها كلُّها مترجَمة.
     وإصلاحُه في ثلاثين موضعِ وصلٍ يُخطئ ويُنسى؛ فيُصلَح قاعدةً هنا: يُقسَم
     النصُّ على فواصله ويُترجَم كلُّ جزءٍ، فإن تُرجم واحدٌ أُخِذ المركَّب.
     (٣٠ سبتمبر ٢٠٢٦ — بعد أن أظهر فحصُ المتصفّح خمسةَ عشرَ شاشةً فيها عربيّ) */
  for(let si = 0; si < TR_SEPS.length; si++){
    const sep = TR_SEPS[si];
    if(k.indexOf(sep) < 0) continue;
    const parts = k.split(sep);
    let hit = false;
    const out = parts.map(function(x){
      const bare = x.trim();
      if(!bare) return x;
      const v = TR1(bare);
      if(v !== bare) hit = true;
      return x.replace(bare, v);
    });
    if(hit) return out.join(sep);
  }
  /* ⚠️ ولا تُترجَم البيانات: اسمُ معلمٍ أو مدرسةٍ يُعرض كما كُتب (قرارُ
     المستشار). فما لا مدخلَ له يعود كما هو، إلا أرقامَه وتواريخَه. */
  return /[٠-٩]|هـ/.test(k) ? enNum(k) : s;
}
function setLang(v){
  LANG = v;
  try{ localStorage.setItem(LANGK, v); }catch(e){}
  applyLang();
  if(ME) shell(); else login();
}
function applyLang(){
  const h = document.documentElement;
  h.lang = LANG === "en" ? "en" : "ar";
  h.dir  = LANG === "en" ? "ltr" : "rtl";
  /* ⛔ خطُّ الجزيرة بلا حروفٍ لاتينية، فالإنجليزيةُ بخطٍّ لاتينيٍّ صريح */
  h.classList.toggle("en", LANG === "en");
}

/* ⚠️ el هو الموضعُ الوحيدُ الذي يصير فيه النصُّ عنصراً في الصفحة، فالترجمةُ
   فيه تشمل نصوصَ الشفرة **ونصوصَ البيانات** (المراحلُ والمؤشراتُ والبنك)
   بلا لمسِ قيمةٍ محفوظة: تسميةُ الخيار تُترجَم و`value` يبقى عربياً. */
const el = (t_,c,x)=>{const e=document.createElement(t_); if(c)e.className=c; if(x!=null)e.textContent=TR(x); return e;};
/* ⛔ الأرقامُ الهندية للعربية وحدَها: «٤٥ من ٤٨» لا تُقرأ في شاشةٍ إنجليزية */
const arn = n => LANG === "en" ? String(n) : String(n).replace(/[0-9]/g, c => "٠١٢٣٤٥٦٧٨٩"[+c]);
const uid = () => Math.random().toString(36).slice(2,10);
let DB = {sched:[], prep:{}, obs:{}, peer:{}, rot:{}}, ME = null, PH = 1, CUR = null;
/* تراجعٌ خفيف: لقطةُ الحصة قبل التغيير لا لقطةُ القاعدة كلِّها */
let UNDO = [];

/* ───────── التخزين: محليٌّ دائماً، ومشتركٌ إن رُبط الخادم ───────── */
function load(){ try{ DB = Object.assign(DB, JSON.parse(localStorage.getItem(KEY)||"{}")); }catch(e){} 
  try{ ME = JSON.parse(localStorage.getItem(KEY+"_me")||"null"); }catch(e){} }
/* ⛔ **جدارُ التخزين كان يُضرَب بلا إنذار.** حدُّ `localStorage` خمسةُ
   ميغابايتَ للنطاق، والقاعدةُ تنمو بكل تحضيرٍ ورصدٍ وبطاقةِ أقرانٍ وسجلِّ
   عمليات — فتبلغه قبل أن يُملأ الجدولُ كلُّه. وكان العلاجُ تنبيهاً **بعد**
   الفشل: «تعذّر الحفظ» وقد ضاع ما كُتب في تلك اللحظة. فصار يُنذَر **قبله**
   عند أربعة أخماس الحدّ، ومرةً واحدةً في الجلسة فلا يُزعج. (١ أكتوبر ٢٠٢٦)
   ⚠️ والمقياسُ بالحروف لا بالبايتات: `localStorage` يخزّن UTF-16، فكلُّ حرفٍ
      بايتان — والعربيُّ حرفٌ واحدٌ لا بايتين كما في UTF-8. */
const LS_CAP = 5 * 1024 * 1024;          /* الحدُّ الشائعُ للنطاق */
let lsWarned = false;
function save(){
  let body = "";
  try{ body = JSON.stringify(DB); }catch(e){}
  try{
    localStorage.setItem(KEY, body);
    /* إنذارٌ قبل الجدار لا بعده */
    const used = body.length * 2;
    if(!lsWarned && used > LS_CAP * 0.8){
      lsWarned = true;
      toast("مساحةُ هذا الجهاز تقارب الامتلاء (" + arn(Math.round(used / 1048576 * 10) / 10)
            + " م.ب من " + arn(5) + ") — أفرغ سلّةَ المحذوفات أو خذ نسخةً احتياطية", "warn");
    }
  }catch(e){
    /* ⛔ ولا يُقال «تعذّر الحفظ» وحدَها: يُقال ما يُفعل، ويُحفظ ما أمكن */
    lsWarned = true;
    alert("⛔ امتلأت مساحةُ هذا المتصفّح، فلم يُحفظ آخرُ تغييرٍ على الجهاز.\n\n"
      + "وما كُتب قبله سليم. والعلاج:\n"
      + "• أفرغ سلّةَ المحذوفات (أدوات المستشار ← السجلّ والاسترداد)\n"
      + "• أو خذ نسخةً احتياطيةً ثم فرّغ البيانات\n\n"
      + (api() ? "ومخزنُك المشترك مربوطٌ — فبياناتُك فيه سليمة."
               : "⚠️ ولا مخزنَ مشتركٌ مربوط — فاربطه قبل أن يضيع شيء."));
  }
  sync();
}
function api(){ try{ return localStorage.getItem(API)||""; }catch(e){ return ""; } }
/* ⛔ **عقدُ المخزن كان بلا مصادقةٍ البتّة.** القراءةُ والكتابةُ والمحوُ على
   قاعدة المدرستين بلا مفتاحٍ ولا رأسِ تفويض — والسرُّ الوحيدُ عنوانُ الخادم،
   وهو يسافر في رابط دعوةٍ يُرسَل عبر واتساب. فمن وقع على الرابط — أو رآه في
   لقطةِ شاشةٍ أو في سجلّ متصفّح — ملكها كلَّها. (أمسكه وكيلُ أمن البيانات)
   والعلاجُ في حدود ما نملك: **مفتاحٌ مشتركٌ يُرسَل مع كل طلب**، يضبطه
   المستشارُ ويُدوِّره متى شاء بلا إعادة نشرٍ للخادم. وفائدتُه الحقيقية:
   ١) العنوانُ وحدَه لم يعد كافياً، ٢) والتدويرُ يُبطل ما تسرّب في لحظة.
   ⚠️ ويسافر في **جزء التجزئة** (`#`) من رابط الدعوة — فلا يُرسَل في ترويسة
      الإحالة ولا يُسجَّل في سجلّات الخوادم الوسيطة.
   ⚠️ وخادمٌ لا يفحصه يتجاهله — فالنشرُ آمنٌ قبل ترقية الخادم وبعدها. */
const SKEY = NS + "_skey";
function skey(){ try{ return localStorage.getItem(SKEY) || ""; }catch(e){ return ""; } }
function apiGet(kind, id){
  const k = skey();
  return api() + "?kind=" + encodeURIComponent(kind) + "&id=" + encodeURIComponent(id)
       + (k ? "&key=" + encodeURIComponent(k) : "");
}
function apiBody(o){
  const k = skey();
  return JSON.stringify(k ? Object.assign({key: k}, o) : o);
}

/* ═════════ حفظٌ صريحٌ · طباعةٌ · تنزيل — في كل شاشةِ إدخال ═════════
   ⛔ كان الحفظُ تلقائياً عند كل تغيير، وأثرُه الوحيدُ **كلمةٌ صغيرةٌ في
      الهيدر** لا تُرى على الجوال أصلاً. فالمعلمُ يكتب خانةً ويخرج ولا يعلم
      أحُفظ أم لا — وهذا وحدَه يكفي ليفقد الثقةَ بالمنصة ويُعيد الكتابة.
      (طلبُ المستشار ١ أكتوبر ٢٠٢٦: «كل صفحة فيها إدخالات ينبغي وجود زر
      للحفظ … ويتاح بعدها الطباعة أو تنزيل الملف»)
   ⚠️ والحفظُ التلقائيُّ **يبقى** — الزرُّ لا يحلُّ محلَّه بل يُطمئن:
      يحفظ، ويدفع فوراً إلى المخزن المشترك، ويقول نتيجةَ ذلك بصريح العبارة. */
/* ═════════ النوافذُ الموحَّدة — بديلُ `alert` الأصلية ═════════
   ⛔ **النوافذُ الأصليةُ ثمانٍ وخمسون موضعاً في المنصة** (٤٢ `alert` · ١٠
      `confirm` · ٦ `prompt`)، وقاعدةُ المستشار تمنعها منذ وقت. وهي:
      · تخرج بخطِّ النظام وبلغته — فيظهر زرُّ «OK» إنجليزياً في شاشةٍ عربية،
      · ولا تُنسَّق ولا تُقرأ بخطِّ المنصة، ولا تُميَّز رسالةُ المنع من الإشعار،
      · وتُجمّد الصفحةَ على الجوال، وبعضُ المتصفحات تكبتها بعد تكرارها،
      · **وتوقف كروم بلا رأسٍ وقوفاً تامّاً** — فما يُجمّد المسبارَ يُجمّد
        المستخدم، وقد ضاع عليَّ بها قياسٌ ثلاثَ مرات. (١ أكتوبر ٢٠٢٦)
   ⚠️ والاستبدالُ **بإعادة تعريف `alert`** لا بتعديل ثمانيةٍ وخمسين نداءً:
      الموضعُ الواحدُ يُنسى، والنداءاتُ الجديدةُ تُكتب بالعادة القديمة. ومن
      كتب `alert("…")` غداً نالته النافذةُ الموحَّدةُ بلا أن يعلم.
   ⚠️ و`confirm` و`prompt` تُعيدان قيمةً **تزامنياً** تُستعمل في شرط، فلا
      تُستبدلان بنافذةٍ غيرِ تزامنيةٍ إلا بإعادة كتابة منطقِها — وهي خطوةٌ
      تالية. فيبقى سلوكُهما كما هو اليوم، ولا يُدَّعى غيرُ ذلك. */
function uiDialog(msg, kind){
  const old = document.getElementById("udlg");
  if(old) old.remove();
  const back = el("div","udlg"); back.id = "udlg";
  const box = el("div","udlgbox" + (kind ? " " + kind : ""));
  box.setAttribute("role", "alertdialog");
  box.setAttribute("aria-modal", "true");
  box.setAttribute("aria-describedby", "udlgtx");
  /* ⚠️ والنافذةُ تُشير إلى نصِّها: `role` و`aria-modal` بلا `describedby`
     تُعلن «نافذة» ولا تقرأ ما فيها على بعض القارئات. */
  const body = el("div","udlgtx"); body.id = "udlgtx";
  String(msg == null ? "" : msg).split("\n").forEach(line=>{
    body.appendChild(el("div", null, line || " "));
  });
  box.appendChild(body);
  const bar = el("div","udlgbar");
  const ok = el("button","b","حسناً");
  const close = ()=>{ back.remove(); try{ if(back.__prev) back.__prev.focus(); }catch(e){} };
  ok.addEventListener("click", close);
  bar.appendChild(ok); box.appendChild(bar);
  back.appendChild(box);
  back.addEventListener("click", e=>{ if(e.target === back) close(); });
  back.addEventListener("keydown", e=>{
    if(e.key === "Escape"){ e.preventDefault(); close(); }
    /* ⚠️ والتركيزُ محبوسٌ في النافذة: من خرج منها بـTab تاه خلفها */
    if(e.key === "Tab"){ e.preventDefault(); ok.focus(); }
  });
  back.__prev = document.activeElement;
  document.body.appendChild(back);
  ok.focus();
  return back;
}
/* ═══ سؤالٌ موحَّدٌ بنعم/لا — بديلُ `confirm` ═══
   ⚠️ **غيرُ تزامنيٍّ بالضرورة**: نافذةُ المتصفّح توقف الشفرةَ حتى يُجاب،
      ولا سبيلَ إلى ذلك في نافذةٍ من صنعنا. فيُعاد كتابةُ كلِّ موضعٍ على
      صيغة `uiAsk(...).then(ok => { if(!ok) return; … })` — اثنا عشرَ موضعاً،
      كلٌّ منها قُرئ وأُعيدت كتابتُه. ولا يُدَّعى أن الاستبدالَ آليّ. */
function uiAsk(msg, okText, kind){
  return new Promise(res=>{
    const old = document.getElementById("udlg");
    if(old) old.remove();
    const back = el("div","udlg"); back.id = "udlg";
    const box = el("div","udlgbox" + (kind ? " " + kind : " warn"));
    box.setAttribute("role", "alertdialog");
    box.setAttribute("aria-modal", "true");
  box.setAttribute("aria-describedby", "udlgtx");
    /* ⚠️ والنافذةُ تُشير إلى نصِّها: `role` و`aria-modal` بلا `describedby`
     تُعلن «نافذة» ولا تقرأ ما فيها على بعض القارئات. */
  const body = el("div","udlgtx"); body.id = "udlgtx";
    String(msg == null ? "" : msg).split("\n").forEach(line=>{
      body.appendChild(el("div", null, line || " "));
    });
    box.appendChild(body);
    const bar = el("div","udlgbar");
    let done = false;
    const end = (v)=>{ if(done) return; done = true; back.remove();
      try{ if(back.__prev) back.__prev.focus(); }catch(e){}
      res(v); };
    const yes = el("button","b" + (kind === "bad" ? " warn" : ""), okText || "متابعة");
    const no  = el("button","b ghost","إلغاء");
    yes.addEventListener("click", ()=>end(true));
    no.addEventListener("click", ()=>end(false));
    bar.appendChild(yes); bar.appendChild(no);
    box.appendChild(bar); back.appendChild(box);
    back.addEventListener("click", e=>{ if(e.target === back) end(false); });
    back.addEventListener("keydown", e=>{
      if(e.key === "Escape"){ e.preventDefault(); end(false); }
      if(e.key === "Tab"){ e.preventDefault();
        (document.activeElement === yes ? no : yes).focus(); }
    });
    back.__prev = document.activeElement;
    document.body.appendChild(back);
    /* ⚠️ التركيزُ على «إلغاء» لا على «متابعة»: فعلٌ لا يُستردُّ لا يُبدأ بضغطة */
    no.focus();
  });
}
/* ═══ سؤالٌ موحَّدٌ بكتابة — بديلُ `prompt` ═══ */
function uiPrompt(msg, def, placeholder){
  return new Promise(res=>{
    const old = document.getElementById("udlg");
    if(old) old.remove();
    const back = el("div","udlg"); back.id = "udlg";
    const box = el("div","udlgbox");
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
  box.setAttribute("aria-describedby", "udlgtx");
    /* ⚠️ والنافذةُ تُشير إلى نصِّها: `role` و`aria-modal` بلا `describedby`
     تُعلن «نافذة» ولا تقرأ ما فيها على بعض القارئات. */
  const body = el("div","udlgtx"); body.id = "udlgtx";
    String(msg == null ? "" : msg).split("\n").forEach(line=>{
      body.appendChild(el("div", null, line || " "));
    });
    const inp = el("input"); inp.type = "text";
    inp.value = def == null ? "" : String(def);
    if(placeholder) inp.placeholder = placeholder;
    inp.className = "udlgin";
    inp.setAttribute("aria-label", TR("القيمة"));
    body.appendChild(inp);
    box.appendChild(body);
    const bar = el("div","udlgbar");
    let done = false;
    const end = (v)=>{ if(done) return; done = true; back.remove();
      try{ if(back.__prev) back.__prev.focus(); }catch(e){}
      res(v); };
    const yes = el("button","b","حسناً"), no = el("button","b ghost","إلغاء");
    yes.addEventListener("click", ()=>end(inp.value));
    no.addEventListener("click", ()=>end(null));
    bar.appendChild(yes); bar.appendChild(no);
    box.appendChild(bar); back.appendChild(box);
    back.addEventListener("click", e=>{ if(e.target === back) end(null); });
    back.addEventListener("keydown", e=>{
      if(e.key === "Escape"){ e.preventDefault(); end(null); }
      if(e.key === "Enter" && document.activeElement === inp){
        e.preventDefault(); end(inp.value); }
    });
    back.__prev = document.activeElement;
    document.body.appendChild(back);
    inp.focus(); inp.select();
  });
}

/* ⛔ تُعاد الكتابةُ على `alert` نفسِها — فيُغطّى كلُّ نداءٍ قائمٍ وقادم */
window.alert = function(msg){
  const t = String(msg == null ? "" : msg);
  uiDialog(t, /^⛔/.test(t) ? "bad" : (/^⚠️/.test(t) ? "warn" : (/^✓/.test(t) ? "ok" : "")));
};

function toast(msg, cls){
  let t = document.getElementById("toast");
  if(!t){
    t = el("div"); t.id = "toast";
    /* ⛔ **الحفظُ والخطأُ كانا صامتَين على القارئ الآلي**: الرسالةُ تظهر ثلاثَ
       ثوانٍ وتذهب، ولا منطقةَ إعلانٍ واحدةً في المنصة كلِّها — فمن لا يرى
       الشاشةَ يضغط «حفظ» ولا يعلم أحُفظ أم رُدَّ. والمعلمُ يُدخل عشرينَ حقلاً.
       فتصير المنطقةُ حيّةً: المطمئنُّ «مؤدَّب» ينتظر صمتَ القارئ، والخطأُ
       «حازمٌ» يقطع. (١ أكتوبر ٢٠٢٦) */
    t.setAttribute("role", "status");
    t.setAttribute("aria-live", "polite");
    t.setAttribute("aria-atomic", "true");
    document.body.appendChild(t);
  }
  /* ⚠️ والنتيجةُ تُعلَن حازمةً، والانتظارُ «مؤدَّبٌ» لا يقطع: «يُحفظ…» رسالةُ
     طريقٍ لا نتيجة، فلها صنفُ `wait` كي لا تُقاطِع ما قبلها. */
  t.setAttribute("aria-live", (cls === "bad" || cls === "warn") ? "assertive" : "polite");
  t.className = "toast " + (cls || "ok") + " on";
  /* ⚠️ والنصُّ يُفرَّغ قبل ملئه: القارئُ لا يُعلن نصّاً لم يتغيّر، فتكرارُ
     الرسالة نفسِها (حفظٌ ثانٍ) كان يمرّ بلا إعلان. */
  t.textContent = "";
  const say = TR(msg);
  setTimeout(()=>{ t.textContent = say; }, 30);
  clearTimeout(t.__h);
  t.__h = setTimeout(()=>{ t.className = "toast " + (cls || "ok"); }, 3200);
}

/* نسخةٌ قائمةٌ بنفسها من الشاشة الحالية: تُفتح وتُطبع على أي جهاز بلا إنترنت.
   ⚠️ تُحوَّل حقولُ الإدخال إلى نصٍّ — وإلّا نزلت صفحةٌ بخاناتٍ فارغة. */
function screenHTML(title){
  const main = document.getElementById("main") || document.body;
  const cl = main.cloneNode(true);
  cl.querySelectorAll("button, .noprint, #scorebar, .abar").forEach(x=>x.remove());
  cl.querySelectorAll("textarea").forEach(x=>{
    const d = document.createElement("div"); d.className = "v";
    d.textContent = x.value || "—"; x.replaceWith(d);
  });
  cl.querySelectorAll("select").forEach(x=>{
    const d = document.createElement("div"); d.className = "v";
    d.textContent = (x.options[x.selectedIndex] || {}).text || "—"; x.replaceWith(d);
  });
  cl.querySelectorAll("input").forEach(x=>{
    const d = document.createElement("span");
    if(x.type === "checkbox" || x.type === "radio") d.textContent = x.checked ? "☑" : "☐";
    else { d.className = "v"; d.textContent = x.value || "—"; }
    x.replaceWith(d);
  });
  const css = Array.prototype.map.call(document.querySelectorAll("style"),
                                       x=>x.textContent).join("\n");
  return "<!doctype html><html dir=\"rtl\" lang=\"" + (LANG === "en" ? "en" : "ar") + "\">"
    + "<head><meta charset=\"utf-8\">"
    + "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
    + "<title>" + title + "</title><style>" + css
    + "\n.v{min-height:1.2em;white-space:pre-wrap}body{padding:14px}</style></head>"
    + "<body>" + cl.innerHTML + "</body></html>";
}
function downloadScreen(title){
  const name = String(title || "صفحة").replace(/[\\/:*?\"<>|]/g, "-") + ".html";
  const blob = new Blob(["﻿" + screenHTML(title)], {type:"text/html;charset=utf-8"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = name;
  document.body.appendChild(a); a.click();
  setTimeout(()=>{ URL.revokeObjectURL(a.href); a.remove(); }, 4000);
  toast("نزل الملفُّ على جهازك: " + name);
}

/* ⛔ يُنادى في **كل** شاشةٍ فيها إدخال — و`respcheck` يفشل عند شاشةٍ فيها
   خانةٌ حيّةٌ ولا شريطَ حفظٍ لها (الفحصُ ⑤ فيه).
   ⚠️ وكان هذا التعليقُ يسمّي حارساً اسمُه `savecheck` **لا وجودَ له** — فوعدٌ
      في تعليقٍ لا يَحرس شيئاً، وقارئُه يطمئنُّ إلى ما ليس. (صُحِّح ١ أكتوبر) */
function actionBar(host, title, opts){
  const o = opts || {};
  const bar = el("div","abar noprint");
  const sv = el("button","b","حفظ");
  sv.addEventListener("click", ()=>{
    if(o.before) o.before();
    save();
    if(!api()){ toast("حُفظ على هذا الجهاز — ولا مخزنَ مشتركاً مربوطاً", "warn"); return; }
    toast("يُحفظ…", "wait");
    syncFlush().then(ok=>toast(ok ? "حُفظ للجميع ✓" : "حُفظ على جهازك — وسيُرسَل عند عودة الشبكة",
                               ok ? "ok" : "warn"));
  });
  bar.appendChild(sv);
  const pr = el("button","b ghost","طباعة");
  pr.addEventListener("click", ()=>{ save(); window.print(); });
  bar.appendChild(pr);
  const dl = el("button","b ghost","تنزيل الملف");
  dl.addEventListener("click", ()=>{ save(); downloadScreen(title); });
  bar.appendChild(dl);
  bar.appendChild(el("i",null,"الحفظُ تلقائيٌّ أيضاً — والزرُّ يؤكّده ويرسله فوراً"));
  host.appendChild(bar);
  return bar;
}
/* ⛔ مؤشّرُ حالة المزامنة في الهيدر. حُذف تعريفُه سهواً ٢٩ سبتمبر ٢٠٢٦ حين
   أُعيدت كتابةُ طبقة المزامنة، وبقيت نداءاتُه السبعة — فكان كلُّ `save()`
   يسقط بـReferenceError بعد أن يكتب محلياً وقبل أن يُزامن. أي أن المنصةَ كانت
   تحفظ على الجهاز ولا تُرسل شيئاً إلى المخزن المشترك. */
function setSyn(t, cls){
  const s = document.getElementById("syn");
  if(!s) return;
  s.textContent = TR(t); s.className = cls || "";
}

/* ═════════ المزامنة ═════════
   ⛔ حدُّ المخزن القديم المجاني **ألفُ كتابةٍ في اليوم** للمنظومة كلِّها لا لكل
      مستخدم. وكانت المزامنة تُكتب بعد كل توقّفٍ يقارب الثانية — فمعلمٌ يملأ
      تحضيراً واحداً كان يستهلك خمسين كتابة، وعشرون معلماً يستنفدون اليومَ كلَّه.
   العلاج: تأخيرٌ اثنتا عشرةَ ثانية · ولا تُكتب إن لم تتغيّر القاعدة فعلاً ·
      ودفعٌ فوريٌّ عند الأفعال الحاسمة وعند مغادرة الصفحة. */
let syncT = null, lastSent = "", pending = false, writeFails = 0;
const SYNC_WAIT = 12000;

/* ⚠️ `__schema` علامةٌ محليةٌ لا بيانات — تُستثنى من الحمولة كي لا تُعامَل
   مفتاحاً سادساً يُهمله دمجُ الخادم. */
function dbSnapshot(){
  try{ const {__schema, ...rest} = DB; return JSON.stringify(rest); }
  catch(e){ return ""; }
}

/* ⛔ **لا تُستبدل شجرةُ البيانات أبداً.** كانت المزامنةُ تفعل `DB = r.data`
   و`Object.assign(DB, r.data)`، والشاشةُ المفتوحةُ تُمسك مرجعاً إلى السجلّ
   (استمارةُ الرصد تُمسك `V`، وشاشةُ التحضير تُمسك `P`) — فما يُكتب بعد
   المزامنة يُكتب في كائنٍ **منبتٍّ** عن القاعدة، ثم يُحفظ ما في القاعدة.
   فيرى المشرفُ درجتَه على الشاشة وليست في المخزن. (٣٠ سبتمبر ٢٠٢٦)
   والدمجُ هنا يحفظ **هويّةَ** كل كائنٍ فيُحدَّث في مكانه. */
function mergeMap(dst, src){
  if(!src || typeof src !== "object") return;
  Object.keys(src).forEach(k=>{
    const a = dst[k], b = src[k];
    if(a && b && typeof a === "object" && typeof b === "object" && !Array.isArray(a)){
      Object.keys(b).forEach(kk=>{ a[kk] = b[kk]; });      /* يبقى الكائنُ نفسَه */
    } else dst[k] = b;
  });
}
function mergeDB(src){
  if(!src || typeof src !== "object") return;
  /* الحصصُ مصفوفةٌ: تُدمج بالمعرّف، ويُحدَّث القائمُ في موضعه */
  if(Array.isArray(src.sched)){
    const by = {}; (DB.sched || []).forEach(x=>{ if(x && x.id) by[x.id] = x; });
    src.sched.forEach(x=>{
      if(!x || !x.id) return;
      const cur = by[x.id];
      if(cur) Object.keys(x).forEach(k=>{ cur[k] = x[k]; });
      else { DB.sched.push(x); by[x.id] = x; }
    });
  }
  ["prep","obs","peer","rot"].forEach(k=>{
    if(src[k] && typeof src[k] === "object"){
      DB[k] = DB[k] || {};
      mergeMap(DB[k], src[k]);
    }
  });
}

function pushNow(){
  clearTimeout(syncT); syncT = null;
  if(!api()) return Promise.resolve(false);
  const body = dbSnapshot();
  if(!body || body === lastSent){ pending = false; setSyn(""); return Promise.resolve(true); }
  setSyn("يُحفظ…");
  return fetch(api(), {method:"POST", headers:{"Content-Type":"text/plain;charset=utf-8"}, body: apiBody({kind:"platform", id:SID, data: JSON.parse(body)})})
    .then(r=>{
      if(r.status === 429 || r.status === 503) throw new Error("limit");
      return r.json();
    })
    .then(r=>{
      if(r && r.ok && r.data){
        mergeDB(r.data);
        try{ localStorage.setItem(KEY, JSON.stringify(DB)); }catch(e){}
      }
      lastSent = dbSnapshot(); pending = false; writeFails = 0;
      setSyn("حُفظ للجميع ✓", "oksyn");
      setTimeout(()=>setSyn(""), 2500);
      return true;
    })
    .catch(e=>{
      writeFails++;
      pending = true;
      setSyn(e.message === "limit" ? "تعذّر الحفظ المشترك — يُعاد قريباً" : "محفوظٌ محلياً — بانتظار الشبكة",
             "warnsyn");
      /* ⚠️ لا تُفقد البيانات: تبقى محليةً ويُعاد الدفعُ بتباعدٍ متزايد */
      if(writeFails <= 6) syncT = setTimeout(pushNow, Math.min(60000, 5000 * writeFails));
      return false;
    });
}
function sync(){
  if(!api()){ setSyn("على هذا الجهاز فقط", "warnsyn"); return; }
  pending = true;
  if(dbSnapshot() === lastSent){ pending = false; return; }
  setSyn("سيُحفظ…");
  clearTimeout(syncT);
  syncT = setTimeout(pushNow, SYNC_WAIT);
}
/* الأفعالُ الحاسمة تُدفع فوراً لا بعد اثنتي عشرة ثانية */
function syncFlush(){ if(api() && pending) return pushNow(); return Promise.resolve(true); }
addEventListener("visibilitychange", ()=>{ if(document.visibilityState === "hidden") syncFlush(); });
addEventListener("pagehide", ()=>{
  if(!api() || !pending) return;
  try{ navigator.sendBeacon(api(),
       new Blob([apiBody({kind:"platform", id:SID, data:DB})], {type:"text/plain"})); }catch(e){}
});
addEventListener("beforeunload", (e)=>{
  if(api() && pending){ syncFlush(); }
});
function pull(){
  if(!api()) return Promise.resolve(false);
  /* ⛔ لا يُسحب وفي الجهاز كتابةٌ لم تُدفع — تُدفع أولاً ثم يُسحب */
  if(pending) return pushNow().then(()=>pullNow());
  return pullNow();
}
function pullNow(){
  if(!api()) return Promise.resolve(false);
  return fetch(apiGet("platform", SID)).then(r=>r.json())
    /* ⛔ **`lastSent` لا يُضبط إلا من دفعةٍ ناجحة.** كان السحبُ يضبطه، فيرى
       `pushNow` أن لا جديدَ فيلغي الدفعَ **ويُعلن نجاحاً** — فما كُتب بين
       دفعةٍ وسحبٍ لا يُدفع أبداً ولا يبقى محلياً. (٣٠ سبتمبر ٢٠٢٦) */
    .then(r=>{ if(r && r.ok && r.data){ mergeDB(r.data);
      try{ localStorage.setItem(KEY, JSON.stringify(DB)); }catch(e){} return true; } return false; })
    .catch(()=>false);
}
/* ═════════ سلّةُ المحذوفات ═════════
   ⛔ لا يُمحى شيءٌ نهائياً بضغطة: يُنقل إلى السلّة بكامله — الحصةُ وتحضيرُها
      ورصدُها وبطاقاتُ أقرانها — ومعه من حذف ومتى، ويُستردّ بنقرة.
   ⚠️ وتُخزَّن داخل `prep` بمفتاحٍ مسبوقٍ بـ`~trash~` لا في مفتاحٍ جديد:
      دالةُ الدمج في الخادم المنشور تدمج `prep` بالمفاتيح وتتجاهل ما عداها،
      فلو وُضعت في مفتاحٍ مستحدَثٍ ضاعت عند أول مزامنةٍ من جهازٍ آخر.
      (وقد نُصّ عليه في شفرة الخادم — وهي في المجلد الخاصّ — ليُراعى عند تحديثه.) */
/* ═════════ سجلُّ العمليات ═════════
   ⚠️ `~trash~` و`~log~` مفاتيحُ جانبيةٌ داخل `prep` — لا تحضيرات. وُضعت هناك
      لأن خادمَ المستشار يدمج خمسةَ مفاتيحَ ويتجاهل ما عداها، فالمفتاحُ الجديد
      يضيع. ويُستثنيان من كل عدٍّ للتحضيرات. */
const TRASH = "~trash~", LOG = "~log~";
const LOG_MAX = 600;                       /* حدٌّ يمنع تضخّم القاعدة */
/* ⚠️ الوقتُ وحده لا يكفي للترتيب: عمليتان في الميلي‑ثانية نفسها تتساويان
   فيختلّ ترتيبُهما. فيُضاف عدّادٌ متسلسلٌ داخل المفتاح، ويُرتَّب بالمفتاح. */
let logSeq = 0;
function logKey(){
  return LOG + Date.now().toString(36) + "-" + (logSeq++).toString(36).padStart(4, "0")
       + "-" + Math.random().toString(36).slice(2, 6);
}
function logAct(act, what, L){
  if(!ME) return;
  DB.prep[logKey()] = {a: act, w: what, by: ME.name, r: ME.role,
                       t: new Date().toISOString(),
                       lid: L ? L.id : "", gk: L ? L.gk : ""};
  const keys = Object.keys(DB.prep).filter(k=>k.indexOf(LOG) === 0).sort();
  if(keys.length > LOG_MAX) keys.slice(0, keys.length - LOG_MAX).forEach(k=>delete DB.prep[k]);
}
function logList(){
  /* يُرتَّب بالمفتاح لا بالوقت: المفتاحُ يحمل الوقتَ ثم التسلسل فلا يتساوى اثنان */
  return Object.keys(DB.prep || {}).filter(k=>k.indexOf(LOG) === 0)
    .sort().reverse()
    .map(k=>DB.prep[k]).filter(Boolean);
}
function trashKey(id){ return TRASH + id; }
function trashList(){
  const all = Object.keys(DB.prep || {}).filter(k=>k.indexOf(TRASH) === 0)
    .map(k=>DB.prep[k]).filter(x=>x && x.L)
    .sort((a,b)=>(b.at||"").localeCompare(a.at||""));
  /* ⛔ **كان للسلّة حقيقتان**: عدّادُ التبويب يُرشِّح بـ`isEval() || t.by===ME.name`
     والعرضُ يُرشِّح بالنطاق — فيقول التبويبُ «٧» ثم لا يجد الفاتحُ إلا اثنتين،
     ويعدُّ فريقُ المتابعة محذوفاتِ المنظومة كلِّها. فالترشيحُ هنا وحدَه،
     وكلُّ قارئٍ يقرأ المرشَّح. (١ أكتوبر ٢٠٢٦) */
  if(isAdmin()) return all;
  /* ⚠️ وفريقُ المتابعة يتابع ولا يحذف — فلا يرى إلا ما حذفه قبلَ المنع */
  if(!isEval() || ME.role === "intqa") return all.filter(t=>t.by === ME.name);
  if(isScopeBound()) return all.filter(t=>t.L && inMyScope(t.L));
  return all;
}
/* ⛔ والاستردادُ والمحوُ حارسُهما واحدٌ مع الحذف: من لا يحذف لا يمحو ولا يستردّ */
function canPurge(L){
  if(!ME) return false;
  if(ME.role === "admin") return true;
  if(ME.role === "intqa") return false;
  return isEval() && inMyScope(L);
}
function canRestore(L){
  if(!ME) return false;
  if(ME.role === "admin") return true;
  if(ME.role === "intqa") return false;
  if(ME.role === "teacher") return isMine(L);
  return isEval() && inMyScope(L);
}
/* ⛔ **الحذفُ كان بلا حارسٍ البتّة.** `myList` يبني قائمتَه من **المجمع
   كلِّه** (ستةُ أعمدةٍ في ثلاث مدارس) لا من مدرسة الوكيل، وزرُّ «حذف» يظهر
   لكل مقيّم — و`dropLesson` لا تفحص نطاقاً ولا اعتماداً. فوكيلُ مدرسةٍ
   يستطيع محوَ **درجةٍ معتمدةٍ مقفولةٍ لمدرسةٍ أخرى** بلا رجعة. والقاعدةُ
   المعلنةُ محروسةٌ في التعديل (`canEdit` تُرجع false للوكيل) ومكشوفةٌ في
   الحذف. (أمسكه وكيلُ رحلة الوكيل التعليمي؛ عولج ١ أكتوبر ٢٠٢٦)
   ⚠️ والحارسُ **عند المصدر** لا عند الزرّ: الأزرارُ تُنسى، والدالّةُ واحدة. */
function canDrop(L){
  if(!L || !ME) return false;
  if(ME.role === "admin") return true;        /* المستشارُ مالكُ المنظومة */
  if(L.approved) return false;                /* معتمدةٌ فمقفولةٌ على الجميع */
  if(ME.role === "teacher") return isMine(L);
  /* ⛔ **فريقُ متابعة التقويم الداخلي يتابع ولا يرصد — فلا يحذف ولا يمحو.**
     كان داخلاً في `isEval` فنال زرَّ الحذف وزرَّ المحو النهائيّ: فالدورُ
     الوحيدُ الممنوعُ من الرصد كان **أقدرَ الأدوار على الإتلاف**. وضياعُ حصةٍ
     معتمدةٍ قبل التقويم خسارةٌ لا تُستردّ. (أمسكه وكيلُ الدَّورَين الجديدَين؛
     عولج ١ أكتوبر ٢٠٢٦) */
  if(ME.role === "intqa") return false;
  if(!isEval()) return false;
  return inMyScope(L);                        /* ولا يتجاوز أحدٌ نطاقَه */
}
function dropWhy(L){
  if(!L) return "لم تُوجد هذه الحصة.";
  if(ME && ME.role === "admin") return "";
  if(L.approved) return "هذه الحصةُ معتمدةٌ ومقفولة — يُفكّ اعتمادُها أولاً.";
  if(ME && ME.role === "teacher" && !isMine(L)) return "هذه الحصةُ ليست باسمك.";
  if(ME && ME.role === "intqa") return TR(D.intqanodel);
  if(!isEval()) return "الحذفُ ليس من صلاحيتك.";
  if(!inMyScope(L)) return "هذه الحصةُ خارجَ نطاقك.";
  return "";
}
function dropLesson(id){
  const L = DB.sched.find(x=>x.id===id);
  /* ⛔ ولا يُحذف شيءٌ خارجَ النطاق ولو نُودي من موضعٍ لم يفحص */
  if(L && !canDrop(L)){ alert("⛔ لم تُحذف: " + dropWhy(L)); return false; }
  if(L){
    const obs = {}, peer = {};
    Object.keys(DB.obs).forEach(k=>{ if(k.indexOf(id+"|")===0) obs[k] = DB.obs[k]; });
    Object.keys(DB.peer).forEach(k=>{ if(k.indexOf(id+"|")===0) peer[k] = DB.peer[k]; });
    DB.prep[trashKey(id)] = {L: JSON.parse(JSON.stringify(L)),
      prep: DB.prep[id] ? JSON.parse(JSON.stringify(DB.prep[id])) : null,
      obs: obs, peer: peer, by: (ME && ME.name) || "—", at: new Date().toISOString()};
  }
  if(L) logAct("حذف", [L.teacher, L.stage, L.period, L.week, L.day].filter(Boolean).join(" · "), L);
  DB.__deleted = (DB.__deleted || []).concat([id]);
  DB.sched = DB.sched.filter(y=>y.id!==id);
  delete DB.prep[id];
  Object.keys(DB.obs).forEach(k=>{ if(k.indexOf(id+"|")===0) delete DB.obs[k]; });
  Object.keys(DB.peer).forEach(k=>{ if(k.indexOf(id+"|")===0) delete DB.peer[k]; });
  purgeTrash();
  save(); syncFlush();
}
/* الاستردادُ يعيد كلَّ ما عُلِّق بالحصة لا الحصةَ وحدها */
/* ⛔ والمحوُ النهائيُّ كان منطقاً في مُستمِع زرٍّ: صار دالّةً حارسُها فيها،
   فمن نادى المحوَ من أي طريقٍ نالَه الحارس. */
function purgeLesson(id){
  const t = DB.prep[trashKey(id)];
  if(!t || !t.L) return false;
  if(!canPurge(t.L)){ uiDialog("⛔ المحوُ النهائيُّ ليس من صلاحيتك هنا.", "bad"); return false; }
  delete DB.prep[trashKey(id)];
  logAct("محوٌ نهائي",
    [t.L.teacher, t.L.stage, t.L.period].filter(Boolean).join(" · "), t.L);
  save(); syncFlush();
  return true;
}
function restoreLesson(id){
  const t = DB.prep[trashKey(id)];
  if(!t || !t.L) return false;
  /* ⛔ **الحارسُ عند المصدر لا عند الزرّ**: `dropLesson` تفحص `canDrop` في
     داخلها، أما الاستردادُ فكان يُحرَس بإخفاء الزرِّ وحدَه — وإخفاءُ زرٍّ ليس
     منعاً. (١ أكتوبر ٢٠٢٦) */
  if(!canRestore(t.L)){ uiDialog("⛔ الاستردادُ ليس من صلاحيتك هنا.", "bad"); return false; }
  if(DB.sched.some(x=>x.gk === t.L.gk && x.id !== id)){
    alert("لا يمكن الاسترداد: خانةُ هذه الحصة شُغِلت بحصةٍ أخرى بعد حذفها.");
    return false;
  }
  DB.sched.push(t.L);
  if(t.prep) DB.prep[t.L.id] = t.prep;
  Object.keys(t.obs || {}).forEach(k=>{ DB.obs[k] = t.obs[k]; });
  Object.keys(t.peer || {}).forEach(k=>{ DB.peer[k] = t.peer[k]; });
  logAct("استرداد", [t.L.teacher, t.L.stage, t.L.period].filter(Boolean).join(" · "), t.L);
  DB.__deleted = (DB.__deleted || []).filter(x=>x !== id);
  delete DB.prep[trashKey(id)];
  save(); syncFlush();
  return true;
}
/* ما مضى عليه ثلاثون يوماً يُمحى نهائياً — وإلا تضخّمت القاعدة بلا حدّ */
function purgeTrash(){
  const cut = Date.now() - 30*24*3600*1000;
  Object.keys(DB.prep || {}).forEach(k=>{
    if(k.indexOf(TRASH) !== 0) return;
    const t = DB.prep[k];
    if(t && t.at && new Date(t.at).getTime() < cut) delete DB.prep[k];
  });
}

/* ───────── أدوات ───────── */
function fld(type, val, onch, opts, ph, ro){
  let e;
  if(type === "sel"){ e = el("select");
    /* ⛔ التسميةُ تُترجَم و«value» يبقى الأصلَ العربي — وإلا انكسر كلُّ مرشِّحٍ
       ومفتاحِ حصة. و`el` هو الذي يترجم التسمية. */
    (opts||[]).forEach(o=>{ const x=el("option",null,o); x.value=o; e.appendChild(x); });
    /* اسمُ الحقل داخل خانة الاختيار نفسها — فلا يُسأل «ماذا أختار؟» */
    /* ⛔ «— choose Teaching approach —» يحتاج ٢٣٢بك في خانةٍ عرضُها ١٤٨:
       صيغةُ «— اختر س —» عربيةُ الطول، وترجمتُها الحرفيةُ تُقتطع مهما صُغّر
       الخط (كان يلزمها ٧بك لتدخل). فالإنجليزيةُ تُسمّي الحقلَ وحدَه — وهو
       عُرفُ الواجهات الإنجليزية أصلاً. (بلاغُ المستشار ٣٠ سبتمبر ٢٠٢٦) */
    const b = el("option", null, LANG === "en"
        ? (ph ? TR(ph) : TR("اختر"))
        : (ph ? "— " + TR("اختر") + " " + TR(ph) + " —" : "— " + TR("اختر") + " —"));
    b.value="";
    e.insertBefore(b, e.firstChild); }
  else if(type === "area"){ e = el("textarea"); }
  else { e = el("input"); e.type = "text"; }
  if(ph) e.placeholder = TR(ph);
  e.value = val == null ? "" : val;
  e.addEventListener("focus", ()=>{ const r = e.closest(".row2,.stg,td,.cellbox,.f,label,div");
    if(r) r.classList.add("editing"); });
  e.addEventListener("blur", ()=>{ document.querySelectorAll(".editing").forEach(x=>x.classList.remove("editing"));
    e.classList.add("touched"); });
  e.addEventListener("input", ()=>{ e.classList.add("touched"); onch(e.value); });
  e.addEventListener("change", ()=>onch(e.value));
  /* ⛔ حقلٌ مقفولٌ يُعطَّل لا يُترك مفتوحاً: القفلُ الذي يُرى في النصّ ولا يقع
     في الحقل يُغري بالكتابة ثم يبتلعها. (٣٠ سبتمبر ٢٠٢٦) */
  if(ro){ e.disabled = true; e.setAttribute("aria-disabled","true"); }
  return e;
}
function lessonTitle(L){
  /* ⚠️ تُترجَم الأجزاءُ لا النصُّ الموصول: «رياضيات · 5/A · فلان» لا مدخلَ له،
     وأجزاؤه لها. والاسمُ يعود كما هو لأنه ليس في المعجم. */
  return [L.subject, L.klass, L.teacher].filter(Boolean).map(TR).join(" · ")
      || "حصة بلا بيانات";
}
/* ⛔ **`L.period` نصُّه «الحصة 1» لا «1»** — فكلُّ موضعٍ يسبقه بكلمة «الحصة»
   يُخرج «الحصة الحصة 1». عولج في رأس الشاشة ٣٠ سبتمبر ٢٠٢٦ **في موضعه
   وحدَه**، وبقي في `inject` (خانةُ «الحصة» في بيانات التحضير) وفي جدول
   «زياراتي» — فرآه المستشارُ ١ أكتوبر. فصار قاعدةً في دالّتين لا تصحيحاً
   في موضع. ⚠️ والرقمُ لاتينيٌّ في المصدر فيُعرَّب بـ`arn`. */
function perNo(L){ return String((L && L.period) || "").replace(/[^\d٠-٩]/g, ""); }
function perLabel(L, withTime){
  const n = perNo(L);
  if(!n) return "";
  return TR("الحصة ") + arn(n) + ((withTime && L && L.time) ? " — " + TR(L.time) : "");
}
/* ⛔ **الفاصلُ «·» بين رقمين هنديين يُقلَب بصرياً**: «الأحد · ٤ أكتوبر · ٢٣
   ربيع الآخر» تُقرأ على الشاشة «الأحد ٤٠ أكتوبر ٢٣٠ ربيع الآخر» — فالنقطةُ
   محايدةُ الاتجاه فتلتصق بالرقم الذي قبلها. وعلامةُ RLM تُثبّت اتجاهَها.
   (شكا منه المستشارُ بلقطةٍ ١ أكتوبر ٢٠٢٦) */
const RLM = "‏";
function joinAr(parts){ return parts.filter(Boolean).join(RLM + " · " + RLM); }

function lessonSub(L){
  /* ⛔ و`L.school` نسخةٌ من `L.stage` (تُكتبان معاً في `ensure`) فلا تُكرَّر */
  return joinAr([L.sector, L.complex, L.stage, L.week, L.day].filter(Boolean).map(TR)
    .concat(perLabel(L) ? [perLabel(L)] : [])
    .concat(L.time ? [TR(L.time)] : []));
}
/* ⚠️ زياراتُ الزائر تُعرف **برقمه الوظيفي** إن وُجد، فالاسمُ يتشابه ويُكتب
   بصيغٍ شتّى. ويُقبل الاسمُ احتياطاً لمن لا رقمَ له في الكشف. */
function isMyVisit(L){
  const e = (ME.emp||"").trim(), n = (ME.name||"").trim();
  if(e && [(L.peer1e||"").trim(), (L.peer2e||"").trim()].indexOf(e) >= 0) return true;
  if(!n) return false;
  /* لا يُطابَق بالاسم على خانةٍ أُسنِدت برقمٍ لشخصٍ آخر */
  if((L.peer1||"").trim() === n && !((L.peer1e||"") && e && L.peer1e !== e)) return true;
  if((L.peer2||"").trim() === n && !((L.peer2e||"") && e && L.peer2e !== e)) return true;
  return false;
}
function myLessons(){
  /* ⛔ المربوطُ بنطاقٍ يرى نطاقَه: كان كلُّ مقيّمٍ يرى الجدولَ كلَّه */
  if(isScopeBound() && !isAdmin()) return DB.sched.filter(inMyScope);
  if(isEval()) return DB.sched;
  /* ⚠️ ومصدرُ «حصصي» واحدٌ مع مصدر «أملك تعديلَها»: كانا اثنين فافترقا. */
  if(ME.role === "teacher") return DB.sched.filter(isMine);
  return DB.sched.filter(isMyVisit);
}
function prog(L){                                   /* تقدّم الحصة */
  const p = DB.prep[L.id], issued = p && p.__issued;
  const obs = Object.keys(DB.obs).filter(k=>k.startsWith(L.id+"|")).length;
  const pr  = Object.keys(DB.peer).filter(k=>k.startsWith(L.id+"|")).length;
  const br  = Object.values(DB.obs).some(o=>o.__lid===L.id && (o.bridge||"").trim());
  return {issued:!!issued, obs, pr, br};
}

/* ───────── شاشة الدخول ───────── */
/* ═════════ بوّابةُ المستشار ═════════
   ⚠️ صفحةٌ ساكنةٌ على مستودعٍ عامّ لا تُخفي سرًّا: من يفتح مصدرَ الصفحة يراه.
      فالمخزونُ هنا **بصمةٌ** لا كلمةٌ — PBKDF2-HMAC-SHA256 بمئةٍ وخمسين ألف
      دورةٍ وملحٍ عشوائي، فاستخراجُ الكلمة منها غيرُ عمليّ. وما تحرسه البوّابةُ
      هو الأزرارُ والأدوات، أما البياناتُ فيحرسها أن عنوانَ المخزن لا يُنشر.
   ⚠️ و`crypto.subtle` لا يعمل على `file://` (سياقٌ غيرُ آمن)، والمستشارُ يفتح
      الملفَّ محلياً أحياناً — فمعه تطبيقٌ خالصٌ يُعطي البصمةَ نفسَها بالضبط. */
const AUTH = (function(){
  /* — SHA-256 خالص — */
  const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
  0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
  0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
  0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
  0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
  0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
  0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
  0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  function sha256(bytes){
    const l=bytes.length, bl=l*8, wl=(((l+8)>>6)+1)<<4, m=new Int32Array(wl);
    for(let i=0;i<l;i++) m[i>>2]|=bytes[i]<<(24-(i%4)*8);
    m[l>>2]|=0x80<<(24-(l%4)*8); m[wl-1]=bl;
    const H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    const w=new Int32Array(64);
    for(let i=0;i<wl;i+=16){
      let a=H[0],b=H[1],c=H[2],d=H[3],e=H[4],f=H[5],g=H[6],h=H[7];
      for(let j=0;j<64;j++){
        if(j<16) w[j]=m[i+j];
        else{ const x=w[j-15],y=w[j-2];
          w[j]=(((x>>>7)|(x<<25))^((x>>>18)|(x<<14))^(x>>>3))+w[j-7]+
               (((y>>>17)|(y<<15))^((y>>>19)|(y<<13))^(y>>>10))+w[j-16]|0; }
        const S1=((e>>>6)|(e<<26))^((e>>>11)|(e<<21))^((e>>>25)|(e<<7));
        const t1=h+S1+((e&f)^(~e&g))+K[j]+w[j]|0;
        const S0=((a>>>2)|(a<<30))^((a>>>13)|(a<<19))^((a>>>22)|(a<<10));
        const t2=S0+((a&b)^(a&c)^(b&c))|0;
        h=g;g=f;f=e;e=d+t1|0;d=c;c=b;b=a;a=t1+t2|0;
      }
      H[0]=H[0]+a|0;H[1]=H[1]+b|0;H[2]=H[2]+c|0;H[3]=H[3]+d|0;
      H[4]=H[4]+e|0;H[5]=H[5]+f|0;H[6]=H[6]+g|0;H[7]=H[7]+h|0;
    }
    const o=new Uint8Array(32);
    for(let i=0;i<8;i++){ o[i*4]=H[i]>>>24&255;o[i*4+1]=H[i]>>>16&255;o[i*4+2]=H[i]>>>8&255;o[i*4+3]=H[i]&255; }
    return o;
  }
  function hmac(key, msg){
    let k = key.length>64 ? sha256(key) : key;
    const ip=new Uint8Array(64), op=new Uint8Array(64);
    for(let i=0;i<64;i++){ const b=i<k.length?k[i]:0; ip[i]=b^0x36; op[i]=b^0x5c; }
    const a=new Uint8Array(64+msg.length); a.set(ip); a.set(msg,64);
    const h1=sha256(a);
    const b2=new Uint8Array(96); b2.set(op); b2.set(h1,64);
    return sha256(b2);
  }
  function pbkdf2JS(pw, salt, it){          /* dkLen = 32 ⇒ كتلةٌ واحدة */
    const b=new Uint8Array(salt.length+4); b.set(salt); b[salt.length+3]=1;
    let u=hmac(pw,b), t=u.slice(0);
    for(let i=1;i<it;i++){ u=hmac(pw,u); for(let j=0;j<32;j++) t[j]^=u[j]; }
    return t;
  }
  const enc = s => new TextEncoder().encode(s);
  const hex = a => Array.from(a).map(b=>b.toString(16).padStart(2,"0")).join("");
  const unhex = s => new Uint8Array(s.match(/../g).map(h=>parseInt(h,16)));
  async function derive(pw, saltHex, it){
    const salt = unhex(saltHex);
    if(typeof crypto !== "undefined" && crypto.subtle){
      try{
        const k = await crypto.subtle.importKey("raw", enc(pw), "PBKDF2", false, ["deriveBits"]);
        const bits = await crypto.subtle.deriveBits(
          {name:"PBKDF2", salt: salt, iterations: it, hash:"SHA-256"}, k, 256);
        return hex(new Uint8Array(bits));
      }catch(e){ /* يسقط إلى الخالص */ }
    }
    return hex(pbkdf2JS(enc(pw), salt, it));
  }
  async function sha256hex(s){ return hex(sha256(enc(s))); }
  return {derive, sha256hex};
})();

/* ⛔ المستشارُ يرى ما لا يراه غيرُه: أدواتِ المخزن ورابطَ الدعوة وسجلَّ
   العمليات والتفريغَ والنسخةَ الاحتياطية. والمقيّمُ (مديرٌ أو وكيلٌ أو مشرف)
   يرى عملَه كلَّه ولا يرى أدواتِ المنظومة. طلبَه المستشارُ ٢٩ سبتمبر ٢٠٢٦. */
function isAdmin(){ return !!ME && ME.role === "admin"; }
/* ═════════ الأدوارُ الخمسة وما يجمعها ═════════
   ⛔ كان «evaluator» دوراً واحداً يجمع المديرَ والوكيلَ والمشرف، ففُصلوا ٢٩
      سبتمبر ٢٠٢٦. وما يُشترك فيه ثلاثتُهم يمرّ بـisEval()، وما يخصّ واحداً
      منهم له حارسُه: isPrincipal() · isDeputy() · isSupervisor().
   ⚠️ ولا يُستبدل نصُّ الشرط داخل هذه التعاريف باستدعاءٍ للدالة نفسِها —
      أصاب ذلك isEval وroleTitle مرّتين فصارتا تستدعيان نفسَيهما. */
/* ⛔ **قرارُ الاجتماع ٣٠ سبتمبر ٢٠٢٦: المقيّمُ هو المشرفُ التربوي وحدَه.**
   والمديرُ يطّلع ويعلّق، والوكيلُ يتأكّد من تعبئة معلميه ويُسنِد الزائرين.
   فانفصل مفهومان كانا واحداً:
     · `canScore()` — من يملأ الاستمارة ويعتمد: المشرفُ وحدَه (ومعه المستشار).
     · `isEval()`   — قيادةٌ ترى المنظومةَ كلَّها: الثلاثةُ كما كانوا.
   ⚠️ وتُركت الخانةُ ev3 للمشرف كما هي فلا تنفصل نتيجةٌ مسجَّلةٌ عن سجلّها. */
const EVAL_ROLES_K = ["principal", "deputy", "supervisor", "cxmgr", "intqa"];

/* ═════════ سجلُّ الإشراف: لكل حصةٍ مشرفُها بالاسم ═════════
   ⛔ كان المشرفُ يختار تخصصَه من قائمة، فيرى حصصَ فريقٍ من مادتين ولا يرى
      كلَّ حصص مادته. صار نطاقُه يُقرأ من سجلّه برقمه الوظيفي: مادتُه
      ومجمعاتُه ومراحلُه ومسارُه — فخطتُه **كلُّ** حصص مادته، لا حصصَ فريق.
   ⚠️ واسمُ المرحلة في الحصة مركَّبٌ («الابتدائية- عرقة») وفي السجلّ مفردٌ،
      فيُقارن أصلُه لا نصُّه كاملاً. */
/* ⛔ **الأرقامُ الهنديةُ كانت تُمحى لا تُقرأ.** كلُّ موضعٍ يقرأ رقماً وظيفياً
   كان يفعل `replace(/\D/g,"")` — و«٢٨٣٣٣» كلُّها غيرُ لاتينيةٍ فتُمحى عن
   آخرها ويبقى نصٌّ فارغ. فمن كتب رقمَه بالعربية — وهو الأصلُ في لوحة مفاتيحه
   وفي بطاقته — لا يدخل، ويُقال له «اكتب رقمك» وقد كتبه.
   (شكا منه المستشارُ بلقطةٍ ١ أكتوبر ٢٠٢٦)
   ⚠️ وتُقبل الفارسيةُ (۰–۹) أيضاً: بعضُ لوحات المفاتيح تُخرجها. */
function latnum(x){
  return String(x == null ? "" : x)
    .replace(/[٠-٩]/g, c=>String(c.charCodeAt(0) - 0x0660))
    .replace(/[۰-۹]/g, c=>String(c.charCodeAt(0) - 0x06f0))
    .replace(/\D/g, "");
}
function supList(){ return D.sups || []; }
function stageBase(st){ return String(st || "").split("- ")[0].trim(); }
function supByEmp(e){
  const k = latnum(e);
  return k ? (supList().find(r=>r.emp === k) || null) : null;
}
function supCovers(r, sector, complex, stage, spec){
  if(!r) return false;
  if((r.sectors || []).indexOf(sector) < 0) return false;
  if((r.complexes || []).indexOf(complex) < 0) return false;
  if((r.stages || []).indexOf(stageBase(stage)) < 0) return false;
  return !!r.allsubj || (r.subjects || []).indexOf(spec) >= 0;
}
function supsForCell(sector, complex, stage, spec){
  return supList().filter(r=>supCovers(r, sector, complex, stage, spec));
}
function supsFor(L){ return L ? supsForCell(L.sector, L.complex, L.stage, L.spec) : []; }
/* ⛔ التخصصُ بلا مشرفٍ لا يبقى بلا تقييم — قرارُ المستشار ٣٠ سبتمبر ٢٠٢٦ */
function isGap(L){ return !!L && supsFor(L).length === 0; }
/* ⛔ **حصةٌ لها مشرفٌ قد لا يحضر**: قرارُ المستشار في مشرفة رياض الأطفال
   العالمي — «حيثُ لا تحضر تساعدها **مديرةُ المدرسة والوكيلةُ التعليمية بذات
   المدرسة** — لا فريقُ المتابعة الرباعي». وهذه الحصةُ ليست «بلا مشرف»،
   فكان الرصدُ محجوزاً على المشرفة وحدَها: إن لم تحضر فلا تقييمَ أبداً.
   و«بذات المدرسة» تُخرج مديرَ المجمع كما تُخرج الفريقَ الرباعي. */
function isAssisted(L){
  const r = supsFor(L);
  return r.length > 0 && r.every(x=>!!x.schoolhelp);
}
/* ومن يَرصد المعان: المدرسةُ وحدَها — لا المجمعُ ولا المتابعة */
function assistRoles(){ return ["principal", "deputy"]; }
/* ⛔ **حارسُ التعارض** (موافقةُ المستشار ٣٠ سبتمبر ٢٠٢٦): المشرفُ في مجمعٍ
   واحدٍ في اليوم. فإن كانت لمشرف هذه الحصة حصةٌ أخرى مسجَّلةٌ في اليوم نفسِه
   من الأسبوع نفسِه في مجمعٍ آخر، فلن يحضر الاثنتين — ويُقال ذلك عند الإدخال
   لا بعد فوات الأسبوع. */
function supConflict(L){
  if(!L || !(L.teacher || "").trim()) return null;
  const mine = supsFor(L);
  if(!mine.length) return null;
  for(const r of mine){
    const other = [];
    (DB.sched || []).forEach(x=>{
      if(!x || x.id === L.id) return;
      if(x.week !== L.week || x.day !== L.day) return;
      if(x.complex === L.complex) return;
      if(!(x.teacher || "").trim()) return;
      if(!supCovers(r, x.sector, x.complex, x.stage, x.spec)) return;
      if(other.indexOf(x.complex) < 0) other.push(x.complex);
    });
    if(other.length) return {name: r.name, other: other};
  }
  return null;
}
/* ⛔ حُذفت `gapTeam()`: معرَّفةٌ ولا يناديها موضعٌ واحد — والميتُ يُحذف لا
   يُصحَّح، وإلّا ظنَّ قارئُها أنّ للفريق اسماً يُشتقُّ من دالّة. (١ أكتوبر) */
/* ⛔ **لم يكن أحدٌ يُعرَّف أيَّ حصةٍ عليه.** `isGap` معرَّفةٌ وتُستعمل في
   `canScore` وحدَها — فلا شارةَ ولا عدَّ ولا مرشِّح. والطريقُ الوحيدُ أن يفتح
   الوكيلُ حصةً حصةً وينظر: أخرجت له الاستمارةُ أم شاشةُ القراءة؟
   وفي البنات **ربعُ الخلايا بلا مشرفٍ مختص** — مُلقاةٌ على الفريق المعاون
   ولا أحدَ يعلم أيُّها، فتبقى بلا رصدٍ حتى يمرّ الأسبوع.
   (أمسكه وكيلُ رحلة الوكيل التعليمي؛ عولج ١ أكتوبر ٢٠٢٦) */
function isMyGap(L){
  if(!L || !ME) return false;
  if(!inMyScope(L)) return false;
  if((D.gapscore || []).indexOf(ME.role) >= 0 && isGap(L)) return true;
  /* ⚠️ والمعانُ يُعدّ مع ما عليه: وإلا بقي بلا شارةٍ ولا عدٍّ كما كان الفراغ */
  return assistRoles().indexOf(ME.role) >= 0 && isAssisted(L);
}
/* عددُ ما عليه من حصصٍ لم تُرصد بعد — يُعرض في الشريط ولا يُبحث عنه */
function myGapCount(){
  try{
    return DB.sched.filter(L=>isMyGap(L)
      && !Object.values(DB.obs || {}).some(v=>v && v.__lid === L.id && v.res && v.res.max > 0)
    ).length;
  }catch(e){ return 0; }
}
/* شارةٌ تُلصق حيث تُعرض الحصة */
function gapTag(L){
  if(!isMyGap(L)) return null;
  /* ⚠️ والشارةُ تقول علّتَها بعينها: «لا مشرفَ لتخصصها» كذبٌ على حصةٍ **لها**
     مشرفٌ قد لا يحضر — فللمعانِ نصُّه. */
  if(isGap(L)){
    const t = el("span","tag no", TR(D.gaptag));
    t.title = TR(D.gaptip);
    return t;
  }
  const t = el("span","tag no", TR(D.asstag));
  t.title = TR(D.asstip);
  return t;
}

/* نطاقُ الداخل: المدرسةُ للمدير والوكيل · المجمعُ لمديره · وما عداهما مفتوح */
function inMyScope(L){
  if(!L || !ME) return false;
  if(ME.role === "cxmgr")
    return L.complex === ME.complex && (!ME.sector || L.sector === ME.sector);
  if(isSchoolBound())
    return L.sector === ME.sector && L.complex === ME.complex && L.stage === ME.school;
  return true;
}
/* ⛔ من يملأ الاستمارة ويعتمد:
     · المشرفُ المختصُّ **لحصته هو** — لا لحصةِ مشرفٍ آخر.
     · فإن لم يكن للتخصص مشرفٌ فالوكيلُ أو المديرُ أو مديرُ المجمع، كلٌّ في نطاقه.
     · وفريقُ متابعة التقويم الداخلي يتابع ولا يرصد. */
function canScore(L){
  if(!ME) return false;
  if(ME.role === "admin") return true;
  if(ME.role === "supervisor"){
    if(!L) return !!supByEmp(ME.emp);
    return supsFor(L).some(r=>r.emp === latnum(ME.emp));
  }
  if((D.gapscore || []).indexOf(ME.role) >= 0 && isGap(L) && inMyScope(L)) return true;
  /* والمعانُ لمدرسته هو — بشرط النطاق كغيره */
  if(assistRoles().indexOf(ME.role) >= 0 && isAssisted(L) && inMyScope(L)) return true;
  return false;
}
function isEval(){ return !!ME && (EVAL_ROLES_K.indexOf(ME.role) >= 0 || ME.role === "admin"); }
function isPrincipal(){ return !!ME && ME.role === "principal"; }
function isDeputy(){ return !!ME && ME.role === "deputy"; }
function isSupervisor(){ return !!ME && ME.role === "supervisor"; }
/* المدرسةُ نطاقٌ ثابتٌ للمدير والوكيل — لا يختارانه في كل شاشة */
function isSchoolBound(){ return isPrincipal() || isDeputy(); }
/* ⛔ **من يُثبَّت نطاقُه عند الدخول فلا يتصفّح غيرَه**: كان مديرُ المجمع
   يختار مجمعَه ثم يبدّله من المرشِّح فيرى المنظومةَ كلَّها، ويحذف فيها.
   (١ أكتوبر ٢٠٢٦) */
function isScopeBound(){ return isSchoolBound() || isCxMgr(); }
function isCxMgr(){ return !!ME && ME.role === "cxmgr"; }
/* من يتنقّل بين المجمعات بتخصصه: المشرفُ والزائر */
function isRoving(){ return isSupervisor() || (ME && ME.role === "peer"); }
/* ⛔ حُذفت `myEvalSlot()`: لم تكن تُنادى من موضعٍ واحد — وصفةُ المقيّم
   تُشتقّ في `evalForms` من خريطة `auto`. والثابتُ الميتُ يُحذف لا يُصحَّح. */
function roleTitle(){
  if(isAdmin()) return TR(D.adminrole || "مديرُ المنصة");
  /* ⚠️ لا تُستبدل هذه السطرُ بـroleTitle() — كان استبدالٌ شاملٌ قد أصابها فصارت
     تستدعي نفسَها بلا نهاية وسقط التطبيقُ كلُّه عند أول رسم. */
  return (D.roles.find(r=>r.k===ME.role)||{}).t || "";
}
/* الدورُ الفعّالُ لترشيح المراحل: `who` في المراحل ما زال يقول "evaluator"،
   فيُترجَم له كلُّ من يقيّم — وتبقى قوائمُ المراحل كما هي بلا مساس. */
function effRole(){ return isEval() ? "evaluator" : ME.role; }

function login(){
  document.body.innerHTML = "";
  applyLang();
  const w = el("div","login");
  /* ⛔ زرُّ اللغة في أول شاشةٍ أيضاً: من لا يقرأ العربية لا يجد سبيلاً إلى
     الإنجليزية لو كان الزرُّ في الهيدر وحدَه — والهيدرُ بعد الدخول. */
  const lb = langBtn("lang top-right");
  lb.style.cssText = "position:absolute;top:14px;inset-inline-end:16px";
  w.style.position = "relative";
  w.appendChild(lb);
  w.appendChild(el("h2","","منصة الحصة الموحَّدة"));
  w.appendChild(el("p","","اختر دورك — ولكل دورٍ ما يخصّه فقط"));
  const rs = el("div","roles");
  let pick = null, picked = null;
  /* ── نطاقُ الدور: يظهر بعد اختياره، ولكل دورٍ سؤالُه لا سؤالُ غيره ── */
  const scope = el("div","scope"); scope.style.display = "none";
  const selSector = el("select"), selComplex = el("select"),
        selSchool = el("select"), selSpec = el("select");
  [["القطاع", selSector], ["المجمع التعليمي", selComplex],
   ["مدرستك", selSchool], ["تخصصك", selSpec]].forEach(([t, e])=>{
    e.setAttribute("aria-label", t);
    const l = el("label","f"); l.appendChild(el("span",null,t)); l.appendChild(e);
    e.__lab = l; scope.appendChild(l);
  });
  const opts = (e, list, keep)=>{
    const cur = keep && list.indexOf(e.value) >= 0 ? e.value : (list[0] || "");
    e.innerHTML = "";
    list.forEach(v=>{ const o = el("option",null,v); o.value = v; e.appendChild(o); });
    e.value = cur;
  };
  const fillComplex = ()=>{
    opts(selComplex, D.complexes[selSector.value] || D.complexlist, true);
    fillSchool();
  };
  const fillSchool = ()=> opts(selSchool, (D.bands[selComplex.value] || [])
      .map(b=>b.stage).filter((v,i,a)=>a.indexOf(v) === i), true);
  opts(selSector, D.sectors); opts(selSpec, D.specs); fillComplex();
  selSector.addEventListener("change", fillComplex);
  selComplex.addEventListener("change", fillSchool);

  const showScope = ()=>{
    const sc = picked ? picked.scope : "";
    scope.style.display = sc ? "" : "none";
    /* ⛔ المدير والوكيل: مدرسةٌ واحدةٌ تُثبَّت. والمشرفُ والزائرُ والمعلم: تخصص. */
    selSector.__lab.style.display  = (sc === "school" || sc === "complex") ? "" : "none";
    selComplex.__lab.style.display = (sc === "school" || sc === "complex") ? "" : "none";
    selSchool.__lab.style.display  = sc === "school" ? "" : "none";
    selSpec.__lab.style.display    = sc === "spec" ? "" : "none";
    whoAmI();
  };
  /* ⛔ **بوّابةُ الدخول كانت لا تُفتح إلا بالفأرة.** البطاقاتُ `div` بمستمعِ
     نقرٍ وحدَه: لا تُركَّز بـTab، ولا تُفتح بالمسافة أو Enter، ولا يُعلن
     قارئُ الشاشة أنها خيارٌ ولا أيُّها مختار — فمن لا يستعمل الفأرةَ **لا
     يدخل المنصةَ أصلاً**. (أمسكه وكيلُ الوصول؛ عولج ١ أكتوبر ٢٠٢٦)
     ⚠️ ولا يكفي `tabindex`: الدورُ (`radio`) وحالةُ الاختيار (`aria-checked`)
        هما ما يجعل قارئَ الشاشة يقول «خيارٌ ١ من ٧، مُحدَّد». */
  D.roles.forEach((r, ri)=>{
    const b = el("div","role");
    b.setAttribute("role", "radio");
    b.setAttribute("aria-checked", "false");
    b.setAttribute("aria-label", TR(r.t) + " — " + TR(r.d));
    b.tabIndex = 0;
    b.appendChild(el("b",null,r.t));
    b.appendChild(el("span",null,r.d));
    const take = ()=>{
      pick = r.k; picked = r;
      [...rs.children].forEach(x=>{ x.classList.remove("on"); x.setAttribute("aria-checked","false"); });
      b.classList.add("on"); b.setAttribute("aria-checked","true");
      showScope();
    };
    b.addEventListener("click", take);
    b.addEventListener("keydown", e=>{
      if(e.key === " " || e.key === "Enter" || e.key === "Spacebar"){
        e.preventDefault(); take(); return;
      }
      /* الأسهمُ تتنقّل بين الخيارات كما في أي مجموعةِ اختيار */
      const ks = ["ArrowDown","ArrowRight","ArrowUp","ArrowLeft"];
      const i = ks.indexOf(e.key);
      if(i < 0) return;
      e.preventDefault();
      const kids = [...rs.children];
      const to = kids[(ri + (i < 2 ? 1 : kids.length - 1)) % kids.length];
      if(to) to.focus();
    });
    rs.appendChild(b);
  });
  rs.setAttribute("role", "radiogroup");
  rs.setAttribute("aria-label", "اختر دورك");
  w.appendChild(rs);
  /* ⛔ الرقمُ الوظيفي هو الهوية: الأسماءُ تتشابه وتُكتب بصيغٍ شتّى، فيظهر الشخصُ
     مرّتين في التقارير. فإن وُجد الرقمُ في الكشف استُدعي الاسمُ منه ولم يُكتب. */
  const hasR = D.roster && Object.keys(D.roster).length;
  const no = el("input"); no.type = "text"; no.inputMode = "numeric";
  const _lens = empLens();
  no.placeholder = (_lens && D.emplen)
    ? "الرقم الوظيفي (" + arn(D.emplen) + " منازل)"
    : "الرقم الوظيفي";
  no.setAttribute("aria-label","الرقم الوظيفي");
  const nm = el("input"); nm.type="text"; nm.placeholder="الاسم الأول واسم العائلة";
  nm.setAttribute("aria-label","الاسم");
  const found = el("div","whois");
  /* ⛔ المشرفُ لا يُسأل عن تخصصه: يُقرأ من سجلّه ويُعرض عليه ليراه قبل الدخول */
  function whoAmI(){
    const k = latnum(no.value);
    if(pick !== "supervisor") return false;
    const r = supByEmp(k);
    if(r){
      nm.value = r.name; nm.readOnly = true;
      found.className = "whois ok";
      found.textContent = r.name + " — "
        + (r.allsubj ? TR("إشرافٌ بالمرحلة") : r.subjects.map(TR).join(" · "))
        + " · " + r.stages.map(TR).join(" + ")
        + " · " + r.complexes.map(TR).join(" + ")
        + " · " + r.sectors.map(TR).join(" + ");
    } else {
      nm.readOnly = false;
      const e = k ? empError(k, "supervisor") : "";
      found.className = "whois" + (e ? " no" : "");
      found.textContent = TR(e);
    }
    return true;
  }
  no.addEventListener("input", ()=>{
    if(whoAmI()) return;
    const k = latnum(no.value);
    const r = D.roster[k];
    if(r){
      nm.value = r.n; nm.readOnly = true;
      found.className = "whois ok";
      /* ⚠️ لغةُ الكشف غيرُ لغة المنصة (E · حاسب آلي · إسلامية)، فتُترجم.
         و«أخرى» تُترك فارغةً يختارها صاحبُها — لا يُخمَّن له تخصص. */
      const sp = (D.specmap || {})[r.s] || "";
      if(sp && D.specs.indexOf(sp) >= 0) selSpec.value = sp;
      if(D.complexes[selSector.value] && D.complexes[selSector.value].indexOf(r.c) >= 0){
        selComplex.value = r.c; fillSchool();
      }
      found.textContent = r.n + " — " + TR(r.s) + (sp && sp !== r.s ? " (" + TR(sp) + ")" : "")
                        + " · " + r.g + " · مجمع " + r.c + " · " + r.k
                        + (sp ? "" : " — تخصصُه «أخرى»، فاختره بنفسك.");
    } else {
      nm.readOnly = false;
      /* ⚠️ الرسالةُ تُقال أثناء الكتابة لا عند الضغط، وتُسمّي العلّةَ بعينها
         — وتُقال **بالدور المختار**: بغيره تُطالِب قائداً بعضوية كشف المعلمين. */
      const e = k ? empError(k, pick) : "";
      found.className = "whois" + (e ? " no" : "");
      found.textContent = TR(e); }
  });
  w.appendChild(no); w.appendChild(found); w.appendChild(nm);
  nm.style.marginBottom="12px";
  w.appendChild(scope);
  const go = el("button","b","دخول");
  go.addEventListener("click", ()=>{
    if(!pick) return alert("اختر دورك أولاً.");
    /* ⛔ التحقّقُ قبل الدخول لا بعده: ما يدخل المخزنَ لا يُصحَّح لاحقاً. */
    const eE = empError(no.value, pick);
    if(eE){ found.className = "whois no"; found.textContent = TR(eE); no.focus(); return alert(eE); }
    const nE = nameError(nm.value);
    if(nE) return alert(nE);
    const sc = picked.scope;
    ME = {role:pick, name:nm.value.trim(), emp:latnum(no.value)};
    if(sc === "school"){
      if(!selSchool.value) return alert("اختر مدرستك — عليها يُبنى كلُّ ما تراه.");
      ME.sector = selSector.value; ME.complex = selComplex.value; ME.school = selSchool.value;
    } else if(sc === "spec"){
      if(!selSpec.value) return alert("اختر تخصصك — به تُعرف حصصك وزياراتك.");
      ME.spec = selSpec.value;
      const cx = selComplex.value;
      if(cx) ME.complex = cx;
    } else if(sc === "sup"){
      /* ⛔ نطاقُ المشرف من سجلّه لا من اختياره — وقد تحقّق منه empError */
      const r = supByEmp(ME.emp);
      if(!r) return alert("هذا الرقمُ ليس في سجلّ الإشراف التربوي.");
      ME.name = r.name;
    } else if(sc === "complex"){
      if(!selComplex.value) return alert("اختر مجمعك — عليه يُبنى كلُّ ما تراه.");
      ME.sector = selSector.value; ME.complex = selComplex.value;
    }
    localStorage.setItem(KEY+"_me", JSON.stringify(ME));
    /* ⚠️ حالةُ الترشيح تُبنى من جديدٍ على نطاق الداخل، وإلا ورث سياقَ سابقه */
    try{ localStorage.removeItem(KEY+"_ctx"); }catch(e){}
    GS = null;
    PH = isEval() ? 1 : (pick === "peer" ? 5 : 2);
    boot();
  });
  w.appendChild(go);
  const note = el("p"); note.style.cssText="margin-top:16px;font-size:14px";
  note.textContent = TR("بياناتك تُحفظ في هذا الجهاز، وتصل إلى المنظومة عبر الرابط الذي زُوّدت به.");
  w.appendChild(note);
  /* ── مدخلُ المستشار: سطرٌ خفيفٌ لا بطاقةٌ بين البطاقات ── */
  if(D.admin){
    const al = el("button","lnk","دخول المستشار ومدير المنصة");
    al.style.cssText = "margin-top:10px;font-size:14px";
    al.addEventListener("click", adminLogin);
    w.appendChild(al);
  }
  if(D.build){ const bs = el("div","bst", D.build); bs.style.marginTop = "10px"; w.appendChild(bs); }
  document.body.appendChild(w);
}


/* ═════════ دخولُ المستشار ═════════
   ⚠️ صراحةً: صفحةٌ ساكنةٌ على مستودعٍ عامّ لا تُخفي محتواها عمّن يقرأ مصدرَها،
      وهذه البوّابةُ تحرس **الأدواتِ** لا البيانات. وحارسُ البيانات الحقيقي أن
      عنوانَ المخزن لا يُنشر، وأن الخادمَ وحدَه يملكها. */
function adminLogin(){
  document.body.innerHTML = "";
  const w = el("div","login");
  w.appendChild(el("h2","","دخولُ المستشار"));
  w.appendChild(el("p","","البريدُ وكلمةُ المرور — ولك وحدك أدواتُ المنظومة"));
  const em = el("input"); em.type="email"; em.placeholder="البريد";
  em.setAttribute("aria-label","البريد"); em.autocomplete="username";
  const pw = el("input"); pw.type="password"; pw.placeholder="كلمة المرور";
  pw.setAttribute("aria-label","كلمة المرور"); pw.autocomplete="current-password";
  pw.style.marginBottom="12px";
  const msg = el("div","whois");
  w.appendChild(em); w.appendChild(pw); w.appendChild(msg);
  const go = el("button","b","دخول");
  const tryIn = ()=>{
    const e = (em.value||"").trim().toLowerCase(), k = pw.value || "";
    if(!e || !k){ msg.className="whois no"; msg.textContent=TR("اكتب البريد وكلمة المرور."); return; }
    go.disabled = true; msg.className="whois"; msg.textContent=TR("يُتحقَّق…");
    AUTH.sha256hex("cls-user|" + e).then(uh=>
      AUTH.derive(k, D.admin.s, D.admin.it).then(ph=>{
        /* ⚠️ المقارنةُ على الاثنين معاً، ورسالةُ الخطأ واحدةٌ لا تُفرّق بينهما */
        if(uh === D.admin.u && ph === D.admin.h){
          ME = {role:"admin", name: D.owner || "مدير المنصة", emp:""};
          localStorage.setItem(KEY+"_me", JSON.stringify(ME));
          PH = 1; boot();
        } else {
          go.disabled = false; pw.value = "";
          msg.className="whois no"; msg.textContent=TR("البريدُ أو كلمةُ المرور غيرُ صحيحة.");
        }
      })).catch(()=>{ go.disabled=false; msg.className="whois no";
                      msg.textContent=TR("تعذّر التحقّق في هذا المتصفح."); });
  };
  go.addEventListener("click", tryIn);
  pw.addEventListener("keydown", ev=>{ if(ev.key === "Enter") tryIn(); });
  w.appendChild(go);
  const bk = el("button","lnk","‹ رجوعٌ إلى اختيار الدور");
  bk.style.cssText="margin-top:14px;font-size:14px";
  bk.addEventListener("click", login);
  w.appendChild(bk);
  if(D.build){ const bs = el("div","bst", D.build); bs.style.marginTop="10px"; w.appendChild(bs); }
  document.body.appendChild(w);
}

/* ═════════ ترتيبُ المراحل ═════════
   ⚠️ مصدرٌ واحدٌ للشريط الجانبي ولأسهم «السابق/التالي» في الهيدر — وإلا تنقّل
      السهمُ إلى مرحلةٍ لا يراها صاحبُها في الشريط. */
/* ═════════ نصُّ المرحلة يتبع قارئَه ═════════
   ⛔ كان نصُّ كل مرحلةٍ واحداً للجميع، فيقرأ مديرُ المدرسة والوكيلُ والمشرفُ
      في «الاستعداد والتحضير»: «اختر حصتك من الجدول» و«املأ خانات التحضير» —
      وهم لا يحضّرون، بل يقرؤون تحضيرَ المعلم ليعرفوا ما يبحثون عن شواهده.
      وفي «تنفيذ الحصة»: «يُمسكها المعلم» — وهم يقرؤونها قبل الدخول.
      نبّه عليه المستشارُ ٢٩ سبتمبر ٢٠٢٦: «أي نصوص لا تعني المستخدم فقم
      بحذفها من لوحاتهم».
   ⚠️ والمرحلةُ نفسُها تبقى (فهم يحتاجون قراءتَها) — الذي يتغيّر اسمُها وشرحُها. */
/* ⛔ **دالّةٌ لا ثابت**: كان ثابتاً يُبنى عند تحميل الشفرة، واللغةُ عربيةٌ
   حينها (الافتراضُ عربيّ)، فتُثبَّت نصوصُه عربيةً ولا يغيّرها تبديلُ اللغة
   بعدها. فظهرت شروحُ مراحل المعلم الزائر والمقيّم عربيةً في الشاشة
   الإنجليزية — ومفاتيحُها في المعجم سليمة. (٣٠ سبتمبر ٢٠٢٦) */
function PHASE_BY_ROLE_OF(){ return {
  2: {
    eval: {t: "تحضيرُ المعلم", s: "تقرؤه قبل الحصة — منه تعرف ما تبحث عن شواهده",
          why: "التحضير توأمُ الاستمارة: كل خانةٍ فيه يقابلها مؤشرٌ تبحث عن شاهده. "
             + "فاقرأه قبل أن تدخل — تدخل وأنت تعرف ما ينوي المعلمُ فعله، لا تكتشفه معه. "
             + "وما لم يُكتب هنا لا يُفترض في الحصة.",
          steps: ["افتح الحصة من الجدول أو من لوحتك.",
                  "اقرأ خريطة الزمن ومراحل الحصة وبطاقة الإستراتيجية.",
                  "ولا تُعدّل شيئاً هنا — التحضيرُ ملكُ صاحبه."]},
  },
  /* ⛔ شريطُ المعلم الزائر أُعيد توظيفُه، ونصوصُ مراحله بقيت للمعلم والمقيّم:
     كان يُقرأ له «يُمسكها المعلمُ في الحصة» و«ارصد الاستمارة مؤشراً مؤشراً»
     و«اطبع تقرير الزيارة وأرسله للمعلم» — وهو لا يمسك الورقةَ ولا يرصد
     استمارةً ولا يُصدر تقريراً. فلكلِّ مرحلةٍ نصُّه هو. (٢٩ سبتمبر ٢٠٢٦)

     ⚠️ وصياغتُها تتجنّب المضارعَ المخاطَبَ («تعرف») وتاءَ الفاعل المفتوحةَ
        («شاهدتَه»): لا قاعدةَ لهما في lfem، وإضافةُ قاعدةٍ عامّةٍ تُفسد
        المضارعَ المؤنَّثَ الغائب («تظهر النتيجة»). فقِيس كلُّ نصٍّ هنا على
        مخرَج البنات قبل إدخاله — والسبعةَ عشرَ نصّاً تخرج مؤنَّثةً بلا بقية. */
  3: {
    peer: {t: "بطاقةُ الزيارة", s: "تُملأ أثناء الحصة أو بعدها مباشرةً",
          why: "زيارتُك إفادةٌ لا درجة: لا استمارةَ مقيّمين عليك ولا مؤشراتٍ تُقيَّم، "
             + "بل وصفُ ما جرى في الحصة، وما أفادك منه، وما ستطبّقه. "
             + "وما يُكتب بعد أيامٍ يذهب أكثرُه.",
          steps: ["اقرأ تحضير زميلك أولاً — فمنه تُعرف مواضعُ الانتباه.",
                  "املأ بطاقة الأقران أثناء الحصة أو بعدها مباشرةً.",
                  "ولا درجةَ عليك: الدرجةُ للمشرفين وقيادة المدرسة."]},
  },
  4: {
    peer: {t: "إجراؤك أنت", s: "ثمرةُ الزيارة — إجراءٌ واحدٌ إلى حصتك",
          why: "آخرُ خطوةٍ في زيارتك ليست حكماً على زميلك، بل التزامٌ على نفسك: "
             + "إجراءٌ واحدٌ محدَّدٌ إلى حصتك القادمة. وهو ما يُتابَع معك أنت.",
          steps: ["اكتب إجراءً واحداً محدَّداً يمكن رؤيته في حصتك.",
                  "وتظهر نتيجةُ الحصة إن رصدها المقيّمون — للاطّلاع لا للتعديل."]},
  },
  6: {
    peer: {t: "تحضيرُ زميلك", s: "اقرأه قبل دخولِ الفصل",
          why: "ورقةٌ مختصرةٌ فيها ما سيُنفَّذ في الحصة: خريطةُ الزمن ومراحلُها "
             + "وبطاقةُ الإستراتيجية. والدخولُ على علمٍ بما سيجري خيرٌ من اكتشافه فيها.",
          steps: ["افتح الزيارة المسنَدة إليك، ثم اقرأ الورقة كاملةً.",
                  "اطبعها أو افتحها على جوالك لتكون بين يديك في الحصة."]},
    eval: {t: "ورقةُ التنفيذ", s: "خلاصةُ التحضير في صفحة — تُقرأ قبل الدخول",
          why: "ورقةٌ مختصرةٌ تجمع ما سيُنفَّذ: خريطةُ الزمن ومراحلُ الحصة وبطاقةُ "
             + "الإستراتيجية والمهمتان المكيَّفة والإثرائية. يُمسكها المعلمُ في الحصة، "
             + "وتقرؤها أنت قبل دخولك فتعرف ما تبحث عن شواهده.",
          steps: ["افتح الحصة، ثم اقرأ الورقة كاملةً.",
                  "اطبعها أو افتحها على جوالك لتكون بين يديك في الحصة."]},
  },
}; }
function phaseFor(p){
  const k = isEval() ? "eval" : ME.role;
  const o = (PHASE_BY_ROLE_OF()[p.id] || {})[k];
  return o ? Object.assign({}, p, o) : p;
}

function navItems(){
  let items = D.phases.filter(p=>p.who.includes(effRole()))
    .map(phaseFor).map(p=>({id:p.id, t:p.t, s:p.s}));
  const mine5 = isEval()
    ? {id:5, t:"لوحة المدرسة والتقارير", s:"تقارير التفعيل والنتائج"}
    : (ME.role === "teacher"
        ? {id:5, t:"تقريري", s:"حصصك ودرجاتُها وإجراءاتُ جسرك"}
        : {id:5, t:"زياراتي المسنَدة", s:"ابدأ من هنا — ما أُسنِد إليك وما بقي"});
  /* ⛔ شريطُ المعلم الزائر: أربعُ خطواتٍ بترتيب زيارته، تبدأ بما أُسنِد إليه،
     وبأسماءٍ تقول له ما يفعل لا ما اسمُ المرحلة — ولا مصفوفةَ جدولةٍ لا يجدولها.
     «حتى لا يضل ويتوه» (٢٩ سبتمبر ٢٠٢٦). */
  if(ME.role === "peer"){
    /* ⛔ كان هنا جدولُ أسماءٍ ثانٍ، فاختلف ما في الشريط عمّا في رأس الشاشة
       والزائرُ يظنُّهما شاشتين. والاسمُ الآن من PHASE_BY_ROLE وحده. */
    return [mine5].concat(
      [6, 3, 4].map(id=>items.find(x=>x.id === id)).filter(Boolean));
  }
  /* ═════════ شريطُ المستشار ═════════
     ⛔ كان شريطُه شريطَ المعلم حرفياً: «الاستعداد والتحضير» و«تنفيذ الحصة»
        و«رصد الحصة» — وهو لا يحضّر ولا ينفّذ ولا يرصد، والنصوصُ تخاطبه
        بـ«اختر حصتك» و«املأ خانات التحضير». نبّه عليه المستشارُ ٢٩ سبتمبر
        ٢٠٢٦: «ليس من الصحيح أن تظهر له هذه العناصر مثله كالمعلم تماماً».
     فصار شريطُه أربعةَ بنودٍ هي عملُه فعلاً: يرى الحالَ، ويهيّئ الجدول،
     ويقرأ التقارير، ويملك أدواتِ المنظومة. ويفتح أي حصةٍ للمراجعة من
     اللوحة أو التقارير — مراجعةً لا تنفيذاً. */
  if(isAdmin()) return [
    {id: 7, t: "لوحةُ المنظومة", s: "حالُ التفعيل في سطرٍ واحد — وما يحتاج تدخّلك"},
    {id: 1, t: "الجدول والإسناد", s: "تهيئةُ الحصص وإسنادُ الزائرين ومتابعتُهما"},
    {id: 5, t: "التقارير", s: "سبعةُ تقاريرَ تُطبع وتُصدَّر"},
    {id: 8, t: "أدواتُ المنصة", s: "المخزن · الدعوة · السجلّ · السلّة · النسخة · التفريغ"},
  ];
  items.push(mine5);
  return items;
}

/* ───────── الهيكل ───────── */
/* ⚠️ استعادةُ التركيز بعد إعادة البناء: من كان يكتب يعود إلى موضعه.
   ولا تُستعاد إلا بطلبٍ صريح (`__refocus`) فلا تُخطف من عنصرٍ آخر. */
function refocusAfterRender(){
  const k = window.__refocus;
  if(!k) return viewFocus();
  window.__refocus = null;
  const e = document.querySelector('[data-refocus="' + k + '"]');
  if(!e) return;
  try{
    e.focus();
    const n = (e.value || "").length;
    if(e.setSelectionRange) e.setSelectionRange(n, n);
  }catch(x){}
}
/* ⛔ **كلُّ رسمٍ يمحو الصفحةَ كلَّها** (`body.innerHTML = ""`) فيسقط التركيزُ
   إلى `body`: من يتنقّل بلوحة المفاتيح يعود إلى أوّل الصفحة بعد كل نقلةٍ
   فيَمسح الهيدرَ والشريطَ من جديدٍ ليصل إلى عمله، ومن يسمع الشاشةَ لا يُخبَر
   أنّ الشاشةَ تغيّرت أصلاً. فيُنقل التركيزُ إلى `main` **عند تغيّر الشاشة
   وحدَه** — لا في كل رسم، وإلّا خُطف من صندوقٍ يُكتب فيه. (١ أكتوبر ٢٠٢٦) */
function viewFocus(){
  try{
    const key = String(PH) + "|" + ((GS && GS.tab) || "") + "|"
              + (typeof RPT === "undefined" ? "" : (RPT || "")) + "|"
              + (typeof CUR === "undefined" ? "" : (CUR || ""));
    if(window.__lastView === key) return;
    const first = window.__lastView === undefined;
    window.__lastView = key;
    if(first) return;                       /* أولُ رسمٍ ليس نقلةً */
    if(window.__wasTyping) return;          /* سُجِّل قبل محو الصفحة */
    const m = document.getElementById("main");
    if(!m) return;
    m.tabIndex = -1;
    m.setAttribute("aria-label", TR("محتوى الشاشة"));
    m.focus({preventScroll: true});
  }catch(e){}
}
function render(){ shell(); }
/* ═════════ زرُّ تبديل اللغة ═════════
   ⛔ في الهيدر كما طلب المستشار (٣٠ سبتمبر ٢٠٢٦) — وفي شاشة الدخول أيضاً،
      فمعلمُ العالمي يقرأ «اختر دورك» قبل أن يصل إلى الهيدر. ولو لم يكن في
      الأولى لم يجد الإنجليزيَّ سبيلاً إلى الإنجليزية. */
function langBtn(cls){
  const b = el("button", cls || "lang", LANG === "en" ? "عربي" : "EN");
  b.title = LANG === "en" ? "التبديل إلى العربية" : "Switch to English";
  b.setAttribute("aria-label", b.title);
  b.addEventListener("click", ()=>setLang(LANG === "en" ? "ar" : "en"));
  return b;
}
function shell(){
  autoPull();
  /* ⛔ **الحالُ تُسجَّل قبل المحو**: `innerHTML = ""` يُفني الخانةَ المركَّزةَ
     فيصير `activeElement` هو `body` — فلو سأل `viewFocus` بعدها لم يعرف أنّ
     المستخدمَ كان يكتب، فخطفَ تركيزَه إلى المحتوى وهو في منتصف كلمة.
     (أمسكه شاهدُ `focuscheck` ١ أكتوبر ٢٠٢٦ — فالفحصُ قبل الدعوى.) */
  const _ae = document.activeElement, _at = _ae && _ae.tagName;
  window.__wasTyping = (_at === "INPUT" || _at === "TEXTAREA" || _at === "SELECT");
  document.body.innerHTML = "";
  const top = el("header","top"), tw = el("div","wrap row");
  const left = el("div"); left.style.cssText="display:flex;align-items:center;gap:12px";
  if(LOGO){ const g=document.createElement("img"); g.src="data:image/jpeg;base64,"+LOGO; left.appendChild(g); }
  const ttl = el("div");
  ttl.appendChild(el("h1",null,"منصة الحصة الموحَّدة"));
  ttl.appendChild(el("div",null,D.school)).style.cssText="font-family:JZL,SK;font-size:14px;opacity:.9";
  left.appendChild(ttl);
  /* تنقّلٌ بين المراحل من الهيدر: السابق والتالي ضمن مراحل هذا الدور */
  const seq = navItems().map(p=>p.id);
  const at = seq.indexOf(PH);
  const nav2 = el("div","pnav");
  const mkn = (t, to, dis) => {
    const b = el("button", dis ? "off" : "", t);
    if(!dis) b.addEventListener("click", ()=>{ PH = to; shell(); window.scrollTo(0,0); });
    b.disabled = !!dis; nav2.appendChild(b);
  };
  mkn("◄ السابق", seq[at-1], at <= 0);
  nav2.appendChild(el("i",null, TR("المرحلة ") + arn(at+1) + TR(" من ") + arn(seq.length)));
  mkn("التالي ►", seq[at+1], at < 0 || at >= seq.length-1);
  const me = el("div","me");
  me.appendChild(langBtn());
  me.appendChild(el("span",null,TR(roleTitle()) + " · " + ME.name));
  const sv = el("span"); sv.id="syn"; sv.style.cssText="font-size:13px;color:#bfe3c9"; me.appendChild(sv);
  const ob = el("button",null,"خروج");
  ob.addEventListener("click", ()=>{ localStorage.removeItem(KEY+"_me"); ME=null; login(); });
  me.appendChild(ob);
  tw.appendChild(left); tw.appendChild(nav2); tw.appendChild(me); top.appendChild(tw); document.body.appendChild(top);

  /* ── الشريط الجانبي الأيمن: مراحل الدور المختار ── */
  const wide = localStorage.getItem(KEY+"_wide") === "1";
  const body = el("div","body" + (wide ? " wide" : ""));
  const side = el("aside","side");
  /* طيُّ الشريط الجانبي: الجدولُ عريضٌ فيأخذ الشاشةَ كلَّها عند الحاجة */
  const fold = el("button","fold", wide ? "‹" : "›");
  fold.title = wide ? "إظهار الشريط" : "طيُّ الشريط لتوسيع الجدول";
  fold.addEventListener("click", ()=>{
    localStorage.setItem(KEY+"_wide", wide ? "0" : "1"); shell();
  });
  side.appendChild(fold);
  const PEER = ME.role === "peer";
  const sh0 = el("div","sh");
  sh0.appendChild(el("b",null, PEER ? "خطواتُ زيارتك" : "مراحل التطبيق"));
  sh0.appendChild(el("i",null,roleTitle()));
  side.appendChild(sh0);
  const nav = el("nav");
  const items = navItems();
  if(PEER){
    /* عدّادٌ يقول للزائر ما ينتظره بلا أن يفتح شيئاً */
    const asg = DB.sched.filter(isMyVisit);
    const doneIds = new Set(Object.keys(DB.peer)
      .filter(k=>k.split("|")[1] === (ME.name||"").trim()).map(k=>k.split("|")[0]));
    const left = asg.filter(L=>!doneIds.has(L.id)).length;
    const bx = el("div","cw");
    bx.appendChild(el("div","cwh","زياراتك"));
    bx.appendChild(el("div","cwt", left ? arn(left) + " زيارةً تنتظر بطاقتك"
                                        : (asg.length ? "أتممتَ زياراتك كلَّها ✓"
                                                      : "لا زياراتٍ مسنَدةً إليك بعد")));
    if(!asg.length) bx.appendChild(el("div","cws",
      "يُسنِدها وكيلُ المدرسة التعليمي — راجعه إن تأخّرت."));
    side.appendChild(bx);
  }
  /* ⛔ **وللفريق المعاون عدّادُه كذلك.** كان للزائر وحدَه، والوكيلُ ومديرُ
     المدرسة ومديرُ المجمع لا يعلمون أن عليهم شيئاً إلا بفتح حصةٍ حصة.
     وفي البنات ربعُ الخلايا بلا مشرفٍ مختص. (١ أكتوبر ٢٠٢٦) */
  else if((D.gapscore || []).indexOf(ME.role) >= 0){
    const n = myGapCount();
    const all = DB.sched.filter(isMyGap).length;
    const bx = el("div","cw");
    bx.appendChild(el("div","cwh","حصصٌ عليك"));
    bx.appendChild(el("div","cwt", n ? arn(n) + " حصةً تنتظر رصدَك"
                                     : (all ? "رصدتَ ما عليك كلَّه ✓"
                                            : "لا حصةَ بلا مشرفٍ مختصٍّ في نطاقك")));
    bx.appendChild(el("div","cws",
      "وهي الحصصُ التي لا مشرفَ لتخصصها — ولولا الفريق المعاون لبقيت بلا تقييم."));
    side.appendChild(bx);
  }
  items.forEach(p=>{
    const b = el("button", p.id===PH ? "on" : "");
    /* ⛔ العددُ موضعُ المرحلة في مسار هذا الدور لا معرّفُها الداخلي: كان
       الشريطُ يقرأ ١ · ٢ · ٦ · ٣ · ٤ · ٥ لأن «تنفيذ الحصة» أُضيفت متأخرةً
       بمعرّف ٦ ووضعُها الثالث. والمعرّفُ يبقى كما هو لأن التوجيهَ عليه.
       (٢٩ سبتمبر ٢٠٢٦) */
    b.appendChild(el("i",null,arn(items.indexOf(p) + 1)));
    const tx = el("span");
    tx.appendChild(el("b",null,p.t));
    tx.appendChild(el("small",null,p.s));
    b.appendChild(tx);
    /* ⛔ **على الجوال كانت تُرى مرحلةٌ واحدةٌ من ستّ**: كلُّ زرٍّ بعرض نصِّه
       كاملاً في سطر (`flex:0 0 auto`) فمجموعُها ١٠٤٨ بكسلاً في شريطٍ عرضُه
       ٣٦٠ — أوّلُها وحدَه ٣٠٤. فلا يعلم فاتحُ المنصة على جواله أنّ خلفَه
       خمسَ مراحل، ولا أنّ الشريطَ يُسحب. فصار شريطَ خُطواتٍ: الحاليةُ باسمها
       والبواقي بأرقامها (قاعدةُ CSS، فلا تنكسر عند تدوير الجهاز)، ولكلٍّ
       اسمُها الكاملُ في `aria-label` و`title` فلا يضيع على قارئ الشاشة ولا
       على من يَمسّ مطوَّلاً. (قِيس على ٣٩٠ و٤٣٠ و٧٦٨ — ١ أكتوبر ٢٠٢٦) */
    const full = TR(p.t) + (p.s ? " — " + TR(p.s) : "");
    b.setAttribute("aria-label", arn(items.indexOf(p) + 1) + " · " + full);
    b.title = full;
    if(p.id === PH) b.setAttribute("aria-current", "step");
    b.addEventListener("click", ()=>{ PH=p.id; shell(); });
    if(p.id === PH) nav.__cur = b;
    nav.appendChild(b);
  });
  side.appendChild(nav);
  /* ⛔ **والشريطُ يسحب نفسَه إلى خطوتك**: ستُّ خطواتٍ في ٣٦٠ بكسلاً تُرى منها
     أربعٌ، فمن كان في الخامسة أو السادسة رأى أرقاماً ليست خطوتَه ولم يرَ
     اسمَها — وهو موضعُه الحالي. يُنادى بعد الإلحاق فيكون للعنصر قياسٌ.
     (١ أكتوبر ٢٠٢٦) */
  if(nav.__cur) setTimeout(()=>{
    try{
      const b = nav.__cur, nr = nav.getBoundingClientRect(), br = b.getBoundingClientRect();
      if(br.left < nr.left || br.right > nr.right)
        b.scrollIntoView({block:"nearest", inline:"center"});
    }catch(e){}
  }, 0);
  /* الحصة المفتوحة، ونقلةٌ سريعة بين مراحلها */
  const L0 = DB.sched.find(x=>x.id===CUR);
  if(L0){
    const cw = el("div","cw");
    cw.appendChild(el("div","cwh","الحصة المفتوحة"));
    cw.appendChild(el("div","cwt", lessonTitle(L0)));
    cw.appendChild(el("div","cws", lessonSub(L0)));
    const g0 = prog(L0);
    const tg = el("div","cwg");
    const tag = (ok,txt)=>tg.appendChild(el("span","tag " + (ok?"ok":"no"), txt));
    tag(g0.issued,"التحضير");
    tag(g0.obs>0,"الرصد " + arn(g0.obs) + "/٣");
    tag(g0.pr>0,"الأقران " + arn(g0.pr) + "/٢");
    cw.appendChild(tg);
    const cb = el("button","b ghost sm","إغلاق الحصة");
    cb.addEventListener("click", ()=>{ CUR=null; shell(); });
    cw.appendChild(cb);
    side.appendChild(cw);
  }
  const st0 = el("div","stbox " + (api() ? "linked" : "local"));
  if(api()){
    /* ⛔ أدواتُ المخزن — الحالةُ و«تحديث» و«رابط الدعوة» و«تغيير» — للمستشار
       وحده. كان يراها كلُّ مقيّمٍ (مديرٌ ووكيلٌ ومشرف)، فطلبَ المستشارُ حصرَها
       فيه: «وهذه كذلك لا تظهر إلا لي أنا فقط كمستشار ومدير للمنصة» (٢٩ سبتمبر
       ٢٠٢٦). وغيرُه لا يرى شيئاً، وتُسحب له البياناتُ تلقائياً عند التنقّل. */
    if(!isAdmin()){ st0.style.display = "none"; }
    else {
      const ln = el("div","okline");
      ln.appendChild(el("b",null,"متصلٌ بمخزن المنظومة"));
      const rf = el("button","lnk","تحديث");
      rf.addEventListener("click", ()=>pull().then(()=>shell()));
      ln.appendChild(rf);
      const inv = el("button","lnk","رابط الدعوة");
      inv.addEventListener("click", invite);
      ln.appendChild(inv);
      const ch = el("button","lnk","تغيير");
      ch.addEventListener("click", srv);
      ln.appendChild(ch);
      st0.appendChild(ln);
    }
  } else if(isAdmin()){
    st0.appendChild(el("b",null,"الحفظ على هذا الجهاز فقط"));
    st0.appendChild(el("span",null,
      "المكتوبُ هنا لا يصل إلى بقية المنظومة، ولا يصل منها شيء — والعلاجُ ربطُ الخادم مرةً واحدة."));
    const sbtn = el("div","stb");
    const lk = el("button","b sm","اربط الخادم");
    lk.addEventListener("click", srv); sbtn.appendChild(lk);
    if(D.guide){
      const gd = el("a","b ghost sm","كيف؟"); gd.href = D.guide; gd.target = "_blank";
      gd.style.textDecoration = "none"; sbtn.appendChild(gd);
    }
    st0.appendChild(sbtn);
  } else {
    /* معلمٌ أو زائرٌ بلا خادم: تنبيهٌ صامتٌ بلا أزرار — الربطُ ليس من شأنه */
    st0.appendChild(el("b",null,"غير متصلٍ بالمنظومة"));
    st0.appendChild(el("span",null,"راجع إدارة التخطيط والاعتماد لتزويدك برابط الدخول الصحيح."));
  }
  side.appendChild(st0);
  const sf = el("div","sf");
  sf.appendChild(el("div",null,D.school));
  if(D.build) sf.appendChild(el("div","bst", D.build));
  side.appendChild(sf);

  const m = el("main"), mw = el("div","mwrap"); m.id = "main"; m.appendChild(mw);
  body.appendChild(side); body.appendChild(m);
  const bw = el("div","wrap"); bw.appendChild(body);
  document.body.appendChild(bw);
  /* تذييلُ المنصة — بتوقيع صاحبها */
  const ft = el("footer"), fw = el("div","wrap frow");
  const f1 = el("div");
  f1.appendChild(el("b",null, TR(D.school) + " — " + TR(D.sysname)));
  f1.appendChild(el("span",null, "من التخطيط إلى الدرجة: جدولٌ واحد · تحضيرٌ واحد · استمارةٌ واحدة · تقاريرُ تُصدر نفسها"));
  const f2 = el("div","sig");
  f2.appendChild(el("b",null, D.owner_role));
  f2.appendChild(el("span",null, D.owner));
  if(D.build) f2.appendChild(el("i",null, D.build));
  fw.appendChild(f1); fw.appendChild(f2); ft.appendChild(fw);
  document.body.appendChild(ft);

  /* ⚠️ شاشتا المستشار (٧ لوحة · ٨ أدوات) ليستا في D.phases — ولهما عنوانُهما
     في الشريط، فلا صندوقَ شرحٍ لهما. وبدون هذا الحارس يسقط الرسمُ كلُّه. */
  if(PH !== 5 && D.phases.some(x=>x.id === PH)){
    const p = phaseFor(D.phases.find(x=>x.id===PH));
    /* ⛔ الشرحُ يُقرأ مرّةً ثم يُزاحم العمل: فيُطوى بزرٍّ ويُحفظ الاختيارُ
       في الجهاز. ويبقى العنوانُ ظاهراً فيُفتح متى احتيج إليه. */
    let fold = false;
    try{ fold = localStorage.getItem(KEY + "_whyfold") === "1"; }catch(e){}
    const why = el("div","why" + (fold ? " min" : ""));
    const fb2 = el("button","fold", fold ? "اعرض الشرح" : "اطوِ الشرح");
    fb2.addEventListener("click", ()=>{
      fold = !fold;
      try{ localStorage.setItem(KEY + "_whyfold", fold ? "1" : "0"); }catch(e){}
      shell();
    });
    why.appendChild(fb2);
    /* ⚠️ والعنوانُ يوافق الشريطَ: الموضعُ لا المعرّف */
    const _pos = navItems().findIndex(x=>x.id === PH);
    why.appendChild(el("h2",null, TR("المرحلة ") + arn(_pos < 0 ? p.id : _pos + 1)
                                  + " · " + TR(p.t)));
    why.appendChild(el("p",null,p.why));
    const ol = el("ol"); p.steps.forEach(x=>ol.appendChild(el("li",null,x))); why.appendChild(ol);
    const dv = el("div","docs");
    /* لا يُعرض للمستخدم إلا ما يعنيه — والنجمةُ تعني الجميع */
    /* ⛔ دليلُ الاستخدام نسختان: عربيةٌ وإنجليزية. ولو عُرض الرابطان معاً
       لفتح الإنجليزيُّ عربياً بعنوانٍ مترجَم — فالرابطُ يتبع لغةَ القارئ،
       ويبقى واحداً لكل دور. (٣٠ سبتمبر ٢٠٢٦) */
    /* ⛔ في مرحلة التحضير للمعلم لهذه الروابطِ بطاقةٌ ظاهرةٌ دائماً
       (`prepTools`)، فلا تُكرَّر هنا — زرّان متطابقان على بُعد سنتيمترات
       يُربكان ولا يُفيدان. (٣٠ سبتمبر ٢٠٢٦) */
    const _ownTools = (PH === 2 && ME.role === "teacher");
    if(!_ownTools) p.docs.forEach(([t,u,r,uen])=>{
      if(r && r !== "*" && r.split(",").indexOf(ME.role) < 0) return;
      const a=el("a",null,t); a.href = (LANG === "en" && uen) ? uen : u;
      a.target="_blank"; dv.appendChild(a);
    });
    /* ⛔ النماذجُ المعبّأةُ انتقلت إلى بطاقة «أدوات التحضير» الظاهرة:
       كانت داخل شرحٍ يُطوى، فلا يراها من طواه — وهي أوّلُ ما يتعلّم منه. */
    why.appendChild(dv);
    mw.appendChild(why);
  }
  ({1:ph1, 2:ph2, 3:ph3, 4:ph4, 5:ph5, 6:ph6, 7:phBoard, 8:phTools})[PH](mw);
  /* ⛔ **اتجاهُ الورقة يتبع الشاشة.** كان في التنسيق قاعدتا `@page`
     متعارضتان: `A4 landscape` ثم `A4` — فتغلب الأخيرةُ ويخرج الورقُ عمودياً
     **دائماً** والقواعدُ مكتوبةٌ للأفقي، فنصفُ المصفوفة خارج الورقة ومن طبع
     لم يحصل على جدوله. وقِيس بطباعةٍ فعلية: ٥٩٥×٨٤٢ أي عمودي. (١ أكتوبر ٢٠٢٦)
     ⚠️ ولا اتجاهَ واحدٌ يصلح للجميع: المصفوفةُ ستةُ أعمدةٍ عريضة (أفقي)،
        والتحضيرُ أربعٌ وسبعون خانةً طولية (عمودي). فيُكتب لكل شاشةٍ اتجاهُها. */
  try{
    let pr = document.getElementById("pagerule");
    if(!pr){ pr = document.createElement("style"); pr.id = "pagerule";
             document.head.appendChild(pr); }
    const wide = (PH === 1) || (PH === 7);     /* المصفوفةُ ولوحةُ المستشار */
    pr.textContent = "@page{size:A4 " + (wide ? "landscape" : "portrait")
                   + ";margin:" + (wide ? "8mm" : "12mm") + "}";
  }catch(e){}
  /* ⛔ **شريطُ الحفظ يُركَّب مركزياً لا في كل شاشةٍ بيدها**: لو نُودي داخلَ
     كلِّ مرحلةٍ لنُسيت واحدةٌ اليومَ أو عند إضافة شاشةٍ غداً. فيُسأل المرسومُ
     نفسُه: أفيه خانةٌ تُكتب؟ فإن كان فله شريطُه. (طلبُ المستشار ١ أكتوبر
     ٢٠٢٦: «كل صفحة فيها إدخالات ينبغي وجود زر للحفظ») */
  /* ⛔ **الجداولُ العريضةُ تُلفُّ مركزياً لا واحداً واحداً.** لففتُ جدولَ
     «الحصص المسجَّلة» بيدي، فأمسك حارسُ المقاسات جدولَ إسناد الزائرين بعده:
     خانةُ «الرقم الوظيفي» خارجَ الشاشة على ٣٢٠ و٣٩٠ بلا طريقةٍ للوصول.
     والعلاجُ قاعدةٌ لا موضع: بعد رسم أي شاشةٍ يُلفُّ كلُّ جدولٍ لم يُلفّ —
     فلا يُنسى جدولٌ اليومَ ولا جدولٌ يُضاف غداً. (١ أكتوبر ٢٠٢٦)
     ⚠️ وتُستثنى **المصفوفةُ الرئيسةُ وحدَها** (`mx`): لها ممرُّها وأعمدتُها
        الثابتة. و`mx2` جداولُ بياناتٍ عاديةٌ تُلفُّ — وكدتُ أستثنيها فأُعيد
        خروجَ زرَّي «افتح» و«حذف» عن الشاشة. */
  try{
    mw.querySelectorAll("table").forEach(t=>{
      if(t.classList.contains("mx")) return;
      if(t.parentElement && t.parentElement.classList.contains("scrollx")) return;
      let p2 = t.parentElement, inside = false;
      while(p2 && p2 !== mw){
        if(p2.classList && p2.classList.contains("scrollx")){ inside = true; break; }
        p2 = p2.parentElement;
      }
      if(inside) return;
      const d = el("div","scrollx");
      t.parentElement.insertBefore(d, t);
      d.appendChild(t);
    });
  }catch(e){ try{ console.error("scrollx:", e); }catch(_){} }
  try{
    const live = mw.querySelector(
      "input:not([disabled]):not([type=hidden]), textarea:not([disabled]), select:not([disabled])");
    if(live){
      const ph = D.phases.find(x=>x.id === PH);
      const cur = DB.sched.find(x=>x.id === CUR);
      const ttl = [D.school, ph ? ph.t : "", (CUR && cur) ? lessonTitle(cur) : ""]
        .filter(Boolean).map(x=>TR(x)).join(" — ");
      actionBar(mw, ttl);
    }
  }catch(e){ try{ console.error("actionBar:", e); }catch(_){} }
  /* ⛔ **بعد رسم المرحلة لا قبلها**: كانت تُنادى عقب التذييل، والصندوقُ
     يُرسم بعده — فتبحث عن عنصرٍ لم يُخلق فلا تُعيد شيئاً. قِيس بكتابة اسمٍ
     حرفاً حرفاً: خرج المؤشّرُ تسعَ مرّاتٍ من تسع. */
  refocusAfterRender();
}

/* ⚠️ صياغةُ الوقت والصفة كانت داخل logView وحدَها، فلمّا احتاجتها اللوحةُ
   كان البديلُ نسخةً ثانيةً تفترق عنها. فاستُخرجتا دالّتين يقرأ منهما الاثنان. */
const ROLE_SHORT = {teacher:"معلم", peer:"زائر", evaluator:"مقيّم",
                    principal:"مدير", deputy:"وكيل", supervisor:"مشرف",
                    supervision:"مدير إشراف", admin:"مشرف المنصة"};
function roleName(k){ return ROLE_SHORT[k] || "—"; }
function agoTxt(t){
  const d = new Date(t || Date.now());
  const mins = Math.floor((Date.now() - d.getTime()) / 60000);
  if(mins < 1) return "الآن";
  if(mins < 60) return "قبل " + arn(mins) + " د";
  if(mins < 1440) return "قبل " + arn(Math.floor(mins / 60)) + " س";
  return arn(d.getDate()) + "/" + arn(d.getMonth() + 1) + " " +
         arn(String(d.getHours()).padStart(2, "0")) + ":" +
         arn(String(d.getMinutes()).padStart(2, "0"));
}

/* ═════════ لوحةُ المنظومة — للمستشار وحده ═════════
   ⛔ عملُ المستشار أن يعرف **أين تقف المنظومة** وما يحتاج تدخّله، لا أن
      يحضّر حصةً. فهذه أولُ شاشةٍ يفتحها: الحالُ في سطر، ثم ما تعطّل. */
function phBoard(m){
  const sch = DB.sched || [];
  const named = sch.filter(L=>(L.teacher||"").trim());
  let issued = 0, obsd = 0, appr = 0, peerd = 0, noPeer = 0;
  named.forEach(L=>{
    const g = prog(L);
    if(g.issued) issued++;
    if(g.obs > 0) obsd++;
    if(g.pr > 0) peerd++;
    if(L.approved) appr++;
    if(!(L.peer1e || L.peer1 || L.peer2e || L.peer2)) noPeer++;
  });
  const linked = !!api();

  /* ── الحالُ في سطر ── */
  const c1 = el("div","card"), h1 = el("h3");
  h1.appendChild(el("span",null,"حالُ المنظومة"));
  h1.appendChild(el("small",null, D.school + (D.stagelabel ? " · " + D.stagelabel : "")));
  c1.appendChild(h1);
  const p1 = el("div","pad");
  kpis(p1, [[arn(named.length), "حصةً مجدولةً باسم معلم"],
            [arn(issued), "صدر تحضيرُها"],
            [arn(obsd), "بدأ رصدُها"],
            [arn(appr), "اعتُمدت نتيجتُها"]]);
  c1.appendChild(p1); m.appendChild(c1);

  /* ── ما يحتاج تدخّلك ── */
  const c2 = el("div","card"), h2 = el("h3");
  h2.appendChild(el("span",null,"ما يحتاج تدخّلك"));
  h2.appendChild(el("small",null,"مرتَّبٌ بالأهمّ — وكلُّ بندٍ يفتح موضعَه"));
  c2.appendChild(h2);
  const p2 = el("div","pad");
  const items = [];
  const add = (bad, txt, act, go) => items.push({bad, txt, act, go});
  add(!linked, linked ? "المخزن المشترك مربوط — ويرى الجميعُ البياناتِ نفسَها"
                      : "المخزن المشترك غيرُ مربوط — ما يُكتب يبقى على جهاز صاحبه",
      linked ? "" : "اربط الخادم", ()=>srv());
  add(!named.length, named.length ? arn(named.length) + " حصةً مجدولةً"
                                  : "لا حصةَ مجدولةٌ بعد — والجدولُ أولُ الطريق",
      "افتح الجدول", ()=>{ PH = 1; setctx("tab","fill"); shell(); });
  add(noPeer > 0, noPeer ? arn(noPeer) + " حصةً بلا معلمٍ زائرٍ مُسنَد"
                         : "كلُّ حصةٍ مجدولةٍ لها زائرُها",
      noPeer ? "افتح الإسناد" : "", ()=>{ PH = 1; setctx("tab","assign"); shell(); });
  /* ⛔ قبل التحضير: هل أدخل الكشفُ كلُّه؟ فالجدولُ الناقصُ لا يُصلحه تحضير. */
  const PE = pendingEntry();
  if(PE) add(PE.left.length > 0, PE.left.length
        ? arn(PE.left.length) + " من " + arn(PE.total) + " بلا حصةٍ مسجَّلةٍ بعد"
        : "كشفُ المعلمين تامُّ الإدخال (" + arn(PE.total) + ")",
      PE.left.length ? "افتح الكشف" : "", ()=>{ PH = 5; RPT = "pending"; shell(); });
  add(named.length > issued, named.length - issued > 0
        ? arn(named.length - issued) + " حصةً لم يصدر تحضيرُها بعد"
        : "كلُّ الحصص صدر تحضيرُها",
      "افتح تقرير التفعيل", ()=>{ PH = 5; RPT = "active"; shell(); });
  add(obsd > appr, obsd - appr > 0
        ? arn(obsd - appr) + " حصةً رُصدت ولم تُعتمد نتيجتُها"
        : "لا حصةَ تنتظر الاعتماد",
      "افتح تقرير المدرسة", ()=>{ PH = 5; RPT = "school"; shell(); });

  items.sort((a,b)=>(b.bad?1:0) - (a.bad?1:0));
  const t = el("table"), tr = el("tr");
  ["", "الحال", ""].forEach(x=>tr.appendChild(el("th",null,x)));
  t.appendChild(tr);
  items.forEach(it=>{
    const r = el("tr");
    const st = el("td");
    st.appendChild(el("span","tag " + (it.bad ? "no" : "ok"), it.bad ? "يحتاج" : "تمّ"));
    r.appendChild(st);
    r.appendChild(el("td",null,it.txt)).style.textAlign = "start";
    const ac = el("td");
    if(it.act){
      const b = el("button","b " + (it.bad ? "" : "ghost"), it.act);
      b.style.cssText = "padding:4px 12px;font-size:14px";
      b.addEventListener("click", it.go); ac.appendChild(b);
    }
    r.appendChild(ac); t.appendChild(r);
  });
  p2.appendChild(t); c2.appendChild(p2); m.appendChild(c2);

  /* ── آخرُ ما جرى ── */
  const lg = logList().slice(0, 6);
  const c3 = el("div","card"), h3 = el("h3");
  h3.appendChild(el("span",null,"آخرُ ما جرى"));
  h3.appendChild(el("small",null,"ستُّ عملياتٍ — والسجلُّ كاملاً في أدوات المنصة"));
  c3.appendChild(h3);
  const p3 = el("div","pad");
  if(!lg.length) p3.appendChild(el("div","empty","لا عمليات بعد."));
  else{
    const t3 = el("table"), r3 = el("tr");
    ["متى","من","الصفة","العملية"].forEach(x=>r3.appendChild(el("th",null,x)));
    t3.appendChild(r3);
    lg.forEach(x=>{
      const r = el("tr");
      [agoTxt(x.t), x.by || "—", roleName(x.r), x.a + (x.w ? " · " + x.w : "")]
        .forEach((v,i)=>{ const td = el("td",null,v); if(i) td.style.textAlign="center"; r.appendChild(td); });
      t3.appendChild(r);
    });
    p3.appendChild(t3);
  }
  c3.appendChild(p3); m.appendChild(c3);
}

/* ═════════ أدواتُ المنصة — للمستشار وحده ═════════ */
function phTools(m){
  const mk = (title, sub, rows) => {
    const c = el("div","card"), h = el("h3");
    h.appendChild(el("span",null,title));
    if(sub) h.appendChild(el("small",null,sub));
    c.appendChild(h);
    const p = el("div","pad");
    rows.forEach(([lab, desc, btn, fn, warn])=>{
      const w = el("div","vday");
      w.appendChild(el("b",null,lab));
      w.appendChild(el("i",null,desc));
      const b = el("button","b " + (warn ? "warn" : "ghost") + " sm", btn);
      b.addEventListener("click", fn);
      b.style.marginInlineStart = "auto";
      w.appendChild(b);
      p.appendChild(w);
    });
    c.appendChild(p); m.appendChild(c);
  };
  mk("المخزن المشترك", api() ? "مربوطٌ — ويرى الجميعُ البياناتِ نفسَها" : "غيرُ مربوط", [
    ["الخادم", api() || "لم يُربط بعد", api() ? "تغيير" : "اربط الخادم", ()=>srv()],
    /* ⛔ مفتاحُ المخزن: كان العقدُ بلا مصادقةٍ البتّة — ومن ملك العنوانَ ملك
       القاعدةَ قراءةً وكتابةً ومحواً. ويُدوَّر بلا إعادة نشرٍ للخادم. */
    ["مفتاح المخزن",
     skey() ? ("مضبوطٌ — " + arn(skey().length) + " حرفاً · ويُرسَل مع كل طلب")
            : "⚠️ غيرُ مضبوط — من يعرف عنوانَ الخادم يقرأ ويكتب ويمحو",
     skey() ? "تدوير" : "اضبط المفتاح", ()=>setKey(), !skey()],
    ["رابط الدعوة", "يُرسَل للمدرسة فيُربط جهازُ من يفتحه تلقائياً — ويحمل المفتاح", "انسخ الرابط", ()=>invite()],
    ["تحديثٌ الآن", "سحبُ ما كتبه غيرُك على أجهزتهم", "تحديث", ()=>pull().then(()=>shell())],
  ]);
  /* ⛔ الكشفُ لم يعد في الصفحة — فلا بدَّ من بابٍ يرفعه، وإلّا دخل أربعُمئةٍ
     وستون معلماً بالكتابة اليدوية ولا يُعرف تخصصُ أحدٍ من رقمه. */
  (function(){
    const n = Object.keys(D.roster || {}).length;
    mk("كشفُ المعلمين", n ? ("محمَّلٌ — " + arn(n) + " معلماً") : "غيرُ محمَّل — الدخولُ بالاسم كتابةً", [
      ["حالُ الكشف", n ? "به يُعرف الاسمُ والتخصصُ والمجمعُ من الرقم الوظيفي"
                       : "⚠️ بلا كشفٍ لا يعمل تقريرُ «من لم يُدخِل حصته» ولا الاستدعاءُ بالرقم",
       "ارفع الكشف", ()=>rosterUp(), !n],
    ]);
  })();
  mk("السجلّ والاسترداد", "ما جرى وما حُذف", [
    ["سجلّ العمليات", "من فعل ماذا ومتى — آخر ٦٠٠ عملية", "افتح السجلّ",
     ()=>{ PH = 1; setctx("tab","log"); shell(); }],
    ["سلّة المحذوفات", "يُحفظ المحذوفُ ثلاثين يوماً ويُستردُّ بنقرة", "افتح السلّة",
     ()=>{ PH = 1; setctx("tab","trash"); shell(); }],
  ]);
  mk("النسخ والتفريغ", "⚠️ الأخيرُ لا يُستردّ", [
    ["نسخةٌ احتياطية", "تُنزَّل بياناتُ المنظومة كلُّها ملفاً على جهازك", "نزّل النسخة", ()=>backup()],
    ["تفريغُ البيانات", "محوٌ كاملٌ على كل الأجهزة — بعد نسخةٍ وتأكيدٍ مكتوب",
     "تفريغ", ()=>wipeAll(), true],
  ]);
}

function srv(){
  const cur = api();
  uiPrompt(
    "الصق رابط المخزن المشترك ليرى كلُّ أفراد المنظومة البيانات نفسها،\n" +
    "أو اتركه فارغاً للعمل على هذا الجهاز وحده:\n\n" +
    /* ⛔ النصُّ يختلف باختلاف من يقرؤه: المستشارُ هو من يُنشئ الخادمَ ويوزّع
       رابطَه، فلا يُقال له «اطلبه من مدير التخطيط» — وهو هو. (٢٩ سبتمبر ٢٠٢٦) */
    (isAdmin()
      ? "وهو رابطُ الخادم الذي نشرتَه — ينتهي بـ.workers.dev أو بنطاقك.\n"
        + "وبعد الربط انسخ «رابط الدعوة» وأرسله للمدارس."
      : "والرابطُ يُطلب من مدير التخطيط والاعتماد المدرسي — ولا يُنشأ من الصفحة."),
    cur, "https://…").then(v=>{
    if(v === null) return;
    const u = v.trim();
    localStorage.setItem(API, u);
    if(!u){ shell(); return; }
    testSrv(u).then(r=>{
      if(!r.ok){ alert("⛔ الرابط لا يستجيب كما ينبغي:\n" + r.why +
        (isAdmin() ? "\n\nتأكّد أنه رابطُ الخادم الذي نشرتَه، بلا مسافةٍ ولا شَرطةٍ في آخره."
                   : "\n\nتأكّد أنه الرابطُ الذي سلَّمه مديرُ التخطيط والاعتماد المدرسي.")); shell(); return; }
      pull().then(()=>{ alert("✓ رُبط المخزن المشترك.\n" + r.note); shell(); });
    });
  });
}
/* اختبارُ الرابط قبل اعتماده.
   ⚠️ درسان تعلَّمناهما من خادمٍ حقيقي:
   ١) دالةُ الدمج تُسقط ما خرج عن بنيتها عمداً، فيُفحَص بمفتاحٍ داخل `rot` لا بحقلٍ مستحدَث.
   ٢) مخزنُ KV «متّسقٌ في النهاية»: القراءةُ فورَ الكتابة قد ترجع قديمةً لثوانٍ.
      فالحكمُ يقع على **ردّ الكتابة نفسه** (وهو يعيد المدموج)، والقراءةُ تُحاوَل
      ثلاثاً بفاصلٍ ولا يُحكم بالفشل إن تأخّرت. */
function testSrv(u){
  const key = "__probe_" + Date.now(), val = "" + Math.random();
  /* ⛔ وفحصُ الخادم يحمل المفتاحَ كغيره — وإلّا رُدَّ بعد ترقية الخادم
     فظنَّ المستشارُ رابطَه خاطئاً وهو سليم. (١ أكتوبر ٢٠٢٦) */
  const _k = skey();
  const g = u + (u.indexOf("?") < 0 ? "?" : "&") + "kind=probe&id=t"
          + (_k ? "&key=" + encodeURIComponent(_k) : "");
  const readBack = (n) => fetch(g).then(r=>r.json())
    .then(r=>{
      if(r && r.ok && r.data && r.data.rot && r.data.rot[key] === val) return true;
      if(n <= 0) return false;
      return new Promise(res=>setTimeout(res, 1500)).then(()=>readBack(n - 1));
    }).catch(()=>false);
  return fetch(u, {method:"POST", headers:{"Content-Type":"text/plain;charset=utf-8"},
      body: apiBody({kind:"probe", id:"t", data:{rot:{[key]: val}}})})
    .then(r=>r.json())
    .then(w=>{
      if(!(w && w.ok && w.data && w.data.rot && w.data.rot[key] === val))
        /* ⛔ ولا تُنشر تعليماتُ الإعداد: كانت تقول للقارئ كيف يُربط المخزنُ
           وما اسمُ متغيّره — وهي في دليل المستشار لا في صفحةٍ عامّة. */
        return {ok:false, why:"استجاب ولم يُرجع ما كُتب فيه — راجع إعدادَ الخادم."};
      return readBack(3).then(seen=>({ok:true, note: seen
        ? "كُتب واستُرجع بنجاح — البيانات ستُشارَك بين الأجهزة."
        : "الكتابةُ تعمل. والقراءةُ تأخّرت ثوانيَ لأن مخزن الخادم يتّسق تدريجياً — وهذا طبيعي."}));
    })
    .catch(e=>({ok:false, why:"تعذّر الاتصال: " + e.message}));
}



/* ═════════ اختيار الحصة ═════════ */
function picker(m, title, cb){
  const list = myLessons();
  const c = el("div","card");
  const h = el("h3"); h.appendChild(el("span",null,title));
  h.appendChild(el("small",null, arn(list.length) + " حصة تخصّك")); c.appendChild(h);
  const p = el("div","pad");
  if(!list.length){
    /* ⛔ «لا حصص» وحدَها طريقٌ مسدود: المعلمُ لا يعرف أعليه أن يسجّل أم ينتظر.
       فتُقال العلّتان ويُعطى الطريقُ إليهما. (٣٠ سبتمبر ٢٠٢٦) */
    if(ME.role === "teacher"){
      p.appendChild(el("div","msg warn",
        "لا حصةَ باسمك في الجدول بعد. وسببُها أحدُ اثنين: إمّا أنك لم تسجّل حصتك "
        + "في جدول الحصص الموحَّدة، وإمّا أن اسمك أو رقمك الوظيفي كُتب في الجدول "
        + "على غير ما دخلتَ به."));
      const bar = el("div","bar");
      const go = el("button","b","اذهب إلى الجدول وسجّل حصتك");
      go.addEventListener("click", ()=>{ PH = 1; setctx("tab","fill"); shell(); });
      bar.appendChild(go);
      p.appendChild(bar);
      const who = el("div","note");
      who.appendChild(el("div",null, "تدخل باسم: " + (ME.name || "—")
        + (ME.emp ? " · الرقم الوظيفي " + arn(ME.emp) : "")
        + " — واكتبه في خلية الجدول كما هو."));
      p.appendChild(who);
    } else {
      p.appendChild(el("div","empty","لا حصص مسنَدة إليك بعد."));
    }
  } else {
    const t = el("table"), tr = el("tr");
    ["الحصة","المدرسة","الموعد","الحالة",""].forEach(x=>tr.appendChild(el("th",null,x)));
    t.appendChild(tr);
    list.forEach(L=>{
      const g = prog(L), r = el("tr");
      r.appendChild(el("td",null, lessonTitle(L)));
      r.appendChild(el("td",null, [L.school,L.stage].filter(Boolean).join(" · ")));
      r.appendChild(el("td",null, joinAr([TR(L.week), TR(L.day), perLabel(L)])));
      const st = el("td");
      st.appendChild(el("span","tag " + (g.issued?"ok":"no"), g.issued?"التحضير مُصدَر":"التحضير لم يُصدَر"));
      r.appendChild(st);
      const b = el("td"); const go = el("button","b alt","افتح"); go.style.padding="5px 14px";
      go.addEventListener("click", ()=>{ CUR = L.id; cb(L); });
      b.appendChild(go); r.appendChild(b);
      t.appendChild(r);
    });
    p.appendChild(t);
  }
  c.appendChild(p); m.appendChild(c);
}

/* ═════════ المرحلة ٣: أداء الحصة ═════════ */
function ph3(m){
  const L = DB.sched.find(x=>x.id===CUR);
  if(!L){ picker(m, ME.role==="peer" ? "اختر الحصة التي تزورها" : "اختر الحصة التي ترصدها", ()=>shell()); return; }
  const P = DB.prep[L.id] || {};
  const head = el("div","card");
  const h = el("h3"); h.appendChild(el("span",null, lessonTitle(L)));
  h.appendChild(el("small",null, lessonSub(L))); head.appendChild(h);
  const hp = el("div","pad"), bar = el("div","bar");
  const back = el("button","b ghost","تغيير الحصة"); back.addEventListener("click", ()=>{ CUR=null; shell(); });
  bar.appendChild(back);
  const pr = el("button","b ghost","طباعة"); pr.addEventListener("click", ()=>window.print()); bar.appendChild(pr);
  hp.appendChild(bar);
  if(!P.__issued){
    const w = el("div","msg bad");
    w.textContent = TR("تحضير هذه الحصة لم يُصدَر بعد — والرصد قبل قراءة التحضير يُفقد الشواهد معناها.");
    hp.appendChild(w);
  }
  head.appendChild(hp); m.appendChild(head);

  /* تحضير المعلم للقراءة */
  const pc = el("div","card");
  const ph = el("h3"); ph.appendChild(el("span",null,"تحضير المعلم — للقراءة"));
  ph.appendChild(el("small",null, P.__issued ? ("صدر: " + P.__issued) : "لم يُصدَر بعد")); pc.appendChild(ph);
  const pp = el("div","pad");
  const det = el("details"); det.appendChild(el("summary",null,"افتح التحضير كاملاً")).style.cssText="cursor:pointer;color:var(--navy);font-weight:700";
  const box = el("div"); box.style.marginTop="10px";
  D.sections.forEach(sec=>{
    const t = el("div"); t.style.cssText="font-weight:700;color:var(--navy2);margin:9px 0 4px";
    t.textContent =TR(TR(sec.t) + " · " + TR(sec.n)); box.appendChild(t);
    sec.rows.forEach(r=>{
      const rw = el("div","row2"), lb = el("div","lab", r.label), fl = pfield(r, P, true);
      rw.appendChild(lb); rw.appendChild(fl); box.appendChild(rw);
    });
  });
  det.appendChild(box); pp.appendChild(det); pc.appendChild(pp); m.appendChild(pc);

  if(ME.role !== "teacher") scorerNote(m, L);
  if(ME.role === "peer") peerCard(m, L);
  /* ⛔ الاستمارةُ للمشرف التربوي وحدَه (قرارُ الاجتماع). والمديرُ يطّلع
     ويعلّق، والوكيلُ يتابع التعبئةَ ولا يرصد. */
  else if(canScore(L)) evalForms(m, L);
  else viewOnly(m, L);
}

/* ═════════ اطّلاعٌ وتعليقٌ بلا رصد ═════════
   ⛔ المديرُ والوكيلُ لا يملآن الاستمارة. وبدل أن تُخفى عنهما الشاشةُ فيحتارا
      «أين ما أعمله؟»، تُعرض لهما نتيجةُ المشرف للاطّلاع، ولمدير المدرسة
      صندوقُ تعليقٍ يُنسب إليه ويظهر في تقرير الحصة. */
function viewOnly(m, L){
  const c = el("div","card"), h = el("h3");
  h.appendChild(el("span",null, isDeputy() ? "متابعةُ الحصة" : "الاطّلاع والتعليق"));
  h.appendChild(el("small",null, isDeputy()
    ? "تتأكّد من تعبئة معلميك — والرصدُ للمشرف التربوي"
    : "ترى ما رصده المشرفُ التربوي، وتكتب تعليقك"));
  c.appendChild(h);
  const p = el("div","pad");
  const obs = Object.values(DB.obs).filter(v=>v.__lid === L.id && v.res);
  if(!obs.length)
    p.appendChild(el("div","msg","لم يرصد المشرفُ التربوي هذه الحصة بعد."));
  else obs.forEach(v=>{
    const r = el("div","msg ok");
    r.appendChild(el("b",null, (v.__by || "—") + " — " + arn(Math.round(v.res.pct || 0)) + "٪"));
    if(v.bridge) r.appendChild(el("span",null,"إجراءُ الجسر: " + v.bridge));
    p.appendChild(r);
  });
  if(isPrincipal()){
    const K = "note|" + L.id + "|" + ME.name;
    DB.notes = DB.notes || {};
    const V = DB.notes[K] = DB.notes[K] || {};
    const lb = el("label","f");
    lb.appendChild(el("span",null,"تعليقُ مدير المدرسة — يظهر في تقرير الحصة"));
    lb.appendChild(fld("area", V.t, v=>{
      V.t = v; V.__lid = L.id; V.__by = ME.name; V.__at = new Date().toISOString(); save();
    }, null, "ملاحظتك على الحصة — لا درجة"));
    p.appendChild(lb);
    const bar = el("div","bar");
    const sv = el("button","b","حفظ التعليق");
    sv.addEventListener("click", ()=>{
      logAct("تعليق مدير", lessonTitle(L), L); save(); syncFlush();
      alert("حُفظ تعليقك — ويظهر في تقرير الحصة.");
    });
    bar.appendChild(sv); p.appendChild(bar);
  }
  c.appendChild(p); m.appendChild(c);
}

function peerCard(m, L){
  const K = L.id + "|" + ME.name;
  /* ⛔ **الفتحُ ليس ملأً**: كان السجلُّ يُنشأ عند الرسم، فيقرأ الزائرُ
     «أتممتَ بطاقتها» ولم يكتب حرفاً، وتُعدُّ في «الأقران ١/٢» للجميع.
     (٣٠ سبتمبر ٢٠٢٦) */
  const V = DB.peer[K] || {};
  let vborn = !!DB.peer[K];
  const vbear = ()=>{ if(!vborn){ DB.peer[K] = V; vborn = true; } };
  const c = el("div","card");
  const h = el("h3"); h.appendChild(el("span",null,"بطاقة زيارة الأقران — شاهدتُ وأطبّق"));
  h.appendChild(el("small",null,"إجراءٌ واحد تنقله لنفسك")); c.appendChild(h);
  const p = el("div","pad");
  D.peerq.forEach((q,i)=>{
    const w = el("div"); w.style.marginBottom="10px";
    const t = el("div","lab", arn(i+1) + " · " + q); t.style.marginBottom="5px";
    w.appendChild(t);
    w.appendChild(fld("area", V["q"+i], v=>{ vbear(); V["q"+i]=v; V.__lid=L.id; V.__by=ME.name; save(); },
                      null, null, !!L.approved));
    p.appendChild(w);
  });
  const dt = el("label","f"); dt.appendChild(el("span",null,"تاريخ التطبيق المزمع"));
  dt.appendChild(fld("txt", V.when, v=>{ vbear(); V.when=v; save(); }, null,
                     "مثال: الأحد القادم — حصة الرابعة", !!L.approved));
  p.appendChild(dt);
  const bar = el("div","bar");
  const done = el("button","b","حفظ البطاقة");
  done.addEventListener("click", ()=>{
    /* ⛔ لا تُحفظ بطاقةٌ خاوية: كان الحفظُ يُطمئن على لا شيء */
    if(!(V["q0"]||"").trim())
      return alert("اكتب أولاً ما شاهدتَه وتنوي تطبيقه — لا تُحفظ بطاقةٌ خاوية.");
    vbear(); V.__done=1; V.__lid=L.id; V.__by=ME.name;
    logAct("بطاقة أقران", lessonTitle(L), L); save(); syncFlush();
    alert("حُفظت بطاقتك — ويظهر إجراؤك في تقاريرك."); shell(); });
  bar.appendChild(done); p.appendChild(bar);
  c.appendChild(p); m.appendChild(c);
}

/* ═════════ توأمةُ الاستمارة والتحضير ═════════
   ⛔ كانت المنصةُ تَعِد: «التحضير توأمُ الاستمارة — كل خانةٍ فيه يقابلها
      مؤشرٌ يبحث عنه الزائر». وعدٌ بلا بنية: لا الزائرُ يعرف أيَّ خانةٍ يقرأ
      لأيِّ مؤشر، ولا أحدَ لاحظ أن ثمانيةَ عشرَ مؤشراً لا خانةَ لها أصلاً.
      فصارت التوأمةُ جدولاً في `indmap.py` محروساً في البناء — وهذه عينُها
      في الشاشة: **تحت كل مؤشرٍ ما كتبه المعلمُ في خانته قبل الحصة**، فيرصد
      الزائرُ ما وُعِد به لا ما يتذكّره. (١ أكتوبر ٢٠٢٦)
   ⚠️ وما لا يُحضَّر يُعلن أنه لا يُحضَّر — إقراراً تربوياً لا اعتذاراً. */
function prepVal(P, e){
  if(e.kind === "ticks") return (e.items || []).filter((_, i)=>P[e.key + "#" + i]).join(" · ");
  return String(P[e.key] == null ? "" : P[e.key]).trim();
}
function twinRows(P, keys){
  const F = (typeof planFields === "function") ? planFields() : [];
  const out = [];
  keys.forEach(k=>{
    const mine = F.filter(e=>e.root === k);
    const got = [];
    mine.forEach(e=>{ const v = prepVal(P, e); if(v) got.push(v); });
    out.push({lab: (D.preplab || {})[k] || k, val: got.join(" · "), n: mine.length});
  });
  return out;
}
function twinCell(td, L, key){
  const mp = (D.indmap || {})[key];
  if(!mp) return;
  const w = el("div","twin");
  if(mp.obs){ w.appendChild(el("span","tag no","بالمشاهدة وحدَها"));
    w.appendChild(el("i",null," — لا شاهدَ له في التحضير، فالأداءُ لا يُكتب قبل الحصة"));
    td.appendChild(w); return; }
  if(mp.rec){ w.appendChild(el("span","tag no","من سجلّ المعلم"));
    w.appendChild(el("i",null," — يُتحقَّق من سجلّ التخطيط والتوزيع الزمني لا من خانة"));
    td.appendChild(w); return; }
  const P = DB.prep[L.id] || {};
  const rows = twinRows(P, mp.f || []);
  const full = rows.filter(x=>x.val);
  if(!full.length){
    w.appendChild(el("span","tag no","لم يُكتب في التحضير"));
    /* ⛔ **الوصلُ قبل الترجمة يُفوّت المفاتيحَ كلَّها**: «الهدف المعرفي ·
       الهدف المهاري» مفتاحٌ مركَّبٌ لا وجودَ له في المعجم، وأجزاؤه مترجَمة.
       فيُترجَم كلُّ جزءٍ وحدَه ثم يُوصل. (١ أكتوبر ٢٠٢٦) */
    w.appendChild(el("i",null, TR(" — خانتُه: ") + rows.map(x=>TR(x.lab)).join(TR(" · "))));
    td.appendChild(w); return;
  }
  full.forEach(x=>{
    const ln = el("div");
    ln.appendChild(el("b",null, TR(x.lab) + ": "));
    ln.appendChild(el("span",null, x.val.length > 180 ? x.val.slice(0, 180) + "…" : x.val));
    w.appendChild(ln);
  });
  const empty = rows.filter(x=>!x.val);
  if(empty.length) w.appendChild(el("i",null,
    TR("ولم يُكتب: ") + empty.map(x=>TR(x.lab)).join(TR(" · "))));
  td.appendChild(w);
}

function evalForms(m, L){
  if(L.approved){
    const w = el("div","card"), p2 = el("div","pad");
    p2.appendChild(el("div","msg ok",
      "هذه الحصة معتمدةٌ ومقفولة — رصدُها مغلقٌ للتعديل. "
      + "ولفكِّ الاعتماد: مرحلةُ «بعد الحصة»."));
    w.appendChild(p2); m.appendChild(w);
  }
  /* ⛔ **لا يُخلق سجلُّ رصدٍ بمجرّد الفتح**: كان الفتحُ وحدَه ينشئ سجلاً
     ويحفظه، فتُحسب له درجةُ صفرٍ كاملةَ الوزن (٢٠٠ في المقام وصفرٌ في البسط)
     وتدخل متوسطَ المدرسة وتقريرَ المعلم وترتيبَ المؤشرات. والفتحُ ليس رصداً.
     (٣٠ سبتمبر ٢٠٢٦) */
  const K = L.id + "|" + ME.name;
  const V = DB.obs[K] || {sc:{}, ind:{}};
  V.__lid = L.id; V.__by = ME.name;
  let born = !!DB.obs[K];
  const bear = ()=>{ if(!born){ DB.obs[K] = V; born = true; } };
  const role = el("div","card");
  const rh = el("h3"); rh.appendChild(el("span",null,"صفتك في هذه الزيارة")); role.appendChild(rh);
  const rp = el("div","pad");
  /* ⛔ الصفةُ تُشتقُّ من الدور الذي دخل به لا تُسأل: كان المقيّمُ دوراً واحداً
     فيختارها بيده، وقد يختار غيرَ صفته فتُنسب درجتُه إلى خانةٍ ليست له.
     ومنذ فصل الأدوار (٢٩ سبتمبر ٢٠٢٦) صارت معلومةً من الدخول. */
  const auto = {principal: D.evalroles[0], deputy: D.evalroles[1],
                supervisor: D.evalroles[2], cxmgr: D.evalroles[3]}[ME.role];
  if(auto){
    /* الصفةُ تُثبَّت في الكائن، ولا تُولِّد سجلاً ولا تُحفظ قبل أول رصد */
    V.role = auto;
    const tag = el("div"); tag.appendChild(el("span","tag ok", auto));
    tag.appendChild(el("small",null," — من دورك عند الدخول، ولا تُبدَّل هنا"));
    rp.appendChild(tag);
  } else {
    rp.appendChild(fld("sel", V.role, v=>{ bear(); V.role=v; save(); }, D.evalroles));
  }
  role.appendChild(rp); m.appendChild(role);

  /* الاستمارة */
  D.domains.forEach((dm,di)=>{
    const c = el("div","card");
    const h = el("h3"); h.appendChild(el("span",null,"المجال " + arn(di+1) + " · " + dm.t));
    const sc = el("small"); sc.id = "dsc"+di; h.appendChild(sc); c.appendChild(h);
    const t = el("table"), tr = el("tr");
    ["#","المؤشر"].forEach(x=>tr.appendChild(el("th",null,x)));
    D.levels.forEach(([n,v])=>tr.appendChild(el("th",null, TR(n)+" ("+arn(v)+")")));
    tr.appendChild(el("th",null,"لا ينطبق"));
    t.appendChild(tr);
    dm.inds.forEach((ind,ii)=>{
      const key = di+"_"+ii, r = el("tr");
      if(V.ind[key] != null) setTimeout(()=>markRow(r, V.ind[key]), 0);
      r.appendChild(el("td",null, arn(di+1)+"·"+arn(ii+1))).style.textAlign="center";
      const itd = el("td"); itd.appendChild(el("div",null, ind));
      twinCell(itd, L, key);            /* ما كتبه المعلمُ في خانة هذا المؤشر */
      r.appendChild(itd);
      /* ⛔ **مؤشرُ البطاقة لا يُرصد يداً**: كان الزائرُ يرصد م٢·٣ بنفسه،
         و«بطاقةُ تشخيص الإستراتيجية» تُنتج له درجةً في الوقت نفسه — رقمان
         لمؤشرٍ واحدٍ يتناقضان، والظاهرُ في الشريط غيرُ الداخلِ في المجموع.
         فصار يُملأ من البطاقة وحدَها ويُقفل. (١ أكتوبر ٢٠٢٦) */
      const fromCard = (key === D.indcard);
      if(fromCard){
        const nt = el("div","twin");
        nt.appendChild(el("span","tag ok","تُحسب من البطاقة"));
        nt.appendChild(el("i",null," — درجتُه تنزل من «بطاقة تشخيص الإستراتيجية» أدناه، ولا تُرصد هنا"));
        itd.appendChild(nt);
      }
      D.levels.concat([["NA",0]]).forEach(([n,v])=>{
        const td = el("td"); td.style.textAlign="center";
        const rb = el("input"); rb.type="radio"; rb.name="o"+key; rb.value = (n==="NA"?"na":v);
        rb.style.cssText="width:17px;height:17px";
        rb.setAttribute("aria-label", TR(ind) + " — " + TR(n));
        if(V.ind[key] === rb.value) rb.checked = true;
        if(fromCard){ rb.disabled = true; rb.id = "cardrb_" + v; }
        rb.addEventListener("focus", ()=>r.classList.add("editing"));
        rb.addEventListener("blur", ()=>r.classList.remove("editing"));
        /* ⚠️ الرصدُ يُلوَّن بدرجته: أخضرُ للمتحقق وأحمرُ لغير المتحقق ورماديٌّ
           لِـ«لا ينطبق» — فيرى الراصدُ بلمحةٍ ما أتمّه وما بقي. */
        if(L.approved) rb.disabled = true;
        rb.addEventListener("change", ()=>{
          const first = Object.keys(V.ind).length === 0;
          bear();                                  /* ⛔ هنا يُولَد السجلُّ لا عند الفتح */
          V.ind[key]=rb.value;
          if(first) logAct("بدء الرصد", (V.role || ME.name) + " — " + lessonTitle(L), L);
          save(); score(L,V); markRow(r, rb.value);
        });
        td.appendChild(rb); r.appendChild(td);
      });
      t.appendChild(r);
    });
    c.appendChild(t); m.appendChild(c);
  });

  /* ⛔ سببُ «لا ينطبق» — يظهر إن وُجدت واحدةٌ، ويُمنع الاعتمادُ بدونه */
  const nabox = el("div","card"); nabox.id = "nabox"; nabox.style.display = "none";
  const nah = el("h3"); nah.appendChild(el("span",null,"سببُ «لا ينطبق»"));
  nah.appendChild(el("small",null,"للاستثناء الحقيقي لا للهروب — والسقفُ عشرةُ مؤشرات"));
  nabox.appendChild(nah);
  const nap = el("div","pad");
  const nw = el("div","msg warn"); nw.id = "nawarn"; nw.style.display = "none";
  nap.appendChild(nw);
  nap.appendChild(el("div","lab","أيُّ المؤشرات ولماذا لا تنطبق على هذه الحصة"));
  nap.appendChild(fld("txt", V.nawhy, v=>{ bear(); V.nawhy = v; save(); score(L,V); },
                      null, "مثال: م٥·١ و٥·٣ — الحصةُ في ملعبٍ بلا سبورةٍ ذكية ولا أجهزة.",
                      !!L.approved));
  nabox.appendChild(nap); m.appendChild(nabox);

  /* بطاقة الإستراتيجية — تُفتح على ما أعلنه المعلم */
  const b = D.bank.find(x=>x.name === L.strategy) || D.bank.find(x=>x.key === V.strat);
  const sc = el("div","card");
  const sh = el("h3"); sh.appendChild(el("span",null,"بطاقة تشخيص الإستراتيجية"));
  sh.appendChild(el("small",null, b ? b.name : "لم تُعلَن إستراتيجيةٌ لهذه الحصة في الجدول")); sc.appendChild(sh);
  const sp = el("div","pad");
  if(b){
    V.strat = b.key;
    const t = el("table"), tr = el("tr");
    ["#","المؤشر"].forEach(x=>tr.appendChild(el("th",null,x)));
    D.slevels.forEach(([n,v])=>tr.appendChild(el("th",null, TR(n)+" ("+arn(v)+")")));
    t.appendChild(tr);
    b.inds.forEach((ind,i)=>{
      const r = el("tr");
      r.appendChild(el("td",null, arn(i+1))).style.textAlign="center";
      r.appendChild(el("td",null, ind));
      D.slevels.forEach(([n,v])=>{
        const td = el("td"); td.style.textAlign="center";
        const rb = el("input"); rb.type="radio"; rb.name="s"+i; rb.value=v;
        rb.style.cssText="width:17px;height:17px";
        if(String(V.sc[i]) === String(v)) rb.checked = true;
        /* ⛔ **الاعتمادُ يقفل البطاقةَ كما يقفل الاستمارة**: كانت مفتوحةً بعده،
           فتتغيّر درجةُ مؤشر الإستراتيجية بعد صدور النتيجة. (٣٠ سبتمبر ٢٠٢٦) */
        if(L.approved) rb.disabled = true;
        rb.addEventListener("change", ()=>{ bear(); V.sc[i]=v; save(); score(L,V); });
        td.appendChild(rb); r.appendChild(td);
      });
      t.appendChild(r);
    });
    sp.appendChild(t);
    const cv = el("div"); cv.style.cssText="color:var(--grey);font-size:14.5px;margin-top:7px";
    cv.textContent =TR(TR("التحويل إلى درجة مؤشر الإستراتيجية: ") + TR(D.convert)); sp.appendChild(cv);
    /* ⛔ **الجمعُ بين وثيقتين كانتا تتناقضان.** الاستمارةُ تشتقُّ درجةَ م٢·٣
       من هذه البطاقة، ودليلُ مستويات الأداء يعطيه رُبريكاً مستقلاً بأربعة
       شواهدَ لا يذكر البطاقةَ — فرقمان لمؤشرٍ واحد. وقرارُ المستشار: موافقةُ
       الاستمارة هي الأصل، والجمعُ إن أمكن. فالدرجةُ من البطاقة، **وشواهدُ
       الدليل تُعرض هنا** فيملؤها الراصدُ وهو يراها. (١ أكتوبر ٢٠٢٦) */
    if((D.m23e || []).length){
      const g = el("div","msg");
      /* ⚠️ الترجمةُ قبل الوصل: المركَّبُ لا مفتاحَ له وأجزاؤه مترجَمة */
      g.appendChild(el("b",null, TR("شواهدُ م٢·٣ من دليل مستويات الأداء — ") + TR(D.m23t)));
      const ul = el("ol"); ul.style.cssText = "padding-inline-start:22px;margin:4px 0 0;font-size:15px";
      D.m23e.forEach(x=>ul.appendChild(el("li",null,x)));
      g.appendChild(ul);
      g.appendChild(el("span",null, TR("ولا يُعدُّ شاهداً: ") + TR(D.m23n)
        + TR(" — ودرجةُ المؤشر تنزل من هذه البطاقة وحدَها، وهذه شواهدُ ما تملؤه.")));
      sp.appendChild(g);
    }
  } else sp.appendChild(el("div","empty","اختر الإستراتيجية في جدول الحصص لتفتح بطاقتها."));
  sc.appendChild(sp); m.appendChild(sc);

  /* ما قاله الطلاب */
  const tc = el("div","card");
  const th = el("h3"); th.appendChild(el("span",null, D.tulab_t)); tc.appendChild(th);
  const tp = el("div","pad");
  D.tulab.forEach((q,i)=>{
    const w = el("div"); w.style.marginBottom="8px";
    w.appendChild(el("div","lab", q)).style.marginBottom="4px";
    w.appendChild(fld("txt", V["tu"+i], v=>{ bear(); V["tu"+i]=v; save(); }, null, null, !!L.approved));
    tp.appendChild(w);
  });
  tc.appendChild(tp); m.appendChild(tc);

  const bar = el("div","score noprint"); bar.id="scorebar"; document.body.appendChild(bar);
  score(L,V);
}

/* ⛔ **سقفُ «لا ينطبق» عشرةُ مؤشراتٍ من الخمسين (٢٠٪) وبسببٍ مكتوب.**
   كانت «لا ينطبق» تُخرج المؤشرَ من المقام بلا سببٍ ولا حدّ — فمن رصد عشرين
   مؤشراً ضعيفاً بـ«لا ينطبق» رفع النسبةَ بلا أن يكذب في سطرٍ واحد. وهي
   للاستثناء الحقيقي (مختبرٌ في درسٍ نظريّ) لا للهروب، وعشرةٌ سعةٌ كافية.
   ⚠️ والنسبةُ تُحسب كما كانت — ولكنها **لا تُعتمد** حتى يُكتب السبب. */
const NACAP = 10;
function naWhy(V){
  const na = (V.res || {}).na || 0;
  if(!na) return "";
  if(na > NACAP) return "«لا ينطبق» في " + arn(na) + " مؤشراً — والسقفُ "
                        + arn(NACAP) + " (خُمسُ الاستمارة). راجع رصدَك.";
  if(!String(V.nawhy || "").trim()) return "اكتب سببَ «لا ينطبق» في "
                        + arn(na) + " مؤشراً — بلا سببٍ لا تُعتمد النتيجة.";
  return "";
}

function score(L,V){
  let got=0, max=0, na=0;
  /* ⛔ درجةُ مؤشر البطاقة تُحسب أولاً وتُكتب في خانته — فلا يبقى رقمان له.
     ومن لم يرصد البطاقةَ لا يُكتب له شيء: الفراغُ أصدقُ من درجةِ واحد. */
  let sgot = 0, sans = 0;
  for(let i = 0; i < 10; i++){
    const x = V.sc[i];
    if(x != null && x !== ""){ sans++; sgot += Number(x) || 0; }
  }
  const m23 = sgot>=90?4: sgot>=75?3: sgot>=50?2:1;
  if(D.indcard){
    if(sans) V.ind[D.indcard] = String(m23); else delete V.ind[D.indcard];
    const rb = document.getElementById("cardrb_" + m23);
    if(rb && sans) rb.checked = true;
  }
  const dpc = [];
  D.domains.forEach((dm,di)=>{
    let dg=0, dm2=0;
    dm.inds.forEach((_,ii)=>{
      const v = V.ind[di+"_"+ii];
      if(v === "na"){ na++; return; }
      if(!v) return;                       /* ⛔ الفراغُ لا يدخل المقام */
      dm2 += 4; dg += parseInt(v,10);
    });
    got += dg; max += dm2;
    /* ⚠️ **ولا أوزانَ للمجالات**: الاستمارةُ الرسميةُ مئتا درجةٍ بخمسين
       مؤشراً متساويةً أربعاً أربعاً، فإدخالُ وزنٍ يُخرجها عن الرسمي. ولئلا
       يختفي مجالٌ ضعيفٌ في مجموعٍ كبير: **لكلِّ مجالٍ نسبتُه ومستواه** هنا،
       وأضعفُها يُسمَّى في النتيجة. (١ أكتوبر ٢٠٢٦) */
    const dp = dm2 ? Math.round(dg/dm2*1000)/10 : null;
    if(dp !== null) dpc.push({i: di, t: dm.t, pct: dp});
    const e = document.getElementById("dsc"+di);
    if(e) e.textContent = TR(dm2 ? (arn(dg) + " من " + arn(dm2) + " · " + arn(dp) + "٪ · " + lvlOf(dp)) : "—");
  });
  /* ⛔ **الفراغُ ليس صفراً**: المؤشرُ غيرُ المرصود كان يُزيد المقامَ أربعةً
     والبسطَ صفراً — أي أشدَّ من «غير متحقق». فيُستثنى من المقام كما تُستثنى
     «لا ينطبق»، ولا تُسنَد نتيجةٌ لاستمارةٍ خاوية. (٣٠ سبتمبر ٢٠٢٦) */
  const answered = Object.keys(V.ind || {}).filter(k=>V.ind[k]).length;
  if(!answered && !Object.keys(V.sc || {}).length){ delete V.res; return; }
  const pct = max ? Math.round(got/max*1000)/10 : 0;
  const lvl = lvlOf(pct);
  /* ⛔ **أرضيّةُ المقياس ٢٥٪ لا صفر**: أضعفُ تقديرٍ في الاستمارة درجةٌ من
     أربع، فمن رُصد بأضعفِ تقديرٍ في الخمسين كلِّها نسبتُه ٢٥٪ لا صفراً.
     والقارئُ يقرأ «٣٠٪» فيظنُّها قريبةً من الصفر وهي قريبةٌ من الأرضيّة.
     فلا تُغيَّر النسبةُ الرسمية (حدودُ ٩٠·٧٥·٥٠ رسميةٌ تُطابق التقويم) —
     **ويُعلَن المدى**: ومعها موقعُها على ٢٥–١٠٠ صريحاً. (١ أكتوبر ٢٠٢٦) */
  const rel = max ? Math.max(0, Math.round((pct - 25) / 75 * 1000) / 10) : 0;
  const weak = dpc.length ? dpc.slice().sort((a,b)=>a.pct-b.pct)[0] : null;
  V.res = {got, max, pct, lvl, na, sgot, m23, rel,
           weak: weak ? ("المجال " + arn(weak.i+1) + " · " + weak.t) : "",
           weakpct: weak ? weak.pct : null};
  const bar = document.getElementById("scorebar");
  if(bar){
    bar.innerHTML = "";
    bar.appendChild(el("span",null,"الاستمارة:"));
    bar.appendChild(el("span","big", arn(got) + " من " + arn(max)));
    bar.appendChild(el("span",null,"(" + arn(pct) + "٪ · " + lvl + ")"));
    bar.appendChild(el("span",null,"| على مدى ٢٥–١٠٠: " + arn(rel) + "٪"));
    bar.appendChild(el("span",null,"| لا ينطبق: " + arn(na) + " من " + arn(NACAP)));
    if(V.strat) bar.appendChild(el("span",null,"| البطاقة: " + arn(sgot) + " من ١٠٠ ← درجة المؤشر " + arn(m23)));
    const go = el("button","b alt","إنهاء ← بعد الحصة");
    go.style.cssText="padding:6px 14px;font-size:15px";
    go.addEventListener("click", ()=>{ save(); PH=4; shell(); });
    bar.appendChild(go);
  }
  const nb = document.getElementById("nabox");
  if(nb) nb.style.display = na ? "" : "none";
  const nw = document.getElementById("nawarn");
  if(nw){ const why = naWhy(V); nw.textContent = TR(why); nw.style.display = why ? "" : "none"; }
  return V.res;
}
/* ⛔ **لا تُعرَّف `lvlOf` هنا**: كانت معرَّفةً أصلاً أسفلَ الملف بحارسِ
   `null` — فكتابةُ تعريفٍ ثانٍ تُلغي الأولَ صامتاً، و`node --check` يمرّ
   عليه. (أمسكه قياسُ الصفحة الحيّة ١ أكتوبر ٢٠٢٦ — وهي العلّةُ نفسُها في
   feedback_blanket_replace_hits_the_definition) */

/* ═════════ المرحلة ٤: بعد الحصة ═════════ */
function ph4(m){
  const L = DB.sched.find(x=>x.id===CUR);
  if(!L){ picker(m, "اختر الحصة", ()=>shell()); return; }
  const rows = Object.entries(DB.obs).filter(([k,v])=>v.__lid===L.id);
  const head = el("div","card");
  const h = el("h3"); h.appendChild(el("span",null, lessonTitle(L)));
  h.appendChild(el("small",null, lessonSub(L))); head.appendChild(h);
  const hp = el("div","pad"), bar = el("div","bar");
  const back = el("button","b ghost","تغيير الحصة"); back.addEventListener("click", ()=>{ CUR=null; shell(); });
  bar.appendChild(back);
  const pr = el("button","b ghost","طباعة التقرير"); pr.addEventListener("click", ()=>window.print()); bar.appendChild(pr);
  if(ME.role !== "teacher"){
    const wa = el("button","b alt","إرسال للمعلم عبر واتساب");
    wa.addEventListener("click", ()=>sendWA(L, rows)); bar.appendChild(wa);
  }
  /* ⛔ الاعتمادُ يقفل الحصة: بعده لا تُعدَّل خانتُها ولا تحضيرُها ولا رصدُها،
     وإلا تغيّرت أسسُ درجةٍ صدرت. والفكُّ بتأكيدٍ ويُسجَّل باسم فاعله.
     ⚠️ **والاعتمادُ لمن يرصد**: صار المشرفَ التربوي وحدَه بقرار الاجتماع،
        فلا يعتمد درجةً من لم يملأ استمارتَها. (٣٠ سبتمبر ٢٠٢٦) */
  if(canScore(L)){
    if(!L.approved){
      const ap = el("button","b","اعتماد النتيجة وقفل الحصة");
      ap.addEventListener("click", ()=>{
        /* ⛔ العدُّ على **ما رُصد** لا على وجود سجلّ: سجلٌّ خاوٍ كان يُجيز الاعتماد */
        if(!rows.some(([,v])=>v && v.res && v.res.max > 0))
          return alert("لا تُعتمد حصةٌ لم يرصدها أحد.");
        /* ⛔ ولا تُعتمد نتيجةٌ رُفع مقامُها بـ«لا ينطبق» بلا سببٍ أو فوق السقف */
        const nab = rows.map(([,v])=>[v, naWhy(v)]).filter(x=>x[1]);
        if(nab.length)
          return alert("⛔ لا تُعتمد النتيجةُ بعد:\n\n"
            + nab.map(x=>"• " + ((x[0].role || x[0].__by || "مقيّم") + ": " + x[1])).join("\n")
            + "\n\nيفتح كلُّ مقيّمٍ استمارتَه ويكتب السبب.");
        uiAsk("بعد الاعتماد تُقفل الحصة: لا يُعدَّل جدولُها ولا تحضيرُها ولا رصدُها.\n\nأتُتابع؟",
              "اعتمدها").then(ok=>{
          if(!ok) return;
          L.approved = {by: ME.name, no: ME.emp || "", at: new Date().toISOString()};
          logAct("اعتماد", lessonTitle(L), L); save(); shell(); syncFlush();
        });
      });
      bar.appendChild(ap);
    } else {
      const un = el("button","b warn","فكُّ الاعتماد");
      un.addEventListener("click", ()=>{
        uiAsk("فكُّ الاعتماد يُعيد فتحَ الحصة للتعديل — ويُسجَّل باسمك.\n\nأتُتابع؟",
              "فُكَّ الاعتماد", "bad").then(ok=>{
          if(!ok) return;
          logAct("فكُّ اعتماد", lessonTitle(L) + " — كان اعتمدها " + (L.approved.by||"—"), L);
          delete L.approved; save(); shell();
        });
      });
      bar.appendChild(un);
    }
  }
  hp.appendChild(bar);
  if(L.approved){
    const lk = el("div","msg ok");
    const d = new Date(L.approved.at);
    lk.textContent = "◆ حصةٌ معتمدةٌ ومقفلة — اعتمدها " + (L.approved.by || "—")
      + " في " + arn(d.getDate()) + "/" + arn(d.getMonth()+1)
      + ". لا تُعدَّل بياناتُها ولا تحضيرُها ولا رصدُها.";
    hp.appendChild(lk);
  }
  head.appendChild(hp); m.appendChild(head);

  const c = el("div","card");
  const ch = el("h3"); ch.appendChild(el("span",null,"نتيجة الزيارة"));
  ch.appendChild(el("small",null, arn(rows.length) + " مقيّماً رصد")); c.appendChild(ch);
  const p = el("div","pad");
  if(!rows.length) p.appendChild(el("div","empty","لم يرصد أحدٌ هذه الحصة بعد."));
  else{
    const t = el("table"), tr = el("tr");
    ["المقيّم","الصفة","الدرجة","النسبة","على مدى ٢٥–١٠٠","المستوى","أضعفُ مجال","لا ينطبق","البطاقة","درجة المؤشر"]
      .forEach(x=>tr.appendChild(el("th",null,x)));
    t.appendChild(tr);
    let sp=0, sn=0;
    const naq = [];
    rows.forEach(([k,v])=>{
      const R = v.res || {};
      sp += R.pct||0; sn++;
      const why = naWhy(v); if(why) naq.push((v.role || v.__by || "مقيّم") + ": " + why);
      const r = el("tr");
      [v.__by, v.role||"—", arn((R.got||0)+" من "+(R.max||0)), arn(R.pct||0)+"٪",
       R.rel == null ? "—" : arn(R.rel)+"٪", R.lvl||"—",
       R.weak ? (R.weak + " — " + arn(R.weakpct) + "٪") : "—",
       arn(R.na||0), arn(R.sgot||0)+" من ١٠٠", arn(R.m23||0)].forEach(x=>r.appendChild(el("td",null,x)));
      t.appendChild(r);
    });
    p.appendChild(t);
    /* ⛔ **المقياسُ يُعلَن ولا يُترك للظنّ**: أضعفُ تقديرٍ درجةٌ من أربع،
       فأرضيّةُ النسبة ٢٥٪ لا صفر — ومن قرأ «٣٥٪» ظنَّها قريبةً من الصفر. */
    const scn = el("div","note");
    scn.appendChild(el("div",null,
      "النسبةُ الرسميةُ من ٢٠٠ درجة، وأرضيّتُها ٢٥٪ لأن أضعفَ تقديرٍ درجةٌ من أربع — "
      + "فعمودُ «على مدى ٢٥–١٠٠» يُظهر الموقعَ الحقيقي بين الأضعفِ والأتمّ. "
      + "والمجالاتُ متساويةُ الوزن (أربعُ درجاتٍ لكل مؤشر) كما في الاستمارة الرسمية، "
      + "ولذلك يُسمَّى أضعفُ مجالٍ صريحاً فلا يختفي في المجموع."));
    if(naq.length){
      const nm = el("div","msg warn");
      nm.textContent = TR("⛔ «لا ينطبق» بلا سببٍ أو فوق السقف — ولا تُعتمد النتيجةُ قبل علاجه: ")
                       + naq.map(x=>TR(x)).join(" · ");
      p.appendChild(nm);
    }
    const avg = sn ? Math.round(sp/sn*10)/10 : 0;
    const k = el("div","kpi"); k.style.marginTop="12px";
    [[arn(avg)+"٪","متوسط النسبة"], [arn(sn),"عدد المقيّمين"],
     [arn(Object.keys(DB.peer).filter(x=>DB.peer[x].__lid===L.id).length),"بطاقات الأقران"]]
      .forEach(([b,s])=>{ const d=el("div"); d.appendChild(el("b",null,b)); d.appendChild(el("span",null,s)); k.appendChild(d); });
    p.appendChild(k);
  }
  c.appendChild(p); m.appendChild(c);

  /* بطاقة الجسر */
  const bc = el("div","card");
  const bh = el("h3"); bh.appendChild(el("span",null,"بطاقة الجسر"));
  bh.appendChild(el("small",null,"إجراءٌ واحد محدد يُنقل إلى الحصص اليومية ويُتحقق منه في الزيارة التالية"));
  bc.appendChild(bh);
  const bp = el("div","pad");
  const K = L.id+"|"+ME.name;
  /* ⛔ **لا سجلَّ رصدٍ لمن لا يرصد**: كان مجرّدُ فتح «بعد الحصة» يُنشئ سجلاً
     باسم الفاتح — زائراً كان أو معلماً أو فريقَ متابعة — فينزل متوسطُ الحصة
     إلى النصف ويُجاز اعتمادُها. (٣٠ سبتمبر ٢٠٢٦) */
  const V = DB.obs[K] || {sc:{}, ind:{}, __lid:L.id, __by:ME.name};
  let oborn = !!DB.obs[K];
  const obear = ()=>{ if(!oborn && canScore(L)){ DB.obs[K] = V; oborn = true; } };
  /* ⛔ التحقّقُ من إجراء الزيارة السابقة **لمن يرصد** وحدَه: كان معروضاً لكل
     من يفتح الشاشة، وكلُّ نقرةٍ فيه تُنشئ سجلَّ رصدٍ باسم الفاتح. (٣٠ سبتمبر) */
  const prev = canScore(L) ? prevBridge(L) : null;
  if(prev){
    const w = el("div","msg ok");
    w.appendChild(el("b",null,"إجراء الزيارة السابقة: "));
    w.appendChild(el("span",null, prev.text));
    bp.appendChild(w);
    const ck = el("div","ticks");
    ["طُبّق ويُرى ثابتاً","طُبّق جزئياً","لم يُطبَّق"].forEach((o,i)=>{
      const l = el("label","tk"), rb = el("input"); rb.type="radio"; rb.name="prevchk"; rb.value=o;
      const K0 = L.id+"|"+ME.name;
      /* ⚠️ `V` معرَّفٌ أعلاه الآن — وكان تحتَه فيُقرأ قبل تعريفه فتسقط
         الشاشةُ بـReferenceError. (أمسكه وكيلُ المراجعة ١ أكتوبر ٢٠٢٦) */
      const V0 = DB.obs[K0] || V;
      if(V0.prevchk===o) rb.checked=true;
      if(L.approved) rb.disabled = true;
      rb.addEventListener("change", ()=>{ obear(); V0.prevchk=o; save(); });
      l.appendChild(rb); l.appendChild(el("span",null,o)); ck.appendChild(l);
    });
    bp.appendChild(ck);
  }
  /* ⛔ **بطاقةُ الجسر لمن يرصد**: كانت مفتوحةً لكل من ليس معلماً، فيكتب فيها
     الزائرُ وفريقُ المتابعة فيُنشَأ لهم سجلُّ رصدٍ بصفر، فينزل متوسطُ الحصة
     إلى النصف ويُجاز اعتمادُها. وتُقفل بالاعتماد كغيرها. (٣٠ سبتمبر ٢٠٢٦) */
  const ro = !canScore(L) || !!L.approved;
  if(ro) bp.appendChild(el("div","ro", (rows.find(([k,v])=>(v.bridge||"").trim())||[null,{}])[1].bridge || "—"));
  else bp.appendChild(fld("area", V.bridge, v=>{ obear(); V.bridge=v; save(); }, null,
    "إجراء واحد محدد يمكن رؤيته — لا عبارة عامة"));
  bc.appendChild(bp); m.appendChild(bc);
}

function prevBridge(L){
  /* ⛔ **الأحدثُ السابقُ، وبالرقم**: كان يأخذ أوّلَ ما يصادفه في المصفوفة —
     وقد يكون حصةً **قادمة** — ويطابق بالاسم خلافاً لقاعدة المنصة. (٣٠ سبتمبر) */
  const wk = (x)=>D.weeks.indexOf(x.week), dy = (x)=>D.days.indexOf(x.day);
  const before = (x)=> wk(x) < wk(L) || (wk(x) === wk(L) && dy(x) < dy(L));
  const sameOne = (x)=> (x.teacherNo && L.teacherNo)
      ? x.teacherNo === L.teacherNo : (x.teacher||"") === (L.teacher||"");
  const same = DB.sched.filter(x=>sameOne(x) && x.id !== L.id && before(x))
      .sort((a,b)=> (wk(b)-wk(a)) || (dy(b)-dy(a)));
  for(const s of same){
    const hit = Object.values(DB.obs).find(v=>v.__lid===s.id && (v.bridge||"").trim());
    if(hit) return {text:hit.bridge, lesson:s};
  }
  return null;
}

function sendWA(L, rows){
  uiPrompt("رقم جوال المعلم (مثال 05xxxxxxxx):", "", "05xxxxxxxx").then(ph=>{
  if(!ph) return;
  /* ⚠️ والأرقامُ الهنديةُ تُقبل هنا أيضاً */
  const num = latnum(ph).replace(/^0/,"966");
  if(num.length < 11) return alert("⛔ رقمٌ غير صحيح.");
  const R = (rows[0]||[null,{}])[1].res || {};
  const br = (rows.find(([k,v])=>(v.bridge||"").trim())||[null,{}])[1].bridge || "";
  const t = ["تقرير زيارة صفية — " + D.school,
    lessonTitle(L), lessonSub(L),
    R.got!=null ? (TR("الاستمارة: ") + R.got + TR(" من ") + R.max + " (" + R.pct + TR("٪ — ") + TR(R.lvl) + ")") : "",
    R.sgot ? ("بطاقة الإستراتيجية: " + R.sgot + " من 100 ← درجة المؤشر " + R.m23) : "",
    br ? ("إجراء بطاقة الجسر: " + br) : "",
    "المقيّم: " + ME.name].filter(Boolean).join("\n");
  window.open("https://wa.me/" + num + "?text=" + encodeURIComponent(t), "_blank");
  });
}

/* ═════════ المرحلة ٥: التقارير ═════════ */
let RPT = "school";
/* ═════════ كشفُ المعلمين مقابلَ الجدول ═════════
   ⛔ «تقريرُ التفعيل» يبني قائمتَه من الموجود في البيانات، فمن لم يُدخل شيئاً
      لا يظهر فيه — ولا يُحصى الغائبُ من حاضرين. فهذا يقيس الجدولَ على الكشف.
   ⚠️ ويُحتسب المعلمُ «مُدخِلاً» بالرقم إن حملته الخانة، وبالاسم بديلاً — وإلا
      حُسب الحاضرُ غائباً فلوحق بلا سبب. */
/* ⛔ **تقريرُ «الإدخالُ الناقص» كان يقيس المنظومةَ كلَّها لا مدرستَه — ولا
   يبلغ الصفرَ أبداً.** يأخذ الكشفَ كلَّه (٤٦٠) و`DB.sched` كلَّها بلا ترشيحٍ
   بنطاق الداخل، مع أن كلَّ سطرٍ في الكشف يحمل قطاعَه ومجمعَه ومرحلتَه.
   فيقول لوكيل مدرسةٍ فيها ٣٤ معلماً: «٤٦٠ من ٤٦٠ بلا حصةٍ مسجَّلة».
   ⚠️ **وفيه ٨٨ اسماً تخصصُهم «أخرى»** — غيرُ معلمين (ومنهم الوكيلُ نفسُه)
      ولا حصةَ لهم أصلاً، فلا تُطبع رسالةُ «تامُّ الإدخال» ولو أتمّ الجميع.
      وتناقضٌ يُثبت العلّة: شاشةُ الإسناد تُسقط أصحابَ «أخرى»، فالكشفُ نفسُه
      يُعامَل معلماً هنا وغيرَ معلمٍ هناك.
   فأداةُ متابعته الأولى — وواجبُه الأول — كانت عديمةَ الفائدة.
   (أمسكه وكيلُ رحلة الوكيل التعليمي؛ عولج ١ أكتوبر ٢٠٢٦) */
function pendingEntry(){
  const R = D.roster || {};
  const sm = D.specmap || {};
  let keys = Object.keys(R);
  if(!keys.length) return null;                 /* لا كشفَ فلا قياس */
  /* ① من لا تخصصَ له في المطابقة ليس معلماً — فلا يُنتظر منه تسجيلُ حصة */
  keys = keys.filter(k=>{
    const sp = (R[k] || {}).s;
    return sp && Object.prototype.hasOwnProperty.call(sm, sp) && sm[sp];
  });
  /* ② ويُقاس على نطاق الداخل: المدرسةُ للمدير والوكيل، والمجمعُ لمديره */
  let scope = "المنظومة كلُّها";
  if(isSchoolBound()){
    const st = stageBase(ME.school || "");
    keys = keys.filter(k=>{
      const r = R[k] || {};
      return r.k === ME.sector && r.c === ME.complex && stageBase(r.g || "") === st;
    });
    scope = ME.school || "";
  } else if(ME.role === "cxmgr"){
    keys = keys.filter(k=>{
      const r = R[k] || {};
      return r.c === ME.complex && (!ME.sector || r.k === ME.sector);
    });
    scope = ME.complex || "";
  }
  const byNo = new Set(), byNm = new Set();
  (DB.sched || []).forEach(L=>{
    if(!(L.teacher||"").trim()) return;
    const e = (L.teacherNo||"").trim();
    if(e) byNo.add(e);
    byNm.add((L.teacher||"").trim());
  });
  const done = [], left = [];
  keys.forEach(k=>{
    const r = R[k] || {};
    const sp = (D.specmap || {})[r.s] || r.s || "—";
    (byNo.has(k) || byNm.has((r.n||"").trim()) ? done : left).push([r.n || "—", k, sp]);
  });
  const coll = new Intl.Collator("ar");
  left.sort((a,b)=>coll.compare(a[0], b[0]));
  return {total: keys.length, done: done.length, left: left, scope: scope};
}

/* ⛔ حصةٌ مسجَّلةٌ بتخصصٍ حُذف من المنصة (كالتحفيظ) لا تجد لها خليةً فلا تُرسَم
   ولا يُعلَن عنها خطأ — فتضيع صامتةً. فتُعدُّ هنا بالاسم قبل كل شيء. */
function orphanSpec(){
  const live = {}; (D.specs || []).forEach(x=>{ live[x] = 1; });
  return (DB.sched || []).filter(L=>L && L.spec && !live[L.spec])
    .map(L=>[L.teacher || "—", L.spec, L.complex + " · " + L.stage,
             L.week + " · " + L.day + " · " + L.period]);
}
function rOrphan(p){
  const o = orphanSpec();
  if(!o.length) return;
  p.appendChild(el("div","msg bad",
    "حصصٌ مسجَّلةٌ بتخصصٍ لم يبقَ في المنصة، فلا خليةَ لها في الجدول ولا تظهر فيه. "
    + "تُنقل إلى تخصصها الصحيح أو تُحذف — ولا تُترك."));
  tbl(p, ["المعلم", "التخصص الملغى", "المدرسة", "موضعُها"], o);
}
function rPending(p){
  rOrphan(p);
  const s = pendingEntry();
  if(!s){
    p.appendChild(el("div","msg bad",
      "لا كشفَ معلمين في هذه المنصة، فلا سبيلَ إلى معرفة الناقص — "
      + "وقياسُ الجدول على الكشف لا على نفسه."));
    return;
  }
  /* ⚠️ والنطاقُ يُقال: «٣٤ معلماً» بلا نطاقٍ تُقرأ على المنظومة كلِّها */
  p.appendChild(el("div","note")).appendChild(el("div",null,
    TR("المقياسُ على نطاقك: ") + TR(s.scope)
    + TR(" — ومن لا تخصصَ تعليميٌّ له في الكشف لا يُنتظر منه تسجيلُ حصة.")));
  kpis(p, [[arn(s.total), "في كشف المعلمين"],
           [arn(s.done), "بحصةٍ في الجدول"],
           [arn(s.left.length), "بلا حصةٍ بعد"],
           [arn(Math.round(s.done / s.total * 100)) + "٪", "نسبةُ الإدخال"]]);
  if(!s.left.length){
    p.appendChild(el("div","msg ok",
      "كشفُ المعلمين تامُّ الإدخال: لكلِّ اسمٍ حصةٌ في الجدول."));
    return;
  }
  p.appendChild(el("div","msg bad",
    "هذه أسماءٌ بلا حصةٍ في الجدول. والجدولُ لا يكتمل قبلها، "
    + "والإسنادُ لا يكون على خانةٍ بلا معلم."));
  tbl(p, ["المعلم", "الرقم الوظيفي", "المادة"], s.left);
}

const REPORTS = [
  ["school",  "تقرير المدارس",        "لكل مدرسة: كم حصة، وكم حُضِّر ورُصد، ومتوسط النسبة"],
  ["teacher", "تقرير المعلمين",       "لكل معلم: عددُ الحصص والنسبةُ والمستوى وإجراءُ الجسر"],
  ["spec",    "تقرير التخصصات",       "لكل مادة: عدد الحصص ومتوسط النسبة — لتُعرف المادة المتعثّرة"],
  ["ind",     "تقرير المؤشرات",       "ترتيب المؤشرات الخمسين بمتوسط درجتها — مادة خطة التحسين"],
  ["strat",   "تقرير الإستراتيجيات",  "أيُّ إستراتيجيةٍ تُطبَّق أكثر، وبأي درجة"],
  ["appr",    "تقرير الاتجاهات",      "توزيع الاتجاهات التدريسية المعلنة"],
  ["active",  "تقرير التفعيل",        "مَن فعّل ومَن لم يفعّل: معلمون ومقيّمون وزائرون"],
  /* ⛔ التفعيلُ يعدّ الحاضرين، وهذا يعدّ الغائبين — ولا يُعرف الغائبُ إلا بالكشف */
  ["pending", "الإدخالُ الناقص",      "كشفُ المعلمين مقابلَ الجدول: من بلا حصةٍ مسجَّلةٍ بعد — بالاسم والرقم الوظيفي والمادة"],
  /* ⛔ **الفجوةُ كانت تُحسب ولا تُعرض**: `isGap` تُقرأ في حارس الرصد وفي بطاقة
     الحصة — حصةً حصة. فمن عليه رصدُها (الوكيلُ أو المديرُ أو مديرُ المجمع) لا
     يجد لها قائمةً، وهي **خُمسُ خلايا البنات**. (١ أكتوبر ٢٠٢٦) */
  ["gap",     "حصصٌ بلا مشرفٍ مختص",  "التخصصاتُ التي لا مشرفَ لها في نطاقك: من يرصدها، وهل رُصدت بعد"],
];

/* ⛔ تقريرُ الفجوة: ما لا مشرفَ لتخصصه في نطاق القارئ، وحالتُه */
function rGap(p){
  const rows = agg().filter(x=>isGap(x.L)).map(x=>{
    const L = x.L, pg = prog(L);
    return [[L.school || L.stage, L.complex].filter(Boolean).join(" · "),
            [L.week, L.day, L.period].filter(Boolean).join(" · "),
            L.spec || "—", L.teacher || "—",
            {tag: pg.issued ? "حُضِّر" : "لم يُحضَّر", cls: pg.issued ? "ok" : "no"},
            {tag: x.obs.length ? "رُصدت" : "لم تُرصد", cls: x.obs.length ? "ok" : "no"},
            L.approved ? "معتمدة" : "—",
            {btn: "افتح", id: L.id}];
  });
  const left = rows.filter(r=>r[5].tag === "لم تُرصد").length;
  kpis(p, [[arn(rows.length), "حصةً بلا مشرفٍ مختص"],
           [arn(rows.length - left), "رُصدت"],
           [arn(left), "تنتظر الرصد"]]);
  if(!rows.length){
    p.appendChild(el("div","msg ok",
      "لا حصةَ في نطاقك بلا مشرفٍ مختص — كلُّ تخصصٍ له مشرفُه."));
    return;
  }
  p.appendChild(el("div","msg warn",
    "هذه حصصُ تخصصاتٍ لا مشرفَ مختصّاً لها، فرصدُها على الفريق المعاون: "
    + (D.gapscore || []).map(k=>TR((D.roles.find(r=>r.k===k)||{}).t || k)).join(TR(" أو "))
    + TR(". ولا يرصدها غيرُهم.")));
  tbl(p, ["المدرسة والمجمع","الموعد","التخصص",D.lab_teacher_short,"التحضير","الرصد","الاعتماد",""], rows);
}

function agg(){                                    /* تجميعٌ واحد تُبنى عليه التقارير كلها */
  const byLesson = {};
  Object.values(DB.obs).forEach(v=>{
    if(!v.__lid || !v.res) return;
    (byLesson[v.__lid] = byLesson[v.__lid] || []).push(v);
  });
  /* ⛔ **التقاريرُ على نطاق صاحبها**: كانت السبعةُ كلُّها تُحسب على
     `DB.sched` كاملاً، فيقرأ مديرُ مدرسةٍ درجاتِ معلمي أربعة مجمعاتٍ
     وقطاعين. و`inMyScope` كانت مبنيّةً ولا تُنادى إلا في حارس الرصد.
     (١ أكتوبر ٢٠٢٦) */
  const src = (isScopeBound() && !isAdmin())
      ? DB.sched.filter(inMyScope) : DB.sched;
  return src.map(L=>{
    const obs = byLesson[L.id] || [];
    const pct = obs.length ? obs.reduce((a,v)=>a+(v.res.pct||0),0)/obs.length : null;
    /* ⛔ بطاقةُ الإستراتيجية تُقسَم على **من فتحها** لا على كل راصد: مشرفٌ
       ٩٠ وآخرُ لم يفتحها كان يُخرج ٤٥. (١ أكتوبر ٢٠٢٦) */
    const sgo = obs.filter(v=>(v.res.sgot || 0) > 0);
    const sg  = sgo.length ? sgo.reduce((a,v)=>a+v.res.sgot,0)/sgo.length : null;
    const peers = Object.values(DB.peer).filter(v=>v.__lid===L.id).length;
    const P = DB.prep[L.id] || {};
    return {L, obs, pct, sg, peers, issued: !!P.__issued,
            bridge: (obs.find(v=>(v.bridge||"").trim())||{}).bridge || ""};
  });
}
function lvlOf(p){ return p==null?"—": p>=90?"متميّز": p>=75?"جيد جداً": p>=50?"جيد":"يحتاج تحسيناً"; }
function avg(a){ return a.length ? Math.round(a.reduce((x,y)=>x+y,0)/a.length*10)/10 : null; }
function num(v){ return v==null ? "—" : arn(v); }

function ph5(m){
  if(ME.role === "teacher") return myTeacherReport(m);
  if(ME.role === "peer") return myPeerReport(m);
  const nav = el("div","card"); const nh=el("h3");
  nh.appendChild(el("span",null,"التقارير"));
  nh.appendChild(el("small",null,"كل ما ينتجه التطبيق — للطباعة أو التصدير")); nav.appendChild(nh);
  const np = el("div","pad"), bb = el("div","bar");
  REPORTS.forEach(([k,t])=>{
    const b = el("button", "b " + (RPT===k ? "" : "ghost"), t);
    b.addEventListener("click", ()=>{ RPT=k; shell(); }); bb.appendChild(b);
  });
  np.appendChild(bb);
  const meta = REPORTS.find(r=>r[0]===RPT);
  np.appendChild(el("div",null,meta[2])).style.cssText="color:var(--grey);font-family:JZL,SK;margin-top:8px";
  const bar2 = el("div","bar");
  const pr = el("button","b ghost","طباعة"); pr.addEventListener("click", ()=>window.print());
  const cs = el("button","b ghost","تصدير CSV"); cs.addEventListener("click", ()=>exportCSV(meta[1]));
  bar2.appendChild(pr); bar2.appendChild(cs);
  /* ⛔ النسخةُ الاحتياطيةُ والتفريغُ للمستشار وحده — الأولى تُنزِّل المنظومةَ
     كلَّها، والثاني يمحوها على كل الأجهزة. (٢٩ سبتمبر ٢٠٢٦) */
  if(isAdmin()){
    const bk = el("button","b ghost","نسخة احتياطية"); bk.addEventListener("click", backup);
    bar2.appendChild(bk);
    const wp = el("button","b warn","تفريغ البيانات");
    wp.title = "محوٌ كاملٌ للمنظومة — بعد نسخةٍ احتياطيةٍ وتأكيدٍ مكتوب";
    wp.style.marginInlineStart = "auto";
    wp.addEventListener("click", wipeAll);
    bar2.appendChild(wp);
  }
  np.appendChild(bar2);
  nav.appendChild(np); m.appendChild(nav);

  const c = el("div","card");
  const h = el("h3"); h.appendChild(el("span",null, meta[1])); c.appendChild(h);
  const p = el("div","pad"); p.id = "rptbody";
  ({school:rSchool, teacher:rTeacher, spec:rSpec, ind:rInd, strat:rStrat, appr:rAppr,
    active:rActive, pending:rPending, gap:rGap})[RPT](p);
  c.appendChild(p); m.appendChild(c);
}

function tbl(p, heads, rows){
  if(!rows.length){ p.appendChild(el("div","empty","لا بيانات بعد — تظهر التقارير بعد جدولة الحصص ورصدها.")); return; }
  const t = el("table"), tr = el("tr");
  heads.forEach(x=>tr.appendChild(el("th",null,x)));
  t.appendChild(tr);
  rows.forEach(r=>{
    const x = el("tr");
    r.forEach((v,i)=>{
      const td = el("td");
      if(v && v.tag){ td.appendChild(el("span","tag "+v.cls, v.tag)); }
      /* ⛔ وزرُّ الفتح في التقرير يُغني عن البحث عن الحصة بعد قراءتها */
      else if(v && v.btn){
        const b = el("button","b alt", v.btn);
        b.style.cssText = "padding:4px 12px;font-size:14px";
        b.addEventListener("click", ()=>{ CUR = v.id; PH = 6; shell(); });
        td.appendChild(b);
      }
      /* ⛔ خلايا التقارير تحمل قيماً مخزَّنة (مادةً ومرحلةً ومستوى) */
      else td.textContent = TR(v == null ? "—" : TR(v));
      if(i) td.style.textAlign = "center";
      x.appendChild(td);
    });
    t.appendChild(x);
  });
  p.appendChild(t);
  window.__rpt = {heads, rows: rows.map(r=>r.map(v=>v && v.tag ? v.tag : v))};
}

function kpis(p, list){
  const k = el("div","kpi"); k.style.marginBottom="12px";
  list.forEach(([b,s])=>{ const d=el("div"); d.appendChild(el("b",null,b)); d.appendChild(el("span",null,s)); k.appendChild(d); });
  p.appendChild(k);
}

function rSchool(p){
  const A = agg(), by = {};
  A.forEach(x=>{ const k = x.L.school || "—"; (by[k] = by[k] || []).push(x); });
  kpis(p, [[arn(A.length),"حصة مجدولة"],
           [arn(A.filter(x=>x.issued).length),"حُضِّرت"],
           [arn(A.filter(x=>x.obs.length).length),"رُصدت"],
           [num(avg(A.filter(x=>x.pct!=null).map(x=>x.pct)))+"٪","متوسط النسبة"]]);
  /* ⚠️ المدرسةُ هي نطاقُ المرحلة نفسه («الابتدائية- النفل»)، فلا يُكرَّر عمودان
     بالقيمة ذاتها: المجمعُ والقطاعُ هما ما يفرّق بينها. */
  tbl(p, ["المدرسة","المجمع","القطاع","الحصص","حُضِّرت","رُصدت","بطاقات الأقران","متوسط النسبة","المستوى"],
    Object.entries(by).map(([k,v])=>{
      const a = avg(v.filter(x=>x.pct!=null).map(x=>x.pct));
      return [k, v[0].L.complex||"—", v[0].L.sector||"—", arn(v.length),
              arn(v.filter(x=>x.issued).length), arn(v.filter(x=>x.obs.length).length),
              arn(v.reduce((s,x)=>s+x.peers,0)), num(a)+"٪", lvlOf(a)];
    }));
}

/* ⛔ التجميعُ بالرقم الوظيفي متى وُجد: الاسمُ وحده يُنشئ شخصين من واحد */
/* ⛔ **هويةُ الشخص في التقارير**: بالرقم إن وُجد، وإلّا بالاسم **مسوَّى** —
   وكان بالاسم كما كُتب، فينقسم «أحمد صيام» و«أحمد صيّام» شخصين في كل
   متوسطٍ وكل عدّ. (١ أكتوبر ٢٠٢٦) */
function whoKey(L){ return (L.teacherNo || "").trim() || ("~" + (arname(L.teacher) || "—")); }
function whoName(L){
  const r = (D.roster||{})[(L.teacherNo||"").trim()];
  return r ? r.n : (L.teacher || "—");
}
function rTeacher(p){
  const A = agg(), by = {};
  A.forEach(x=>{ const k = whoKey(x.L); (by[k] = by[k] || []).push(x); });
  tbl(p, ["المعلم","الرقم الوظيفي","المدرسة","المادة","حصصه","حُضِّرت","رُصدت",
          "متوسط النسبة","المستوى","البطاقة","إجراء الجسر"],
    Object.entries(by).map(([k,v])=>{
      const a = avg(v.filter(x=>x.pct!=null).map(x=>x.pct));
      const s = avg(v.filter(x=>x.sg!=null).map(x=>x.sg));
      const br = (v.find(x=>x.bridge)||{}).bridge || "";
      return [whoName(v[0].L), (v[0].L.teacherNo||"—"), v[0].L.school||"—",
              v[0].L.subject||"—", arn(v.length),
              arn(v.filter(x=>x.issued).length), arn(v.filter(x=>x.obs.length).length),
              num(a)+"٪", lvlOf(a), s==null?"—":num(s)+" من ١٠٠", br || "—"];
    }));
}

function rSpec(p){
  const A = agg(), by = {};
  A.forEach(x=>{ const k = x.L.subject || "—"; (by[k] = by[k] || []).push(x); });
  const rows = Object.entries(by).map(([k,v])=>{
    const a = avg(v.filter(x=>x.pct!=null).map(x=>x.pct));
    return [k, arn(v.length), arn(new Set(v.map(x=>whoKey(x.L))).size),
            arn(v.filter(x=>x.issued).length), num(a)+"٪", lvlOf(a), a];
  }).sort((x,y)=>(x[6]==null?999:x[6])-(y[6]==null?999:y[6]));
  tbl(p, ["المادة","الحصص","المعلمون","حُضِّرت","متوسط النسبة","المستوى"], rows.map(r=>r.slice(0,6)));
}

function rInd(p){
  const acc = {};
  Object.values(DB.obs).forEach(v=>{
    Object.entries(v.ind||{}).forEach(([k,val])=>{
      if(val === "na" || !val) return;
      (acc[k] = acc[k] || []).push(Number(val));
    });
  });
  const rows = Object.entries(acc).map(([k,arr])=>{
    const [di,ii] = k.split("_").map(Number);
    const dm = D.domains[di] || {inds:[]};
    const a = avg(arr);
    return [arn(di+1)+"·"+arn(ii+1), (dm.inds[ii]||"—"), arn(arr.length), num(a) + " من ٤",
            {tag: a>=3.5?"قوي": a>=2.5?"متوسط":"ضعيف", cls: a>=3.5?"ok": a>=2.5?"mid":"no"}, a];
  }).sort((x,y)=>x[5]-y[5]);
  if(rows.length) kpis(p, [[arn(rows.length),"مؤشراً مرصوداً"],
    [rows[0][0],"أضعف مؤشر"], [rows[rows.length-1][0],"أقوى مؤشر"]]);
  tbl(p, ["الرمز","المؤشر","مرات الرصد","متوسط الدرجة","الحكم"], rows.map(r=>r.slice(0,5)));
}

function rStrat(p){
  const A = agg(), by = {};
  A.forEach(x=>{ const k = x.L.strategy || "—"; (by[k] = by[k] || []).push(x); });
  tbl(p, ["الإستراتيجية","مرات الإعلان","المعلمون","متوسط البطاقة من ١٠٠","درجة المؤشر"],
    Object.entries(by).map(([k,v])=>{
      const s = avg(v.filter(x=>x.sg!=null).map(x=>x.sg));
      const m = s==null?null: s>=90?4: s>=75?3: s>=50?2:1;
      return [k, arn(v.length), arn(new Set(v.map(x=>whoKey(x.L))).size), num(s), num(m)];
    }).sort((a,b)=>b[1].length-a[1].length));
}

function rAppr(p){
  const A = agg(), by = {};
  A.forEach(x=>{ const k = x.L.approach || "—"; (by[k] = by[k] || []).push(x); });
  tbl(p, ["الاتجاه التدريسي","الحصص","المعلمون","متوسط النسبة"],
    Object.entries(by).map(([k,v])=>{
      const a = avg(v.filter(x=>x.pct!=null).map(x=>x.pct));
      return [k, arn(v.length), arn(new Set(v.map(x=>whoKey(x.L))).size), num(a)+"٪"];
    }));
}

function rActive(p){
  /* كل فردٍ في المنظومة وما فعّله فعلاً */
  const people = {};
  /* ⛔ المفتاحُ الرقمُ الوظيفي متى وُجد: الاسمُ وحده يجعل «محمد العلي» و«محمد علي»
     شخصين، فينقسم تفعيلُ الواحد على اثنين. */
  const put = (name, role, no) => { if(!(name||"").trim()) return;
    const k = (no||"").trim() || ("~" + name.trim());
    people[k] = people[k] || {name:name.trim(), no:(no||"").trim(),
                              roles:new Set(), sched:0, prep:0, obs:0, peer:0};
    if(no && !people[k].no) people[k].no = no;
    people[k].roles.add(role); return people[k]; };
  DB.sched.forEach(L=>{
    const t = put(L.teacher, "معلم", L.teacherNo); if(t) t.sched++;
    /* ⛔ **الزائرُ برقمه كالمعلم**: كان يُدخَل بالاسم وحدَه فيصير مفتاحُه
       «~الاسم»، فينقسم الشخصُ الواحدُ صفّين — صفُّ «معلم» بحصصه وصفُّ
       «زائر · لم يفعّل». والرقمُ موجودٌ بجانبه في `peer1e`. (١ أكتوبر ٢٠٢٦) */
    [[L.peer1, L.peer1e], [L.peer2, L.peer2e]].forEach(([n, no])=>{
      const x = put(n, "زائر", no); if(x) x.sched += 0;
    });
    [L.ev1, L.ev2, L.ev3, L.ev4].forEach(n=>put(n, "مقيّم"));
  });
  Object.entries(DB.prep).forEach(([lid,P])=>{
    if(lid.indexOf(TRASH) === 0 || lid.indexOf(LOG) === 0) return;   /* مفاتيحُ جانبية */
    if(!P.__issued) return;
    const L = DB.sched.find(x=>x.id===lid); if(!L) return;
    const x = put(L.teacher, "معلم", L.teacherNo); if(x) x.prep++;
  });
  /* ⛔ الرصدُ يُنسب إلى المقيّم المسنَد في الجدول لا إلى اسم الدخول:
     لو اختلف الاسمان حرفاً ظهر الشخصُ مرتين — مرةً «لم يفعّل» ومرةً «مفعِّل».
     ومفتاحُ الرصد يحمل صفةَ المقيّم، فمنها يُعرف صاحبُها في الجدول. */
  const SLOT = {}; D.evalroles.forEach((r,i)=>{ SLOT[r] = ["ev1","ev2","ev3","ev4"][i]; });
  Object.entries(DB.obs).forEach(([k,v])=>{
    const L = DB.sched.find(z=>z.id===v.__lid) || {};
    const role = k.split("|")[1] || "";
    const named = L[SLOT[role]] || v.__by;
    const x = put(named, "مقيّم"); if(x){ x.obs++; if(v.__by && v.__by !== named) x.alias = v.__by; }
  });
  Object.entries(DB.peer).forEach(([k,v])=>{
    const named = k.split("|")[1] || v.__by;     /* مفتاحُ الأقران يحمل اسمَ الزائر */
    const x = put(named, "زائر"); if(x) x.peer++;
  });
  const rows = Object.values(people).map(x=>{
    const active = x.prep + x.obs + x.peer;
    return [x.name + (x.alias ? "  (دخل باسم: " + x.alias + ")" : ""), x.no || "—",
            [...x.roles].join(" · "), arn(x.sched), arn(x.prep), arn(x.obs), arn(x.peer),
            {tag: active ? "مفعِّل" : "لم يفعّل", cls: active ? "ok" : "no"}, active];
  }).sort((a,b)=>a[8]-b[8]);
  const off = rows.filter(r=>!r[8]).length;
  kpis(p, [[arn(rows.length),"فرداً في المنظومة"], [arn(rows.length-off),"فعّلوا"], [arn(off),"لم يفعّلوا"]]);
  tbl(p, ["الاسم","الرقم الوظيفي","الدور","حصصه المجدولة","تحضيرات صدرت",
          "استمارات رصدها","بطاقات أقران","التفعيل"],
    rows.map(r=>r.slice(0,8)));
}

function exportCSV(name){
  const R = window.__rpt;
  if(!R) return alert("لا جدول لتصديره.");
  const esc = v => '"' + String(v==null?"":v).replace(/"/g,'""') + '"';
  const csv = "﻿" + [R.heads.map(esc).join(","), ...R.rows.map(r=>r.map(esc).join(","))].join("\n");
  const a = document.createElement("a");
  a.href = "data:text/csv;charset=utf-8," + encodeURIComponent(csv);
  a.download = name + ".csv"; a.click();
}

/* ═════════ الإقلاع ═════════ */
let lastPull = 0;
/* غيرُ المقيّم لا يملك زرَّ تحديث، فتُسحب له البياناتُ تلقائياً كل نصف دقيقة عند التنقّل */
function autoPull(){
  if(!api() || isAdmin()) return;
  const now = Date.now();
  if(now - lastPull < 30000) return;
  lastPull = now;
  pull().then(ok=>{ if(ok && PH !== 2) render(); });
}
function boot(){ if(!ME) login(); else shell(); }
/* ⛔ لا يُطلب من معلمةٍ أن تلصق رابطاً: الرابطُ الذي تصلها يحمل المخزن في #srv=
   فيُربط جهازُها من أول فتحةٍ ثم يُنظَّف العنوان فلا يبقى فيه شيء. */
function adoptSrv(){
  try{
    const h = location.hash || "", q = location.search || "";
    let m = h.match(/[#&]srv=([^&]+)/) || q.match(/[?&]srv=([^&]+)/);
    if(!m) return false;
    const u = decodeURIComponent(m[1]);
    if(!/^https?:\/\//.test(u)) return false;
    /* ومعه مفتاحُ المخزن إن حمله الرابط */
    const mk = h.match(/[#&]k=([^&]+)/) || q.match(/[?&]k=([^&]+)/);
    const kk = mk ? decodeURIComponent(mk[1]) : "";
    if(kk){ try{ localStorage.setItem(SKEY, kk); }catch(e){} }
    if(api() === u && !kk) return false;
    localStorage.setItem(API, u);
    history.replaceState(null, "", location.pathname);
    return true;
  }catch(e){ return false; }
}
/* هجرةٌ: مدرستا عرقه الابتدائيتان اندمجتا، فتُنسب حصصُهما القديمة إلى المدموجة */
function migrate(){
  /* خريطةُ الزمن كانت تُحفظ بالموضع (t_0…t_6)، فتُنقل إلى مفاتيحها */
  Object.values(DB.prep || {}).forEach(P=>{
    if(!P || P.__tmig) return;
    let moved = 0;
    (D.tlegacy || []).forEach((k, j)=>{
      if(P["t_" + j] != null && P["t_" + j] !== ""){ P["tk_" + k] = P["t_" + j]; moved++; }
      delete P["t_" + j];
    });
    if(moved) P.__tmig = 1;
  });
  const OLDST = {"الابتدائية- أولية":"الابتدائية- عرقة", "الابتدائية- عليا":"الابتدائية- عرقة"};
  const OLDWK = D.wmig || {};
  let n = 0;
  (DB.sched||[]).forEach(L=>{
    const st = OLDST[L.stage];
    if(st){ L.stage = st; L.school = st; n++; }
    /* ⚠️ «الأسبوع السادس» موجودٌ في الترقيمين، فتُقرأ الخريطةُ مرةً واحدةً
       على القيمة الأصلية — ولو استُبدل تتابعاً لانزلق الأسبوعُ مرتين. */
    const wk = OLDWK[L.week];
    if(wk){ L.week = wk; const c = calOf(wk);
            if(c && c.days[L.day]){ L.date = c.days[L.day].g;
              L.datetxt = c.days[L.day].gt; L.hijri = c.days[L.day].ht; } n++; }
    if(!L.sector){ L.sector = D.sectors[0]; n++; }
    if(st || wk || L.gk.split("|").length < 7)
      L.gk = [L.sector, L.complex, L.stage, L.period, L.week, L.day, L.spec].join("|");
  });
  if(n) save();
}
load();
/* ⛔ **الهجرةُ مرةً واحدةً أبداً**: كانت تُنادى في كل إقلاع، فأيُّ مفتاحٍ فيها
   يوافق قيمةً قائمةً ينقل السجلَّ في كل فتحةِ صفحة. وعلامةُ الإصدار تمنع ذلك
   ولو عاد مفتاحٌ ملغومٌ يوماً. والاستثناءُ يُرى ولا يُبلَع. (٣٠ سبتمبر ٢٠٢٦) */
try{ if(DB.__schema !== 3){ migrate(); DB.__schema = 3; save(); } }
catch(e){ try{ console.error("migrate:", e); }catch(_){}
  try{ setSyn("تعذّرت هجرةُ البيانات — راجع إدارة التخطيط", "warnsyn"); }catch(_){} }
adoptSrv();
/* ⛔ **هجرةُ المخزن المشترك** — لا تكفي هجرةُ الجهاز: السجلُّ القديمُ على
   الخادم كان اسمُه `db`، وهو في الواقع سجلُّ البنين (نسخةُ البنات وُلدت بعده).
   فينُقل مرةً واحدةً إلى `ikm_db`، **وبشرطين** لا يُستثنى منهما: أن يكون
   الجديدُ خالياً فلا يُطمَس شيء، وأن يكون القديمُ ذا حصص. ولا يُحذف القديم.
   ⚠️ ولا تجري لنسخة البنات أبداً: `db` ليس سجلَّها. (١ أكتوبر ٢٠٢٦) */
function moveSrv(){
  if(NS !== "ikm" || !api()) return Promise.resolve(false);
  try{ if(localStorage.getItem(NS + "_srv_moved")) return Promise.resolve(false); }
  catch(e){ return Promise.resolve(false); }
  const mark = ()=>{ try{ localStorage.setItem(NS + "_srv_moved", "1"); }catch(e){} };
  return fetch(apiGet("platform", SID)).then(r=>r.json())
    .then(nw=>{
      const cur = (nw && nw.ok && nw.data) ? nw.data : null;
      if(cur && ((cur.sched||[]).length || Object.keys(cur.prep||{}).length)){ mark(); return false; }
      return fetch(apiGet("platform", "db")).then(r=>r.json()).then(od=>{
        const old = (od && od.ok && od.data) ? od.data : null;
        if(!old || !(old.sched||[]).length){ mark(); return false; }
        return fetch(api(), {method:"POST", headers:{"Content-Type":"text/plain;charset=utf-8"},
            body: apiBody({kind:"platform", id:SID, data:old})})
          .then(r=>r.json())
          .then(r=>{ if(r && r.ok){ mark(); return true; } return false; });
      });
    })
    .catch(()=>false);
}
/* ═════════ كشفُ المعلمين — يُحمَّل ولا يُضمَّن ═════════
   ⛔ كان الكشفُ (٤٦٠ اسماً ورقماً وظيفياً) مكتوباً في شفرة الصفحة المنشورة،
      و**الرقمُ الوظيفي هو كلمةُ الدخول** — فكان كشفَ هوياتٍ ومفاتيحَ معاً
      لكل من يفتح «عرض المصدر». فأُخرج من البناء كلَّه (١ أكتوبر ٢٠٢٦).
   الآن: يرفعه المستشارُ مرةً إلى المخزن المشترك، ويُقرأ منه عند الإقلاع
      ويُحفظ على الجهاز ليعمل بعدها بلا شبكة. ومن لا كشفَ عنده يكتب اسمَه
      كما كان يفعل قبل الكشف — فلا تتعطّل المنصةُ بغيابه. */
const RKEY = KEY + "_roster";
function rosterLocal(){
  try{ const t = localStorage.getItem(RKEY); if(t) D.roster = JSON.parse(t) || {}; }catch(e){}
}
function rosterPull(){
  if(!api()) return Promise.resolve(false);
  return fetch(apiGet("platform", NS + "_roster")).then(r=>r.json())
    .then(r=>{
      const d = (r && r.ok && r.data) ? r.data : null;
      if(!d || !Object.keys(d).length) return false;
      D.roster = d;
      try{ localStorage.setItem(RKEY, JSON.stringify(d)); }catch(e){}
      return true;
    }).catch(()=>false);
}
/* ⛔ ولا يُرفع كشفٌ لا تعرف المنصةُ مادةَ كلِّ سطرٍ فيه: كان حارسُ البناء
   يفحص ذلك، وقد خرج الكشفُ من البناء — فينتقل الحارسُ إلى لحظة الرفع.
   ومن يمرّ بلا مطابقةٍ يدخل صاحبُه بلا تخصصٍ ولا يُنبَّه أحد. */
function rosterCheck(d){
  if(!d || typeof d !== "object" || Array.isArray(d)) return "الملفُّ ليس كشفاً — يُتوقَّع كائنٌ مفاتيحُه الأرقامُ الوظيفية.";
  const ks = Object.keys(d);
  if(!ks.length) return "الكشفُ خالٍ.";
  const bad = ks.filter(k=>!/^\d+$/.test(k)).slice(0, 5);
  if(bad.length) return "مفاتيحُ غيرُ رقمية: " + bad.join(" · ");
  const noname = ks.filter(k=>!(d[k] && d[k].n)).slice(0, 5);
  if(noname.length) return "سطورٌ بلا اسم: " + noname.join(" · ");
  const sm = D.specmap || {};
  const nos = [];
  ks.forEach(k=>{ const sp = (d[k]||{}).s || ""; if(!(sp in sm) && nos.indexOf(sp) < 0) nos.push(sp); });
  if(nos.length) return "موادُّ لا تعرفها المنصة: " + nos.slice(0, 6).join(" · ")
                        + "\n\nراجع مديرَ التخطيط والاعتماد المدرسي قبل الرفع.";
  return "";
}
function rosterUp(){
  if(!isAdmin()) return;
  if(!api()){ alert("⛔ اربط المخزنَ المشترك أولاً — الكشفُ يُرفع إليه لا إلى الجهاز."); return; }
  const inp = document.createElement("input");
  inp.type = "file"; inp.accept = ".json,application/json";
  inp.addEventListener("change", ()=>{
    const f = inp.files && inp.files[0]; if(!f) return;
    const fr = new FileReader();
    fr.onload = ()=>{
      let d = null;
      try{ d = JSON.parse(String(fr.result)); }catch(e){ alert("⛔ الملفُّ ليس JSON سليماً: " + e.message); return; }
      /* يَقبل الحمولةَ كما يكتبها المولّد، أو الكشفَ وحدَه */
      if(d && d.data && typeof d.data === "object" && !d.n) d = d.data;
      const why = rosterCheck(d);
      if(why){ alert("⛔ لم يُرفع الكشف.\n\n" + why); return; }
      const n = Object.keys(d).length;
      uiAsk("رفعُ كشفِ " + arn(n) + " معلماً إلى المخزن المشترك.\n\n"
        + "يحلُّ محلَّ الكشف القائم، ويراه كلُّ من فتح المنصةَ بعد ربطِ الخادم.\n\n"
        + "أتُتابع؟", "ارفعه").then(ok=>{
      if(!ok) return;
      fetch(api(), {method:"POST", headers:{"Content-Type":"text/plain;charset=utf-8"},
          body: apiBody({kind:"platform", id:NS+"_roster", data:d, __replace:true})})
        .then(r=>r.json())
        .then(r=>{
          if(!(r && r.ok)){ alert("⛔ لم يستجب الخادمُ للرفع."); return; }
          D.roster = d;
          try{ localStorage.setItem(RKEY, JSON.stringify(d)); }catch(e){}
          logAct("رفع كشف المعلمين", arn(n) + " معلماً", null);
          save();
          alert("✓ رُفع الكشف: " + arn(n) + " معلماً.");
          shell();
        })
        .catch(e=>alert("تعذّر الاتصال بالخادم: " + e.message));
      });
    };
    fr.readAsText(f, "utf-8");
  });
  inp.click();
}
rosterLocal();
if(api()) moveSrv().then(()=>Promise.all([pull(), rosterPull()])).then(boot); else boot();

/* ═════════ المرحلة ٢: الاستعداد والتحضير ═════════ */
/* ⛔ أدواتُ التحضير الأربع: نموذجُه الورقي ونشرتُه، وبنكُ بطاقات الإستراتيجيات
   التسع عشرة، ونشراتُ الاتجاهات الستة. كانت مخبوءةً داخل شرحِ المرحلة المطويّ،
   وبنكُ البطاقات لم يكن في هذه المرحلة أصلاً — وهي أوّلُ ما يحتاجه المعلم.
   (طلبُ المستشار ٣٠ سبتمبر ٢٠٢٦) */
/* ═════════ مساحةُ الاطّلاع — قسمان لا بطاقتان متفرّقتان ═════════
   ⛔ كانت النشراتُ أزراراً في بطاقة «أدوات التحضير» والنماذجُ المعبّأةُ سطوراً
      فوقها بلا عنوانٍ يفصلهما — فلا يعرف المعلمُ أيُّها نموذجٌ يُحاكيه وأيُّها
      نشرةٌ يقرؤها قبل أن يبدأ. فصارت مساحةً واحدةً بقسمَين صريحَين:
      **نماذجُ تحضيرٍ وفق تخصصه** · و**نشراتٌ تُقرأ قبل التحضير**.
      (طلبُ المستشار ١ أكتوبر ٢٠٢٦)
   ⚠️ والنشراتُ ثلاثٌ بأسمائها لا «وثائقُ المرحلة» كلُّها: شرحُ نموذج التحضير ·
      بنكُ بطاقات الإستراتيجيات · شرحُ الاتجاهات التدريسية. والقالبُ الورقيُّ
      ليس نشرةً — محلُّه «طريقة التحضير» حيث يُنزَّل. */
/* الطريقةُ المختارةُ تُحفظ على الجهاز فلا يُسأل المعلمُ في كل مرة */
const WAYK = KEY + "_prepway";
function prepWay(){
  let w = "e";
  try{ w = localStorage.getItem(WAYK) || "e"; }catch(e){}
  return ["p", "e", "ai"].indexOf(w) < 0 ? "e" : w;
}
/* ⛔ **ومساحةُ الطرق تظهر قبل اختيار الحصة أيضاً**: كان المعلمُ يفتح المرحلةَ
   الثانيةَ فيرى قائمةَ حصصه وحدَها — ولا يعلم أن له ثلاثَ طرقٍ أصلاً، ولا
   يستطيع تنزيلَ القالب الورقي قبل أن يختار حصة. وتنزيلُ القالب لا ينتظر
   اختيارَ حصة. (طلبُ المستشار ١ أكتوبر ٢٠٢٦) */
function wayCard(way){
  const wc = el("div","card");
  const wh = el("h3");
  wh.appendChild(el("span",null,"طريقة التحضير"));
  wh.appendChild(el("small",null,"اختر طريقتك — والنموذجُ الإلكترونيُّ أسفلَها في الحالتين"));
  wc.appendChild(wh);
  const wp = el("div","pad");
  const ways = el("div","ways");
  [["p",  "القالب الورقي",      "تُنزّله وتكتبه بيدك — وورد أو PDF للطباعة"],
   ["e",  "التحضير الإلكتروني", "تملأ الخانات هنا في المنصة، ويُحفظ ويُطبع ويُنزَّل"],
   ["ai", "التحضير بالذكاء الاصطناعي", "تنسخ الأمرَ، تُلصقه في المساعد خارج المنصة، ثم تُلصق جوابَه هنا فتُملأ الخانات"]
  ].forEach(([k, t, d])=>{
    const b = el("button", "way" + (way === k ? " on" : ""));
    b.appendChild(el("b",null,t));
    b.appendChild(el("span",null,d));
    b.addEventListener("click", ()=>{
      try{ localStorage.setItem(WAYK, k); }catch(e){}
      shell(); window.scrollTo(0, 0);
    });
    ways.appendChild(b);
  });
  wp.appendChild(ways);
  if(way === "p"){
    const pz = el("div","msg");
    pz.appendChild(el("b",null,"نزّل القالبَ واكتبه بيدك"));
    pz.appendChild(el("span",null,
      "وإن أردتَ أن يُرصد تحضيرُك في المنصة فأدخِله بعد ذلك في «التحضير الإلكتروني» — "
      + "أو ارفع ملفَ وورد في «التحضير بالذكاء الاصطناعي» فيُوزَّع على الخانات."));
    wp.appendChild(pz);
    const dl = el("div","bar");
    ((D.phases || []).find(x=>x.id === 2) || {docs: []}).docs
      .filter(d=>Array.isArray(d) && String(d[0]).indexOf("القالب الورقي") === 0)
      .forEach(([t, u, , uen])=>{
        const a = el("a","b", t); a.href = (LANG === "en" && uen) ? uen : u;
        a.target = "_blank"; a.rel = "noopener"; dl.appendChild(a);
      });
    wp.appendChild(dl);
  } else if(way === "ai"){
    wp.appendChild(el("div","msg",
      "اختر حصتك من القائمة أعلاه — فمساحةُ صياغة الأمر تُبنى من درسك وإستراتيجيتك."));
  }
  wc.appendChild(wp);
  return wc;
}
function prepTools(m){
  const ph = (D.phases || []).find(x=>x.id === 2) || {};
  const all = (ph.docs || []).filter(d=>Array.isArray(d) && d[1]
      && (!d[2] || d[2] === "*" || d[2].split(",").indexOf(ME.role) >= 0));
  /* النشراتُ = وثائقُ المرحلة ما خلا القالبَ الورقي (محلُّه طريقةُ التحضير) */
  const sheets = all.filter(d=>String(d[0]).indexOf("القالب الورقي") !== 0);
  const models = modelList();
  if(!sheets.length && !models.length) return;
  const c = el("div","card"), h = el("h3");
  h.appendChild(el("span",null,"للاطّلاع قبل التحضير"));
  h.appendChild(el("small",null,"نماذجُ في تخصصك · ونشراتٌ تشرح النموذجَ والإستراتيجيات والاتجاهات"));
  c.appendChild(h);
  const p = el("div","pad");

  /* ① نماذجُ تحضيرٍ وفق تخصصه */
  const s1 = el("div","sect");
  s1.appendChild(el("b",null,"نماذج تحضير للاطّلاع عليها وفق تخصصك"));
  if(models.length){
    const sp = (gctx().spec) || "";
    s1.appendChild(el("i",null, "تخصصك: " + TR(sp) + " — نماذجُ معبّأةٌ تُحاكي طريقةَ التحضير، مرتَّبةً بالمرحلة"));
    const byStage = {};
    models.forEach(x=>{ (byStage[x.stage] = byStage[x.stage] || []).push(x); });
    ["الابتدائية","المتوسطة","الثانوية"].forEach(st=>{
      const arr = byStage[st]; if(!arr || !arr.length) return;
      const r = el("div","mrow");
      r.appendChild(el("i",null, st));
      const ul = el("div","docs");
      arr.forEach(x=>{
        const a = el("a","mini", x.t.split("—").slice(1).join("—").trim() || x.t);
        a.href = x.u; a.target = "_blank"; a.rel = "noopener"; a.title = x.t; ul.appendChild(a);
      });
      r.appendChild(ul); s1.appendChild(r);
    });
  } else {
    /* ⛔ ولا يُترك القسمُ خاوياً بلا كلمة: يُقال لِمَ لا نموذجَ له */
    s1.appendChild(el("div","empty",
      ME.role !== "teacher"
        ? "النماذجُ المعبّأةُ تُعرض للمعلم القائم بالحصة وفق تخصصه."
        : "لا نموذجَ معبّأٌ في تخصصك بعد — واطّلع على النشرات أدناه."));
  }
  p.appendChild(s1);

  /* ② نشراتٌ تُقرأ قبل التحضير */
  const s2 = el("div","sect");
  s2.appendChild(el("b",null,"نشرات للاطّلاع عليها قبل التحضير"));
  s2.appendChild(el("i",null,"شرحُ نموذج التحضير · بنكُ بطاقات الإستراتيجيات · شرحُ الاتجاهات التدريسية"));
  const bar = el("div","bar");
  sheets.forEach(([t, u, r, uen])=>{
    const a = el("a","b ghost", t);
    a.href = (LANG === "en" && uen) ? uen : u;
    a.target = "_blank"; a.rel = "noopener";
    bar.appendChild(a);
  });
  s2.appendChild(bar);
  p.appendChild(s2);
  c.appendChild(p); m.appendChild(c);
}
/* نماذجُ تخصصِ المعلم — تُقرأ مرةً وتُستعمل في موضعين */
function modelList(){
  if(ME.role !== "teacher" || !D.models) return [];
  return D.models[(gctx().spec) || ""] || [];
}
/* بطاقةُ الإستراتيجية المعلنة: مؤشراتُها العشرة ورابطُ بطاقتها المطبوعة */
function stratCard(m, L, P){
  const st = (P && P.f_strat) || (L && L.strategy) || "";
  const b = D.bank.find(x=>x.name === st);
  const c = el("div","card"), h = el("h3");
  h.appendChild(el("span",null,"بطاقة الإستراتيجية المعلنة"));
  h.appendChild(el("small",null, st || "لم تُعلَن بعد"));
  c.appendChild(h);
  const p = el("div","pad");
  if(!b){
    p.appendChild(el("div","empty",
      "اختر الإستراتيجية في خانة الجدول أو في التحضير، فتظهر مؤشراتُها العشرة هنا "
      + "ومعها رابطُ بطاقتها."));
  } else {
    p.appendChild(el("div","note")).appendChild(el("div",null,
      "مؤشراتُ تطبيقها العشرة — وهي ما يرصده الزائر في حصتك:"));
    const ol = el("ol"); ol.style.cssText = "padding-inline-start:22px;font-size:15.5px";
    b.inds.forEach(x=>ol.appendChild(el("li",null,x)));
    p.appendChild(ol);
    if(b.u){
      const bar = el("div","bar");
      /* ⚠️ الوصلُ قبل الترجمة يُفوّت المفتاحين معاً: يُترجَم كلُّ جزءٍ وحدَه
         ثم يُوصل — واسمُ الإستراتيجية له مفتاحُه في المعجم. */
      const a = el("a","b"); a.textContent = TR("افتح بطاقة «") + TR(b.name) + "»";
      a.href = b.u; a.target = "_blank"; a.rel = "noopener";
      bar.appendChild(a); p.appendChild(bar);
    }
  }
  c.appendChild(p); m.appendChild(c);
}
function ph2(m){
  const L = DB.sched.find(x=>x.id===CUR);
  if(!L){
    picker(m, "اختر الحصة التي تحضّر لها", ()=>shell());
    if(ME.role === "teacher") m.appendChild(wayCard(prepWay()));
    prepTools(m);
    return;
  }
  const P = DB.prep[L.id] = DB.prep[L.id] || {};
  /* ⛔ **التحضيرُ ملكُ صاحبه**: كان الحرسُ بالدور وحدَه، فيفتح معلمٌ تحضيرَ
     زميله ويعدّله ويُصدره باسمه — وخانةُ الجدول محروسةٌ بـ`isMine` والبابُ
     الخلفيُّ مفتوح. (٣٠ سبتمبر ٢٠٢٦) */
  const ro = ME.role !== "teacher" || !isMine(L) || !!L.approved;
  const head = el("div","card");
  const h = el("h3"); h.appendChild(el("span",null, lessonTitle(L)));
  h.appendChild(el("small",null, lessonSub(L))); head.appendChild(h);
  const hp = el("div","pad"), bar = el("div","bar");
  const back = el("button","b ghost","تغيير الحصة");
  back.addEventListener("click", ()=>{ CUR=null; shell(); });
  bar.appendChild(back);
  if(!ro){
    const iss = el("button","b"); iss.id="issue";
    iss.addEventListener("click", ()=>issue(L,P));
    bar.appendChild(iss);
    let sh = false;
    const ha = el("button","b ghost","إظهار كل التلميحات");
    ha.addEventListener("click", ()=>{ sh=!sh;
      document.querySelectorAll(".hint").forEach(x=>x.style.display = sh ? "" : "none");
      ha.textContent = TR(sh ? "إخفاء التلميحات" : "إظهار كل التلميحات"); });
    bar.appendChild(ha);
  }
  const pr = el("button","b ghost","طباعة"); pr.addEventListener("click", ()=>window.print());
  bar.appendChild(pr);
  hp.appendChild(bar);
  const out = el("div"); out.id = "issueOut"; hp.appendChild(out);
  if(P.__issued){
    const w = el("div","msg ok"); w.textContent = TR("صدر هذا التحضير في " + P.__issued);
    hp.appendChild(w);
  }
  /* ⛔ **لا صفحةَ ميتةٌ بلا كلمة.** كان المعلمُ إذا لم تُعدَّ الحصةُ له يرى
     الصفحةَ كلَّها معطَّلةً — لا لوحةَ ذكاءٍ ولا خانةً تُكتب — ولا سطرَ يقول
     لِمَ. فيظنُّ المنصةَ عاطلةً وهي تمنعه بحقّ. والسببُ يُقال، ويُعطى مخرَجٌ:
     إن كانت حصتَه فعلاً صحَّح الاسمَ بنقرةٍ ويُسجَّل ذلك. (١ أكتوبر ٢٠٢٦) */
  if(ro && ME.role === "teacher" && !L.approved){
    const why = notMineWhy(L);
    if(why){
      const w = el("div","msg warn");
      w.appendChild(el("div",null, "⛔ التحضيرُ مقفولٌ لأن هذه الحصةَ ليست باسمك. " + why));
      w.appendChild(el("div",null, "ولا يُحضَّر عن معلمٍ غيرِه — فالتحضيرُ شاهدُ صاحبه."));
      const fx = el("button","b sm","هذه حصتي — صحِّح الاسمَ إلى اسمي");
      fx.style.marginTop = "7px";
      fx.addEventListener("click", ()=>{
        uiAsk("ستُسجَّل هذه الحصةُ باسمك: " + (ME.name||"") + "\n\n"
          + "ويُسجَّل التغييرُ في سجلّ العمليات باسمك وتاريخه. أتُتابع؟",
          "سجّلها باسمي").then(ok=>{
          if(!ok) return;
          const was = L.teacher || "—";
          L.teacher = ME.name; if(ME.emp) L.teacherNo = ME.emp;
          logAct("تصحيح اسم المعلم", "كانت باسم " + was + " وصارت باسم " + ME.name, L);
          save(); shell();
        });
      });
      w.appendChild(fx);
      hp.appendChild(w);
    }
  }
  head.appendChild(hp); m.appendChild(head);
  /* ضخُّ بيانات الحصة الأساسية من خليّة الجدول — كما في نموذج إكسل التحضير */
  inject(L, P);
  const c0 = el("div","card"); const h0 = el("h3");
  h0.appendChild(el("span",null,"بيانات الحصة"));
  h0.appendChild(el("small",null,"مضخوخةٌ من خليّة الجدول — أكمل ما بقي")); c0.appendChild(h0);
  const src = el("div","srcbar");
  src.appendChild(el("span",null,"مصدرها: " + lessonSub(L)));
  const rb = el("button","b ghost sm","أعد الضخّ من الجدول");
  /* ⛔ يكتب فوق ما كتبه المعلم — فلا يُنفَّذ إلا بعد أن يُسمّى له ما سيضيع */
  rb.addEventListener("click", ()=>{
    const will = [["الاسم", P.i_teacher], ["المادة", P.i_subject], ["الفصل", P.i_klass],
                  ["الحصة", P.i_period], ["التاريخ", P.i_date], ["الإستراتيجية", P.f_strat]]
                 .filter(x=>(x[1]||"").trim()).map(x=>x[0]);
    const go = ()=>{ inject(L, P, true); save(); shell(); };
    if(!will.length){ go(); return; }
    uiAsk("سيُكتب فوق ما أدخلتَه في: " + will.join(" · ")
      + "\nوتُستبدل قيمُها بما في الجدول.\n\nأتُتابع؟", "أعِد الضخّ")
      .then(ok=>{ if(ok) go(); });
  });
  if(ME.role === "teacher") src.appendChild(rb);
  c0.appendChild(src);
  const g0 = el("div","grid"); g0.style.padding = "14px 16px";
  D.info.forEach(f=>{
    const w = el("label","f");
    /* ⚠️ التسميةُ ووحدتُها يُترجَمان على حدة: «زمن الحصة (د)» لا مفتاحَ
       له، و«زمن الحصة» و«د» لهما. */
    w.appendChild(el("span",null, TR(f.l) + (f.u ? " (" + TR(f.u) + ")" : "")));
    if(ro) w.appendChild(el("div","ro", P["i_"+f.k] || "—"));
    else w.appendChild(fld("txt", P["i_"+f.k], v=>{ P["i_"+f.k]=v; save(); refresh(P); }));
    g0.appendChild(w);
  });
  c0.appendChild(g0); m.appendChild(c0);
  stratCard(m, L, P);
  /* ⛔ **بعد بيانات الحصة وبعد بطاقة الإستراتيجية**: الأمرُ يُبنى منهما —
     عنوانُ الدرس وصفحاتُه وزمنُه والإستراتيجيةُ والاتجاه. فلو سبقهما لنسخ
     المعلمُ أمراً فارغاً. (طلبُ المستشار ٣٠ سبتمبر ٢٠٢٦) */
  /* ═════════ مساحةُ «طريقة التحضير» — ثلاثُ طرقٍ يختار المعلمُ منها ═════════
     ⛔ كانت الطرقُ الثلاثُ متفرّقةً: القالبُ الورقيُّ رابطاً في بطاقة أدوات،
        والتحضيرُ الإلكترونيُّ خاناتٍ تبدأ فجأةً، ولوحةُ الذكاء بينهما — فلا
        يعلم المعلمُ أن له خياراً أصلاً. فصارت مساحةً واحدةً يختار منها، وما
        اختاره يُحفظ على جهازه فلا يُسأل في كل مرة.
        (طلبُ المستشار ١ أكتوبر ٢٠٢٦ — وهو ما اتُّفق عليه من قبل) */
  let way = prepWay();
  if(!ro){
    const wc = wayCard(way);
    m.appendChild(wc);
    /* ③ مساحةُ الذكاء الاصطناعي — صياغةُ الأمر ونسخُه، ثم لصقُ الجواب */
    if(way === "ai") importPanel(m, L, P);
  }
  prepTools(m);

  /* ⚠️ والنموذجُ الإلكترونيُّ يبقى ظاهراً في «الإلكتروني» و«الذكاء» — فالأخيرُ
     يملؤه، فلا بدَّ أن يراه المعلمُ ليراجعه. ويُخفى في «الورقي» وحدَه.
     وللمُطّلعِ (ro) يبقى ظاهراً دائماً: هو جاء ليقرأه. */
  if(!ro && way === "p"){
    const nt = el("div","card"), np = el("div","pad");
    np.appendChild(el("div","msg",
      "اخترتَ القالبَ الورقي — فخاناتُ التحضير الإلكتروني مطويّةٌ الآن. "
      + "اختر «التحضير الإلكتروني» أعلاه لتظهر."));
    nt.appendChild(np); m.appendChild(nt);
  } else D.sections.forEach(sec=>{
    const c = el("div","card"), hh = el("h3");
    hh.appendChild(el("span",null, sec.t)); hh.appendChild(el("small",null, sec.n));
    c.appendChild(hh);
    const pd = el("div","pad");
    sec.rows.forEach(r=>{
      const rw = el("div","row2"), lb = el("div","lab"), fl = el("div");
      const tt = el("div"); tt.textContent = TR(r.label); lb.appendChild(tt);
      if(r.ind){ const i = el("div"); i.style.cssText = "font-size:12.5px;color:var(--teal2);font-weight:400";
        i.textContent =TR(TR("يغذّي ") + TR(r.ind)); lb.appendChild(i); }
      if(r.hint && !ro){
        const hb = el("button","hb noprint","؟");
        const hd = el("div","hint", r.hint); hd.style.display = "none";
        hb.addEventListener("click", ()=>{ hd.style.display = hd.style.display === "none" ? "" : "none"; });
        lb.appendChild(hb); fl.appendChild(hd);
      }
      if(r.note){ const n = el("div");
        n.style.cssText = "color:var(--grey);font-size:14px;margin-bottom:4px";
        n.textContent = TR(r.note) + ":"; fl.appendChild(n); }
      fl.appendChild(pfield(r, P, ro));
      rw.appendChild(lb); rw.appendChild(fl); pd.appendChild(rw);
    });
    c.appendChild(pd); m.appendChild(c);
  });
  refresh(P);
}

function pfield(r, P, ro){
  const K = "f_" + r.k;
  const set = (k,v)=>{ P[k]=v; save(); refresh(P); };
  /* ⚠️ عنوانُ الحقل في عمودٍ مجاورٍ لا في <label for>, فيُحقن aria-label
     وإلا قرأ قارئُ الشاشة حقلاً بلا اسم. */
  const A = (e, extra)=>{ if(e && e.setAttribute)
    e.setAttribute("aria-label", r.label + (extra ? " — " + extra : "")); return e; };
  if(r.t === "line") return ro ? el("div","ro", P[K]||"—") : A(fld("txt", P[K], v=>set(K,v)));
  if(r.t === "area") return ro ? el("div","ro", P[K]||"—") : A(fld("area", P[K], v=>set(K,v)));
  if(r.t === "select") return ro ? el("div","ro", P[K]||"—") : A(fld("sel", P[K], v=>set(K,v), r.items, r.label));
  if(r.t === "lines"){
    const w = el("div");
    for(let i=1;i<=r.n;i++){
      const ln = el("div"); ln.style.cssText = "display:flex;gap:8px;align-items:center;margin:3px 0";
      ln.appendChild(el("b",null, arn(i) + "."));
      const kk = K + "_" + i;
      ln.appendChild(ro ? el("div","ro", P[kk]||"—") : A(fld("txt", P[kk], v=>set(kk,v)), arn(i)));
      w.appendChild(ln);
    }
    return w;
  }
  if(r.t === "ticks" || r.t === "ticks_note"){
    const w = el("div");
    if(ro){ const pk = r.items.filter((_,i)=>P[K+"#"+i]);
      w.appendChild(el("div","ro", pk.length ? pk.join("  ·  ") : "—")); }
    else{
      const tw = el("div","ticks");
      r.items.forEach((it,i)=>{
        const l = el("label","tk"), cb = el("input"); cb.type = "checkbox";
        cb.checked = !!P[K+"#"+i];
        cb.setAttribute("aria-label", r.label + " — " + it);
        cb.addEventListener("change", ()=>set(K+"#"+i, cb.checked));
        l.appendChild(cb); l.appendChild(el("span",null,it)); tw.appendChild(l);
      });
      w.appendChild(tw);
    }
    if(r.t === "ticks_note"){
      const n = el("div"); n.style.marginTop = "6px";
      n.appendChild(ro ? el("div","ro", P[K+"_note"]||"—") : A(fld("txt", P[K+"_note"], v=>set(K+"_note",v)), r.note||"كيف"));
      w.appendChild(n);
    }
    return w;
  }
  if(r.t === "time"){
    /* ⛔ مجموعتان لا سطرٌ واحد — مطابقاً للمطبوع حرفاً بحرف:
       لو صُفَّت خانتا التمايز مع صف المجموع قرأها القارئُ جامعةً فبلغ ٦١ والحصةُ ٤٥.
       فالأولى: التهيئة · التنفيذ · التقويم · الغلق · المجموع (وهو مجموعُ الأربع).
       والثانية تحتها: زمنا التمايز — وهما **داخل** التنفيذ لا يُضافان. */
    const w = el("div");
    const g1 = el("div","g5");
    D.tmain.forEach(k=>{
      const lb = D.tlabels[k], b = el("div");
      b.appendChild(el("label", k === "total" ? "auto" : null, lb));
      if(k === "total"){
        const d = el("div","ro sum"); d.id = "tsumcell";
        d.textContent = TR(arn(tsum(P).parts)); b.appendChild(d);
      } else {
        const K2 = "tk_" + k;
        /* ⛔ لا إعادةَ بناءٍ عند كل حرف: كانت تُفقد التركيزَ وتقفز الصفحةُ لأعلى.
           تُحدَّث خانةُ المرحلة في مكانها وحدها. */
        b.appendChild(ro ? el("div","ro", P[K2]||"—")
          : A(fld("txt", P[K2], v=>{ P[K2] = v; fillStageTimes(P);
              syncStageInputs(P); save(); refresh(P); }), lb));
      }
      g1.appendChild(b);
    });
    w.appendChild(g1);
    const hd = el("div","tdiff");
    hd.textContent =TR(TR(D.tdifft) + TR(" — داخلَه لا يُضافان إليه:"));
    w.appendChild(hd);
    const g2 = el("div","g2");
    D.tdiff.forEach(k=>{
      const lb = D.tlabels[k], K2 = "tk_" + k, b = el("div","care");
      b.appendChild(el("label",null,lb));
      b.appendChild(ro ? el("div","ro", P[K2]||"—")
        : A(fld("txt", P[K2], v=>set(K2,v)), lb));
      g2.appendChild(b);
    });
    w.appendChild(g2);
    if(!ro){
      const rb = el("button","b ghost sm","وزّع الزمن على المراحل");
      rb.style.cssText = "margin-top:9px";
      rb.title = "التهيئةُ والغلقُ كما في الخريطة، والتنفيذُ والتقويمُ يُقسمان على النشاطين";
      rb.addEventListener("click", ()=>{
        const mine = D.stages.filter(([k])=>(P["st_"+k+"_time"]||"").trim() && !P["st_"+k+"_time_auto"])
                             .map(([,n])=>n);
        const go2 = ()=>{ fillStageTimes(P, true); save(); shell(); };
        if(!mine.length){ go2(); return; }
        uiAsk("سيُكتب فوق الأزمنة التي كتبتَها بنفسك في: "
          + mine.join(" · ") + "\n\nأتُتابع؟", "وزّعها").then(ok=>{ if(ok) go2(); });
      });
      w.appendChild(rb);
    }
    const s2 = el("div"); s2.id = "tsum";
    s2.style.cssText = "display:flex;gap:10px;flex-wrap:wrap;margin-top:8px;font-size:14.5px";
    w.appendChild(s2);
    return w;
  }
  if(r.t === "stages"){
    const w = el("div"), hd = el("div","stg");
    ["المرحلة", D.lab_t, D.lab_l, "نمط العمل وتقويمه"].forEach(x=>{
      const d = el("div","stn",x); d.style.color = "var(--teal2)"; hd.appendChild(d); });
    w.appendChild(hd);
    D.stages.forEach(([k,name])=>{
      const st = el("div","stg"), c0 = el("div","stn",name);
      c0.appendChild(ro ? el("div","ro", (P["st_"+k+"_time"]||"—") + " د")
                        : (function(){
                            const e2 = A(fld("txt", P["st_"+k+"_time"], v=>{
                              P["st_"+k+"_time_auto"] = 0;   /* صار بيد المعلم */
                              set("st_"+k+"_time", v);
                            }, null, "الزمن"), name + " — الزمن");
                            e2.dataset.stt = k; return e2;
                          })());
      st.appendChild(c0);
      st.appendChild(ro ? el("div","ro", P["st_"+k+"_t"]||"—") : A(fld("area", P["st_"+k+"_t"], v=>set("st_"+k+"_t",v)), name + " — " + D.lab_t));
      st.appendChild(ro ? el("div","ro", P["st_"+k+"_l"]||"—") : A(fld("area", P["st_"+k+"_l"], v=>set("st_"+k+"_l",v)), name + " — " + D.lab_l));
      const md = el("div");
      D.modes.forEach((grp,gi)=>{
        if(ro){ const pk = grp.filter((_,i)=>P["st_"+k+"_m"+gi+"#"+i]);
          md.appendChild(el("div",null, pk.join(" · ") || "—")); }
        else{
          const tw = el("div","ticks"); tw.style.gap = "2px 10px";
          grp.forEach((it,i)=>{
            const l = el("label","tk"), cb = el("input"); cb.type = "checkbox";
            cb.checked = !!P["st_"+k+"_m"+gi+"#"+i];
            cb.style.cssText = "width:15px;height:15px";
            cb.addEventListener("change", ()=>set("st_"+k+"_m"+gi+"#"+i, cb.checked));
            l.style.fontSize = "13.5px";
            l.appendChild(cb); l.appendChild(el("span",null,it)); tw.appendChild(l);
          });
          md.appendChild(tw);
        }
      });
      st.appendChild(md); w.appendChild(st);
    });
    return w;
  }
  return el("div");
}

function n2(x){
  const m = String(x||"").replace(/[٠-٩]/g, d=>"٠١٢٣٤٥٦٧٨٩".indexOf(d));
  const v = parseFloat(m); return isNaN(v) ? 0 : v;
}
/* ⚠️ خريطةُ الزمن أربعُ خاناتٍ ومراحلُ الحصة أربع، لكنّ «التنفيذ» يتوزّع على
   النشاطين و«التقويم» بينهما. فالاقتراحُ: التهيئةُ والغلقُ كما هما، والتنفيذُ
   والتقويمُ يُقسمان على النشاطين — ويبقى للمعلم تعديلُهما. */
function stageTimes(P){
  const ex = n2(P.tk_exec), ev = n2(P.tk_eval), body = ex + ev;
  return {warm: n2(P.tk_warm), close: n2(P.tk_close),
          act1: Math.ceil(body/2), act2: Math.floor(body/2)};
}
/* ⛔ الزمنُ يتبع الخريطة ما دام لم يُلمَس بيد: يُعلَّم المولَّدُ بـ`_auto`،
   فإن عدّله المعلمُ سقطت العلامةُ وصار رأيُه هو المعتمد. */
function fillStageTimes(P, force){
  const t = stageTimes(P); let n = 0;
  D.stages.forEach(([k])=>{
    const key = "st_" + k + "_time", flag = key + "_auto";
    if(t[k] == null) return;
    const mine = (P[key]||"").trim() && !P[flag];      /* كتبه المعلمُ بنفسه */
    if(!force && mine) return;
    const v = t[k] > 0 ? arn(t[k]) : "";
    if(P[key] !== v){ P[key] = v; n++; }
    P[flag] = 1;
  });
  return n;
}
/* ⛔ وحُذفت `stagesSum(P)`: مجموعُ أزمنة المراحل يُحسب في موضعه من خريطة
   الزمن، وهذه نسخةٌ ثانيةٌ لا يناديها شيء — ونسختان تفترقان. (١ أكتوبر) */
function tsum(P){
  /* ⚠️ بالمفتاح لا بالموضع: إعادةُ ترتيب الخانات لا تُزحزح قيمةً واحدة */
  const parts = D.tsum_keys.reduce((a,k)=>a + n2(P["tk_"+k]), 0);
  const total = n2(P["i_dur"]);                 /* زمنُ الحصة من بيانات الحصة */
  const care = n2(P["tk_care"]), gift = n2(P["tk_gift"]);
  const exec = n2(P["tk_exec"]);
  const stg = D.stages.reduce((a,[k])=>a + n2(P["st_"+k+"_time"]), 0);
  return {parts, total, care, gift, exec, stg,
          ok: total > 0 && parts === total,
          stgok: stg === 0 || stg === parts,
          inside: (care + gift) <= (exec || parts)};
}
function missing(P){
  const out = [];
  D.info.forEach(f=>{ if(["teacher","subject","klass","topic","dur"].includes(f.k) && !(P["i_"+f.k]||"").trim()) out.push(f.l); });
  D.sections.forEach(sec=>sec.rows.forEach(r=>{
    if(!r.req) return;
    const K = "f_" + r.k;
    if(["line","area","select"].includes(r.t)){ if(!(P[K]||"").trim()) out.push(r.label); }
    else if(r.t === "lines"){ if(!(P[K+"_1"]||"").trim()) out.push(r.label); }
    else if(r.t === "ticks" || r.t === "ticks_note"){
      if(!r.items.some((_,i)=>P[K+"#"+i])) out.push(r.label);
      if(r.t === "ticks_note" && !(P[K+"_note"]||"").trim()) out.push(r.label + " (كيف؟)");
    }
    else if(r.t === "time"){
      const t = tsum(P);
      if(!t.total) out.push("خريطة الزمن — اكتب «زمن الحصة» في بيانات الحصة أولاً");
      else if(!t.ok) out.push("خريطة الزمن — المجموع " + arn(t.parts) + " والمطلوب " + arn(t.total)
                              + " (الفرق " + arn(Math.abs(t.parts - t.total)) + " د)");
      if(!t.inside) out.push("زمنا الأولى بالرعاية والموهوبين أكبرُ من زمن التنفيذ — وهما داخله لا خارجه");
      if(t.parts && !t.stgok) out.push("أزمنةُ المراحل مجموعها " + arn(t.stg)
        + " وخريطةُ الزمن " + arn(t.parts) + " — اضغط «وزّع الزمن على المراحل»");
    }
    else if(r.t === "stages"){ D.stages.forEach(([k,n])=>{
      if(!(P["st_"+k+"_t"]||"").trim() || !(P["st_"+k+"_l"]||"").trim()) out.push("مرحلة " + n); }); }
  }));
  return [...new Set(out)];
}
function refresh(P){
  const ts0 = tsum(P), cell = document.getElementById("tsumcell");
  if(cell){ cell.textContent = TR(arn(ts0.parts));
    cell.className = "ro sum " + (ts0.total ? (ts0.ok ? "good" : "bad") : ""); }
  const s = document.getElementById("tsum");
  if(s){
    const t = tsum(P); s.innerHTML = "";
    const mk = (txt,bg,fg)=>{ const e = el("span",null,txt);
      e.style.cssText = "border-radius:6px;padding:3px 9px;background:" + bg + ";color:" + (fg||"inherit"); return e; };
    s.appendChild(mk("مجموع المراحل: " + arn(t.parts), "var(--head)"));
    s.appendChild(mk("زمن الحصة: " + (t.total ? arn(t.total) : "—"), "var(--head)"));
    s.appendChild(mk(t.ok ? "✓ متطابق" : "✗ غير متطابق",
      t.ok ? "var(--okbg)" : "var(--badbg)", t.ok ? "var(--ok)" : "var(--bad)"));
  }
  const b = document.getElementById("issue");
  if(b){ const mm = missing(P);
    b.textContent = TR(mm.length ? ("إصدار التحضير — ينقصه " + arn(mm.length)) : "إصدار التحضير ✓"); }
}
/* ⛔ **الوعدُ كان أوسعَ من الحارس.** تقول المنصةُ في ثلاثة مواضع: «إصدارُ
   التحضير لا يعمل قبل اكتمال كل خانةٍ يقابلها مؤشر» — و`missing()` يفحص
   `req` وحدَه. وثلاثَ عشرةَ خانةً تحمل مؤشراً ولا تحمل `req`، فيُصدَّر
   التحضيرُ و**أحدَ عشرَ مؤشراً (٤٤ درجةً = ٢٢٪) بلا شاهدٍ مخطَّطٍ له**،
   والمعلمُ يرى «إصدار التحضير ✓» فيطمئنّ. (أمسكه وكيلُ الإشراف التربوي)
   ⚠️ **ولا تُجعل كلُّها إلزاميةً**: «توظيفُ التقنية» في حصةِ تربيةٍ بدنيةٍ
      في الملعب شاهدٌ كاذبٌ لو أُلزم به. فالحارسُ يبقى على الإلزاميّ، ويُقال
      للمعلم **بالعدد والدرجة** ما يتركه — ويُصحَّح الوعدُ ليطابق الفعل. */
function weakFields(P){
  const out = [];
  (D.sections || []).forEach(sec=>(sec.rows || []).forEach(r=>{
    if(r.req || !r.ind) return;
    const K = "f_" + r.k;
    let empty = false;
    if(["line", "area", "select"].indexOf(r.t) >= 0) empty = !String(P[K] || "").trim();
    else if(r.t === "lines") empty = !String(P[K + "_1"] || "").trim();
    else if(r.t === "ticks" || r.t === "ticks_note")
      empty = !(r.items || []).some((_, i)=>P[K + "#" + i]);
    if(empty) out.push({label: r.label, ind: r.ind});
  }));
  return out;
}
/* عددُ المؤشرات التي تبقى بلا شاهدٍ مخطَّط — ودرجتُها من المئتين */
function weakMarks(w){
  const set = {};
  w.forEach(x=>String(x.ind || "").split("·").forEach(i=>{ const k = i.trim(); if(k) set[k] = 1; }));
  const n = Object.keys(set).length;
  return {inds: n, marks: n * 4, list: Object.keys(set)};
}
function issue(L,P){
  const out = document.getElementById("issueOut"); out.innerHTML = "";
  const mm = missing(P);
  if(mm.length){
    const box = el("div","msg bad");
    box.appendChild(el("b",null,"لا يُصدَّر التحضير قبل اكتمال ما يقابله مؤشرٌ في الاستمارة — الناقص:"));
    const ul = el("ul"); mm.forEach(x=>ul.appendChild(el("li",null,x))); box.appendChild(ul);
    out.appendChild(box); window.scrollTo({top:0,behavior:"smooth"}); return;
  }
  P.__issued = new Date().toISOString().slice(0,16).replace("T"," ");
  logAct("إصدار التحضير", lessonTitle(L), L); syncFlush();
  save(); refresh(P);
  const box = el("div","msg ok");
  box.appendChild(el("b",null,"صدر التحضير. "));
  box.appendChild(el("span",null,"ظهر الآن للزائرين والمقيّمين في مرحلة أداء الحصة."));
  out.appendChild(box);
  /* ⚠️ ويُقال له ما تركه — بالعدد والدرجة لا بتحذيرٍ مبهم */
  const wk = weakFields(P);
  if(wk.length){
    const m2 = weakMarks(wk), w2 = el("div","msg warn");
    w2.appendChild(el("b",null,
      "صدر — ومعه " + arn(wk.length) + " خانةً ذاتَ مؤشرٍ تركتَها فارغة: "
      + arn(m2.inds) + " مؤشراً (" + arn(m2.marks) + " درجةً من ٢٠٠) يبحث الزائرُ عن شاهدها ولا يجده في تحضيرك."));
    w2.appendChild(el("span",null,
      wk.slice(0, 8).map(x=>TR(x.label) + " (" + TR(x.ind) + ")").join(TR(" · "))
      + (wk.length > 8 ? " …" : "")
      + " — واترك ما لا ينطبق على حصتك فعلاً، فالشاهدُ الكاذبُ أسوأُ من الفراغ."));
    out.appendChild(w2);
  }
}

/* ═════════ المرحلة ١: جدول الحصص الموحَّدة للتقويم الخارجي ═════════
   ⛔ لا يُذكر اسمُ البرنامج السابق في أي نصٍّ يراه المستخدم: هو برنامجٌ آخر،
      وهذه منصةُ الحصص الموحَّدة وحدها. (وبنيةُ الجدول مستمَدّةٌ من ملفٍ سابق.)
   · صفوفُ الجدول: (الأسبوع × اليوم × تخصص الزائر)، وأعمدتُه الحصصُ بأوقاتها،
     وتحت كل حصةٍ خمسةُ حقول. وبنيةُ الأعمدة تأتي من D.bands لا من افتراض.
   · والدورانُ مقروءٌ من الورقة الأولى لا محسوباً — وله وجهان:
     «من يزورنا» للمدرسة، و«أين أزور» للمشرف.
   · ولا أربعاء، والأسبوعُ الرابعُ ثلاثةُ أيامٍ لا أربعة — كما في الأصل. */
let GS = null;
function gctx(){
  if(!GS){
    try{ GS = JSON.parse(localStorage.getItem(KEY+"_ctx")||"null"); }catch(e){}
    GS = GS || {};
  }
  /* ── النطاقُ يُورَث من الدخول: المدرسةُ للمدير والوكيل، والتخصصُ لمن يتنقّل ── */
  if(!GS.sector) GS.sector = (ME && ME.sector) || D.sectors[0];
  const cl = D.complexes[GS.sector] || D.complexlist;
  if(!GS.complex || cl.indexOf(GS.complex) < 0) GS.complex = (ME && ME.complex &&
      cl.indexOf(ME.complex) >= 0) ? ME.complex : cl[0];
  if(!Array.isArray(GS.stages)) GS.stages = [];
  if(GS.spec == null) GS.spec = (ME && ME.spec) || "";
  /* ⛔ المديرُ والوكيلُ مربوطان بمدرستهما: القطاعُ والمجمعُ والمدرسةُ تُفرض ولا
     تُترك للاختيار، فلا يريان جدولَ مدرسةٍ ليست لهما. (٢٩ سبتمبر ٢٠٢٦) */
  if(typeof isSchoolBound === "function" && isSchoolBound() && ME.school){
    GS.sector = ME.sector || GS.sector;
    GS.complex = ME.complex || GS.complex;
    GS.stages = [ME.school];
  }
  /* ⛔ ومديرُ المجمع مربوطٌ بقطاعه ومجمعه — ومدارسُ المجمع كلُّها له */
  else if(typeof isCxMgr === "function" && isCxMgr() && ME.complex){
    GS.sector = ME.sector || GS.sector;
    GS.complex = ME.complex;
  }
  /* والمشرفُ يفتح على خطته لا على جدولٍ لا يملك فيه خانة */
  if(!GS.tab && ME && ME.role === "supervisor") GS.tab = "visits";
  if(!GS.tab) GS.tab = (ME && ME.role === "peer") ? "visits" : "fill";
  /* تبويبٌ محفوظٌ من دورٍ آخر لا يُعرض لهذا الدور */
  if(ME && ME.role === "teacher" && (GS.tab === "sup" || GS.tab === "visits")) GS.tab = "fill";
  if(ME && typeof isSchoolBound === "function" && isSchoolBound()
     && (GS.tab === "sup" || GS.tab === "visits")) GS.tab = "fill";
  return GS;
}
function setctx(k,v){ gctx()[k]=v; localStorage.setItem(KEY+"_ctx", JSON.stringify(GS)); }
function bandsOf(cx){ return D.bands[cx] || []; }
function schoolsOf(cx){                              /* أسماءُ المدارس = نطاقاتُ المراحل */
  const out = [];
  bandsOf(cx).forEach(b=>{ if(out.indexOf(b.stage) < 0) out.push(b.stage); });
  return out;
}
function groupOf(cx, wk, day){ return ((D.rot[cx]||{})[wk]||{})[day] || ""; }
/* ⚠️ في العالمي يزور فريقُ الهوية الوطنية مجمعاً بعينه في يومٍ بعينه، فقد يجتمع
   مع الفريق الدائر في اليوم نفسه — فتُعاد مجموعتان لا واحدة. */
function groupsOf(c, wk, day){
  const out = [];
  const g = groupOf(c.complex, wk, day);
  if(g) out.push(g);
  if(c.sector === "عالمي" && D.natdays && D.natdays[day] === c.complex
     && out.indexOf(D.natgroup) < 0) out.push(D.natgroup);
  return out;
}
function isNatSpec(sp){ return (D.natspecs||[]).indexOf(sp) >= 0; }
function calOf(wk){ return D.cal.find(c=>c.w === wk) || null; }
function todayISO(){ const d = new Date();
  return d.getFullYear() + "-" + String(d.getMonth()+1).padStart(2,"0") + "-" + String(d.getDate()).padStart(2,"0"); }
/* الأسبوعُ الجاري: الذي يقع اليومُ بين طرفيه — وإلا فالقادمُ الأقرب */
function currentWeek(){
  const t = todayISO();
  const inIt = D.cal.find(c=>t >= c.from && t <= c.to);
  if(inIt) return inIt.w;
  const next = D.cal.find(c=>t < c.from);
  return next ? next.w : null;
}
function dayDate(wk, day){ const c = calOf(wk); return c ? (c.days[day]||{}) : {}; }
function gkey(cx, band, wk, day, spec){
  return [gctx().sector, cx, band.stage, band.per, wk, day, spec].join("|");
}
function findLesson(gk){ return DB.sched.find(x=>x.gk === gk); }
/* ⛔ خانةُ المعلم تُعرف بالرقم الوظيفي لا بالاسم: الأسماءُ تُكتب بصيغٍ شتّى،
   فمن كُتب اسمُه في الخانة بصيغةٍ تخالف ما دخل به **لم يستطع تعديلَ خانته هو**،
   ولم تظهر حصتُه في «جدولي» ولا في «تقريري». والاسمُ يبقى بديلاً لخانةٍ لا
   رقمَ فيها — ولا يُطابَق بالاسم على خانةٍ رقمُها لغيره. (٣٠ سبتمبر ٢٠٢٦)
   وهي القاعدةُ نفسُها في isMyVisit للزيارات المسنَدة. */
/* ═════════ بوّابةُ الدخول: تحقُّقٌ من الرقم والاسم ═════════
   ⛔ كانت تقبل كلَّ شيء: حرفاً واحداً اسماً، ورقماً من منزلة، وحروفاً بدل
      أرقام، **ورقماً فارغاً**. فدخل الناسُ بأسماءٍ لا تُطابق كشفاً، وظهر
      الشخصُ مرّتين في التقارير. (بلاغُ المشرفة العامة ٣٠ سبتمبر ٢٠٢٦)

   ⚠️ وطولُ الرقم **يُشتقُّ من الكشف لا يُثبَّت**: قيل إنها خمسُ منازل، وفي
      كشف ابن خلدون ٣٨ رقماً من أربع من أصل ٤٦٠ — فقفلُها على خمسٍ يحرم
      أصحابَها. وأرقامُ قادةَ عشرُ منازل. فلكلِّ منصةٍ أطوالُ كشفها. */
function empLens(){
  const R = D.roster || {}, ks = Object.keys(R);
  if(!ks.length) return null;
  return ks.map(k=>k.length).filter((v,i,a)=>a.indexOf(v) === i).sort();
}
function empError(raw, role){
  const k = latnum(raw);
  if(!k) return "اكتب رقمك الوظيفي — به تُعرف حصصك.";
  /* ⛔ المشرفُ يُعرف من **سجلّ الإشراف** لا من كشف المعلمين: به يُقرأ تخصصُه
     ومجمعاتُه ومراحلُه، فلا يختارها بيده. (٣٠ سبتمبر ٢٠٢٦) */
  if(role === "supervisor")
    return supByEmp(k) ? "" : "هذا الرقمُ ليس في سجلّ الإشراف التربوي — راجع "
         + (D.adminref || "إدارة التخطيط والاعتماد المدرسي") + ".";
  /* ⛔ **كشفُ المنسوبين كشفُ معلمين** — ٤٦٠ رقماً تخصصاتُها موادٌّ دراسية، وليس
     فيه مديرٌ ولا وكيلٌ ولا مديرُ مجمعٍ ولا فريقُ متابعة. وكان التحقّقُ يطالب
     كلَّ دورٍ بالوجود فيه، فكانت القياداتُ الأربعُ **تُحجب عن الدخول** متى
     حُمِّل الكشفُ من المخزن — ونجت التجربةُ المحليةُ لأن الكشفَ كان فارغاً
     فيها، فالفارغُ يُسقط التحقّقَ كلَّه. فصار لكل دورٍ مَرجعُه:
       · المشرفُ ← سجلُّ الإشراف التربوي (أعلاه).
       · المعلمُ والزائرُ ← كشفُ المنسوبين، فهما منه.
       · القياداتُ ← لا سجلَّ لها، فتُفحص القاعدةُ ولا يُطالَب بعضويةٍ لا تُوجد.
     (قِيس بـ`empprobe.py` ١ أكتوبر ٢٠٢٦) */
  const ROSTERED = ["teacher", "peer"];
  const R = D.roster || {}, lens = empLens();
  if(role && ROSTERED.indexOf(role) < 0){
    if(D.emplen && k.length !== D.emplen)
      return "الرقمُ الوظيفي " + arn(D.emplen) + " منازل — وهذا " + arn(k.length) + ".";
    return "";
  }
  /* ⛔ **الكشفُ أولاً ثم الطول**: قاعدةُ المدرسة خمسُ منازل، وفي كشفها ٣٨
     رقماً من أربعٍ (١١٤١–٩٧٣٩) لأصحابٍ قائمين. فلو قُدّم الطولُ على الكشف
     حُرم هؤلاء من الدخول بأرقامهم الحقيقية. فمن كان في الكشف دخل بطوله
     كما هو، والقاعدةُ تُطبَّق على من ليس فيه. (٣٠ سبتمبر ٢٠٢٦) */
  if(lens && Object.prototype.hasOwnProperty.call(R, k)) return "";
  if(lens && D.emplen && k.length !== D.emplen)
    return "الرقمُ الوظيفي " + arn(D.emplen) + " منازل — وهذا " + arn(k.length) + ".";
  if(lens) return "هذا الرقمُ ليس في كشف المنسوبين — راجع "
         + (D.adminref || "إدارة التخطيط والاعتماد المدرسي") + ".";
  return "";
}
/* ⛔ والاسمُ اسمُ شخصٍ وعائلة: كان يُقبل حرفٌ واحد. */
function nameError(raw){
  const n = String(raw || "").trim().replace(/\s+/g, " ");
  if(!n) return "اكتب اسمك — به تُعرف حصصك.";
  if(/[0-9٠-٩]/.test(n)) return "الاسمُ حروفٌ لا أرقام.";
  if(n.split(" ").filter(x=>x.length >= 2).length < 2)
    return "اكتب الاسمَ الأولَ واسمَ العائلة على الأقل.";
  if(n.length < 6) return "الاسمُ قصيرٌ — اكتبه كما هو مسجَّل.";
  return "";
}

/* ⛔ **مسافةٌ واحدةٌ كانت تقتل صفحةَ المعلم صامتةً.** بعد نزع الكشف من
   الصفحة (١ أكتوبر ٢٠٢٦) صار الاسمُ يُكتب **مرتين**: في خانة الجدول وعند
   الدخول. وكان التطابقُ حرفياً تامّاً — فـ«معلم التجربة » (بمسافةٍ لاحقة)
   لا تساوي «معلمُ التجربة»، فيصير `isMine` كاذباً **فتُقفل الصفحةُ كلُّها**:
   تختفي لوحةُ التحضير بالذكاء الاصطناعي، وتتعطّل الخاناتُ الأربعُ والسبعون،
   **ولا تُكتب كلمةٌ تقول لِمَ**. وهذا ما شكا منه المستشارُ: «لم أعد أرى
   التحضير بالذكاء الاصطناعي» و«أتِح التحضيرَ كتابياً للمعلم» — عطلٌ واحد.
   ⚠️ والتسويةُ **للمقارنة وحدَها**: المخزونُ يبقى كما كتبه صاحبُه. */
function arname(x){
  return String(x || "")
    .replace(/[ً-ْٰـ]/g, "")   /* تشكيلٌ وتطويل */
    .replace(/[آأإ]/g, "ا")     /* آ إ أ ← ا */
    .replace(/ى/g, "ي")                   /* ى ← ي */
    .replace(/ة/g, "ه")                   /* ة ← ه */
    .replace(/\s+/g, " ")
    .trim();
}
function isMine(L){
  const e = (ME.emp||"").trim(), n = arname(ME.name), le = (L.teacherNo||"").trim();
  if(e && le) return le === e;
  if(!n) return false;
  if(le && e && le !== e) return false;
  return arname(L.teacher) === n;
}
/* لِمَ لا تُعدُّ هذه الحصةُ له — بالنصّ، ليُقرأ على الشاشة لا ليُخمَّن */
function notMineWhy(L){
  if(!ME || ME.role !== "teacher") return "";
  if(isMine(L)) return "";
  const e = (ME.emp||"").trim(), le = (L.teacherNo||"").trim();
  if(e && le && le !== e)
    return "هذه الحصةُ مسجَّلةٌ بالرقم الوظيفي " + arn(le) + " وأنت داخلٌ بالرقم " + arn(e) + ".";
  const lt = String(L.teacher||"").trim();
  if(!lt) return "خانةُ المعلم في هذه الحصة فارغة.";
  return "هذه الحصةُ مسجَّلةٌ باسم «" + lt + "» وأنت داخلٌ باسم «" + (ME.name||"") + "».";
}
/* المقيّمُ يكتب في الجدول كلِّه · والمعلمُ في مدارسه التي اختارها وفي خانته وحدها */
function canEdit(c, band, L){
  if(L && L.approved) return false;          /* ⛔ معتمدةٌ فمقفولة — حتى للمقيّم */
  /* ⛔ **الجدولُ لا يُعدَّل إلا من المعلم القائم بالحصة** (قرارُ الاجتماع
     ٣٠ سبتمبر ٢٠٢٦): رآه المستشارُ محرَّراً في شاشتَي المشرف والمدير.
     ويبقى للمستشار وحدَه طريقُ إصلاحٍ — فهو مالكُ المنظومة ولا سواه. */
  if(isAdmin()) return true;
  if(ME.role !== "teacher") return false;
  if(c.stages.length && c.stages.indexOf(band.stage) < 0) return false;
  return !L || !(L.teacher||"").trim() || isMine(L);
}

function ph1(m){
  const c = gctx(), T = ME.role === "teacher";
  const top = el("div","card");
  const th = el("h3");
  th.appendChild(el("span",null,"جدول الحصص الموحَّدة للتقويم الخارجي"));
    /* ⚠️ وصفُ البنية يُقرأ من البيانات: مدرسةٌ واحدةٌ لا تشبه مجمعاً بمدارس. */
  th.appendChild(el("small",null, D.lab_gridsub ||
    "البنيةُ نفسها: الأسبوع واليوم وتخصص الزائر صفوفاً، ومدارسُ المجمع وحصصُها أعمدة"));
  top.appendChild(th);
  const tp = el("div","pad");
  const gr = el("div","grid");
  const lab = (t)=>{ const w = el("label","f"); w.appendChild(el("span",null,t)); return w; };
  const ws = lab("نوع التعليم");
  ws.appendChild(fld("sel", c.sector, v=>{
    setctx("sector", v);
    const l = D.complexes[v] || [];
    if(l.indexOf(c.complex) < 0) setctx("complex", l[0] || "");
    setctx("stages", []); shell();
  }, D.sectors));
  gr.appendChild(ws);
  const wc = lab("المجمع التعليمي");
  wc.appendChild(fld("sel", c.complex, v=>{ setctx("complex", v); setctx("stages", []); shell(); },
                     D.complexes[c.sector] || D.complexlist));
  gr.appendChild(wc);
  /* ⛔ التخصصُ مرشِّحٌ لكل من يتنقّل — لا للمعلم وحده. كان المشرفُ يرى المجمعَ
     كلَّه ويبحث بيده: «أليس من المفترض أن يوجد زر خاص باختيار تخصص المشرف
     التربوي الزائر لتظهر حصصه فقط». (٢٩ سبتمبر ٢٠٢٦) */
  if(T || isRoving()){
    const ws = lab(T ? "تخصصك" : "التخصص الذي تزوره");
    ws.appendChild(fld("sel", c.spec, v=>{ setctx("spec", v); shell(); },
                       T ? D.specs : ["كل التخصصات"].concat(D.specs)));
    gr.appendChild(ws);
  }
  /* ⛔ ومرشِّحُ اليوم: «وكذلك زر لليوم الذي يزور فيه لتظهر له حصص ذلك اليوم» */
  if(!T){
    const wd = lab("اليوم");
    wd.appendChild(fld("sel", c.vday || "كل الأيام",
                       v=>{ setctx("vday", v === "كل الأيام" ? "" : v); shell(); },
                       ["كل الأيام"].concat(D.days)));
    gr.appendChild(wd);
  }
  tp.appendChild(gr);
  /* ⛔ زيارةُ اليوم بضغطةٍ: يضبط الأسبوعَ واليومَ والمجمعَ الذي يزوره فريقُه */
  if(isSupervisor()){
    const qb = el("div","bar");
    const t0 = el("button","b sm","زيارتي اليوم");
    t0.title = "يضبط الأسبوعَ واليومَ والمجمعَ من تاريخ اليوم";
    t0.addEventListener("click", ()=>{ jumpToToday(); shell(); });
    qb.appendChild(t0);
    const aw = el("button","b ghost sm","كلُّ الأسبوع");
    aw.addEventListener("click", ()=>{ setctx("vday",""); shell(); });
    qb.appendChild(aw);
    const hint = el("small",null, todayHint());
    hint.style.cssText = "margin-inline-start:10px;color:var(--grey)";
    qb.appendChild(hint);
    tp.appendChild(qb);
  }

  /* ⚠️ المعلمُ قد يكون منتدباً، فيختار أكثر من مرحلةٍ يدرّس فيها */
  const sw = el("div","stpick");
  /* ⛔ المديرُ والوكيلُ لا يختاران مدرسةً: مدرستُهما واحدةٌ ثُبِّتت عند الدخول،
     فيُعرض اسمُها ولا يُعرض اختيار. (٢٩ سبتمبر ٢٠٢٦) */
  const bound = isSchoolBound() && ME.school;
  if(bound){
    sw.appendChild(el("b",null,"مدرستك:"));
    const tag = el("div","ticks");
    tag.appendChild(el("span","tag ok", ME.school + " · مجمع " + ME.complex));
    sw.appendChild(tag);
    sw.appendChild(el("small",null,
      "أعمدةُ مدرستك وحدها مفتوحةٌ لك — ولتغييرها اخرج وادخل بمدرسةٍ أخرى."));
  }
  if(!bound) sw.appendChild(el("b",null, T ? "مراحلُ التدريس — اختر واحدةً أو أكثر:"
                                : "ترشيحُ الأعمدة بالمدرسة (اختياري):"));
  const sl = el("div","ticks");
  if(!bound) schoolsOf(c.complex).forEach(st=>{
    const l = el("label","tk"), cb = el("input"); cb.type = "checkbox";
    cb.checked = c.stages.indexOf(st) >= 0;
    cb.addEventListener("change", ()=>{
      const a = c.stages.slice(), i = a.indexOf(st);
      if(cb.checked){ if(i < 0) a.push(st); } else if(i >= 0) a.splice(i,1);
      setctx("stages", a); shell();
    });
    l.appendChild(cb); l.appendChild(el("span",null,st)); sl.appendChild(l);
  });
  if(!bound) sw.appendChild(sl);
  if(T && !bound) sw.appendChild(el("small",null, c.stages.length
    ? "الأعمدةُ المفتوحةُ للإدخال: " + c.stages.join(" · ") + " — وسواها للقراءة."
    : "لا مرحلةَ مختارةٌ بعد، فكلُّ الأعمدة مفتوحةٌ للإدخال."));
  tp.appendChild(sw);

  const bar = el("div","bar");
  const tab = (k, t)=>{
    const b = el("button","b " + (c.tab === k ? "" : "ghost"), t);
    b.addEventListener("click", ()=>{ setctx("tab", k); shell(); });
    bar.appendChild(b);
  };
  /* ⛔ لا يُعرض زرٌّ لمن لا يملك فعلَه: الزائرُ لا يعدّل خانةً فلا معنى لتراجعه */
  if(ME.role !== "peer"){
    const ub = el("button","b ghost", UNDO.length ? "تراجع (" + arn(UNDO.length) + ")" : "تراجع");
    ub.disabled = !UNDO.length;
    if(UNDO.length) ub.title = "آخر تغيير: " + UNDO[UNDO.length-1].label;
    ub.addEventListener("click", undo);
    bar.appendChild(ub);
  }
  /* ═════════ أزرارُ كلِّ دورٍ وحدَه ═════════
     ⛔ «ما لا يخصه قم بحذفه واستبداله بما يخصه فقط» (٢٩ سبتمبر ٢٠٢٦):
        · المديرُ والوكيلُ لا يتنقّلان بين المجمعات، فلا «خطة زياراتي» ولا
          «أين أزور — جدول المشرفين»؛ ولهما بدلاً منهما «جدول مدرستي».
        · الوكيلُ وحدَه يُسنِد المعلمين الزائرين — فله «إسناد الزائرين».
        · الزائرُ لا يُعدّل خانةً، فلا تراجعَ ولا سلّةَ ولا جدولَ تعبئة. */
  const R = ME.role;
  tab("fill", R === "teacher" ? "جدولي"
            : (R === "peer" ? "جدول المجمع (للاطّلاع)"
            : (isSchoolBound() ? "جدول مدرستي" : "جدول التعبئة")));
  if(R !== "peer"){
    const n = trashList().length;
    if(n) tab("trash", "سلّة المحذوفات (" + arn(n) + ")");
  }
  if(isAdmin()) tab("log", "سجلّ العمليات");        /* ⛔ سجلُّ من فعل ماذا — للمستشار وحده */
  if(isDeputy()) tab("assign", "إسناد الزائرين");
  if(isRoving()) tab("visits", R === "peer" ? "زياراتي المسنَدة" : "خطة زياراتي");
  tab("school", R === "teacher" ? "من يزورنا"
              : (isSchoolBound() ? "من يزور مدرستنا" : "جدول المجمع"));
  /* جدولُ دوران المشرفين لا يعني إلا من يدور فيه */
  if(isSupervisor() || isAdmin()) tab("sup", "أين أزور — جدول المشرفين");
  const pr = el("button","b ghost","طباعة"); pr.addEventListener("click", ()=>window.print());
  bar.appendChild(pr);
  if(isAdmin()){        /* ⛔ النسخةُ الاحتياطيةُ تُنزِّل بياناتِ المنظومة كلِّها */
    const bk = el("button","b ghost","نسخة احتياطية"); bk.addEventListener("click", backup); bar.appendChild(bk);
  }
  tp.appendChild(bar);
  top.appendChild(tp); m.appendChild(top);

  /* مرشِّحاتٌ تختصر ٤٨ صفاً إلى ما يعنيك */
  if(c.tab === "fill"){
    const fb = el("div","filt");
    /* ⛔ **كلُّ حرفٍ كان يُعيد بناءَ الصفحة** (redrawGrid ← shell)، فيُهدم
       الصندوقُ الذي تكتب فيه ويضيع المؤشّر، فيضطرُّ المستخدمُ للنقر من جديد
       مع كل حرف. (بلاغُ المستشار ٣٠ سبتمبر ٢٠٢٦ بصورة.)
       فصار: تأخيرٌ قصيرٌ يجمع الحروف، ثم إعادةُ بناءٍ واحدة، **ويُستعاد
       التركيزُ وموضعُ المؤشّر** بعدها — وهذا هو الشاهدُ لا التأخيرُ وحدَه. */
    const q = fld("txt", c.q||"", v=>{
      setctx("q", v);
      clearTimeout(window.__qT);
      window.__qT = setTimeout(()=>{ window.__refocus = "q"; redrawGrid(); }, 260);
    }, null, "ابحث باسم معلمٍ أو فصل");
    q.dataset.refocus = "q";
    q.setAttribute("aria-label", "بحثٌ في الجدول");
    fb.appendChild(q);
    /* ⛔ القيمةُ الفارغةُ ليست خياراً في القائمة، فيعرض المتصفحُ «— اختر —»
       ويظنُّ القارئُ أن عليه اختياراً. والفارغُ معناه «كل الأسابيع» فيُسمَّ به. */
    const wk = fld("sel", c.onlyw || "كل الأسابيع",
                   v=>{ setctx("onlyw", v === "كل الأسابيع" ? "" : v); shell(); },
                   ["كل الأسابيع"].concat(D.weeks));
    wk.setAttribute("aria-label", "ترشيحٌ بالأسبوع"); fb.appendChild(wk);
    const only = el("label","tk");
    const cb = el("input"); cb.type="checkbox"; cb.checked = !!c.onlyfull;
    cb.addEventListener("change", ()=>{ setctx("onlyfull", cb.checked); shell(); });
    only.appendChild(cb); only.appendChild(el("span",null,"المعبّأ فقط")); fb.appendChild(only);
    const now = el("button","b ghost sm","اذهب إلى الأسبوع الجاري");
    now.addEventListener("click", ()=>{ setctx("onlyw", currentWeek() || ""); shell(); });
    fb.appendChild(now);
    tp.appendChild(fb);
  }
  /* ⛔ العددُ حيث يعمل: الوكيلُ لا لوحةَ منظومةٍ له، فلو لم يُعرض هنا لم يعرف
     من لم يُدخِل إلا أن يمسح الجدولَ بعينه — وهذا لا يُطمئن على كشفٍ كامل.
     ⛔ **ومديرُ المجمع كان محجوباً عنها** مع أن `pendingEntry` تحسب نطاقَه
        بعينه، وهو من يتابع المجمعَ كلَّه. وكذلك فريقُ متابعة التقويم الداخلي
        — ومتابعةُ الناقص **هي عملُه**. (١ أكتوبر ٢٠٢٦) */
  if(c.tab === "fill" && (isScopeBound() || isAdmin() || ME.role === "intqa")){
    const s = pendingEntry();
    if(s && s.left.length){
      const mb = el("div","msg bad");
      mb.appendChild(el("b",null, arn(s.left.length) + " من " + arn(s.total)
                                 + " بلا حصةٍ مسجَّلةٍ بعد — " + TR(s.scope)));
      mb.appendChild(el("span",null, " — والجدولُ ناقصٌ حتى تُسجَّل. "));
      const go = el("button","b ghost sm","افتح الكشف");
      go.addEventListener("click", ()=>{ PH = 5; RPT = "pending"; shell(); });
      mb.appendChild(go);
      tp.appendChild(mb);
    } else if(s){
      tp.appendChild(el("div","msg ok",
        "كشفُ المعلمين تامُّ الإدخال (" + arn(s.total) + ")."));
    }
  }
  if(c.tab === "log") return logView(m, c);
  if(c.tab === "assign") return assignView(m, c);
  if(c.tab === "trash") return trashView(m, c);
  if(c.tab === "visits") return visitPlan(m, c);
  if(c.tab === "school") return rotSchool(m, c);
  if(c.tab === "sup") return rotSup(m, c);
  grid(m, c, T);
  myList(m, c);
}

/* صفوفُ الورقة: الأسبوع × اليوم × تخصصَي مجموعة ذلك اليوم */
function rowsOf(c){
  const out = [];
  const only = c.onlyw && c.onlyw !== "كل الأسابيع" ? c.onlyw : null;
  /* ⛔ مرشِّحا المشرف: تخصصُه ويومُ زيارته. كان يرى صفوفَ المجمع كلِّها (أربعُ
     مجموعاتٍ × ثمانيةُ تخصصاتٍ × أربعةُ أيام) ويبحث بيده. (٢٩ سبتمبر ٢٠٢٦)
     ⚠️ ولا يُرشَّح للمعلم بهذين: تخصصُه يلوّن صفَّه ولا يُخفي ما عداه، ليرى
        جدولَ مدرسته كاملاً كما في الإكسل. */
  const filt = !!(ME && isRoving());
  const oneSpec = filt && c.spec && c.spec !== "كل التخصصات" ? c.spec : null;
  const oneDay = filt && c.vday ? c.vday : null;
  D.weeks.forEach(wk=>{
    if(only && wk !== only) return;
    D.days.forEach(day=>{
      if(oneDay && day !== oneDay) return;
      const gs = groupsOf(c, wk, day);
      if(!gs.length) return;
      const dt = dayDate(wk, day);
      let i = 0;
      gs.forEach(gp=>{
        (D.pairs[gp] || []).forEach(sp=>{
          if(oneSpec && sp !== oneSpec) return;
          out.push({wk, day, gp, spec: sp, sub: i++, dt, nat: gp === D.natgroup});
        });
      });
    });
  });
  return out;
}

/* ═════════ زيارةُ اليوم ═════════
   ⛔ المشرفُ يفتح المنصةَ صباحَ يوم زيارته، فيجب أن تكون أمامه بلا بحث:
      الأسبوعُ من التقويم، واليومُ من اسم اليوم، والمجمعُ من جدول دوران فريقه. */
const DOW = ["الأحد","الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت"];
function todayName(){ return DOW[new Date().getDay()]; }
function supComplexOn(wk, day){
  /* ⛔ المسجَّلُ في سجلّ الإشراف: مجمعُه من مواده هو — وأولُ ما تطلبه مواده
     في ذلك اليوم. ومن ليس فيه يبقى على دوران فريقه. */
  const r = ME && ME.role === "supervisor" ? supByEmp(ME.emp) : null;
  if(r){ const v = supVisits(r, wk, day); return v.length ? v[0].cx : ""; }
  const gp = groupOfSpec(gctx().spec, gctx().sector);
  if(!gp) return "";
  if(gp === D.natgroup) return (D.natdays || {})[day] || "";
  return ((D.sup[gp] || {})[wk] || {})[day] || "";
}
function jumpToToday(){
  const wk = currentWeek() || D.weeks[0];
  setctx("onlyw", wk);
  const dn = todayName();
  /* ⚠️ الجمعةُ والسبتُ والأربعاءُ ليست أيامَ زيارة، فيُنتقل إلى أقرب يومٍ فيه
     لفريقه مجمع — ولا تُترك الشاشةُ فارغةً بلا تفسير. */
  const days = D.days.indexOf(dn) >= 0
      ? [dn].concat(D.days.filter(d=>d !== dn))
      : D.days.slice();
  let hit = "";
  for(const d of days){ if(supComplexOn(wk, d)){ hit = d; break; } }
  if(!hit){ setctx("vday",""); return false; }
  setctx("vday", hit);
  const cx = supComplexOn(wk, hit);
  if(cx && (D.complexes[gctx().sector] || []).indexOf(cx) >= 0){
    setctx("complex", cx); setctx("stages", []);
  }
  return true;
}
function todayHint(){
  const wk = currentWeek();
  const dn = todayName();
  if(!wk) return "اليومُ خارج أسابيع التقويم";
  const cx = supComplexOn(wk, dn);
  /* ⚠️ الوصلُ قبل الترجمة يُفوّت المفاتيح: اسمُ اليوم والأسبوعُ والمجمعُ لكلٍّ
     مفتاحُه، والنصُّ الموصولُ لا مفتاحَ له. وكان «الخميس» يبقى عربياً في
     الشاشة الإنجليزية. (١ أكتوبر ٢٠٢٦)
     ⛔ و«فريقك» لغةُ عهدٍ مضى: النطاقُ صار فردياً من سجلّ الإشراف. */
  return cx ? (TR("اليوم: ") + TR(dn) + " · " + TR(wk) + " · " + TR("مجمع ") + TR(cx))
            : (TR(dn) + TR(" ليس يومَ زيارةٍ لك — يُنتقل إلى أقرب يوم"));
}

function grid(m, c, T){
  const bands = bandsOf(c.complex), rows = rowsOf(c);
  const CURW = currentWeek();
  const g = el("div","card");
  const gh = el("h3");
  gh.appendChild(el("span",null,"مجمع " + c.complex + " · " + c.sector));
  gh.appendChild(el("small",null, arn(rows.length) + " صفاً · " + arn(bands.length) + " عمود حصة"));
  const CURW2 = CURW;
  g.appendChild(gh);
  const wrap = el("div","gwrap");
  const t = el("table","mx");

  /* ⚠️ مع table-layout:fixed تأتي الأعرضُ من صف الرأس الأول، والرأسُ المدموج
     (المدرسة) يقسّم عرضَه على حصصه — فتضيق أعمدةُ المدرسة ذات الثلاث حصص
     وتتّسع ذاتُ الحصتين، فتتداخل الكلمات. و`colgroup` يفرض عرضاً واحداً لكلٍّ. */
  const cg = document.createElement("colgroup");
  /* ⛔ **على الجوال كانت أعمدةُ التسمية تلتهم الشاشة.** ثلاثةٌ ثابتةٌ بـ٣٠٤
     بكسلاً (٨٨+١٠٤+١١٢) — أي **٧٨٪ من شاشة ٣٩٠ قبل أن يبدأ العمل**، ويبقى
     للحصة ٨٦ بكسلاً من ١٨٦. فالمعلمُ يفتح جدولَه على جواله فلا يرى منه شيئاً.
     فتُضيَّق التسميةُ ويُوسَّع العمل: ٥٢+٥٦+٦٠ وحصةٌ ١٦٤ — فيصير نصيبُ العمل
     ٤٩٪ بدل ٢٢٪ من المساحة المرئية. (قِيس بإطارٍ بعرضٍ حقيقيٍّ ١ أكتوبر ٢٠٢٦)
     ⚠️ والجدولُ يبقى ممرَّراً أفقياً — لا يُصغَّر النصُّ ليُحشر، فالقراءةُ
        أولى من رؤية كل شيءٍ دفعةً واحدة. */
  const narrow = (typeof matchMedia === "function")
                 && matchMedia("(max-width:760px)").matches;
  const LW = narrow ? [52, 56, 60] : [88, 104, 112];
  const BW = narrow ? "164px" : "186px";
  LW.forEach(w=>{ const c = document.createElement("col"); c.style.width = w+"px"; cg.appendChild(c); });
  bands.forEach(()=>{ const c = document.createElement("col"); c.style.width = BW; cg.appendChild(c); });
  t.appendChild(cg);

  /* رأسٌ من ثلاثة صفوف كما في الملف: المدرسة ثم الحصة ثم الحقول */
  const h1 = el("tr");
  const corner = el("th","corner","المرحلة"); corner.colSpan = 3; corner.rowSpan = 2; h1.appendChild(corner);
  let i = 0;
  while(i < bands.length){
    let j = i; while(j < bands.length && bands[j].stage === bands[i].stage) j++;
    const th = el("th","band" + (T && c.stages.length && c.stages.indexOf(bands[i].stage) < 0 ? " off" : ""));
    th.colSpan = j - i; th.textContent = TR(bands[i].stage);
    h1.appendChild(th); i = j;
  }
  t.appendChild(h1);
  const h2 = el("tr");
  /* ⛔ أُلغي عمودُ «الحصة ٣ (صفوف أولية)» ٢٩ سبتمبر ٢٠٢٦: مشرفُ الأولية صار
     يتابع الابتدائيةَ كلَّها (أولية + عليا)، فتكفيه الأولى والثانية. فلم يبقَ
     عمودٌ زائدٌ ولا تمييزَ له. */
  bands.forEach(b=>{
    const th = el("th");
    th.appendChild(el("b",null, b.per));
    th.appendChild(el("i",null, b.time ? "غالباً " + b.time : "—"));
    h2.appendChild(th);
  });
  t.appendChild(h2);
  const h3 = el("tr");
  ["الأسبوع","اليوم", D.lab_spec].forEach(x=>h3.appendChild(el("th","sub3",x)));
  bands.forEach(()=>h3.appendChild(el("th","sub3",
    D.lab_teacher_short + " · إستراتيجية · اتجاه · فصل · بدء")));
  t.appendChild(h3);

  const qq = (c.q||"").trim();
  const keep = rows.filter(r=>{
    if(!qq && !c.onlyfull) return true;
    const any = bands.some(b=>{
      const L = findLesson(gkey(c.complex, b, r.wk, r.day, r.spec));
      if(!L || !(L.teacher||"").trim()) return false;
      if(c.onlyfull && !qq) return true;
      const hay = (L.teacher||"") + " " + (L.klass||"") + " " + (L.strategy||"");
      return hay.indexOf(qq) >= 0;
    });
    return any;
  });
  const shown = (qq || c.onlyfull) ? keep : rows;
  if(!shown.length){
    wrap.appendChild(el("div","empty","لا صفَّ يطابق الترشيح — أزل البحث أو «المعبّأ فقط»."));
    g.appendChild(wrap); m.appendChild(g); return;
  }
  let lw = null, ld = null;
  shown.forEach(r=>{
    const tr = el("tr", r.sub ? "" : "sep");
    if(r.wk !== lw){
      const td = el("td","cw" + (r.wk === CURW ? " now" : ""));
      td.rowSpan = shown.filter(x=>x.wk === r.wk).length;
      td.appendChild(el("b",null, r.wk));
      const cc = calOf(r.wk);
      if(cc){ td.appendChild(el("i",null, cc.range)); td.appendChild(el("u",null, cc.hrange)); }
      tr.appendChild(td); lw = r.wk; ld = null;
    }
    const dk = r.wk + "|" + r.day;
    if(dk !== ld){
      const isToday = r.dt && r.dt.g === todayISO();
      const td = el("td","cd" + (isToday ? " today" : ""));
      td.rowSpan = shown.filter(x=>x.wk === r.wk && x.day === r.day).length;
      td.appendChild(el("b",null, r.day + (isToday ? "  ●" : "")));
      if(r.dt && r.dt.gt){
        td.appendChild(el("i",null, r.dt.gt));
        td.appendChild(el("u",null, r.dt.ht));
      }
      const gsAll = groupsOf(c, r.wk, r.day);
      /* ⚠️ تُترجَم كلُّ مجموعةٍ ثم تُوصل — والوصلُ قبل الترجمة يُفوّتها */
      td.appendChild(el("div","gsel ro2", gsAll.map(TR).join(" + ")));
      tr.appendChild(td); ld = dk;
    }
    const mine = ME.role === "teacher" && r.spec === gctx().spec;
    const sc = el("td","cs" + (mine ? " hit" : "") + (r.nat ? " nat" : ""));
    sc.appendChild(el("div",null, r.spec));
    if(r.nat) sc.appendChild(el("div","natmark", D.natgroup));
    if(mine) sc.appendChild(el("div","mark","تخصصك"));
    tr.appendChild(sc);
    bands.forEach(b=>{
      const td = el("td","cell");
      td.appendChild(cellEditor(c, b, r));
      tr.appendChild(td);
    });
    t.appendChild(tr);
  });
  wrap.appendChild(t); g.appendChild(wrap);
  const n = el("div","pad note");
  n.appendChild(el("div",null,
    "وقتُ البدء يُكتب في الخانة — فقد تختلف مواعيدُ الحصص بين مدارس المجمع الواحد، "
    + "والمكتوبُ في رأس العمود هو الغالبُ في الملف تذكيراً لا إلزاماً."));
  g.appendChild(n);
  m.appendChild(g);
}

function cellEditor(c, band, r){
  const gk = gkey(c.complex, band, r.wk, r.day, r.spec);
  const w = el("div","cellbox");
  const cur = () => findLesson(gk);
  const ensure = ()=>{
    let x = cur();
    if(!x){
      x = {id:uid(), gk:gk, sector:c.sector, complex:c.complex, stage:band.stage, school:band.stage,
           period:band.per, week:r.wk, day:r.day, date:(r.dt||{}).g || "",
           datetxt:(r.dt||{}).gt || "", hijri:(r.dt||{}).ht || "", spec:r.spec, group:r.gp,
           subject:r.spec, teacher:"", strategy:"", approach:"", klass:"", time:"",
           peer1:"", peer2:"", peer1e:"", peer2e:"", ev1:"", ev2:"", ev3:"", ev4:""};
      DB.sched.push(x);
    }
    return x;
  };
  const L0 = cur(), ed = canEdit(c, band, L0);
  const paint = ()=>{
    const x = cur(), on = !!(x && (x.teacher||"").trim());
    w.className = "cellbox" + (on ? (ME.role === "teacher" && !isMine(x) ? " other" : " on") : "")
                            + (ed ? "" : " locked") + (x && x.approved ? " appr" : "");
    const a = w.querySelector(".crow2"); if(a) a.style.display = on ? "" : "none";
  };
  const mk = (key, ph, opts, cls, lock, after) => {
    const x = cur(), v = x ? (x[key]||"") : "";
    if(!ed){ const d = el("div","cin ro2" + (cls ? " "+cls : ""), v || "—"); w.appendChild(d); return; }
    /* ⛔ حقلٌ مقفولٌ برسالته: لو تُرك حقلاً حرّاً كتب المعلمُ فيه إستراتيجيةً
       لا تنتمي لاتجاهه — وهو ما جاء التقييدُ ليمنعه. */
    if(lock){
      const d = el("div","cin ro2 lock", lock);
      d.title = lock; w.appendChild(d); return;
    }
    const e = fld(opts ? "sel" : "txt", v, val=>{
      snap(gk, "تعديل " + ph);
      const y = ensure(), was = y[key];
      y[key] = val;
      /* ⚠️ تغييرُ الاتجاه يُسقط إستراتيجيةً لا تنتمي إليه: لو بقيت لعُرضت
         خانةً فارغةً وقيمتُها محفوظةٌ في الخلف — فيظنُّها المعلمُ مختارة. */
      if(key === "approach"){
        const lst = (D.appstrat || {})[val] || [];
        if((y.strategy || "") && lst.indexOf(y.strategy) < 0){
          logAct("تعديل", "إسقاط إستراتيجية لا تناسب الاتجاه: «" + y.strategy + "»", y);
          y.strategy = "";
        }
      }
      if(key === "teacher"){
        /* ⛔ **لا يُمحى رقمٌ بتعديل نصّ**: كانت المطابقةُ حرفيةً تامّةً على
           الكشف، فأيُّ مسافةٍ أو تصحيحِ حرفٍ يمحو الرقمَ — وفي نسخة البنات
           (بلا كشف) يمحوه دائماً. فينقسم الشخصُ الواحدُ شخصين في التقارير.
           (٣٠ سبتمبر ٢٠٢٦) */
        /* ⚠️ وبالتسوية لا بالحرف: «أحمد صيام» و«أحمد صيّام» و«احمد صيام»
           شخصٌ واحد، وكان فرقُ حرفٍ يُفوّت الرقمَ فيُحرم صاحبُه منه. */
        const vn = arname(val);
        const hit = Object.keys(D.roster||{}).find(k=>arname(D.roster[k].n) === vn);
        if(hit) y.teacherNo = hit;
        else if(!(val||"").trim()) y.teacherNo = "";
      }
      if(key === "teacher" && (val||"").trim() && !(was||"").trim())
        logAct("تسجيل حصة", val + " — " + band.stage + " · " + band.per + " · " + r.wk + " " + r.day, y);
      else if(String(was||"") !== String(val||""))
        logAct("تعديل", ph + ": «" + (was||"—") + "» ← «" + (val||"—") + "»", y);
      if(!(y.teacher||"").trim() && !y.strategy && !y.approach && !(y.klass||"").trim()
         && !(y.time||"").trim() && !DB.prep[y.id])
        DB.sched = DB.sched.filter(z=>z.id!==y.id);
      save(); paint();
      /* ⛔ الحارسُ بعد الحفظ لا قبلَه: يقيس على الجدول كما صار */
      if(after) try{ after(cur()); }catch(e){}
    }, opts, ph);
    e.className = "cin" + (cls ? " " + cls : "");
    if(opts) e.title = ph;
    w.appendChild(e);
  };
  mk("teacher", D.lab_teacher_short, null, "nm", null, x=>{
    const cf = supConflict(x);
    if(cf) alert(TR("مشرفُ هذه المادة (") + cf.name + TR(") له حصةٌ مسجَّلةٌ في ")
      + cf.other.map(TR).join(TR(" و")) + TR(" في اليوم نفسِه من هذا الأسبوع، ")
      + TR("ولا يكون في مجمعين في يوم. انقل هذه الحصة إلى يومٍ أو أسبوعٍ آخر."));
  });
  /* ⛔ **الاتجاهُ قبل الإستراتيجية**: الاتجاهُ يحدّد أيَّ إستراتيجيةٍ تُختار،
     فلو جاء بعدها اختار المعلمُ من تسعَ عشرةَ ثم عرف أنها لا تناسب اتجاهه.
     (طلبُ المستشار ٣٠ سبتمبر ٢٠٢٦) */
  mk("approach", "الاتجاه التدريسي", D.approaches);
  /* ⚠️ وقائمةُ الإستراتيجيات تُقصَر على إستراتيجيات الاتجاه المختار — وهي
     من نشرات الاتجاهات المعتمدة. وما لم يُختر اتجاهٌ فلا قائمةَ بل تنبيه. */
  const _apr = (cur() || {}).approach || "";
  const _sl = (D.appstrat || {})[_apr];
  mk("strategy", "الاستراتيجية", _sl && _sl.length ? _sl : null, null,
     _apr ? "" : "اختر الاتجاه التدريسي أولاً");
  /* ⛔ **اسمُ المادةِ يُكتب في الخانة.** كان يُملأ من عمود تخصص الزائر ولا
     يُعدَّل — فيصحُّ في التعليم العام ولا يصحُّ في **رياض الأطفال**: موادُّها
     ليست من التخصصات السبعة، وتقييمُها لمديرة الروضة ومديرة المجمع وفريق
     المتابعة لا لمشرفِ تخصص. فلا حاجةَ إلى قائمةٍ تُستخرج — تكتبها المعلمةُ
     بنفسها، ويبقى تخصصُ العمود افتراضاً لمن لا يكتب.
     (قرارُ المستشار ١ أكتوبر ٢٠٢٦) */
  const rowsub = el("div","crow1");
  if(ed){
    const sb = fld("txt", L0 ? (L0.subject||"") : "",
      v=>{ snap(gk,"تعديل المادة"); ensure().subject = v; save(); paint(); },
      null, "اسم المادة (" + TR(r.spec) + ")");
    sb.className = "cin sm"; rowsub.appendChild(sb);
  } else rowsub.appendChild(el("div","cin sm ro2", (L0 && L0.subject) || "—"));
  w.appendChild(rowsub);

  const rowlet = el("div","crow");
  if(ed){
    const kl = fld("txt", L0 ? (L0.klass||"") : "", v=>{ snap(gk,"تعديل الفصل"); ensure().klass = v; save(); paint(); }, null, "الفصل");
    const tm = fld("txt", L0 ? (L0.time||"") : "", v=>{ snap(gk,"تعديل الوقت"); ensure().time = v; save(); paint(); }, null, band.time || "وقت البدء");
    kl.className = "cin sm"; tm.className = "cin sm";
    rowlet.appendChild(kl); rowlet.appendChild(tm);
  } else {
    rowlet.appendChild(el("div","cin sm ro2", (L0 && L0.klass) || "—"));
    rowlet.appendChild(el("div","cin sm ro2", (L0 && L0.time) || "—"));
  }
  w.appendChild(rowlet);
  if(ed && ME.role === "teacher" && !(L0 && (L0.teacher||"").trim())){
    const me = el("button","cme","سجّلني هنا");
    me.addEventListener("click", ()=>{ snap(gk,"تسجيل الاسم");
      const y = ensure(); y.teacher = ME.name; y.teacherNo = ME.emp || "";
      logAct("تسجيل حصة", ME.name + " — " + band.stage + " · " + band.per + " · " + r.wk + " " + r.day, y);
      save(); shell(); });
    w.appendChild(me);
  }
  /* ⛔ وشارةُ «عليك» في الخانة نفسِها — فهي أولُ ما تقع عليه العين، ولا
     يُطلب من أحدٍ أن يفتح حصةً حصةً ليعرف أيُّها عليه. (١ أكتوبر ٢٠٢٦) */
  if(L0){
    const _g = gapTag(L0);
    if(_g){ const gw = el("div"); gw.style.marginTop = "2px"; gw.appendChild(_g); w.appendChild(gw); }
  }
  const act = el("div","crow2");
  const st = el("button","cst","ابدأ الحصة ←");
  st.addEventListener("click", ()=>{ const y = cur(); if(!y) return; CUR = y.id; PH = 2; shell(); });
  act.appendChild(st);
  if(ed && L0 && ((L0.teacher||"").trim() || L0.strategy || (L0.klass||"").trim())){
    const cx2 = el("button","cclr","✕");
    cx2.title = "مسحُ هذه الخانة";
    cx2.setAttribute("aria-label", "مسح خانة الحصة");
    cx2.addEventListener("click", ()=>clearCell(gk));
    act.appendChild(cx2);
  }
  w.appendChild(act);
  paint();
  return w;
}

/* الوجه الأول من الورقة الأولى: من يزور هذا المجمع */
function rotSchool(m, c){
  const card = el("div","card"), h = el("h3");
  h.appendChild(el("span",null,"جدول زيارات المجمعات"));
  h.appendChild(el("small",null,"أيُّ فريقِ تخصّصٍ يزور المجمع في كل يومٍ من كل أسبوع"));
  card.appendChild(h);
  const wrap = el("div","gwrap");
  D.complexlist.forEach(cx=>{
    const ttl = el("div","wk", "مجمع " + cx + (cx === c.complex ? "  ← مجمعك" : ""));
    if(cx === c.complex) ttl.className = "wk on";
    wrap.appendChild(ttl);
    const t = el("table","mx2"), hr = el("tr");
    hr.appendChild(el("th",null,"اليوم \\ الأسبوع"));
    D.weeks.forEach(w=>{
      const th = el("th");
      th.appendChild(el("b",null,w));
      const cc = calOf(w); if(cc) th.appendChild(el("i",null, cc.range));
      hr.appendChild(th);
    });
    t.appendChild(hr);
    D.days.forEach(d=>{
      const r = el("tr");
      r.appendChild(el("td","cs", d));
      D.weeks.forEach(w=>{
        const v = groupOf(cx, w, d);
        const td = el("td","mid", v || "—");
        if(!v) td.className += " dim";
        r.appendChild(td);
      });
      t.appendChild(r);
    });
    wrap.appendChild(t);
  });
  card.appendChild(wrap); m.appendChild(card);
}

/* الوجه الثاني: أين يزور فريقُ كل تخصص */
function rotSup(m, c){
  const card = el("div","card"), h = el("h3");
  h.appendChild(el("span",null,"جدول زيارات المشرفين"));
  h.appendChild(el("small",null,"إلى أي مجمعٍ يذهب فريقُ كل تخصصٍ في كل يومٍ من كل أسبوع"));
  card.appendChild(h);
  const wrap = el("div","gwrap");
  /* ⛔ «فريقك» تُعرف من **سجلّ الإشراف** لمن هو فيه: قد يحمل مادتين في
     مجموعتين، فيُعلَّم كلتاهما. ومن ليس في السجلّ يبقى على تخصص سياقه. */
  const _me = ME && ME.role === "supervisor" ? supByEmp(ME.emp) : null;
  const mine = {};
  if(_me){
    Object.keys(D.pairs).forEach(k=>{
      if((D.pairs[k] || []).some(sp=>!!_me.allsubj || (_me.subjects||[]).indexOf(sp) >= 0))
        mine[k] = 1;
    });
  } else {
    Object.keys(D.pairs).forEach(k=>{ if(D.pairs[k].indexOf(gctx().spec) >= 0) mine[k] = 1; });
  }
  D.specgroups.forEach(gp=>{
    /* ⚠️ الاسمُ يُترجَم قبل وصل اللاحقة — والوصلُ أولاً يُفوّت المفتاح */
    const ttl = el("div","wk" + (mine[gp] ? " on" : ""),
                   TR(gp) + (mine[gp] ? TR("  ← فريقك") : ""));
    wrap.appendChild(ttl);
    const t = el("table","mx2"), hr = el("tr");
    hr.appendChild(el("th",null,"اليوم \\ الأسبوع"));
    D.weeks.forEach(w=>{
      const th = el("th");
      th.appendChild(el("b",null,w));
      const cc = calOf(w); if(cc) th.appendChild(el("i",null, cc.range));
      hr.appendChild(th);
    });
    t.appendChild(hr);
    D.days.forEach(d=>{
      const r = el("tr");
      r.appendChild(el("td","cs", d));
      D.weeks.forEach(w=>{
        const v = ((D.sup[gp]||{})[w]||{})[d] || "";
        const td = el("td","mid", v || "—");
        if(!v) td.className += " dim";
        r.appendChild(td);
      });
      t.appendChild(r);
    });
    wrap.appendChild(t);
  });
  card.appendChild(wrap); m.appendChild(card);
}

function myList(m, c){
  let here = DB.sched.filter(x=>x.gk && x.gk.indexOf(c.sector + "|" + c.complex + "|") === 0);
  if(ME.role === "teacher") here = here.filter(isMine);
  /* ⛔ **القائمةُ كانت تعرض المجمعَ كلَّه لمن نطاقُه مدرسة.** ستةُ أعمدةٍ في
     ثلاث مدارس أمام وكيلِ مدرسةٍ واحدة — ومعها زرُّ حذف. فيرى حصصَ غيره
     ويحذفها. و`inMyScope` كانت معرَّفةً ولا تُستعمل هنا. (١ أكتوبر ٢٠٢٦) */
  else if(isScopeBound()) here = here.filter(inMyScope);
  const s2 = el("div","card"), sh = el("h3");
  sh.appendChild(el("span",null, ME.role === "teacher" ? "حصصك المسجَّلة" : "الحصص المسجَّلة في المجمع"));
  /* ⚠️ والعدُّ يقول ما يقع عليه لا مجرّدَ العدد */
  const _mg = here.filter(isMyGap).length;
  sh.appendChild(el("small",null, arn(here.length) + " حصة"
    + (_mg ? (" · منها " + arn(_mg) + " عليك (لا مشرفَ لتخصصها)") : "")));
  s2.appendChild(sh);
  const sp = el("div","pad");
  if(!here.length){
    sp.appendChild(el("div","empty", ME.role === "teacher"
      ? "لا حصةَ مسجَّلةٌ بعد — والتسجيل بزرّ «سجّلني هنا» في خانة الحصة التي ستُنفَّذ فيها."
      : "لم تُسجَّل حصصٌ بعد في هذا المجمع."));
  } else {
    const tb = el("table"), tr = el("tr");
    const heads = ["المدرسة والحصة","الأسبوع واليوم", D.lab_teacher_short, "الاستراتيجية والاتجاه", D.lab_spec];
    if(ME.role !== "teacher") heads.push("الزائران","المقيّمون");
    heads.push("التقدّم","");
    heads.forEach(x=>tr.appendChild(el("th",null,x)));
    tb.appendChild(tr);
    here.forEach(L=>{
      const pg = prog(L), r = el("tr");
      r.appendChild(el("td",null, [L.stage, L.period, L.time].filter(Boolean).join(" · ")));
      r.appendChild(el("td",null, [L.week, L.day].filter(Boolean).join(" · ")));
      r.appendChild(el("td",null, [L.teacher, L.klass].filter(Boolean).join(" · ") || "—"));
      r.appendChild(el("td",null, [L.strategy, L.approach].filter(Boolean).join(" · ") || "—"));
      r.appendChild(el("td",null, L.spec || "—"));
      if(ME.role !== "teacher"){
        /* ⛔ كان نصًّا حرًّا بالأسماء يراه كلُّ مقيّمٍ ويكتب فيه — والأسماءُ
           تتشابه. صار عرضاً للقراءة، والإسنادُ بالرقم في تبويب «إسناد
           الزائرين» عند الوكيل وحده. (٢٩ سبتمبر ٢٠٢٦) */
        const pe = el("td","nar");
        const names = [L.peer1, L.peer2].filter(Boolean);
        if(names.length) pe.textContent = TR(names.join(" · "));
        else{
          pe.appendChild(el("span","tag no","لم يُسنَد"));
          if(isDeputy()){
            const g = el("button","lnk","أسنِدهما");
            g.addEventListener("click", ()=>{ setctx("tab","assign"); shell(); });
            pe.appendChild(g);
          }
        }
        r.appendChild(pe);
        const ev = el("td","nar");
        ev.appendChild(fld("txt", [L.ev1,L.ev2,L.ev3,L.ev4].filter(Boolean).join("، "), v=>{
          const a = v.split(/[،,]/).map(z=>z.trim());
          L.ev1=a[0]||""; L.ev2=a[1]||""; L.ev3=a[2]||""; L.ev4=a[3]||""; save();
        }, null, "المقيّمون الثلاثة"));
        r.appendChild(ev);
      }
      const td = el("td");
      const tag = (cls,txt)=>{ td.appendChild(el("span","tag "+cls,txt)); td.appendChild(document.createTextNode(" ")); };
      /* ⛔ الشارةُ أولاً: هي الجوابُ عن سؤاله الأول «أيُّ حصةٍ عليّ؟» */
      const _gt = gapTag(L);
      if(_gt){ td.appendChild(_gt); td.appendChild(document.createTextNode(" ")); }
      if(L.approved) tag("ok", "معتمدة ◆");
      tag(pg.issued?"ok":"no", pg.issued?"حُضِّر":"لم يُحضَّر");
      tag(pg.obs>=3?"ok":(pg.obs?"mid":"no"), "تقييم "+arn(pg.obs)+"/٣");
      tag(pg.pr>=2?"ok":(pg.pr?"mid":"no"), "أقران "+arn(pg.pr)+"/٢");
      r.appendChild(td);
      const ac = el("td","nowrap");
      const go = el("button","b alt","افتح"); go.style.cssText="padding:4px 12px;font-size:14px";
      go.addEventListener("click", ()=>{ CUR = L.id; PH = 2; shell(); });
      ac.appendChild(go);
      /* ⚠️ ولا يُعرض الزرُّ لمن لا يملكه: الحارسُ عند المصدر يمنع، والزرُّ
         الظاهرُ بلا صلاحيةٍ يُغري ثم يُحبط. */
      if(canDrop(L)){
        const x = el("button","b warn","حذف"); x.style.cssText="padding:4px 10px;font-size:14px;margin-inline-start:6px";
        x.addEventListener("click", ()=>{
          uiAsk("حذفُ هذه الحصة وكلِّ ما عُلِّق بها؟\n\n"
            + "تُنقل إلى سلّة المحذوفات وتُستردُّ منها ثلاثين يوماً.",
            "احذفها", "bad").then(ok=>{ if(!ok) return; dropLesson(L.id); shell(); });
        });
        ac.appendChild(x);
      }
      r.appendChild(ac);
      tb.appendChild(r);
    });
    sp.appendChild(tb);
  }
  s2.appendChild(sp); m.appendChild(s2);
}

function backup(){
  const a = document.createElement("a");
  a.href = "data:application/json;charset=utf-8," + encodeURIComponent(JSON.stringify(DB, null, 1));
  a.download = "نسخة-منصة-الحصة-الموحدة.json"; a.click();
}


/* ══ ضخُّ بيانات الحصة من الجدول إلى التحضير ══
   يُملأ الفارغ فقط، فلا يُمحى ما كتبه المعلم — إلا بطلبه (force). */
function inject(L, P, force){
  const set = (k, v) => { if(v && (force || !P[k])) P[k] = v; };
  set("i_teacher", L.teacher);
  set("i_subject", L.subject || L.spec);
  set("i_klass",   L.klass);
  set("i_period",  perLabel(L, true));
  set("i_date",    joinAr([L.day, L.datetxt, L.hijri]) || joinAr([L.week, L.day]));
  set("f_strat",   L.strategy);
  if(L.approach){
    const i = D.approaches.indexOf(L.approach);
    if(i >= 0){
      const any = D.approaches.some((_,k)=>P["f_dir#"+k]);
      if(force || !any) P["f_dir#"+i] = true;
    }
  }
  return P;
}

/* ⛔ وحُذفت `rekeySchool(c, old, new)`: كانت تُعيد ترقيم المفاتيح عند تغيير
   اسم المدرسة «فلا تُيتَّم حصة» — **ولا يناديها شيء**. وهي تحرس حالةً لا
   تقع: لا حقلَ نصيّاً لاسم المدرسة في المنصة، بل تُختار من قائمة `bands`
   المعتمدة. فحارسٌ لم يُنفَّذ أسوأُ من غيابه: يُطمئن قارئَه إلى حمايةٍ
   ليست قائمة. (١ أكتوبر ٢٠٢٦) */

/* رابطُ الدعوة: عنوانُ المنصة ومعه المخزن — تُرسله فيُفتح مربوطاً بلا لصقٍ ولا شرح */
/* ضبطُ مفتاح المخزن وتدويرُه — للمستشار وحدَه */
function setKey(){
  if(!isAdmin()) return;
  const cur = skey();
  uiPrompt("مفتاحُ المخزن المشترك — يُرسَل مع كل طلبٍ إلى الخادم.\n\n"
    + "اكتب مفتاحاً طويلاً (٢٤ حرفاً فأكثر) لا يُخمَّن، أو اتركه فارغاً لتوليد واحد.\n"
    + (cur ? "\n⚠️ وتدويرُه يقطع الأجهزةَ التي تحمل القديمَ حتى يصلها رابطُ دعوةٍ جديد.\n" : "")
    + "\n⚠️ ولا يعمل حتى يفحصه الخادمُ — راجع دليلَ الاستضافة.", cur, "").then(v=>{
    if(v === null) return;
    let k = String(v).trim();
    if(!k){
      /* مولَّدٌ من مصدرٍ عشوائيٍّ معمّى لا من الوقت */
      const a = new Uint8Array(24);
      (crypto && crypto.getRandomValues) ? crypto.getRandomValues(a)
        : a.forEach((_, i)=>{ a[i] = Math.floor(Math.random() * 256); });
      k = Array.prototype.map.call(a, x=>("0" + x.toString(16)).slice(-2)).join("");
    }
    if(k.length < 24){ alert("⛔ المفتاحُ قصير: " + arn(k.length) + " حرفاً، والأدنى ٢٤."); return; }
    try{ localStorage.setItem(SKEY, k); }catch(e){}
    logAct("ضبط مفتاح المخزن", cur ? "تدويرٌ" : "ضبطٌ أول", null);
    save();
    alert("✓ ضُبط المفتاح.\n\nانسخ رابطَ الدعوة وأرسله من جديدٍ ليحمله إلى الأجهزة.");
    shell();
  });
}
function invite(){
  /* ⚠️ المفتاحُ في `#` لا في `?`: جزءُ التجزئة لا يُرسَل في ترويسة الإحالة
     ولا يُسجَّل في سجلّات الخوادم الوسيطة. */
  const k = skey();
  const u = location.origin + location.pathname + "#srv=" + encodeURIComponent(api())
          + (k ? "&k=" + encodeURIComponent(k) : "");
  const done = ()=>alert("نُسخ رابط الدعوة.\n\nأرسله لمن يعنيه — يفتحه فيُربط جهازه تلقائياً،\n"
    + "ولا يُطلب منه لصقُ شيء.\n\n" + u);
  if(navigator.clipboard && navigator.clipboard.writeText)
    navigator.clipboard.writeText(u).then(done).catch(()=>uiPrompt("انسخ رابط الدعوة:", u));
  else uiPrompt("انسخ رابط الدعوة:", u);
}

/* ══ التراجع: يحفظ حال الحصة قبل كل تغيير، ويعيدها بنقرة ══ */
function snap(gk, label){
  const L = DB.sched.find(x=>x.gk === gk);
  /* ⛔ **اللقطةُ تلتقط ما يُحذف كلَّه**: كانت تلتقط الحصةَ وتحضيرَها فقط،
     فيُعيد التراجعُ حصةً بلا رصدٍ ولا بطاقاتِ أقران — وتبدو سليمةً وليست.
     (٣٠ سبتمبر ٢٠٢٦) */
  const obs = {}, pr = {};
  if(L){
    Object.keys(DB.obs || {}).forEach(k=>{ if(DB.obs[k] && DB.obs[k].__lid === L.id) obs[k] = DB.obs[k]; });
    Object.keys(DB.peer || {}).forEach(k=>{ if(k.split("|")[0] === L.id) pr[k] = DB.peer[k]; });
  }
  UNDO.push({gk: gk, label: label, obs: obs, peerc: pr,
             lesson: L ? JSON.parse(JSON.stringify(L)) : null,
             prep: L && DB.prep[L.id] ? JSON.parse(JSON.stringify(DB.prep[L.id])) : null});
  if(UNDO.length > 25) UNDO.shift();
}
function undo(){
  const u = UNDO.pop();
  if(!u) return;
  const cur = DB.sched.find(x=>x.gk === u.gk);
  if(u.lesson){
    if(cur) Object.assign(cur, u.lesson);
    else DB.sched.push(u.lesson);
    if(u.prep) DB.prep[u.lesson.id] = u.prep;
    /* ⛔ ويُعادُ ما التقطته اللقطةُ كلُّه — وإلا عادت الحصةُ بلا رصدٍ ولا أقران */
    Object.keys(u.obs || {}).forEach(k=>{ DB.obs[k] = u.obs[k]; });
    Object.keys(u.peerc || {}).forEach(k=>{ DB.peer[k] = u.peerc[k]; });
  } else if(cur){
    dropLesson(cur.id);                      /* لم تكن موجودةً فتُحذف حذفاً معلَناً */
    shell(); return;
  }
  save(); shell();
}
/* مسحُ الخانة: يُنبَّه إن كان فيها تحضيرٌ أو رصد */
function clearCell(gk){
  const L = DB.sched.find(x=>x.gk === gk);
  if(!L) return;
  const p = prog(L);
  const go = ()=>{ snap(gk, "مسحُ خانة"); dropLesson(L.id); shell(); };
  if(!(p.issued || p.obs || p.pr)){ go(); return; }
  uiAsk("هذه الحصة فيها " +
    [p.issued ? "تحضيرٌ مُصدَر" : "", p.obs ? "رصدٌ " + arn(p.obs) : "", p.pr ? "أقران " + arn(p.pr) : ""]
      .filter(Boolean).join(" و") + ".\nالمسحُ يحذفها وما عُلِّق بها. أتُتابع؟",
    "امسحها", "bad").then(ok=>{ if(ok) go(); });
}

/* ═════════ المرحلة ٦: تنفيذ الحصة — ورقةُ التنفيذ ═════════
   المعلمُ يُمسكها في الحصة، والزائرُ يقرؤها قبل دخوله. مصدرُها التحضيرُ المُصدَر
   لا إدخالٌ جديد، فلا تتكرّر الكتابةُ ولا تفترق الورقةُ عن التحضير. */
/* ⛔ لا حصةَ بلا مقيّمٍ معلوم: إمّا مشرفُها بالاسم، وإمّا الفريقُ المعاون —
   ولا تُترك الخانةُ صامتةً فيظنَّ كلٌّ أن غيرَه يرصدها. */
function scorerNote(m, L){
  const sup = supsFor(L), c = el("div","card"), p2 = el("div","pad");
  if(sup.length){
    p2.appendChild(el("div","msg ok", TR("المقيّم: ")
      + sup.map(r=>r.name).join(TR(" · ")) + TR(" — ")
      + TR(D.evalroles[2]) + TR(". والمديرُ يطّلع ويعلّق، والوكيلُ يتابع التعبئة.")));
  } else {
    p2.appendChild(el("div","msg warn", TR("لا مشرفَ مختصٌّ لهذا التخصص في هذه المدرسة، ")
      + TR("فالتقييمُ للفريق المعاون: ")
      + (D.gapscore||[]).map(k=>TR((D.roles.find(r=>r.k===k)||{}).t || k)).join(TR(" أو "))
      + TR(".")));
  }
  const cf = supConflict(L);
  if(cf) p2.appendChild(el("div","msg bad", TR("تعارض: مشرفُ هذه المادة (") + cf.name
    + TR(") له حصةٌ في ") + cf.other.map(TR).join(TR(" و"))
    + TR(" في اليوم نفسِه من هذا الأسبوع.")));
  c.appendChild(p2); m.appendChild(c);
}
function ph6(m){
  const L = DB.sched.find(x=>x.id===CUR);
  if(!L){ picker(m, "اختر الحصة لعرض ورقة تنفيذها", ()=>shell()); return; }
  const P = DB.prep[L.id] || {};
  const head = el("div","card");
  const h = el("h3");
  h.appendChild(el("span",null, lessonTitle(L)));
  h.appendChild(el("small",null, lessonSub(L))); head.appendChild(h);
  const hp = el("div","pad"), bar = el("div","bar");
  const back = el("button","b ghost","تغيير الحصة");
  back.addEventListener("click", ()=>{ CUR=null; shell(); });
  bar.appendChild(back);
  const pr = el("button","b","اطبع ورقة التنفيذ");
  pr.addEventListener("click", ()=>window.print()); bar.appendChild(pr);
  hp.appendChild(bar);
  if(!P.__issued){
    const w = el("div","msg bad");
    w.textContent = ME.role === "teacher"
      ? "لم تُصدَر ورقةُ التحضير بعد — أكملها في مرحلة «الاستعداد والتحضير» ثم عد إلى هنا."
      : "تحضيرُ هذه الحصة لم يُصدَر بعد، فورقةُ التنفيذ ناقصة.";
    hp.appendChild(w);
  } else hp.appendChild(el("div","msg ok","ورقةُ تنفيذٍ من تحضيرٍ صدر في " + P.__issued));
  head.appendChild(hp); m.appendChild(head);

  const box = (title, note) => {
    const c = el("div","card"), hh = el("h3");
    hh.appendChild(el("span",null,title));
    if(note) hh.appendChild(el("small",null,note));
    c.appendChild(hh); const p2 = el("div","pad"); c.appendChild(p2); m.appendChild(c); return p2;
  };
  const line = (p2, k, v) => {
    const r = el("div","runrow");
    r.appendChild(el("b",null,k)); r.appendChild(el("div",null, v || "—"));
    p2.appendChild(r);
  };
  /* بطاقةُ الحصة */
  const b0 = box("بطاقة الحصة", "من الجدول والتحضير");
  const g0 = el("div","grid");
  D.info.forEach(f=>{
    const w = el("label","f"); w.appendChild(el("span",null,f.l));
    w.appendChild(el("div","ro", P["i_"+f.k] || "—")); g0.appendChild(w);
  });
  b0.appendChild(g0);
  /* الأهداف والسؤال الأساسي */
  const b1 = box("السؤال الأساسي والأهداف", "ما تُقاس عليه الحصة");
  line(b1, "السؤال الأساسي", P.f_q_main);
  ["obj_know","obj_skill","obj_emo"].forEach((k,i)=>{
    const lab = ["الهدف المعرفي","الهدف المهاري","الهدف الوجداني"][i];
    const vs = [P["f_"+k+"_1"], P["f_"+k+"_2"]].filter(Boolean);
    line(b1, lab, vs.join(" · "));
  });
  /* خريطة الزمن */
  const b2 = box("خريطة الزمن", "بالدقائق — ومجموعُها زمنُ الحصة");
  const tw = el("div","g5");
  D.tmain.forEach(k=>{
    const d = el("div"); d.appendChild(el("label",null, D.tlabels[k]));
    d.appendChild(el("div", k === "total" ? "ro sum" : "ro",
                     k === "total" ? arn(tsum(P).parts) : (P["tk_"+k] || "—")));
    tw.appendChild(d);
  });
  b2.appendChild(tw);
  const th2 = el("div","tdiff", TR(D.tdifft) + TR(" — داخلَه لا يُضافان إليه:"));
  b2.appendChild(th2);
  const tw2 = el("div","g2");
  D.tdiff.forEach(k=>{
    const d = el("div","care"); d.appendChild(el("label",null, D.tlabels[k]));
    d.appendChild(el("div","ro", P["tk_"+k] || "—")); tw2.appendChild(d);
  });
  b2.appendChild(tw2);
  /* مراحل الحصة */
  const b3 = box("مراحل الحصة", "ما يفعله كلٌّ في كل مرحلة");
  D.stages.forEach(([k,name])=>{
    const r = el("div","stg");
    const c0 = el("div","stn", name);
    c0.appendChild(el("div","ro", (P["st_"+k+"_time"]||"—") + " د")); r.appendChild(c0);
    r.appendChild(el("div","ro", P["st_"+k+"_t"] || "—"));
    r.appendChild(el("div","ro", P["st_"+k+"_l"] || "—"));
    const md = el("div");
    D.modes.forEach((grp,gi)=>{
      const pk = grp.filter((_,i)=>P["st_"+k+"_m"+gi+"#"+i]);
      md.appendChild(el("div","ro", pk.length ? pk.join(" · ") : "—"));
    });
    r.appendChild(md); b3.appendChild(r);
  });
  /* الإستراتيجية وبطاقتها */
  const st = P.f_strat || L.strategy || "";
  const bank = D.bank.find(x=>x.name === st);
  const b4 = box("الإستراتيجية المعلنة", st || "لم تُعلَن");
  if(bank){
    const ul = el("ol"); ul.style.cssText = "padding-inline-start:22px;font-size:15.5px";
    bank.inds.forEach(x=>ul.appendChild(el("li",null,x)));
    b4.appendChild(el("div",null,"مؤشراتُ تطبيقها العشرة — وهي ما يرصده الزائر:"))
      .style.cssText = "font-family:JZL,SK;color:var(--grey);margin-bottom:6px";
    b4.appendChild(ul);
  } else b4.appendChild(el("div","empty","اختر الإستراتيجية في التحضير لتظهر بطاقتُها هنا."));
  /* المهمتان والربط */
  const b5 = box("التمايز والربط بالحياة", "ما يُرى في الحصة لا ما يُقال");
  line(b5, "المهمة المكيَّفة", P.f_adapt);
  line(b5, "المهمة الإثرائية", P.f_enrich);
  line(b5, "الربط بالحياة", P.f_life);
  line(b5, "نشاط التفكير", P.f_think);
  line(b5, "المهمة على المنصة", P.f_platform);
  /* التقويم */
  const b6 = box("التقويم والتغذية الراجعة", "أدواتُ الحصة");
  line(b6, "التقويم التشخيصي", P.f_diag);
  line(b6, "التقويم البنائي", P.f_form);
  line(b6, "التغذية الراجعة", P.f_fb);
  line(b6, "التقييم الختامي", [P.f_final_1, P.f_final_2].filter(Boolean).join(" · "));
  line(b6, "أسئلة التفكير العليا", [P.f_higher_1, P.f_higher_2].filter(Boolean).join(" · "));
  line(b6, "قيمة الأسبوع", P.f_value);
}

function redrawGrid(){ shell(); }

/* ═════════ خطةُ زيارات المشرف/الزائر ═════════
   ⚠️ المشرفُ لا يبقى في مجمعٍ واحد: دورانُ الفرق ينقله كل يومٍ إلى مجمعٍ آخر.
   فالخطةُ تُبنى من SUP (أين يزور فريقُه) ثم تُجمع حصصُ تخصصه في ذلك المجمع
   مرتَّبةً بترتيب الحصص — وهو ترتيبُ يومه فعلاً: ابتدائيةٌ ثم متوسطةٌ ثم ثانوية. */
function groupOfSpec(sp, sector){
  /* في العالمي تعود موادُّ الهوية الثلاثُ إلى فريقها لا إلى الفرق الدائرة */
  if(sector === "عالمي" && isNatSpec(sp)) return D.natgroup;
  let g = "";
  Object.keys(D.pairs).forEach(k=>{ if(k !== D.natgroup && (D.pairs[k]||[]).indexOf(sp) >= 0) g = k; });
  return g;
}
/* ⛔ زياراتُ صاحب السجلّ: لكل يومٍ ما تطلبه **مواده هو** في مجمعاته — وقد
   تطلبه مجمعان في يومٍ واحدٍ وهو لا يكون إلا في واحد، فيُعلَن التعارضُ ولا
   يُخفى. (سجلُّ الإشراف ٣٠ سبتمبر ٢٠٢٦) */
function supVisits(r, week, day){
  const out = [];
  (r.sectors || []).forEach(sec=>{
    (r.complexes || []).forEach(cx=>{
      if(((D.complexes || {})[sec] || []).indexOf(cx) < 0) return;
      const nat = (D.natspecs || []);
      const mine = sp => !!r.allsubj || (r.subjects || []).indexOf(sp) >= 0;
      let specs = [];
      /* في العالمي لموادِّ الهوية رحلتُها الثابتة لا الدوران */
      if(sec === "عالمي" && (D.natdays || {})[day] === cx)
        specs = nat.filter(mine);
      const gp = (((D.rot || {})[cx] || {})[week] || {})[day] || "";
      specs = specs.concat(((D.pairs || {})[gp] || []).filter(sp=>{
        if(sec === "عالمي" && nat.indexOf(sp) >= 0) return false;
        return mine(sp);
      }));
      if(specs.length) out.push({sector: sec, cx: cx, specs: specs});
    });
  });
  return out;
}
function supPlan(m, c, r){
  const card = el("div","card"), h = el("h3");
  h.appendChild(el("span",null,"خطة الزيارات"));
  h.appendChild(el("small",null, r.name + " — "
    + (r.allsubj ? TR("إشرافٌ بالمرحلة") : r.subjects.map(TR).join(" · "))));
  card.appendChild(h);
  const tp = el("div","pad"), fb = el("div","filt");
  const wk = fld("sel", c.vwk || currentWeek() || D.weeks[0],
                 v=>{ setctx("vwk", v); shell(); }, D.weeks, "الأسبوع");
  wk.setAttribute("aria-label","الأسبوع"); fb.appendChild(wk);
  const pr = el("button","b ghost sm","اطبع الخطة");
  pr.addEventListener("click", ()=>window.print()); fb.appendChild(pr);
  tp.appendChild(fb); card.appendChild(tp); m.appendChild(card);

  const week = c.vwk || currentWeek() || D.weeks[0], cal = calOf(week);
  let total = 0, ready = 0, clash = 0;
  const wrap = el("div","card"), wh = el("h3");
  wh.appendChild(el("span",null, week));
  wh.appendChild(el("small",null, cal ? cal.range + " · " + cal.hrange : ""));
  wrap.appendChild(wh);
  const body = el("div","pad");
  D.days.forEach(day=>{
    const vs = supVisits(r, week, day);
    if(!vs.length) return;
    /* ⛔ **التعارضُ يُقاس على المسجَّل لا على الدوران**: الدورانُ قد يطلبه في
       مجمعين ولا حصةَ في أحدهما — فلا تعارضَ حينئذٍ. ولو حُذِّر على الطلب
       وحدَه لصارت أربعةُ أيامٍ «متعارضة» وهي خاليةٌ، فيُهمَل التحذيرُ كلُّه.
       فتُجمع الصفوفُ أولاً، ثم يُحذَّر إن حملت الحصصُ مجمعين في يومٍ واحد. */
    const packs = vs.map(v=>{
      const rows = [];
      v.specs.forEach(spec=>{
        bandsOf(v.cx).forEach(b=>{
          if((r.stages || []).indexOf(stageBase(b.stage)) < 0) return;
          const L = findLesson([v.sector, v.cx, b.stage, b.per, week, day, spec].join("|"));
          if(!L || !(L.teacher||"").trim()) return;
          const pg = prog(L);
          total++; if(pg.issued) ready++;
          rows.push([L.time || b.time || "—", b.stage, b.per, spec, L.teacher, L.klass || "—",
                     [L.strategy, L.approach].filter(Boolean).join(" · ") || "—",
                     {tag: pg.issued ? "حُضِّر" : "لم يُحضَّر", cls: pg.issued ? "ok" : "no"},
                     {btn: "افتح", id: L.id}]);
        });
      });
      return {v: v, rows: rows};
    });
    const busy = packs.filter(x=>x.rows.length);
    if(busy.length > 1){
      clash++;
      body.appendChild(el("div","msg bad", TR("تعارض: ") + TR(day) + TR(" — موادُّك في ")
        + busy.map(x=>TR(x.v.cx)).join(TR(" و")) + TR(". والزيارةُ مجمعٌ واحدٌ في اليوم، ")
        + TR("فاختر واحداً ونقِّل الباقي إلى أسبوعٍ آخر مع الوكيل.")));
    }
    packs.forEach(x=>{
      const v = x.v, dt = cal ? (cal.days[day] || {}) : {};
      const dh = el("div","vday");
      dh.appendChild(el("b",null, TR(day) + TR(" — مجمع ") + TR(v.cx)
                       + (D.sectors.length > 1 ? " · " + TR(v.sector) : "")));
      dh.appendChild(el("i",null, [dt.gt, dt.ht].filter(Boolean).join(" · ")));
      body.appendChild(dh);
      if(!x.rows.length){
        body.appendChild(el("div","vempty",
          "لا حصصَ مسجَّلةً لموادك في هذا المجمع بعد — راجع مسؤول الجدولة."));
        return;
      }
      vtable(body, x.rows);
    });
  });
  wrap.appendChild(body);
  const kp = el("div","pad");
  kpis(kp, [[arn(total),"حصة في خطتك"], [arn(ready),"جاهزةٌ بتحضيرٍ مُصدَر"],
            [arn(total-ready),"تنتظر تحضيرها"], [arn(clash),"يومٌ فيه تعارض"]]);
  wrap.insertBefore(kp, body);
  m.appendChild(wrap);
  const n = el("div","card"), np = el("div","pad note");
  np.appendChild(el("div",null,
    "الترتيبُ هو ترتيبُ يومك فعلاً: تبدأ بالابتدائية ثم المتوسطة ثم الثانوية بحسب أوقات الحصص. "
    + "و«افتح» تعرض ورقةَ تنفيذ الحصة — اقرأها قبل دخولك فهي ما تبحث عن شواهده."));
  n.appendChild(np); m.appendChild(n);
}
function vtable(body, rows){
  const t = el("table"), hr = el("tr");
  ["وقت البدء","المدرسة","الحصة","التخصص",D.lab_teacher_short,"الفصل",
   "الإستراتيجية والاتجاه","التحضير",""].forEach(x=>hr.appendChild(el("th",null,x)));
  t.appendChild(hr);
  rows.forEach(r=>{
    const tr = el("tr");
    r.forEach(cell=>{
      const td = el("td");
      if(cell && cell.tag) td.appendChild(el("span","tag "+cell.cls, cell.tag));
      else if(cell && cell.btn){
        const b = el("button","b alt", cell.btn);
        b.style.cssText = "padding:4px 12px;font-size:14px";
        b.addEventListener("click", ()=>{ CUR = cell.id; PH = 6; shell(); });
        td.appendChild(b);
      } else td.textContent = TR(cell);
      tr.appendChild(td);
    });
    t.appendChild(tr);
  });
  body.appendChild(t);
}
function visitPlan(m, c){
  /* ⛔ المشرفُ المسجَّلُ خطتُه من سجلّه. ومن ليس فيه (كالزائر) يبقى على الفريق. */
  const _r = ME && ME.role === "supervisor" ? supByEmp(ME.emp) : null;
  if(_r) return supPlan(m, c, _r);
  const myGp = groupOfSpec(c.spec, c.sector);
  const card = el("div","card"), h = el("h3");
  h.appendChild(el("span",null,"خطة الزيارات"));
  h.appendChild(el("small",null, myGp
    ? (TR("فريق ") + TR(myGp) + (myGp === D.natgroup ? " — " + TR(D.natsup) : ""))
    : "اختر تخصصك لتظهر خطتك"));
  card.appendChild(h);
  const tp = el("div","pad"), fb = el("div","filt");
  const sp = fld("sel", c.spec, v=>{ setctx("spec", v); shell(); }, D.specs, "التخصص");
  sp.setAttribute("aria-label","تخصصك"); fb.appendChild(sp);
  const wk = fld("sel", c.vwk || currentWeek() || D.weeks[0],
                 v=>{ setctx("vwk", v); shell(); }, D.weeks, "الأسبوع");
  wk.setAttribute("aria-label","الأسبوع"); fb.appendChild(wk);
  const pr = el("button","b ghost sm","اطبع الخطة");
  pr.addEventListener("click", ()=>window.print()); fb.appendChild(pr);
  tp.appendChild(fb); card.appendChild(tp); m.appendChild(card);
  if(!myGp){
    const w = el("div","card"), p2 = el("div","pad");
    p2.appendChild(el("div","empty","اختر تخصصك أعلاه لتُبنى خطةُ زياراتك."));
    w.appendChild(p2); m.appendChild(w); return;
  }
  const week = c.vwk || currentWeek() || D.weeks[0];
  const cal = calOf(week);
  let total = 0, ready = 0;
  const wrap = el("div","card");
  const wh = el("h3");
  wh.appendChild(el("span",null, week));
  wh.appendChild(el("small",null, cal ? cal.range + " · " + cal.hrange : "")); wrap.appendChild(wh);
  const body = el("div","pad");
  D.days.forEach(day=>{
    const cx = myGp === D.natgroup ? (D.natdays||{})[day] : ((D.sup[myGp]||{})[week]||{})[day];
    if(!cx) return;
    const dt = cal ? (cal.days[day]||{}) : {};
    const dh = el("div","vday");
    dh.appendChild(el("b",null, TR(day) + TR(" — مجمع ") + TR(cx)));
    dh.appendChild(el("i",null, [dt.gt, dt.ht].filter(Boolean).join(" · ")));
    body.appendChild(dh);
    const bands = bandsOf(cx);
    const rows = [];
    (D.pairs[myGp]||[]).forEach(spec=>{
      bands.forEach(b=>{
        const L = findLesson([c.sector, cx, b.stage, b.per, week, day, spec].join("|"));
        if(!L || !(L.teacher||"").trim()) return;
        const pg = prog(L);
        total++; if(pg.issued) ready++;
        rows.push([L.time || b.time || "—", b.stage, b.per, spec, L.teacher, L.klass || "—",
                   [L.strategy, L.approach].filter(Boolean).join(" · ") || "—",
                   {tag: pg.issued ? "حُضِّر" : "لم يُحضَّر", cls: pg.issued ? "ok" : "no"},
                   {btn: "افتح", id: L.id}]);
      });
    });
    if(!rows.length){
      body.appendChild(el("div","vempty","لا حصصَ مسجَّلةً لتخصصك في هذا المجمع بعد — راجع مسؤول الجدولة."));
      return;
    }
    const t = el("table");
    const hr = el("tr");
    ["وقت البدء","المدرسة","الحصة","التخصص",D.lab_teacher_short,"الفصل","الإستراتيجية والاتجاه","التحضير",""]
      .forEach(x=>hr.appendChild(el("th",null,x)));
    t.appendChild(hr);
    rows.forEach(r=>{
      const tr = el("tr");
      r.forEach(cell=>{
        const td = el("td");
        if(cell && cell.tag) td.appendChild(el("span","tag "+cell.cls, cell.tag));
        else if(cell && cell.btn){
          const b = el("button","b alt", cell.btn);
          b.style.cssText = "padding:4px 12px;font-size:14px";
          b.addEventListener("click", ()=>{ CUR = cell.id; PH = 6; shell(); });
          td.appendChild(b);
        } else td.textContent = TR(cell);
        tr.appendChild(td);
      });
      t.appendChild(tr);
    });
    body.appendChild(t);
  });
  wrap.appendChild(body);
  const kp = el("div","pad");
  kpis(kp, [[arn(total),"حصة في خطتك"], [arn(ready),"جاهزةٌ بتحضيرٍ مُصدَر"],
            [arn(total-ready),"تنتظر تحضيرها"]]);
  wrap.insertBefore(kp, body);
  m.appendChild(wrap);
  const n = el("div","card"), np = el("div","pad note");
  np.appendChild(el("div",null,
    "الترتيبُ هو ترتيبُ يومك فعلاً: تبدأ بالابتدائية ثم المتوسطة ثم الثانوية بحسب أوقات الحصص. "
    + "و«افتح» تعرض ورقةَ تنفيذ الحصة — اقرأها قبل دخولك فهي ما تبحث عن شواهده."));
  n.appendChild(np); m.appendChild(n);
}

/* تلوينُ صفّ المؤشر بحسب ما رُصد فيه */
function markRow(r, val){
  if(!r || !r.classList) return;
  r.classList.remove("m4","m3","m2","m1","mna");
  if(val === "na") r.classList.add("mna");
  else if(val === "4") r.classList.add("m4");
  else if(val === "3") r.classList.add("m3");
  else if(val === "2") r.classList.add("m2");
  else if(val === "1") r.classList.add("m1");
}

/* تحديثُ خانات أزمنة المراحل في مكانها — بلا إعادة بناءٍ تُفقد التركيز */
function syncStageInputs(P){
  document.querySelectorAll("[data-stt]").forEach(e=>{
    const v = P["st_" + e.dataset.stt + "_time"] || "";
    if(e.value !== v) e.value = v;
  });
}

/* ═════════ عرضُ سلّة المحذوفات ═════════ */
function trashView(m, c){
  /* ⛔ **السلّةُ كانت تعرض للمقيّم محذوفاتِ المنظومة كلِّها** — ومعها «محوٌ
     نهائيٌّ» بلا استرداد. فوكيلُ مدرسةٍ يمحو إلى الأبد ما حذفته مدرسةٌ أخرى.
     فصار الترشيحُ في `trashList()` وحدَها، وهذه تقرأ المرشَّح. */
  const list = trashList();
  const card = el("div","card"), h = el("h3");
  h.appendChild(el("span",null,"سلّة المحذوفات"));
  h.appendChild(el("small",null,"يُحفظ المحذوفُ ثلاثين يوماً ثم يُمحى نهائياً"));
  card.appendChild(h);
  const p = el("div","pad");
  if(!list.length){
    p.appendChild(el("div","empty","لا محذوفات — وما يُحذف يظهر هنا ويُستردّ بنقرة."));
  } else {
    const t = el("table"), tr = el("tr");
    ["الحصة","الموعد","المدرسة","ما حُذف معها","من حذفها","متى",""]
      .forEach(x=>tr.appendChild(el("th",null,x)));
    t.appendChild(tr);
    list.forEach(e=>{
      const L = e.L, r = el("tr");
      r.appendChild(el("td",null, [L.teacher, L.klass, L.spec].filter(Boolean).join(" · ") || "—"));
      r.appendChild(el("td",null, [L.week, L.day, L.period, L.time].filter(Boolean).join(" · ")));
      r.appendChild(el("td",null, [L.stage, L.complex].filter(Boolean).join(" · ")));
      const what = [];
      if(e.prep && e.prep.__issued) what.push("تحضيرٌ مُصدَر");
      else if(e.prep) what.push("تحضيرٌ غيرُ مُصدَر");
      const no = Object.keys(e.obs||{}).length, np = Object.keys(e.peer||{}).length;
      if(no) what.push("رصد " + arn(no));
      if(np) what.push("أقران " + arn(np));
      r.appendChild(el("td",null, what.join(" · ") || "—"));
      r.appendChild(el("td",null, e.by || "—"));
      const d = new Date(e.at || Date.now());
      const days = Math.floor((Date.now() - d.getTime())/86400000);
      r.appendChild(el("td",null, days <= 0 ? "اليوم" : "قبل " + arn(days) + " يوماً"));
      const ac = el("td","nowrap");
      if(canRestore(L)){
        const rb = el("button","b alt","استرداد");
        rb.style.cssText = "padding:5px 14px;font-size:14px";
        rb.addEventListener("click", ()=>{ if(restoreLesson(L.id)){ setctx("tab","fill"); shell(); } });
        ac.appendChild(rb);
      } else ac.appendChild(el("span","tag","للاطّلاع"));
      if(canPurge(L)){
        const xb = el("button","b warn","محوٌ نهائي");
        xb.style.cssText = "padding:5px 10px;font-size:14px;margin-inline-start:6px";
        xb.addEventListener("click", ()=>{
          /* ⚠️ والحارسُ في `purgeLesson` نفسِها — ونطاقُ السلّة وحدَه لا يكفي:
             من بلغه مفتاحُ حصةٍ خارجَ نطاقه محاها بلا رجعة. */
          uiAsk("محوٌ نهائيٌّ لا يُستردُّ بعده. أتُتابع؟", "امحُها نهائياً", "bad").then(ok=>{
            if(ok && purgeLesson(L.id)) shell();
          });
        });
        ac.appendChild(xb);
      }
      r.appendChild(ac); t.appendChild(r);
    });
    p.appendChild(t);
  }
  card.appendChild(p); m.appendChild(card);
  const n = el("div","card"), np2 = el("div","pad note");
  np2.appendChild(el("div",null,
    "الاستردادُ يعيد الحصةَ وتحضيرَها ورصدَها وبطاقاتِ أقرانها معاً. "
    + "ويمتنع إن كانت خانتُها قد شُغِلت بحصةٍ أخرى بعد الحذف."));
  n.appendChild(np2); m.appendChild(n);
}

/* ═════════ إسنادُ المعلمين الزائرين — للوكيل التعليمي ═════════
   ⛔ طلبَه المستشارُ ٢٩ سبتمبر ٢٠٢٦: «لا تنسى إسناد الحصص المعدة للحضور بواسطة
      الوكيل التعليمي للمعلمين الزائرين حتى تظهر في حساباتهم».
   ⚠️ والإسنادُ **بالرقم الوظيفي** لا بالاسم: الأسماءُ تتشابه وتُكتب بصيغٍ شتّى
      فيرى معلمٌ زيارةَ آخر. ويُحفظ الاسمُ معه ليُقرأ، والمطابقةُ على الرقم.
      (حقول: peer1/peer2 للاسم — كما كانت — وpeer1e/peer2e للرقم.) */
function assignView(m, c){
  const card = el("div","card"), h = el("h3");
  h.appendChild(el("span",null,"إسناد المعلمين الزائرين"));
  h.appendChild(el("small",null,
    "لكل حصةٍ زائران — يُسنَدان بالرقم الوظيفي فتظهر الحصةُ في حسابَيهما"));
  card.appendChild(h);
  const tp = el("div","pad"), fb = el("div","filt");
  const wk = fld("sel", c.onlyw || "كل الأسابيع",
                 v=>{ setctx("onlyw", v === "كل الأسابيع" ? "" : v); shell(); },
                 ["كل الأسابيع"].concat(D.weeks), "الأسبوع");
  wk.setAttribute("aria-label","الأسبوع"); fb.appendChild(wk);
  const dy = fld("sel", c.vday || "كل الأيام",
                 v=>{ setctx("vday", v === "كل الأيام" ? "" : v); shell(); },
                 ["كل الأيام"].concat(D.days), "اليوم");
  dy.setAttribute("aria-label","اليوم"); fb.appendChild(dy);
  const on = el("label","tk"), cb = el("input"); cb.type = "checkbox";
  cb.checked = !!c.asgOnly;
  cb.addEventListener("change", ()=>{ setctx("asgOnly", cb.checked); shell(); });
  on.appendChild(cb); on.appendChild(el("span",null,"ما لم يُسنَد بعد"));
  fb.appendChild(on);
  tp.appendChild(fb); card.appendChild(tp); m.appendChild(card);

  /* حصصُ مدرسته وحدها — لا المجمع كلُّه */
  let here = DB.sched.filter(L=> L.complex === ME.complex
      && (!ME.school || L.stage === ME.school));
  if(c.onlyw) here = here.filter(L=>L.week === c.onlyw);
  if(c.vday)  here = here.filter(L=>L.day === c.vday);
  here = here.filter(L=>(L.teacher||"").trim());
  if(c.asgOnly) here = here.filter(L=>!(L.peer1e||L.peer1||L.peer2e||L.peer2));
  const box = el("div","card"), bh = el("h3");
  bh.appendChild(el("span",null, ME.school || ME.complex));
  bh.appendChild(el("small",null, arn(here.length) + " حصةً مجدولةً باسم معلمٍ"));
  box.appendChild(bh);
  const bp = el("div","pad");
  if(!here.length){
    bp.appendChild(el("div","empty",
      "لا حصةَ تطابق الترشيح — وتُسنَد الزياراتُ بعد أن يُكتب اسمُ المعلم في خانتها."));
    box.appendChild(bp); m.appendChild(box); return;
  }
  const t = el("table"), tr = el("tr");
  ["الموعد","الحصة والمدرسة","المعلم","التخصص","الزائر ١","الزائر ٢"]
    .forEach(x=>tr.appendChild(el("th",null,x)));
  t.appendChild(tr);
  /* ═════════ مرشَّحو الزيارة ═════════
     ⛔ شرطان من قرار الاجتماع (٣٠ سبتمبر ٢٠٢٦):
        ١. من التخصص نفسِه أو التخصصات القريبة (مجموعةُ التخصص في `pairs`).
        ٢. **ولا حصةَ له في وقت الحصة نفسِه** — وإلا أُسنِدت إليه زيارةٌ
           يستحيل حضورُها، ولا يُكتشف ذلك إلا يومَ الزيارة.
     ⚠️ والتعارضُ يُقاس على الأسبوع واليوم والحصة معاً لا على الحصة وحدها. */
  const nearSpecs = (sp)=>{
    const out = [sp];
    Object.keys(D.pairs || {}).forEach(g=>{
      if((D.pairs[g] || []).indexOf(sp) >= 0)
        (D.pairs[g] || []).forEach(x=>{ if(out.indexOf(x) < 0) out.push(x); });
    });
    return out;
  };
  const busyAt = (empNo, name, L)=>DB.sched.some(x=>
       x.id !== L.id && x.week === L.week && x.day === L.day
    && String(x.period) === String(L.period)
    && (((empNo && (x.teacherNo||"").trim() === empNo))
        || (!(x.teacherNo||"").trim() && name && (x.teacher||"").trim() === name)
        || (empNo && [(x.peer1e||"").trim(), (x.peer2e||"").trim()].indexOf(empNo) >= 0)));
  const candidates = (L, otherNo)=>{
    const want = nearSpecs(L.spec || L.subject || "");
    const R = D.roster || {}, out = [];
    Object.keys(R).forEach(k=>{
      const r = R[k] || {};
      const sp = (D.specmap || {})[r.s] || r.s || "";
      if(want.indexOf(sp) < 0) return;                    /* تخصصٌ بعيد */
      if(k === (L.teacherNo || "")) return;               /* صاحبُ الحصة */
      if((r.n || "") === (L.teacher || "")) return;
      if(k === otherNo) return;                           /* الزائرُ الآخر */
      if(busyAt(k, r.n, L)) return;                       /* عنده حصةٌ حينها */
      out.push({no: k, n: r.n || k, sp: sp, same: sp === (L.spec || L.subject)});
    });
    /* نفسُ التخصص أولاً ثم القريب، وكلٌّ بالاسم */
    const coll = new Intl.Collator("ar");
    return out.sort((a, b)=> (a.same === b.same)
      ? coll.compare(a.n, b.n) : (a.same ? -1 : 1));
  };

  /* خانةُ رقمٍ تُظهر الاسمَ من الكشف وتحفظ الاثنين */
  const slot = (L, i)=>{
    const ke = "peer" + i + "e", kn = "peer" + i;
    const td = el("td","nar"), box2 = el("div");
    /* ⛔ قائمةُ مرشَّحين بدل رقمٍ حرّ: الرقمُ الحرُّ يقبل معلمَ مادةٍ بعيدةٍ
       أو معلماً عنده حصةٌ في الوقت نفسِه — ولا يُكتشف إلا يومَ الزيارة. */
    const other = (L["peer" + (i === 1 ? 2 : 1) + "e"] || "").trim();
    const cand = candidates(L, other);
    if((D.roster && Object.keys(D.roster).length)){
      const names = cand.map(x=>x.n + " — " + x.sp + " (" + x.no + ")");
      const curName = L[ke] && D.roster[L[ke]]
        ? (D.roster[L[ke]].n + " — " + ((D.specmap||{})[D.roster[L[ke]].s] || D.roster[L[ke]].s || "")
           + " (" + L[ke] + ")") : "";
      /* ⚠️ المُسنَدُ سابقاً يبقى معروضاً وإن صار مشغولاً — وإلا اختفى صامتاً */
      const opts = curName && names.indexOf(curName) < 0 ? [curName].concat(names) : names;
      const sel = fld("sel", curName, v=>{
        const mm = String(v).match(/\((\d+)\)\s*$/);
        const k = mm ? mm[1] : "";
        L[ke] = k; L[kn] = k && D.roster[k] ? D.roster[k].n : "";
        save();
        logAct("إسناد زائر", (L[kn] || "—") + " ← " + lessonTitle(L), L);
        syncFlush(); shell();
      }, opts, "الزائر " + arn(i));
      sel.className = "cin";
      box2.appendChild(sel);
      if(!cand.length)
        box2.appendChild(el("div","whois no","لا مرشَّحَ من تخصصه متفرِّغٌ في هذا الوقت"));
      else box2.appendChild(el("div","whois", arn(cand.length) + " مرشَّحاً متفرِّغاً"));
      td.appendChild(box2); return td;
    }
    const inp = el("input"); inp.type = "text"; inp.inputMode = "numeric";
    inp.value = L[ke] || ""; inp.placeholder = "الرقم الوظيفي";
    inp.setAttribute("aria-label", "الرقم الوظيفي للزائر " + arn(i));
    const who = el("div","whois");
    const paint = ()=>{
      const k = latnum(inp.value);
      const r = D.roster[k];
      if(!k){ who.className = "whois"; who.textContent = TR(L[kn] || ""); return; }
      if(r){ who.className = "whois ok"; who.textContent = TR(r.n); }
      else  { who.className = "whois no"; who.textContent = TR("لا يطابق رقماً في الكشف"); }
    };
    inp.addEventListener("input", paint);
    inp.addEventListener("change", ()=>{
      const k = latnum(inp.value);
      const r = D.roster[k];
      L[ke] = k;
      L[kn] = r ? r.n : (k ? L[kn] || "" : "");
      save();
      logAct("إسناد زائر", (r ? r.n : k || "—") + " ← " + lessonTitle(L), L);
      paint();
    });
    paint();
    box2.appendChild(inp); box2.appendChild(who); td.appendChild(box2);
    return td;
  };
  here.forEach(L=>{
    const r = el("tr");
    r.appendChild(el("td",null,[L.week, L.day, L.time].filter(Boolean).join(" · ")));
    r.appendChild(el("td",null,[L.period, L.stage].filter(Boolean).join(" · ")));
    r.appendChild(el("td",null, L.teacher || "—"));
    r.appendChild(el("td",null, L.spec || "—"));
    r.appendChild(slot(L, 1));
    r.appendChild(slot(L, 2));
    t.appendChild(r);
  });
  bp.appendChild(t); box.appendChild(bp); m.appendChild(box);
}

/* ═════════ عرضُ سجلّ العمليات — للمقيّم ═════════ */
function logView(m, c){
  const all = logList();
  const card = el("div","card"), h = el("h3");
  h.appendChild(el("span",null,"سجلّ العمليات"));
  h.appendChild(el("small",null, arn(all.length) + " عملية · تُحفظ آخرُ " + arn(LOG_MAX)));
  card.appendChild(h);
  const tp = el("div","pad"), fb = el("div","filt");
  const who = [...new Set(all.map(x=>x.by).filter(Boolean))];
  const f1 = fld("sel", c.lgby||"", v=>{ setctx("lgby", v); shell(); }, ["الجميع"].concat(who), "الشخص");
  f1.setAttribute("aria-label","ترشيحٌ بالشخص"); fb.appendChild(f1);
  const acts = [...new Set(all.map(x=>x.a).filter(Boolean))];
  const f2 = fld("sel", c.lgact||"", v=>{ setctx("lgact", v); shell(); }, ["كل العمليات"].concat(acts), "نوع العملية");
  f2.setAttribute("aria-label","ترشيحٌ بنوع العملية"); fb.appendChild(f2);
  const pr = el("button","b ghost sm","طباعة السجل");
  pr.addEventListener("click", ()=>window.print()); fb.appendChild(pr);
  tp.appendChild(fb); card.appendChild(tp); m.appendChild(card);

  let list = all;
  if(c.lgby && c.lgby !== "الجميع") list = list.filter(x=>x.by === c.lgby);
  if(c.lgact && c.lgact !== "كل العمليات") list = list.filter(x=>x.a === c.lgact);
  const w = el("div","card"), p = el("div","pad");
  if(!list.length) p.appendChild(el("div","empty","لا عمليات مطابقة."));
  else {
    const t = el("table"), tr = el("tr");
    ["متى","من","الصفة","العملية","التفصيل"].forEach(x=>tr.appendChild(el("th",null,x)));
    t.appendChild(tr);
    list.slice(0, 300).forEach(e=>{
      const r = el("tr");
      r.appendChild(el("td",null, agoTxt(e.t)));
      r.appendChild(el("td",null, e.by || "—"));
      r.appendChild(el("td",null, roleName(e.r)));
      const ac = el("td");
      const cls = e.a === "حذف" ? "no" : (e.a === "استرداد" || e.a === "إصدار التحضير" ? "ok" : "mid");
      ac.appendChild(el("span","tag " + cls, e.a || "—"));
      r.appendChild(ac);
      r.appendChild(el("td",null, e.w || "—"));
      t.appendChild(r);
    });
    p.appendChild(t);
    if(list.length > 300)
      p.appendChild(el("div","note","عُرضت أحدثُ ٣٠٠ عملية من " + arn(list.length) + "."));
  }
  w.appendChild(p); m.appendChild(w);
  const n = el("div","card"), np = el("div","pad note");
  np.appendChild(el("div",null,
    "يُسجَّل ما يغيّر الحقيقة: تسجيلُ حصةٍ وتعديلُ حقلٍ وحذفٌ واستردادٌ وإصدارُ تحضيرٍ "
    + "وبدءُ رصدٍ وبطاقةُ أقرانٍ وتغييرُ دوران — ولا تُسجَّل القراءةُ ولا التنقّل."));
  n.appendChild(np); m.appendChild(n);
}

/* ═════════ تقريرُ المعلم عن نفسه ═════════ */
function myTeacherReport(m){
  const mine = DB.sched.filter(L=>
    (ME.emp && L.teacherNo === ME.emp) || (L.teacher||"").trim() === (ME.name||"").trim());
  const A = agg().filter(x=>mine.some(L=>L.id === x.L.id));
  const pcts = A.filter(x=>x.pct != null).map(x=>x.pct);
  const card = el("div","card"), h = el("h3");
  h.appendChild(el("span",null,"تقريري — " + ME.name));
  h.appendChild(el("small",null, ME.emp ? "الرقم الوظيفي " + ME.emp : ""));
  card.appendChild(h);
  const p = el("div","pad");
  kpis(p, [[arn(mine.length),"حصةً لك"],
           [arn(A.filter(x=>x.issued).length),"حضّرتَها وأصدرتَها"],
           [arn(A.filter(x=>x.obs.length).length),"رُصدت"],
           [num(avg(pcts)) + "٪","متوسط نسبتك"]]);
  card.appendChild(p); m.appendChild(card);
  const w = el("div","card"), wh = el("h3");
  wh.appendChild(el("span",null,"حصصك")); w.appendChild(wh);
  const wp = el("div","pad");
  if(!mine.length){
    /* ⛔ تقريرٌ بلا حصصٍ كان ثلاثةَ أصفارٍ وسطراً ميّتاً — لا يقول للمعلم
       أين يبدأ. (مسحُ المنظومة ٣٠ سبتمبر ٢٠٢٦) */
    wp.appendChild(el("div","msg warn",
      "لا حصةَ باسمك في الجدول بعد، فلا تقريرَ لك. وتقريرُك يُبنى وحدَه متى "
      + "سجّلتَ حصتك في الجدول وأصدرتَ تحضيرَها ورصدها المشرف."));
    const bar = el("div","bar");
    const g1 = el("button","b","اذهب إلى الجدول وسجّل حصتك");
    g1.addEventListener("click", ()=>{ PH = 1; setctx("tab","fill"); shell(); });
    bar.appendChild(g1);
    const g2 = el("button","b ghost","افتح صفحة التحضير");
    g2.addEventListener("click", ()=>{ PH = 2; shell(); });
    bar.appendChild(g2);
    wp.appendChild(bar);
    wp.appendChild(el("div","note")).appendChild(el("div",null,
      "تدخل باسم: " + (ME.name || "—")
      + (ME.emp ? " · الرقم الوظيفي " + arn(ME.emp) : "")
      + " — واكتبه في خلية الجدول كما هو."));
  } else {
    const t = el("table"), tr = el("tr");
    ["الموعد","المدرسة والحصة","الإستراتيجية","التحضير","الرصد","نسبتك","المستوى","إجراء الجسر",""]
      .forEach(x=>tr.appendChild(el("th",null,x)));
    t.appendChild(tr);
    A.forEach(x=>{
      const L = x.L, r = el("tr");
      r.appendChild(el("td",null,[L.week,L.day,L.time].filter(Boolean).join(" · ")));
      r.appendChild(el("td",null,[L.stage,L.period].filter(Boolean).join(" · ")));
      r.appendChild(el("td",null,[L.strategy,L.approach].filter(Boolean).join(" · ")||"—"));
      const a = el("td");
      a.appendChild(el("span","tag "+(x.issued?"ok":"no"), x.issued?"صدر":"لم يصدر"));
      if(L.approved) a.appendChild(el("span","tag ok"," معتمدة ◆"));
      r.appendChild(a);
      r.appendChild(el("td",null, arn(x.obs.length) + "/٣"));
      r.appendChild(el("td",null, x.pct==null ? "—" : num(x.pct)+"٪"));
      r.appendChild(el("td",null, lvlOf(x.pct)));
      r.appendChild(el("td",null, x.bridge || "—"));
      const ac = el("td");
      const go = el("button","b alt","افتح"); go.style.cssText="padding:4px 12px;font-size:14px";
      go.addEventListener("click", ()=>{ CUR = L.id; PH = x.issued ? 6 : 2; shell(); });
      ac.appendChild(go); r.appendChild(ac);
      t.appendChild(r);
    });
    wp.appendChild(t);
  }
  w.appendChild(wp); m.appendChild(w);
  /* أضعفُ مؤشراتك — من رصد المقيّمين */
  const acc = {};
  A.forEach(x=>x.obs.forEach(v=>{
    Object.entries(v.ind||{}).forEach(([k,val])=>{
      if(val === "na" || !val) return; (acc[k] = acc[k] || []).push(Number(val));
    });
  }));
  const ind = Object.entries(acc).map(([k,arr])=>{
    const [di,ii] = k.split("_").map(Number);
    const dm = D.domains[di] || {inds:[]};
    return [arn(di+1)+"·"+arn(ii+1), dm.inds[ii]||"—", avg(arr)];
  }).sort((a,b)=>a[2]-b[2]).slice(0,8);
  if(ind.length){
    const c2 = el("div","card"), h2 = el("h3");
    h2.appendChild(el("span",null,"أضعفُ مؤشراتك"));
    h2.appendChild(el("small",null,"ثمانيةٌ ترتيباً — ابدأ بها في حصتك القادمة")); c2.appendChild(h2);
    const p2 = el("div","pad");
    tbl(p2, ["الرمز","المؤشر","متوسطك من ٤"],
      ind.map(r=>[r[0], r[1], num(r[2])]));
    c2.appendChild(p2); m.appendChild(c2);
  }
  const bar = el("div","card"), bp = el("div","pad bar");
  const pr = el("button","b ghost","اطبع تقريري");
  pr.addEventListener("click", ()=>window.print()); bp.appendChild(pr);
  bar.appendChild(bp); m.appendChild(bar);
}

/* ═════════ سجلُّ زيارات الزائر ═════════ */
function myPeerReport(m){
  const me = (ME.name||"").trim();
  const asg = DB.sched.filter(isMyVisit);
  const done = Object.keys(DB.peer).filter(k=>k.split("|")[1] === me);
  const doneIds = new Set(done.map(k=>k.split("|")[0]));
  const card = el("div","card"), h = el("h3");
  h.appendChild(el("span",null,"سجلّ زياراتي — " + ME.name)); card.appendChild(h);
  const p = el("div","pad");
  kpis(p, [[arn(asg.length),"زيارةً مسنَدةً إليك"],
           [arn(asg.filter(L=>doneIds.has(L.id)).length),"أتممتَ بطاقتها"],
           [arn(asg.filter(L=>!doneIds.has(L.id)).length),"تنتظر بطاقتك"]]);
  card.appendChild(p); m.appendChild(card);
  const w = el("div","card"), wh = el("h3");
  wh.appendChild(el("span",null,"زياراتك")); w.appendChild(wh);
  const wp = el("div","pad");
  if(!asg.length){
    /* ⛔ «لا زيارات» وحدَها لا تقول لِمَ ولا متى — والزائرُ يُسنَد بالرقم
       الوظيفي، فلو كُتب رقمٌ غيرُ رقمه لم يرَ شيئاً ولم يعرف السبب. */
    wp.appendChild(el("div","msg warn",
      "لا زيارةَ مسنَدةً إليك بعد. والزياراتُ يُسنِدها الوكيلُ التعليمي من "
      + "شاشة «إسناد الزائرين» بالرقم الوظيفي — فإن لم تظهر زيارتُك فراجعه "
      + "وتأكّد أن رقمك المسجَّل هو الذي دخلتَ به."));
    wp.appendChild(el("div","note")).appendChild(el("div",null,
      "تدخل باسم: " + (ME.name || "—")
      + (ME.emp ? " · الرقم الوظيفي " + arn(ME.emp) : "")));
  } else {
    wp.appendChild(el("div","note")).appendChild(el("div",null,
      "لكل زيارة: اقرأ تحضير المعلم قبل دخولك — فهو ما تبحث عن شواهده — "
      + "ثم املأ بطاقة الأقران وانقل إجراءً واحداً لنفسك."));
    const t = el("table"), tr = el("tr");
    ["الموعد","المجمع والمدرسة","المعلم","التخصص","تحضيره","بطاقتك",""]
      .forEach(x=>tr.appendChild(el("th",null,x)));
    t.appendChild(tr);
    asg.forEach(L=>{
      const pg = prog(L), r = el("tr");
      r.appendChild(el("td",null,[L.week,L.day,L.time].filter(Boolean).join(" · ")));
      r.appendChild(el("td",null,[L.complex,L.stage].filter(Boolean).join(" · ")));
      r.appendChild(el("td",null, L.teacher || "—"));
      r.appendChild(el("td",null, L.spec || "—"));
      const a = el("td");
      a.appendChild(el("span","tag "+(pg.issued?"ok":"no"), pg.issued?"صدر":"لم يصدر"));
      r.appendChild(a);
      const b = el("td");
      const has = doneIds.has(L.id);
      b.appendChild(el("span","tag "+(has?"ok":"no"), has?"مكتملة":"لم تُملأ"));
      r.appendChild(b);
      const ac = el("td");
      const go = el("button","b alt", has ? "راجع" : "املأ");
      go.style.cssText="padding:4px 12px;font-size:14px";
      go.addEventListener("click", ()=>{ CUR = L.id; PH = 3; shell(); });
      ac.appendChild(go); r.appendChild(ac);
      t.appendChild(r);
    });
    wp.appendChild(t);
  }
  w.appendChild(wp); m.appendChild(w);
  const bar = el("div","card"), bp = el("div","pad bar");
  const pr = el("button","b ghost","اطبع سجلّي");
  pr.addEventListener("click", ()=>window.print()); bp.appendChild(pr);
  bar.appendChild(bp); m.appendChild(bar);
}

/* ═════════ تفريغُ البيانات — محروسٌ بثلاث بوّابات ═════════
   ⛔ لا يُفتح إلا للمقيّم · ويأخذ نسخةً احتياطيةً أولاً · ويطلب كلمةً مكتوبة.
      ويستعمل `__replace` لأن الدمجَ في الخادم يمنع المحوَ عمداً. */
function wipeAll(){
  if(!isAdmin()) return;          /* ⛔ بوّابةٌ رابعة: الدورُ نفسُه */
  const n = DB.sched.length, p = Object.keys(DB.prep).filter(k=>k.indexOf(TRASH)&&k.indexOf(LOG)).length;
  /* ⛔ ثلاثُ بوّاباتٍ متسلسلةٌ — ولا تُدمج: الأولى تُعلم بما يضيع، والثانية
     تطلب كلمةً تُكتب بيدٍ فلا تُضغط سهواً. (وغيرُ تزامنيةٍ الآن) */
  uiAsk("تفريغٌ كاملٌ لبيانات المنظومة على كل الأجهزة:\n\n"
    + "• " + arn(n) + " حصة\n• التحضيراتُ والرصدُ وبطاقاتُ الأقران\n"
    + "• سلّةُ المحذوفات وسجلُّ العمليات\n\nلا يُستردُّ شيءٌ بعده. أتُتابع؟",
    "أفهم — تابِع", "bad").then(ok=>{
    if(!ok) return;
    return uiPrompt("ستُحفظ نسخةٌ احتياطيةٌ على جهازك أولاً.\n\n"
      + "للتأكيد اكتب كلمة:  تفريغ", "", "تفريغ").then(w=>{
      if((w||"").trim() !== "تفريغ"){ alert("أُلغي التفريغ."); return; }
      wipeGo();
    });
  });
}
/* ⚠️ فُصل جسمُ التفريغ في دالّةٍ لأن التأكيدَ صار غيرَ تزامنيّ */
function wipeGo(){
  backup();                                    /* نسخةٌ قبل المحو */
  const empty = {sched:[], prep:{}, obs:{}, peer:{}, rot:{}};
  DB = empty; lastSent = ""; UNDO = [];
  try{ localStorage.setItem(KEY, JSON.stringify(DB)); }catch(e){}
  if(!api()){ alert("فُرّغت بيانات هذا الجهاز."); shell(); return; }
  fetch(api(), {method:"POST", headers:{"Content-Type":"text/plain;charset=utf-8"},
      body: apiBody({kind:"platform", id:SID, data:empty, __replace:true})})
    .then(r=>r.json())
    .then(r=>{
      if(r && r.ok && r.replaced){
        lastSent = dbSnapshot();
        logAct("تفريغ البيانات", "بدايةٌ نظيفةٌ بعد التجربة", null);
        save();
        alert("فُرّغت بيانات المنظومة على المخزن المشترك.\nوالنسخةُ الاحتياطيةُ على جهازك.");
      } else {
        alert("⛔ لم يستجب الخادمُ للاستبدال.\n\n"
              + (isAdmin() ? "خادمُك يعمل بشفرةٍ قديمةٍ لا تعرف الاستبدال — انشر النسخة الجديدة ثم أعد المحاولة."
                           : "راجع مديرَ التخطيط والاعتماد المدرسي لترقيته ثم أعد المحاولة."));
      }
      shell();
    })
    .catch(e=>{ alert("تعذّر الاتصال بالخادم: " + e.message); shell(); });
}
