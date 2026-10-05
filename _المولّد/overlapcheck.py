# -*- coding: utf-8 -*-
"""حارسُ تداخل النصوص — نصٌّ يركب نصّاً على شاشةِ جوال.

⛔ **بلاغُ المستشار بصورةٍ من جواله ٥ أكتوبر ٢٠٢٦**: اسمُ المرحلة الحالية
   يطفو فوق أرقام المراحل ٢ و٣ و٤ في الشريط. و`respcheck` يمرّ — لأنه يقيس
   **الفيضانَ خارج الشاشة** لا **ركوبَ النصِّ على النصّ**. فبقي العيبُ
   منشوراً ولا حارسَ له.

⚠️ **والإطارُ الخامُ يكذب مرّتين**، وبلا علاجهما صرخ الكاشفُ ثمانيَ عشرةَ
   صرخةً الحقُّ منها اثنتان:
     ① ما يطفو بتصميمه (الشريطُ السفليُّ الثابت · الترويسةُ اللاصقة) ليس
        تداخلاً — فيُسقَط هو وكلُّ ما تحته.
     ② وما يُقصُّ في ممرِّ تمريرٍ يبقى له إطارٌ في الصفحة وإن لم يُرَ. فيُقاس
        **الإطارُ المرئيُّ**: تقاطعُ العنصر مع كلِّ جدٍّ يقصّ — وهو وحدَه ما
        يراه المستخدم.

⚠️ ويُقاس داخل إطارٍ مضمَّنٍ بعرضٍ مفروض: لكروم بلا رأسٍ حدٌّ أدنى للنافذة.
الأرضيّة: `FLOOR` شاشةً مقيسةً فعلاً — وفحصٌ لم يَقِس شيئاً فاشلٌ لا ناجح.
"""
import html as H
import json
import os
import re
import subprocess
import sys

import probedir as PRB

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D8 = os.path.join(ROOT, "٨ - النموذج الرقمي (تجربة)")
SRC = {"بنين": os.path.join(D8, "منصة الحصة الموحَّدة — ابن خلدون.html"),
       "بنات": os.path.join(D8, "منصة الحصة الموحَّدة — ابن خلدون (بنات).html")}
WIDTHS = [320, 390, 430, 768]
# (الدور، المرحلة، التبويب، أبها حصةٌ مفتوحة)
VIEWS = [("teacher", 1, "fill", False), ("teacher", 2, "", True),
         ("supervisor", 3, "", True), ("principal", 5, "", False)]
FLOOR = len(WIDTHS) * len(VIEWS) * len(SRC)      # ٣٢ شاشة
MIN_OVERLAP = 4                                  # بكسل — أقلُّ منه حدُّ رسمٍ لا تداخل

BOOT = r"""
<script>
window.__RUN = function(role, ph, tab, open_){
 try{
  localStorage.clear(); load();
  var SEC=D.sectors[0], CX=D.complexlist[0], bands=(D.bands[CX]||[]);
  var wk=D.weeks[0], day=D.days[0];
  var gp=((D.rot[CX]||{})[wk]||{})[day]||Object.keys(D.pairs)[0];
  var sp=(D.pairs[gp]||D.specs)[0], b=bands[0];
  if(open_){
    var L={id:"ov1",sector:SEC,complex:CX,stage:b.stage,school:b.stage,period:b.per,
      week:wk,day:day,spec:sp,teacher:"أ. المقياس",klass:"١/أ",grade:"الصف الرابع",
      topic:"درسُ القياس",pages:"٢٤ — ٢٧",time:b.time,
      strategy:(D.bank[0]||{}).name,approach:D.approaches[0]};
    L.gk=[L.sector,L.complex,L.stage,L.period,L.week,L.day,L.spec].join("|");
    DB.sched=[L]; DB.prep["ov1"]={__issued:"١١ أكتوبر", i_teacher:"أ. المقياس"};
  }
  var SUP=(D.sups||[]).filter(function(r){return !r.allsubj && r.subjects.length===1;})[0];
  var me={role:role,name:"أ. المقياس",emp:"30100",spec:sp};
  if(role==="supervisor"&&SUP){ me.name=SUP.name; me.emp=SUP.emp; }
  if(role==="principal"||role==="deputy"){ me.sector=SEC; me.complex=CX; me.school=b.stage; }
  ME=me; localStorage.setItem(KEY+"_me", JSON.stringify(ME));
  try{ localStorage.removeItem(KEY+"_ctx"); }catch(e){}
  GS=null; PH=ph; CUR=open_?"ov1":null; save(); shell();
  if(tab){ setctx("tab",tab); shell(); }

  function vis(e){
    var r=e.getBoundingClientRect();
    var L2=r.left,T=r.top,R2=r.right,B=r.bottom;
    for(var q=e.parentElement;q&&q!==document.documentElement;q=q.parentElement){
      var qs=getComputedStyle(q);
      if(!/(auto|scroll|hidden)/.test(qs.overflowX+" "+qs.overflowY)) continue;
      var rq=q.getBoundingClientRect();
      L2=Math.max(L2,rq.left); T=Math.max(T,rq.top);
      R2=Math.min(R2,rq.right); B=Math.min(B,rq.bottom);
    }
    if(R2<=L2||B<=T) return null;
    return {left:L2,top:T,right:R2,bottom:B,width:R2-L2,height:B-T};
  }
  var leaf=[].slice.call(document.querySelectorAll("body *")).filter(function(e){
    if(e.children.length) return false;
    if(!(e.textContent||"").trim()) return false;
    var s=getComputedStyle(e);
    if(s.display==="none"||s.visibility==="hidden"||+s.opacity===0) return false;
    for(var q=e;q&&q!==document.body;q=q.parentElement){
      var qs=getComputedStyle(q);
      if(qs.position==="fixed"||qs.position==="absolute"||qs.position==="sticky") return false;
    }
    var r=vis(e);
    return !!r && r.width>4 && r.height>4;
  });
  var hits=[];
  for(var i=0;i<leaf.length;i++)for(var j=i+1;j<leaf.length;j++){
    var a=leaf[i],bb=leaf[j];
    if(a.contains(bb)||bb.contains(a)) continue;
    var ra=vis(a), rb=vis(bb); if(!ra||!rb) continue;
    var ox=Math.min(ra.right,rb.right)-Math.max(ra.left,rb.left);
    var oy=Math.min(ra.bottom,rb.bottom)-Math.max(ra.top,rb.top);
    if(ox>__MIN__ && oy>__MIN__)
      hits.push({a:(a.textContent||"").trim().slice(0,30),
                 b:(bb.textContent||"").trim().slice(0,30),
                 ox:Math.round(ox),oy:Math.round(oy)});
  }
  return {n:leaf.length, hits:hits.slice(0,6)};
 }catch(e){ return {err:String(e).slice(0,90)}; }
};
</script>
"""

HOST = """<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0}iframe{width:%dpx;height:844px;border:0}</style></head><body>
<iframe id="f" src="%s"></iframe><pre id="out"></pre>
<script>
var JOBS = %s;
setTimeout(function(){
  var R=[];
  try{
    for(var i=0;i<JOBS.length;i++){
      var j=JOBS[i];
      R.push({v:j[0]+"/"+j[1]+(j[2]?"/"+j[2]:""),
              r:f.contentWindow.__RUN(j[3],j[4],j[5],j[6])});
    }
  }catch(e){ R.push({v:"FATAL", r:{err:String(e).slice(0,90)}}); }
  document.getElementById("out").textContent = JSON.stringify(R);
}, 2200);
</script></body></html>"""


def run(lbl, src, width):
    p = PRB.probe("ov_%s_%d.html" % (lbl, width))
    open(p, "w", encoding="utf-8").write(
        open(src, encoding="utf-8").read() + BOOT.replace("__MIN__", str(MIN_OVERLAP)))
    jobs = [[v[0], v[1], v[2], v[0], v[1], v[2], v[3]] for v in VIEWS]
    h = PRB.probe("ovh_%s_%d.html" % (lbl, width))
    open(h, "w", encoding="utf-8").write(
        HOST % (width, "file://" + p.replace(" ", "%20"), json.dumps(jobs, ensure_ascii=False)))
    out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                          "--allow-file-access-from-files", "--virtual-time-budget=20000",
                          "--window-size=1500,1100", "--dump-dom", "file://" + h],
                         capture_output=True, text=True).stdout
    os.remove(p); os.remove(h)
    m = re.search(r'<pre id="out">(.*?)</pre>', out, re.S)
    return json.loads(H.unescape(m.group(1))) if (m and m.group(1).strip()) else []


def main():
    seen = bad = 0
    for lbl, src in SRC.items():
        for w in WIDTHS:
            rows = run(lbl, src, w)
            if not rows:
                print("  ⛔ %s / %d — لم يُقَس شيء" % (lbl, w)); bad += 1; continue
            for r in rows:
                d = r.get("r") or {}
                if d.get("err"):
                    print("  ⛔ %s · %s / %d — سقطت: %s" % (lbl, r["v"], w, d["err"]))
                    bad += 1; continue
                seen += 1
                for x in d.get("hits", []):
                    bad += 1
                    print("  ⛔ %s · %s / %d — «%s» × «%s» (%d×%d بكسل)"
                          % (lbl, r["v"], w, x["a"], x["b"], x["ox"], x["oy"]))
    print("  شاشاتٌ مقيسة: %d · تداخلات: %d" % (seen, bad))
    if seen < FLOOR:
        print("⛔ الأرضيّة %d ووُجد %d — الفحصُ لم يَقِس ما يكفي." % (FLOOR, seen))
        return 1
    if bad:
        print("⛔ نصٌّ يركب نصّاً — لا يُسلَّم.")
        return 1
    print("  ✓ لا نصَّ يركب نصّاً على أيِّ عرض")
    return 0


if __name__ == "__main__":
    sys.exit(main())
