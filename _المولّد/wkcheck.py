# -*- coding: utf-8 -*-
"""حارسُ WebKit — المنصةُ على محرّك سفاري وآيفون لا على كروم وحدَه.

⛔ **كلُّ حرّاسي كانت كروم**، فما قيل عن iOS كان استنتاجاً لا قياساً. وأتمتةُ
   سفاري تحتاج تمكيناً يدويّاً، فبُني مُشغّلٌ صغيرٌ بـ`WKWebView` من إطار
   النظام (`wkrun.swift`) — **لا إذنَ ولا نقرة**، والمحرّكُ هو هو.

⚠️ ويُخدَم الملفُّ عبر http لا من القرص: `file:` يمنع `fetch` النسبيَّ ويمنع
   الانضمامَ المبنيَّ — فالفحصُ من القرص يمرُّ بلا أن يقيس ما يراه المستخدم.
⚠️ **ولا يُكتب في قاعدة المدارس**: أولُ ما يفعله المسبارُ `localStorage.clear()`
   فيسقط عنوانُ المخزن، ولا دفعةَ بلا عنوان. (وقد وقع هذا فعلاً: مسابرُ
   كروم سحبت بياناتِ معلماتٍ حقيقيات قبل أن أُغلقه — ٥ أكتوبر ٢٠٢٦.)

ما يُقاس على مقاسات الآيفون: ألّا يفيض شيءٌ عن عرض الشاشة · ألّا يركب نصٌّ
نصّاً · ألّا تكون شاشةٌ خاويةً أو بلا مخرج · وأن يُقلع التطبيقُ أصلاً.
"""
import http.server
import json
import os
import re
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# ⚠️ المُشغّلُ يُبنى عند أول حاجةٍ من مصدره المجاور — فلا يعتمد الحارسُ على
#    ملفٍّ في `/tmp` يُمحى عند إعادة التشغيل، ولا يُشحن ثنائيٌّ في المستودع.
WK = os.path.join(tempfile.gettempdir(), "wkrun_ikc")
SWIFT = os.path.join(HERE, "wk", "wkrun.swift")


def ensure_runner():
    if os.path.exists(WK) and os.path.getmtime(WK) >= os.path.getmtime(SWIFT):
        return True
    r = subprocess.run(["swiftc", "-O", "-o", WK, SWIFT], capture_output=True, text=True)
    return os.path.exists(WK)
D8 = os.path.join(ROOT, "٨ - النموذج الرقمي (تجربة)")
SRC = {"بنين": "منصة الحصة الموحَّدة — ابن خلدون.html",
       "بنات": "منصة الحصة الموحَّدة — ابن خلدون (بنات).html"}
# مقاساتُ آيفون الحقيقية (نقاطٌ لا بكسلات)
SIZES = [("آيفون SE 375", 375, 667), ("آيفون 14 390", 390, 844),
         ("آيفون برو ماكس 430", 430, 932), ("آيفون أفقي 844", 844, 390)]
VIEWS = [("teacher", 1, "fill"), ("supervisor", 3, ""), ("deputy", 5, "")]
FLOOR = len(SIZES) * len(VIEWS) * len(SRC)

JS = r"""
(function(){
 try{
  localStorage.clear(); load();
  var SEC=D.sectors[0], CX=D.complexlist[0], bands=(D.bands[CX]||[]);
  var wk=D.weeks[0], day=D.days[0];
  var gp=((D.rot[CX]||{})[wk]||{})[day]||Object.keys(D.pairs)[0];
  var sp=(D.pairs[gp]||D.specs)[0], b=bands[0];
  var L={id:"wk1",sector:SEC,complex:CX,stage:b.stage,school:b.stage,period:b.per,
    week:wk,day:day,spec:sp,teacher:"أ. القياس",klass:"١/أ",grade:"الصف الرابع",
    topic:"درسٌ",pages:"٢٤",time:b.time,strategy:(D.bank[0]||{}).name,approach:D.approaches[0]};
  L.gk=[L.sector,L.complex,L.stage,L.period,L.week,L.day,L.spec].join("|");
  DB.sched=[L]; DB.prep["wk1"]={__issued:"١١ أكتوبر"};
  var SUP=(D.sups||[]).filter(function(r){return !r.allsubj && r.subjects.length===1;})[0];
  var me={role:"__ROLE__",name:"أ. القياس",emp:"30100",spec:sp};
  if(me.role==="supervisor"&&SUP){ me.name=SUP.name; me.emp=SUP.emp; }
  if(me.role==="deputy"){ me.sector=SEC; me.complex=CX; me.school=b.stage; }
  ME=me; GS=null; PH=__PH__; CUR=(__PH__===3?"wk1":null); shell();
  if("__TAB__"){ setctx("tab","__TAB__"); shell(); }

  function vis(e){
    var r=e.getBoundingClientRect(), L2=r.left,T=r.top,R=r.right,B=r.bottom;
    for(var q=e.parentElement;q&&q!==document.documentElement;q=q.parentElement){
      var qs=getComputedStyle(q);
      if(!/(auto|scroll|hidden)/.test(qs.overflowX+" "+qs.overflowY)) continue;
      var rq=q.getBoundingClientRect();
      L2=Math.max(L2,rq.left); T=Math.max(T,rq.top);
      R=Math.min(R,rq.right); B=Math.min(B,rq.bottom);
    }
    if(R<=L2||B<=T) return null;
    return {left:L2,top:T,right:R,bottom:B,width:R-L2,height:B-T};
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
    var r=vis(e); return !!r && r.width>4 && r.height>4;
  });
  var over=[];
  for(var i=0;i<leaf.length;i++)for(var j=i+1;j<leaf.length;j++){
    var a=leaf[i],bb=leaf[j];
    if(a.contains(bb)||bb.contains(a)) continue;
    var ra=vis(a), rb=vis(bb); if(!ra||!rb) continue;
    var ox=Math.min(ra.right,rb.right)-Math.max(ra.left,rb.left);
    var oy=Math.min(ra.bottom,rb.bottom)-Math.max(ra.top,rb.top);
    if(ox>4&&oy>4) over.push((a.textContent||"").trim().slice(0,22)+" × "+
                             (bb.textContent||"").trim().slice(0,22));
  }
  var W=document.documentElement.clientWidth, spill=[];
  [].slice.call(document.querySelectorAll("body *")).forEach(function(e){
    var s=getComputedStyle(e);
    if(s.position==="fixed") return;
    var r=e.getBoundingClientRect();
    if(r.width>0 && (r.right>W+2 || r.left<-2)){
      for(var q=e.parentElement;q&&q!==document.body;q=q.parentElement){
        var qs=getComputedStyle(q);
        if(/(auto|scroll)/.test(qs.overflowX)) return;
      }
      spill.push((e.textContent||e.tagName).trim().slice(0,22));
    }
  });
  var m=document.querySelector("main")||document.body;
  return JSON.stringify({w:W, n:leaf.length,
    txt:(m.innerText||"").replace(/\s+/g," ").trim().length,
    acts:m.querySelectorAll("button,a[href],input,select,textarea").length,
    over:over.slice(0,5), spill:spill.slice(0,5)});
 }catch(e){ return JSON.stringify({fatal:String(e).slice(0,140)}); }
})();
"""


def serve(d):
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k): super().__init__(*a, directory=d, **k)
        def log_message(self, *a): pass
    socketserver.TCPServer.allow_reuse_address = True
    s = socketserver.TCPServer(("127.0.0.1", 0), H)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, s.server_address[1]


def main():
    if not ensure_runner():
        print("⛔ تعذّر بناءُ مُشغّل WebKit من", SWIFT); return 1
    tmp = tempfile.mkdtemp(); os.makedirs(os.path.join(tmp, "p"))
    srv, port = serve(tmp)
    seen = bad = 0
    for lbl, fn in SRC.items():
        shutil.copy(os.path.join(D8, fn), os.path.join(tmp, "p", "page.html"))
        for role, ph, tab in VIEWS:
            jsf = os.path.join(tmp, "probe.js")
            open(jsf, "w", encoding="utf-8").write(
                JS.replace("__ROLE__", role).replace("__PH__", str(ph)).replace("__TAB__", tab))
            for nm, w, h in SIZES:
                r = subprocess.run([WK, "http://127.0.0.1:%d/p/page.html" % port, jsf,
                                    str(w), str(h), "5200"],
                                   capture_output=True, text=True, timeout=90)
                try:
                    d = json.loads(r.stdout.strip() or "{}")
                except Exception:
                    d = {}
                tag = "%s · %s/%s%s · %s" % (lbl, role, ph, ("/" + tab if tab else ""), nm)
                if d.get("fatal") or not d:
                    print("  ⛔ %-44s سقطت: %s" % (tag, (d.get("fatal") or r.stderr.strip())[:70]))
                    bad += 1; continue
                if d.get("w") != w:
                    print("  ⛔ %-44s قيس على %s لا %d" % (tag, d.get("w"), w)); bad += 1; continue
                seen += 1
                why = []
                if d.get("over"): why.append("تداخل: " + " | ".join(d["over"]))
                if d.get("spill"): why.append("فيضان: " + " | ".join(d["spill"]))
                if d.get("txt", 0) < 260: why.append("خاوية %d حرفاً" % d.get("txt", 0))
                if d.get("acts", 0) < 1: why.append("مسدودة")
                if why:
                    bad += 1
                    print("  ⛔ %-44s %s" % (tag, " · ".join(why)[:90]))
    srv.shutdown(); shutil.rmtree(tmp, ignore_errors=True)
    print("  شاشاتٌ مقيسةٌ على WebKit: %d · معيبة: %d" % (seen, bad))
    if seen < FLOOR:
        print("⛔ الأرضيّة %d ووُجد %d — لم يُقَس ما يكفي." % (FLOOR, seen)); return 1
    if bad:
        print("⛔ المنصةُ على محرّك سفاري لا تُسلَّم."); return 1
    print("  ✓ لا فيضانَ ولا تداخلَ ولا شاشةَ خاويةٍ على محرّك سفاري")
    return 0


if __name__ == "__main__":
    sys.exit(main())
