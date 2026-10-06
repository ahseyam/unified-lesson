/* ═════════════════ استيرادُ تحضيرٍ جاهز ═════════════════
   ⛔ **العلّةُ المقيسة**: قبل «إصدار التحضير» يملأ المعلمُ ٣٣ خانةً إلزاميةً
      و٧ لخريطة الزمن و١٢ لمراحل الحصة — نحو ٥٢ إدخالاً. وهي شكوى المشرفة
      العامة في عرض المنصة (٣٠ سبتمبر ٢٠٢٦): «إجراءاتُ التحضير كثيرة».

   والحلُّ **لا يُنقص خانةً واحدة** — فكلُّ خانةٍ يقابلها مؤشرٌ في الاستمارة،
   وحذفُها حذفُ شاهد. وإنما يُنقل الكتابةُ إلى حيث يُحسنها المعلم: يكتب
   تحضيرَه خارجاً (بذكاءٍ اصطناعيٍّ أو بيده)، ثم يُدخله هنا دفعةً واحدة.

   طريقان، وكلاهما بلا خادمٍ ولا مفتاحٍ ولا تكلفة:
     ١. **أمرٌ جاهز** يُنسخ من المنصة وفيه بياناتُ الحصة وأسماءُ الحقول
        بصيغةٍ مفروضة، فيلصقه المعلمُ في أي مساعدٍ ويلصق الجوابَ هنا.
     ٢. **ملفُّ وورد** (.docx) يُقرأ في المتصفّح نفسِه.

   ⛔ ولا PDF: نصُّ العربية فيه يخرج مشوَّهاً (كافٌ فارسيةٌ وحروفٌ ملتصقة)،
      فتوزيعُه على الخانات يملؤها بخطأٍ لا يُكتشف. (قاعدةٌ مثبتةٌ من قبل.)

   ⚠️ ولا يُكتب فوق شيءٍ بلا إذن: يُعرض ما سيُملأ وما سيُستبدل، ويؤكّد
      المعلمُ، وتُؤخذ لقطةُ تراجعٍ قبل الكتابة.
*/

/* ── مفتاحُ كل حقلٍ في التخزين، مطابقاً لـpfield حرفاً بحرف ── */
/* ⚠️ و`root` أُضيف ليُعرف من أيِّ صفٍّ خرجت الخانةُ المُسطَّحة — به تُبنى
   توأمةُ الاستمارة والتحضير في شاشة الرصد. (١ أكتوبر ٢٠٢٦) */
function planFields(){
  const out = [];
  (D.sections || []).forEach(sec=>{
    (sec.rows || []).forEach(r=>{
      if(!r.k) return;
      const K = "f_" + r.k;
      if(r.t === "line" || r.t === "area" || r.t === "select")
        out.push({root: r.k, lab: r.label, base: r.label, kind: r.t, key: K, items: r.items || null});
      else if(r.t === "lines")
        for(let i = 1; i <= (r.n || 1); i++)
          out.push({root: r.k, lab: r.label + " (" + arn(i) + ")", base: r.label, idx: i,
                    kind: "line", key: K + "_" + i});
      else if(r.t === "ticks" || r.t === "ticks_note"){
        out.push({root: r.k, lab: r.label, base: r.label, kind: "ticks", key: K, items: r.items || []});
        if(r.t === "ticks_note")
          out.push({root: r.k, lab: r.label + " — " + (r.note || "كيف"), kind: "line", key: K + "_note"});
      }
      else if(r.t === "time")
        (D.tkeys || []).forEach(k=>{
          if(k === "total") return;          /* المجموعُ يُحسب لا يُملأ */
          out.push({root: r.k, lab: "الزمن — " + (D.tlabels || {})[k], kind: "num", key: "tk_" + k});
        });
      else if(r.t === "stages")
        (D.stages || []).forEach(([k, name])=>{
          out.push({root: r.k, lab: name + " — الزمن", kind: "num", key: "st_" + k + "_time"});
          out.push({root: r.k, lab: name + " — " + D.lab_t, kind: "area", key: "st_" + k + "_t"});
          out.push({root: r.k, lab: name + " — " + D.lab_l, kind: "area", key: "st_" + k + "_l"});
          (D.modes || []).forEach((grp, gi)=>
            out.push({root: r.k, lab: name + " — نمط العمل " + arn(gi + 1), kind: "ticks",
                      key: "st_" + k + "_m" + gi, items: grp}));
        });
    });
  });
  return out;
}

/* ── الأمرُ الجاهز ──
   ⛔ **الأمرُ يحمل الحصةَ بعينها لا عنواناً عامّاً** (طلبُ المستشار ٣٠ سبتمبر
      ٢٠٢٦): المادةُ والصفُّ وعنوانُ الدرس و**صفحاتُه في كتاب المنهج السعودي**،
      والإستراتيجيةُ المعلنةُ **بمؤشراتها العشرة** التي يرصدها الزائر، والاتجاهُ
      التدريسيُّ **بشواهده الثلاثة**، ونموذجُ التحضير بحقوله كلِّها، وقيودُ
      خريطة الزمن التي يحرسها الإصدار — **وطلبُ تصميم وسائلَ** تناسب
      الإستراتيجيةَ وما اختاره المعلم.
   ⚠️ والمفاتيحُ `i_topic` و`i_dur` لا `f_topic` و`f_dur`: بياناتُ الحصة في
      `D.info` مسبوقةٌ بـ`i_`، وكان الأمرُ يقرأ مفتاحين غيرَ موجودين فيخرج
      «(اكتب اسم الدرس هنا)» و«٤٥» دائماً. */
/*@noi18n*/
function planPrompt(L, P){
  const F = planFields();
  const g = k => ((P && P["i_" + k]) || "").toString().trim();
  const dur = g("dur") || "٤٥";
  const strat = (P && P.f_strat) || L.strategy || "";
  const appr = (P && P.f_dir) || L.approach || "";
  const bank = (D.bank || []).find(x=>x.name === strat);
  const ad = (D.apprdet || {})[appr];

  const head = [
    "أنت مساعدٌ خبيرٌ بالمناهج الدراسية السعودية وبالتخطيط للحصة الصفية.",
    "اكتب لي تحضيراً كاملاً لهذه الحصة بعينها، مبنيّاً على محتوى الكتاب المقرَّر.",
    "",
    "═══ بياناتُ الحصة ═══",
    "المادة: " + (g("subject") || L.subject || "—"),
    "الصف/الشعبة: " + (g("klass") || L.klass || "—"),
    "المرحلة والمدرسة: " + [L.stage, L.complex].filter(Boolean).join(" · "),
    "عنوان الدرس: " + (g("topic") || "(اكتب عنوان الدرس هنا)"),
    "رقم الدرس: " + (g("lesson_no") || "—"),
    "صفحاتُ الدرس في الكتاب: " + (g("pages") || "(اكتب أرقام الصفحات هنا)"),
    "زمن الحصة بالدقائق: " + dur,
    "عدد الطلاب: " + (g("count") || "—"),
    ""
  ];

  if(appr){
    head.push("═══ الاتجاه التدريسي المعلَن: " + appr + " ═══");
    if(ad && ad.what) head.push("تعريفُه: " + ad.what);
    if(ad && (ad.evid || []).length){
      head.push("وشواهدُه التي يبحث عنها الزائرُ في الحصة — فليُبنَ التحضيرُ عليها:");
      ad.evid.forEach((x,i2)=>head.push("  " + (i2+1) + ") " + x));
    }
    head.push("");
  }
  if(bank){
    head.push("═══ الإستراتيجية المعلَنة: " + bank.name + " ═══");
    head.push("وتُرصد بعشرة مؤشراتٍ في بطاقة تشخيصها — فليُحقّق التحضيرُ كلَّ واحدٍ منها:");
    bank.inds.forEach((x,i2)=>head.push("  " + (i2+1) + ") " + x));
    head.push("");
  }

  head.push("═══ وسائلُ الحصة (مطلوبٌ تصميمُها لا ذكرُها) ═══",
    "صمِّم لي وسائلَ وأدواتٍ تُستعمل في هذه الحصة بعينها، متوافقةً مع الإستراتيجية",
    "والاتجاه أعلاه ومع محتوى صفحات الكتاب المذكورة، واكتب كلَّ وسيلةٍ جاهزةً",
    "للاستعمال لا وصفاً لها: نصَّ بطاقةِ المهمة، وأسئلةَ ورقة العمل بإجاباتها،",
    "وجدولَ التقويم بمعاييره، وما يُعرض على الشاشة أو يُعلَّق في الصف.",
    "وضَعْ هذه الوسائلَ في حقول «مصادر التعلم» و«داعمات البيئة» و«أوراق العمل»",
    "وفي حقول مراحل الحصة، كلُّ وسيلةٍ في مرحلتها.",
    "");

  head.push("═══ قيودٌ لا يُقبل التحضيرُ بدونها ═══",
    "١) مجموعُ أزمنة (التهيئة + التنفيذ + التقويم + الغلق) = " + dur + " دقيقةً بالضبط.",
    "٢) ومجموعُ أزمنة مراحل الحصة الأربع = " + dur + " دقيقةً كذلك.",
    "٣) وزمنُ «الأولى بالرعاية» وزمنُ «الموهوبين» داخلَ زمن التنفيذ فلا يتجاوزانه.",
    "٤) كلُّ خانةٍ تُملأ بنصٍّ محدَّدٍ يُرى في الحصة — لا بعباراتٍ عامّةٍ مثل",
    "   «مراعاة الفروق الفردية» بلا مهمّةٍ مكتوبة.",
    "");

  /* ⛔ **اللصقُ كان يفشل إذا أجاب المساعدُ بالإنجليزية** — بلاغُ أ. محمد
     أبو نار عبر وكيل عرقة عالمي (٦ أكتوبر ٢٠٢٦). والسببُ أن التوزيعَ كان
     يُطابق **اسمَ الحقل العربيَّ** وحدَه: فمساعدٌ يكتب تحضيراً إنجليزياً
     يُترجم أسماءَ الحقول معه، فلا يُطابق شيء. وقِيس العطبُ قبل علاجه:
     بجوابٍ إنجليزيٍّ ضاعت **٢٨ خانةً من ٧٦ صامتةً** — والأسوأُ أنها لا تفشل
     فشلاً بيّناً بل تمتلئ ناقصةً فيظنُّها المعلمُ تامّة.
     ⚠️ فصار لكلِّ حقلٍ **رمزٌ لاتينيٌّ لا يُترجَم** يُكتب بين قوسين معقوفين،
        وبه يقع التوزيعُ أيّاً كانت لغةُ الجواب. والاسمُ يبقى للقراءة. */
  head.push("⛔ أجب بهذه الصيغة حرفياً: سطرٌ لكل حقل يبدأ بـ### ثم اسمُ الحقل، ثم رمزُه",
    "   بين قوسين معقوفين، ثم نقطتان، ثم القيمة.",
    "⛔ والرمزُ بين [ ] يُنسخ كما هو ولا يُترجَم ولا يُحذَف — به تُوزَّع إجابتُك على الخانات.",
    "ولا تكتب مقدّمةً ولا خاتمةً ولا شرحاً خارج الأسطر.",
    "وما كان اختياراً من قائمةٍ فاكتب أحدَ خياراتها كما هو.",
    "ويجوز أن تكتب قيمَ الحقول بالعربية أو بالإنجليزية بحسب لغة تدريس المادة —",
    "   ولا يتغيّر بذلك شيءٌ من الصيغة ولا من الرموز.",
    "");

  const body = F.map(f=>{
    let hint = "";
    if(f.kind === "ticks") hint = "  (اختر من: " + (f.items || []).join(" · ") + ")";
    else if(f.kind === "select") hint = "  (اختر من: " + (f.items || []).join(" · ") + ")";
    else if(f.kind === "num") hint = "  (رقمٌ بالدقائق)";
    return "### " + f.lab + " [" + f.key + "]:" + hint;
  });
  return head.concat(body).join("\n");
}
/*@/noi18n*/

/* ── قراءةُ الجواب: يُقبل «###» وتُتسامَح المسافاتُ والنقطتان ── */
function planParse(txt){
  const lines = String(txt || "").replace(/\r/g, "").split("\n");
  const out = {}, codes = {}; let cur = null;
  lines.forEach(ln=>{
    const m = ln.match(/^\s*#{2,}\s*(.+?)\s*[:：]\s*(.*)$/);
    if(m){
      let lab = m[1];
      /* ⚠️ الرمزُ بين [ ] إن وُجد: هو المرساةُ التي لا تُترجَم. ويُنزع من
         الاسم قبل مطابقته، فجوابٌ قديمٌ بلا رمزٍ يُطابَق بالاسم كما كان. */
      let code = "";
      const cm = lab.match(/\[\s*([A-Za-z0-9_#]+)\s*\]\s*$/);
      if(cm){ code = cm[1]; lab = lab.slice(0, cm.index); }
      /* ⛔ التلميحُ بين قوسين يُحذف، **ورقمُ السطر لا**: كان
         «أسئلة الوحدة (١)» يصير «أسئلة الوحدة» فلا يطابق حقلاً، وضاعت
         ستةُ حقولِ أسطرٍ صامتةً — كشفه فحصُ التوزيع لا العين. */
      cur = lab.replace(/\s*\((?:\s*(?:اختر|choose|رقم|a number)[^)]*)\)\s*$/, "").trim();
      out[cur] = (m[2] || "").trim();
      if(code) codes[cur] = code;
    } else if(cur && ln.trim()){
      out[cur] = (out[cur] ? out[cur] + "\n" : "") + ln.trim();
    }
  });
  /* ⚠️ الرموزُ تُعلَّق على الخريطة **غيرَ معدودة**: `Object.keys` يبقى أسماءَ
     الحقول وحدَها، فلا يتغيّر عقدُ الدالّة على من يقرؤها. */
  try{ Object.defineProperty(out, "__codes", {value: codes, enumerable: false}); }catch(e){}
  return out;
}

/* ⚠️ المطابقةُ مجرَّدةٌ من التشكيل وعلامات الترقيم: المساعدُ قد يكتب
   «الهدف المعرفي» بلا ضمّة، أو يضيف نقطةً — ولا يُهدر الحقلُ لذلك. */
function planNorm(s){
  return String(s || "")
    .replace(/[ً-ْـ]/g, "")
    /* ⛔ الأرقامُ الهنديةُ تُوحَّد لا تُمحى: كانت تُحذف مع الرموز فتساوى
       «نمط العمل ١» و«نمط العمل ٢» وذهب أحدُهما — كشفه فحصُ التوزيع. */
    .replace(/[٠-٩]/g, function(c){ return "٠١٢٣٤٥٦٧٨٩".indexOf(c); })
    .replace(/[أإآٱ]/g, "ا").replace(/ة/g, "ه").replace(/ى/g, "ي")
    .replace(/[^ء-يA-Za-z0-9]+/g, " ")
    .trim().toLowerCase();
}

/* ── التوزيعُ على الخانات: يُرجع ما سيُملأ وما يُستبدل وما لم يُفهم ── */
/* ⚠️ **ثلاثُ مراسٍ لا واحدة**، بهذا الترتيب:
   ① الرمزُ اللاتينيُّ بين [ ] — لا يُترجَم، فيصحُّ بأي لغةٍ أجاب المساعد.
   ② الاسمُ العربيُّ — لمن نسخ أمراً قديماً قبل إضافة الرموز.
   ③ الاسمُ الإنجليزيُّ من معجم الواجهة — لمن ترجم المساعدُ عنوانَه وحذف الرمز.
      ويُبنى للحقول المرقَّمة تركيباً («أسئلة الوحدة (١)» ⇐ «Unit questions (1)»)،
      ولا يُسجَّل اسمٌ إنجليزيٌّ **مشتركٌ بين حقلين** فيُخلط بينهما. */
function planPlan(P, map){
  const F = planFields(), byLab = {}, byKey = {}, en = {}, dupEN = {};
  const I = (typeof I18N !== "undefined" && I18N) ? I18N : {};
  F.forEach(f=>{
    byLab[planNorm(f.lab)] = f;
    byKey[f.key] = f;
    let e = I[f.lab] || "";
    if(!e && f.base && I[f.base])
      e = I[f.base] + (f.idx ? " (" + f.idx + ")" : "");
    if(e){
      const n = planNorm(e);
      if(en[n] && en[n] !== f) dupEN[n] = true;
      else en[n] = f;
    }
  });
  const codes = map.__codes || {};
  const fill = [], over = [], unknown = [];
  Object.keys(map).forEach(lab=>{
    const val = (map[lab] || "").trim();
    const nl = planNorm(lab);
    const f = byKey[codes[lab]] || byLab[nl] || (dupEN[nl] ? null : en[nl]);
    if(!f){ if(val) unknown.push(lab); return; }
    if(!val) return;
    const had = f.kind === "ticks"
      ? (f.items || []).some((_, i)=>P[f.key + "#" + i])
      : !!String(P[f.key] || "").trim();
    (had ? over : fill).push({f: f, val: val});
  });
  return {fill: fill, over: over, unknown: unknown};
}

function planApply(P, items){
  let n = 0;
  items.forEach(function(it){
    const f = it.f, v = it.val;
    if(f.kind === "ticks"){
      /* ⚠️ يُطابَق كلُّ خيارٍ بالتجريد: «فردي.» و«فردي» واحد */
      const picked = v.split(/[·,،\n\/]+/).map(planNorm).filter(Boolean);
      (f.items || []).forEach(function(it2, i){
        const hit = picked.some(function(x){
          const y = planNorm(it2);
          return x === y || (x.length > 2 && y.indexOf(x) >= 0)
                          || (y.length > 2 && x.indexOf(y) >= 0);
        });
        if(hit){ P[f.key + "#" + i] = true; n++; }
      });
      return;
    }
    if(f.kind === "select"){
      /* ⛔ لا تُكتب قيمةٌ ليست في القائمة: تُحفظ ولا تُعرض فيظنُّها المعلمُ مملوءة */
      const hit = (f.items || []).find(function(x){
        return planNorm(x) === planNorm(v) || planNorm(v).indexOf(planNorm(x)) >= 0; });
      if(hit){ P[f.key] = hit; n++; }
      return;
    }
    if(f.kind === "num"){
      const d = String(v).replace(/[٠-٩]/g, function(c){ return "٠١٢٣٤٥٦٧٨٩".indexOf(c); })
                         .match(/\d+/);
      if(d){ P[f.key] = d[0]; n++; }
      return;
    }
    P[f.key] = v; n++;
  });
  return n;
}

/* ═════════ قراءةُ ملفّ وورد في المتصفّح بلا مكتبة ═════════
   ⚠️ الـdocx ملفُّ zip، وفيه «word/document.xml». والمتصفّحاتُ الحديثةُ فيها
   DecompressionStream فيُفكُّ بلا تنزيل مكتبةٍ تزيد حجمَ الصفحة ميجابايت.
   جُرِّب على ملفٍ حقيقي: ٦١ فقرةً و٢٨٣٨ حرفاً. */
async function docxText(buf){
  /* ⛔ يُفحص وجودُ فاكِّ الضغط قبل العمل: متصفّحٌ قديمٌ يسقط بلا رسالةٍ
     مفهومة، فيُقال له الطريقُ الآخر (اللصق) بدل أن يُترك حائراً. */
  if(typeof DecompressionStream === "undefined")
    throw new Error("متصفّحُك لا يفكُّ ملفات وورد — حدّثه، أو الصق النصَّ في الصندوق بدل رفع الملف.");
  const dv = new DataView(buf), u8 = new Uint8Array(buf);
  let eocd = -1;
  for(let i = u8.length - 22; i >= 0 && i > u8.length - 66000; i--)
    if(dv.getUint32(i, true) === 0x06054b50){ eocd = i; break; }
  if(eocd < 0) throw new Error("الملفُّ ليس مستندَ وورد (.docx)");
  const n = dv.getUint16(eocd + 10, true);
  let off = dv.getUint32(eocd + 16, true);
  for(let k = 0; k < n; k++){
    const nl = dv.getUint16(off + 28, true), xl = dv.getUint16(off + 30, true),
          cl = dv.getUint16(off + 32, true), lho = dv.getUint32(off + 42, true),
          method = dv.getUint16(off + 10, true), csize = dv.getUint32(off + 20, true);
    const name = new TextDecoder().decode(u8.subarray(off + 46, off + 46 + nl));
    if(name === "word/document.xml"){
      const lnl = dv.getUint16(lho + 26, true), lel = dv.getUint16(lho + 28, true);
      const raw = u8.subarray(lho + 30 + lnl + lel, lho + 30 + lnl + lel + csize);
      let xml;
      if(method === 0) xml = new TextDecoder().decode(raw);
      else xml = await new Response(new Blob([raw]).stream()
                   .pipeThrough(new DecompressionStream("deflate-raw"))).text();
      /* كلُّ فقرةٍ سطر، وكلُّ <w:t> نصّ */
      return (xml.match(/<w:p[ >][\s\S]*?<\/w:p>/g) || []).map(function(p){
        return (p.match(/<w:t[^>]*>[^<]*<\/w:t>/g) || [])
                 .map(function(t){ return t.replace(/<[^>]+>/g, ""); }).join("");
      }).join("\n");
    }
    off += 46 + nl + xl + cl;
  }
  throw new Error("لم يُوجد نصُّ المستند داخل الملف");
}

/* ═════════ اللوحةُ في شاشة التحضير ═════════ */
function importPanel(m, L, P){
  const c = el("div","card"), h = el("h3");
  h.appendChild(el("span",null,"طريقة التحضير بالذكاء الاصطناعي"));
  /* ⛔ ملخّصُ الطريقة بجوار العنوان بحجمٍ يُقرأ — لا سطراً في الشرح المطويّ:
     المعلمُ يفهم الطريقةَ من سطرٍ واحدٍ قبل أن يضغط. (طلبُ المستشار) */
  h.appendChild(el("small",null,
    "تنسخ أمراً يحمل درسَك وإستراتيجيتَك واتجاهَك، ويكتب لك المساعدُ التحضيرَ ووسائلَه، فتُلصقه هنا فيملأ الخانات"));
  c.appendChild(h);
  const pad = el("div","pad");

  const steps = el("div","msg");
  steps.appendChild(el("b",null,"كيف تعمل — أربع خطوات"));
  const ol = el("ol"); ol.style.cssText = "padding-inline-start:22px;margin:6px 0 0;font-size:15.5px";
  [ "**أكمل بيانات الحصة أعلاه** (عنوان الدرس وصفحاته في الكتاب وزمن الحصة) واختر الإستراتيجية والاتجاه — فمنها يُبنى الأمر.",
    "**انسخ الأمر**: يحمل مادتك وصفَّك وعنوانَ درسك وصفحاته، ومؤشرات إستراتيجيتك العشرة، وشواهد اتجاهك الثلاثة، ونموذجَ التحضير بحقوله.",
    "**ألصقه في أي مساعدٍ ذكيّ** — ويطلب منه الأمرُ أيضاً أن يُصمّم وسائلَ الحصة جاهزةً للاستعمال لا أن يصفها.",
    "**ألصق جوابه هنا** (أو ارفع ملف وورد) ثم «وزّع على الخانات» — فتمتلئ الخاناتُ كلُّها، وتُراجعها وتُصدر تحضيرك."
  ].forEach(t=>{
    const li = el("li");
    t.split("**").forEach((part,ix)=>{
      li.appendChild(ix % 2 ? el("b",null,part) : el("span",null,part));
    });
    ol.appendChild(li);
  });
  steps.appendChild(ol);
  pad.appendChild(steps);

  const bar = el("div","bar");
  const cp = el("button","b","انسخ الأمر");
  cp.addEventListener("click", ()=>{
    const txt = planPrompt(L, P);
    const done = ()=>alert("نُسخ الأمر.\n\nألصقه في المساعد، ثم أعد الجوابَ كاملاً إلى الصندوق أدناه.");
    if(navigator.clipboard && navigator.clipboard.writeText)
      navigator.clipboard.writeText(txt).then(done).catch(()=>uiPrompt("انسخ الأمر:", txt));
    else uiPrompt("انسخ الأمر:", txt);
  });
  bar.appendChild(cp);

  /* ⚠️ رفعُ الملف: وورد وحدَه. والـPDF مرفوضٌ بنصٍّ يقول لماذا لا بصمت. */
  const up = el("button","b ghost","ارفع ملف وورد (.docx)");
  const fi = el("input"); fi.type = "file"; fi.accept = ".docx"; fi.style.display = "none";
  up.addEventListener("click", ()=>fi.click());
  bar.appendChild(up); bar.appendChild(fi);
  pad.appendChild(bar);

  const ta = fld("area", "", ()=>{}, null, "ألصق هنا جواب المساعد، أو نصَّ تحضيرك بصيغة ### اسم الحقل: القيمة");
  ta.rows = 6; ta.style.cssText = "width:100%;min-height:120px;margin-top:10px";
  pad.appendChild(ta);

  const out = el("div"); out.style.marginTop = "8px";
  const go = el("button","b","وزّع على الخانات");
  go.style.marginTop = "8px";
  const run = (txt)=>{
    out.innerHTML = "";
    const map = planParse(txt);
    if(!Object.keys(map).length){
      const w = el("div","msg bad");
      w.appendChild(el("b",null,"لم أجد حقولاً بصيغة ### اسم الحقل: القيمة"));
      w.appendChild(el("span",null,"تأكّد أن المساعد أجاب بالصيغة المطلوبة في الأمر، أو أعد نسخ الأمر."));
      out.appendChild(w); return;
    }
    const plan = planPlan(P, map);
    if(!plan.fill.length && !plan.over.length){
      /* ⛔ **ولا يُترك المعلمُ بـ«راجع الصيغة»**: الغالبُ أن المساعدَ ترجم
         أسماءَ الحقول وحذف رموزَها — فيُقال له السببُ والمخرَج. */
      const w = el("div","msg bad");
      w.appendChild(el("b",null,"لم يطابق أيُّ حقلٍ أسماءَ الخانات"));
      w.appendChild(el("span",null,
        "والغالبُ أن المساعدَ غيّر أسماءَ الحقول أو حذف رموزَها بين [ ]. "
        + "انسخ الأمرَ من جديد — فهو يحمل لكلِّ حقلٍ رمزاً يُوزَّع به مهما كانت لغةُ الجواب — "
        + "ثم اطلب منه إعادةَ الجواب بالصيغة نفسِها مع إبقاء ما بين [ ] كما هو."));
      out.appendChild(w);
      return;
    }
    const s = el("div","msg ok");
    s.appendChild(el("b",null, "سيُملأ " + arn(plan.fill.length) + " خانةً"
      + (plan.over.length ? "، ويُستبدل ما في " + arn(plan.over.length) + " خانةً مكتوبةً" : "")));
    if(plan.unknown.length)
      s.appendChild(el("span",null,"ولم أعرف: " + plan.unknown.slice(0,6).join(" · ")));
    out.appendChild(s);
    const ok = el("button","b");
    ok.textContent = plan.over.length ? "أدخِله واستبدل المكتوب" : "أدخِله";
    ok.addEventListener("click", ()=>{
      const go2 = ()=>{
        snap(L.gk, "استيراد تحضير");      /* ⛔ لقطةُ تراجعٍ قبل الكتابة */
        const n = planApply(P, plan.fill.concat(plan.over));
        logAct("استيراد تحضير", lessonTitle(L) + " — " + arn(n) + " خانة", L);
        save(); shell();
        alert("✓ أُدخل " + arn(n) + " خانة.\n\nراجعها ثم اضغط «إصدار التحضير».");
      };
      if(!plan.over.length){ go2(); return; }
      uiAsk("سيُستبدل ما كتبتَه في " + arn(plan.over.length) + " خانة.\n\nأتُتابع؟",
            "استبدِله").then(y=>{ if(y) go2(); });
    });
    out.appendChild(ok);
  };
  go.addEventListener("click", ()=>run(ta.value));
  fi.addEventListener("change", async ()=>{
    const f = fi.files && fi.files[0];
    if(!f) return;
    if(/\.pdf$/i.test(f.name)){
      alert("ملفُّ PDF لا يُقرأ هنا: نصُّ العربية فيه يخرج مشوَّهاً فيملأ الخاناتِ بخطأ.\n\n"
          + "احفظ تحضيرك بصيغة وورد (.docx) وأعد الرفع.");
      fi.value = ""; return;
    }
    try{
      const txt = await docxText(await f.arrayBuffer());
      ta.value = txt; run(txt);
    }catch(e){ alert("تعذّرت قراءةُ الملف: " + e.message); }
    fi.value = "";
  });
  pad.appendChild(go); pad.appendChild(out);
  c.appendChild(pad); m.appendChild(c);
}
