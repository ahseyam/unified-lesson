# -*- coding: utf-8 -*-
"""⛔ «المعجمُ كامل» ليست «الشاشةُ إنجليزية»: النصُّ قد يُحقن بـinnerHTML أو
   بـtextContent مباشرةً فلا يمرَّ على el()، أو يُبنى بوصلٍ فيفوت اللفّ.
   فتُفتح كلُّ شاشةٍ لكل دورٍ بالإنجليزية ويُقرأ ما فيها حرفاً حرفاً.

⚠️ وتُستثنى البياناتُ المزروعةُ عربيةً (أسماءُ المعلمين والمدارس والمجمعات)
   لأن قرارَ المستشار أن تبقى كما هي."""
import html as H
import json
import os
import re
import subprocess
import sys
import probedir as PRB   # نسخُ الفحص خارج شجرة التسليم

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = os.path.dirname(os.path.abspath(__file__))
D8 = "/Users/ahmadseyam/Desktop/نموذج تحضير الدرس - بطاقة الملاحظة الصفية/٨ - النموذج الرقمي (تجربة)"

# الشاشاتُ: (الدور، المرحلة، التبويب/التقرير)
VIEWS = [("teacher",1,"fill"),("teacher",2,None),("teacher",6,None),("teacher",5,None),
         ("peer",5,None),("peer",6,None),("peer",3,None),("peer",4,None),
         ("principal",1,"fill"),("principal",2,None),("principal",3,None),
         ("principal",4,None),("principal",5,"school"),("principal",5,"pending"),
         ("deputy",1,"assign"),("deputy",1,"fill"),("deputy",5,"active"),
         ("supervisor",1,"fill"),("supervisor",1,"visits"),("supervisor",1,"sup"),
         ("supervisor",3,None),("supervisor",5,"ind"),
         ("admin",7,None),("admin",8,None),("admin",1,"log"),("admin",5,"teacher")]

BOOT = r"""
<script>
window.__R = [];
setTimeout(function(){
 try{
  localStorage.clear();
  setLang("en");
  var SEC=D.sectors[0], CX=D.complexlist[0], bands=D.bands[CX]||[];
  var wk=D.weeks[0], day=D.days[0];
  var gp=((D.rot[CX]||{})[wk]||{})[day] || Object.keys(D.pairs)[0];
  var sp=(D.pairs[gp]||D.specs)[0];
  /* ⛔ تُختار مرحلةٌ **لها مشرفُها**: الحالةُ العامّةُ أن للحصة مشرفاً، وخليةُ
     الفجوة لها فحصُها في supcheck. وأولُ أعمدة البنات رياضُ الأطفال وهي بلا
     مشرفةٍ في الوطني، فكانت الشاشةُ تُرسَم رصداً لا اطّلاعاً. */
  var b=bands.filter(function(x){
        return supsForCell(SEC,CX,x.stage,sp).length > 0; })[0] || bands[0];
  var L={id:"x1", gk:[SEC,CX,b.stage,b.per,wk,day,sp].join("|"),
    sector:SEC,complex:CX,stage:b.stage,school:b.stage,week:wk,day:day,
    period:b.per.replace(/\D/g,""),time:b.time,teacher:"__T__",teacherNo:"",
    subject:sp,spec:sp,klass:"5/A",strategy:(D.bank[0]||{}).name,
    approach:D.approaches[0],peer1:"__P__",peer2:"",peer1e:"",peer2e:"",
    ev1:"",ev2:"",ev3:""};
  DB.sched.push(L);
  DB.prep["x1"]={__issued:1,subject:sp,klass:"5/A",teacher:"__T__",
    tmain:{warm:"5",exec:"18",eval:"17",close:"5",total:"45"},tdiff:{care:"6",gift:"6"}};
  save();
  var VS = __VIEWS__;
  VS.forEach(function(v){
    var role=v[0], ph=v[1], tab=v[2];
    ME={role:role,name:(role==="admin"?"__A__":"__T__"),emp:"",spec:D.specs[0]};
    if(role==="principal"||role==="deputy"||role==="admin"){
      ME.sector=SEC; ME.complex=CX; ME.school=b.stage;
    }
    localStorage.setItem(KEY+"_me",JSON.stringify(ME));
    try{ localStorage.removeItem(KEY+"_ctx"); }catch(e){}
    GS=null; CUR="x1"; PH=ph;
    if(tab==="pending"||tab==="active"||tab==="ind"||tab==="teacher"||tab==="school"){ RPT=tab; }
    shell();
    if(tab && ["fill","assign","log","visits","sup","school"].indexOf(tab)>=0){
      setctx("tab",tab); shell();
    }
    __R.push([role+"/"+ph+"/"+(tab||"-"), (document.body.innerText||"")]);
  });
  /* وشاشةُ الدخول */
  ME=null; login();
  __R.push(["login/-/-", (document.body.innerText||"")]);
  document.title="DONE";
  window.__OUT = JSON.stringify(__R);
 }catch(e){ document.title="ERR|"+e.message+" @ "+(e.stack||"").split("\n")[1]; }
}, 250);
</script>
"""


def run(src, tag):
    boot = (BOOT.replace("__VIEWS__", json.dumps(VIEWS))
                .replace("__T__", "Ms. Sample Teacher" if "بنات" in src else "Mr. Sample Teacher")
                .replace("__P__", "Peer Sample").replace("__A__", "Admin"))
    p = PRB.probe("en_%s.html" % tag)
    open(p, "w", encoding="utf-8").write(
        open(src, encoding="utf-8").read().replace("</body>", "</body>") + boot
        + '<script>setTimeout(function(){var d=document.createElement("pre");'
          'd.id="dump";d.textContent=window.__OUT||"";document.body.appendChild(d);},900);</script>')
    out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                          "--virtual-time-budget=12000", "--dump-dom", "file://" + p],
                         capture_output=True, text=True).stdout
    t = re.search(r"<title>(.*?)</title>", out, re.S)
    ttl = H.unescape(t.group(1)) if t else "?"
    if ttl.startswith("ERR"):
        print("  ⛔ " + ttl); return False
    m = re.search(r'<pre id="dump">(.*?)</pre>', out, re.S)
    if not m:
        print("  ⛔ لم يُستخرج النصّ"); return False
    rows = json.loads(H.unescape(m.group(1)))
    AR = re.compile(r"[ؠ-يٱ-ۓ]+")
    # ما يبقى عربياً بالقرار: الأسماءُ والمدارسُ والمجمعات
    allow = set()
    h = open(src, encoding="utf-8").read()
    i = h.index("{", h.index("const D =")); Dd, _ = json.JSONDecoder().raw_decode(h[i:])
    # ⚠️ وكشفُ المعلمين لم يعد في الصفحة (نُزع ١ أكتوبر ٢٠٢٦) — فهذه الحلقةُ
    #    لا تُنتج شيئاً اليوم، وتبقى لتعمل إن أُعيد الكشفُ يوماً. وبنزعه
    #    انخفضت الكلماتُ المُستثناةُ من ٦٨٨ إلى ١٣٩ — فصار الفحصُ أشدّ.
    for v in (Dd.get("roster") or {}).values():
        allow |= {str(v.get(k) or "") for k in v}
    allow |= set(Dd.get("complexlist") or []) | set(Dd.get("bands") or {})
    # ⛔ عناوينُ المستندات المنشورة: ملفاتٌ عربيةٌ على الموقع — تُعرض بأسمائها
    for _m in sum((Dd.get("models") or {}).values(), []):
        allow |= {str(_m.get(k) or "") for k in _m}
    for bb in sum((Dd.get("bands") or {}).values(), []):
        allow |= {str(bb.get(k) or "") for k in bb}
    for g, wkx in (Dd.get("sup") or {}).items():
        for w, dd in wkx.items(): allow |= set(dd.values())
    allow |= {"أ. أحمد صيام", "أ. محمود كامل", "أ. هدى المشجري"}
    # ⛔ **أسماءُ المشرفين لا تُترجَم** (قرارُ المستشار)، وهي تُعرض في بطاقة
    #    «من يقيّم هذه الحصة» — فتُعفى من السجلّ نفسِه لا بقائمةٍ تُكتب بيد.
    allow |= {str(r.get("name") or "") for r in (Dd.get("sups") or [])}
    # ⛔ «عربي» تسميةُ زرِّ العودة إلى العربية — بقاؤها عربيةً هو الصواب،
    #    فمن لا يقرأ الإنجليزية يحتاج أن يقرأها هو.
    allow |= {"عربي"}
    allow_words = set()
    for a in allow:
        allow_words |= set(AR.findall(a or ""))
    # ⛔ **ثقبان كانا يُمرِّران العمى** (١ أكتوبر ٢٠٢٦):
    #    ١) `rows` خاويةٌ ← الحلقةُ لا تدور و`ok` يبقى True فيُعلن النجاح
    #       وقد لم تُفحَص شاشةٌ واحدة.
    #    ٢) شاشةٌ نصُّها خاوٍ تُطبَع «✓ ٠ حرفاً» — ولا عربيَّ فيها لأن لا شيءَ
    #       فيها. والشاشةُ الفارغةُ عطلٌ لا نجاح.
    # ⚠️ **الأرضيّةُ تُحسب ولا تُخمَّن**: كتبتُها أربعين فسقط الفحصُ وهو سليم
    #    (الشاشاتُ ٢٦ مع شاشة الدخول = ٢٧). فصارت عددَ الشاشات المعرَّفةِ
    #    نفسَه — فلا تدريجَ ولا تخمين، وتُمسك نقصانَ شاشةٍ واحدةٍ لو سقطت.
    FLOOR_ROWS, FLOOR_CHARS = len(VIEWS) + 1, 260
    ok = True
    if len(rows) != FLOOR_ROWS:
        print("  ⛔ %d شاشةً والمنتظَرُ %d (%d شاشةً مُعرَّفةً + شاشةُ الدخول)."
              " شاشةٌ لم تُفحَص — والفحصُ الناقصُ فاشل."
              % (len(rows), FLOOR_ROWS, len(VIEWS)))
        ok = False
    for name, txt in rows:
        if len(txt) < FLOOR_CHARS:
            ok = False
            print("  ⛔ %-22s %d حرفاً فقط — شاشةٌ خاويةٌ لا تُفحَص" % (name, len(txt)))
            continue
        words = [w for w in AR.findall(txt) if w not in allow_words]
        if words:
            ok = False
            print("  ⛔ %-22s %d كلمةً عربيةً: %s" % (name, len(words), "، ".join(sorted(set(words))[:8])))
        else:
            print("  ✓ %-22s %d حرفاً" % (name, len(txt)))
    return ok


# ⚠️ يُحرَس التشغيل: الفحصُ العربيُّ يستورد هذا الملفَّ لمُمهِّده، فلو نُفِّذ
#    عند الاستيراد لأُخرج تقريرُ الإنجليزية وخرج البرنامجُ قبل العربي.
if __name__ == "__main__":
    good = True
    for tag, fn in (("بنين", "منصة الحصة الموحَّدة — ابن خلدون.html"),
                    ("بنات", "منصة الحصة الموحَّدة — ابن خلدون (بنات).html")):
        print("══════ %s — الوضع الإنجليزي ══════" % tag)
        good &= run(os.path.join(D8, fn), tag)
        print()
    sys.exit(0 if good else 1)
