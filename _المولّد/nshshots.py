# -*- coding: utf-8 -*-
"""لقطاتٌ حيّةٌ من منصة الحصة الموحَّدة — لنشرات الاستخدام الخمس.

⛔ اللقطةُ من المنصة نفسِها لا من رسمٍ ولا من نموذجٍ مصوَّر: تُنسخ الصفحةُ
   المنشورة، ويُحقن فيها مُمهِّدٌ يزرع بياناتٍ واقعيةً ويدخل بالدور المطلوب
   ويفتح الشاشةَ المطلوبة، ثم يُصوَّر ما يراه المستخدمُ فعلاً.

⚠️ ولا يُكتب في الصفحة المنشورة شيء: النسخةُ في المؤقّت، والأصلُ لا يُمَسّ.

⚠️ والبياناتُ المزروعةُ بأسماءٍ **مستعارةٍ صراحةً** («أ. نموذج …») لئلا تُنسب
   درجةٌ إلى معلمٍ حقيقيٍّ في نشرةٍ تُوزَّع.

الاستعمال: CLS_GENDER=m|f python3 nshshots.py [اسم اللقطة…]
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRATCH = ("/private/tmp/claude-501/-Users-ahmadseyam-Desktop--------------------/"
           "0867de99-3862-4f08-89c9-d58bbdaafa97/scratchpad/nsh")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
GENDER = os.environ.get("CLS_GENDER", "m")
G = lambda m, f: f if GENDER == "f" else m

SRC = os.path.join(ROOT, "٨ - النموذج الرقمي (تجربة)",
                   "منصة الحصة الموحَّدة — ابن خلدون" + G("", " (بنات)") + ".html")
# ⛔ لقطاتُ الدليل الإنجليزي في مجلدٍ خاصٍّ بها: الشاشةُ غيرُ الشاشة، فلو
#    خُلطت بالعربية كُتب فوقها ودخلت الدليلَ العربيَّ لقطةٌ إنجليزية.
LANG = os.environ.get("CLS_LANG", "ar")
OUT = os.path.join(ROOT, "١٠ - أدلّة استخدام المنصة", "صور",
                   "English" if LANG == "en" else G("بنين", "بنات"))
os.makedirs(OUT, exist_ok=True)
os.makedirs(SCRATCH, exist_ok=True)

# ═════════ البياناتُ المزروعة ═════════
# ⚠️ الأسماءُ مستعارةٌ صراحةً، والحصصُ قليلةٌ مختارةٌ لتملأ الشاشةَ بلا فوضى.
TEACH = G("أ. نموذج الغامدي", "أ. نموذج الغامدي")
PEER1 = G("أ. نموذج القحطاني", "أ. نموذج القحطاني")
EV = G("أ. نموذج الشهري", "أ. نموذج الشهري")

SEED = r"""
(function(){
  var SEC = D.sectors[0], CX = D.complexlist[0];
  var bands = (D.bands[CX]||[]);
  var wk = (D.cal && D.cal[0] ? D.cal[0].w : D.weeks[0]);
  var day = D.days[0];
  /* الحصصُ تُبنى على مجموعة التخصص الزائرة فعلاً في ذلك اليوم، وإلا لم تظهر */
  var gp = ((D.rot[CX]||{})[wk]||{})[day] || Object.keys(D.pairs)[0];
  var specs = (D.pairs[gp]||D.specs).slice(0, 2);
  var mk = function(i, band, spec, teacher, done){
    var id = "demo" + i;
    var L = {
      id: id, gk: [SEC, CX, band.stage, band.per, wk, day, spec].join("|"),
      sector: SEC, complex: CX, stage: band.stage, school: band.stage,
      week: wk, day: day, period: band.per.replace(/\D/g, ""), time: band.time,
      teacher: teacher, subject: spec, klass: "__KLASS__" + (i + 1),
      strategy: (D.bank && D.bank[i] ? D.bank[i][1] : ""),
      approach: (D.ticks && D.ticks.dir ? D.ticks.dir[i % D.ticks.dir.length] : ""),
      spec: spec, peer1: "__PEER__", peer1e: "", peer2: "", peer2e: "",
      ev1: "__EV__", ev2: "", ev3: ""
    };
    DB.sched.push(L);
    if (done) {
      DB.prep[id] = {__issued: 1, subject: spec, klass: L.klass, teacher: teacher,
                     title: "__TITLE__", goals: "__GOALS__",
                     tmain: {warm: "٥", exec: "١٨", eval: "١٧", close: "٥", total: "٤٥"},
                     tdiff: {care: "٦", gift: "٦"}};
    }
    return L;
  };
  var i = 0, made = [];
  bands.forEach(function(b){
    specs.forEach(function(sp){
      if (i < 4) made.push(mk(i++, b, sp, i === 1 ? "__TEACH__" : "__TEACH__ " + i, i <= 2));
    });
  });
  window.__DEMO = made;
  save();
})();
"""

VIEWS = {}


def view(name, role, **kw):
    VIEWS[name] = dict(role=role, **kw)


# ── ما يُصوَّر لكل دور ──
view("login", None, raw="login()")
view("login_teacher", None, raw='login(); __pickRole("teacher")')
view("login_sup", None, raw='login(); __pickRole("supervisor")')
view("login_prin", None, raw='login(); __pickRole("principal")')

view("t_grid", "teacher", ph=1, tab="fill")
view("t_prep", "teacher", ph=2, cur=0)
view("t_run", "teacher", ph=6, cur=0)
view("t_report", "teacher", ph=5)

view("p_visits", "peer", ph=5)
view("p_read", "peer", ph=6, cur=0)
view("p_card", "peer", ph=3, cur=0)
view("p_result", "peer", ph=4, cur=0)

view("m_school", "principal", ph=1, tab="fill")
view("m_obs", "principal", ph=3, cur=0)
view("m_approve", "principal", ph=4, cur=0)
view("m_reports", "principal", ph=5)

view("w_school", "deputy", ph=1, tab="fill")
view("w_assign", "deputy", ph=1, tab="assign")
view("w_pending", "deputy", ph=5, rpt="pending", fakeroster=True)
view("w_obs", "deputy", ph=3, cur=0)

view("s_grid", "supervisor", ph=1, tab="fill")
view("s_plan", "supervisor", ph=1, tab="visits")
view("s_rot", "supervisor", ph=1, tab="sup")
view("s_obs", "supervisor", ph=3, cur=0)

# ⛔ الدَّوران الجديدان (٣٠ سبتمبر ٢٠٢٦) بقيا بلا دليلٍ ولا لقطة — والنشراتُ
#    خمسٌ والأدوارُ سبعة. (١ أكتوبر ٢٠٢٦)
view("login_cx", None, raw='login(); __pickRole("cxmgr")')
view("c_grid", "cxmgr", ph=1, tab="fill")
view("c_gap", "cxmgr", ph=5, rpt="gap")
view("c_obs", "cxmgr", ph=3, cur=0)
view("c_reports", "cxmgr", ph=5)

view("login_iq", None, raw='login(); __pickRole("intqa")')
view("q_grid", "intqa", ph=1, tab="fill")
view("q_gap", "intqa", ph=5, rpt="gap")
view("q_note", "intqa", ph=4, cur=0)

BOOT = r"""
<script>
window.__pickRole = function(k){
  var t = (D.roles.find(function(r){return r.k===k;})||{}).t || "";
  var cards = [].slice.call(document.querySelectorAll("div.role"));
  for (var i=0;i<cards.length;i++){
    if ((cards[i].textContent||"").indexOf(t) >= 0){ cards[i].click(); return true; }
  }
  return false;
};
window.__go = function(){
  try{
    localStorage.clear();
    /* ⛔ تُبدَّل اللغةُ **قبل** الزرع والرسم: setLang تُعيد الرسمَ بنفسها،
       فلو جاءت بعده رُسمت الشاشةُ مرّتين وبقيت الأولى في الصورة. */
    if(__LANG__ === "en" && typeof setLang === "function"){ LANG = "en"; applyLang(); }
    __SEED__
    var V = __VIEW__;
    if (V.raw){ eval(V.raw);
      document.title = "READY|" + (document.body.innerText||"").replace(/\s+/g," ").slice(0,150);
      return; }
    ME = Object.assign({role: V.role, name: "__ME__", emp: ""}, V.me || {});
    localStorage.setItem(KEY + "_me", JSON.stringify(ME));
    try{ localStorage.removeItem(KEY + "_ctx"); }catch(e){}
    GS = null;
    if (V.tab) setctx("tab", V.tab);
    if (V.rpt) RPT = V.rpt;      /* التقريرُ المطلوبُ بعينه لا أوّلُ تقرير */
    /* ⛔ كشفٌ مستعارٌ للّقطة: التقريرُ يسمّي من لم يُدخِل، والدليلُ يُوزَّع
       على الكشف نفسِه — فلا يُصوَّر فيه اسمُ معلمٍ حقيقي. */
    if (V.fakeroster){
      var FR = {}, i;
      for (i = 1; i <= 9; i++)
        FR["90000000" + i] = {n: "أ. نموذج " + ["الغامدي","القحطاني","الشهري","الزهراني",
          "العمري","الحربي","المالكي","الدوسري","السبيعي"][i-1],
          s: D.specs[(i-1) % D.specs.length], q: ""};
      D.roster = FR;
      var ks = Object.keys(FR);
      DB.sched.forEach(function(L, k){
        if (k < 3){ L.teacher = FR[ks[k]].n; L.teacherNo = ks[k]; }
      });
      save();
    }
    if (V.cur != null && window.__DEMO && __DEMO[V.cur]) CUR = __DEMO[V.cur].id;
    PH = V.ph || 1;
    shell();
    document.title = "READY|" + (document.body.innerText||"").replace(/\s+/g," ").slice(0,150);
  }catch(e){ document.title = "ERR " + e.message; }
};
setTimeout(window.__go, 120);
</script>
"""


def build(name):
    v = VIEWS[name]
    me = {"teacher": TEACH, "peer": PEER1, "principal": EV,
          "deputy": EV, "supervisor": EV}.get(v.get("role"), EV)
    vv = dict(v)
    if v.get("role") in ("principal", "deputy"):
        vv["me"] = {"sector": "__SEC__", "complex": "__CX__", "school": "__SCH__"}
    elif v.get("role") in ("supervisor", "peer", "teacher"):
        vv["me"] = {"spec": "__SPEC__"}
    seed = (SEED.replace("__TEACH__", TEACH).replace("__PEER__", PEER1)
                .replace("__EV__", EV)
                .replace("__KLASS__", G("الفصل ", "الفصل "))
                .replace("__TITLE__", G("درسُ اليوم", "درسُ اليوم"))
                .replace("__GOALS__", G("أن يتمكّن المتعلم من …", "أن تتمكّن المتعلمة من …")))
    boot = (BOOT.replace("__SEED__", seed)
                .replace("__VIEW__", json.dumps(vv, ensure_ascii=False))
                .replace("__ME__", me)
                .replace("__LANG__", json.dumps(LANG)))
    # القيمُ التي لا تُعرف إلا داخل الصفحة تُحسب هناك
    boot = boot.replace('"__SEC__"', "D.sectors[0]") \
               .replace('"__CX__"', "D.complexlist[0]") \
               .replace('"__SCH__"', "(D.bands[D.complexlist[0]]||[])[0].stage") \
               .replace('"__SPEC__"', "D.specs[0]")
    html = open(SRC, encoding="utf-8").read() + boot
    p = os.path.join(SCRATCH, "run_%s.html" % name)
    open(p, "w", encoding="utf-8").write(html)
    return p


def _dom_text(p, wait):
    """نصُّ الشاشة كما يراه المستخدم — للتحقّق من أن المصوَّر هو المقصود."""
    import re as _r
    out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                          "--virtual-time-budget=%d" % wait, "--dump-dom", "file://" + p],
                         capture_output=True, text=True).stdout
    m = _r.search(r"<title>(.*?)</title>", out, _r.S)
    import html as _h
    return _h.unescape(m.group(1)) if m else ""


def shot(name, w=1500, h=1000, wait=6000):
    p = build(name)
    png = os.path.join(SCRATCH, "%s.png" % name)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars", "--force-device-scale-factor=2",
                    "--window-size=%d,%d" % (w, h),
                    "--virtual-time-budget=%d" % wait,
                    "--screenshot=" + png, "file://" + p], capture_output=True)
    if not os.path.exists(png):
        return None, "لم تُلتقط"
    im = Image.open(png).convert("RGB")
    # ⚠️ يُقصُّ البياضُ المحيط: الشاشةُ الكبيرةُ حول بطاقةٍ صغيرة تُخرج صورةً
    #    معظمُها فراغٌ فتصغر في النشرة حتى لا تُقرأ.
    bg = Image.new("RGB", im.size, (255, 255, 255))
    from PIL import ImageChops
    bbox = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 14 else 0).getbbox()
    if bbox:
        pad = 16
        im = im.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                      min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad)))
    im = ImageOps.expand(im, border=3, fill=(53, 94, 145))
    dst = os.path.join(OUT, "%s.png" % name)
    im.save(dst, optimize=True)
    txt = _dom_text(p, wait)
    ok = txt.startswith("READY")
    return dst, "%4dx%-4d %s %s" % (im.width, im.height, "✓" if ok else "⛔",
                                    txt.split("|", 1)[-1][:70] if ok else txt[:60])


if __name__ == "__main__":
    want = sys.argv[1:] or list(VIEWS)
    for n in want:
        if n not in VIEWS:
            print("  ⛔ لا لقطةَ بهذا الاسم:", n)
            continue
        dst, info = shot(n)
        print("  %-12s %s" % (n, info if dst else "⛔ " + info))
