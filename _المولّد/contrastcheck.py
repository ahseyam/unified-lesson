# -*- coding: utf-8 -*-
"""⛔ «غيّرتُ اللون» ليست «صار يُقرأ»: يُقاس **تباينُ كل نصٍّ مع خلفيته
   الفعلية** في كل شاشةٍ ولكل دور، بمعيار WCAG.

⚠️ والخلفيةُ الفعليةُ تُتتبَّع صعوداً في الآباء حتى أولِ لونٍ غيرِ شفّاف —
   فالعنصرُ الشفّافُ يرث خلفيةَ أبيه، ولا يُقاس على «transparent».

الحدّ: ٤٫٥ للنصّ العادي و٣٫٠ للكبير (١٨٫٦٦بك فأكثر، أو ١٤بك عريض)."""
import html as H, json, os, re, subprocess, sys
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE=os.path.dirname(os.path.abspath(__file__))
D8="/Users/ahmadseyam/Desktop/نموذج تحضير الدرس - بطاقة الملاحظة الصفية/٨ - النموذج الرقمي (تجربة)"
import i18ncheck_en as T   # ⛔ كان «test_en» باسمه القديم فلم يكن الفحصُ يعمل
import probedir as PRB   # نسخُ الفحص خارج شجرة التسليم

BOOT = r"""
<script>
function _rgb(s){ var m=String(s).match(/[\d.]+/g); return m ? m.map(Number) : null; }
function _lum(c){
  var a=c.slice(0,3).map(function(v){ v/=255;
    return v<=0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055,2.4); });
  return 0.2126*a[0]+0.7152*a[1]+0.0722*a[2];
}
function _bg(e){
  /* ⛔ تُتتبَّع الخلفيةُ صعوداً: الشفّافُ يرث، ولا يُقاس عليه.
     ⚠️ **والمتدرِّجُ خلفيةٌ أيضاً**: الهيدرُ والشريطُ الجانبيُّ بخلفيةٍ
        متدرِّجة، و`backgroundColor` يُرجع لها الشفّافَ — فمشى الماسحُ إلى
        الجسم وقال «أبيضُ على أبيض» في ستِّ مئةِ موضعٍ سليم. فيُقرأ أولُ
        لونٍ في `backgroundImage` متى كان متدرِّجاً. */
  for(var n=e; n && n !== document.documentElement; n=n.parentElement){
    var st=getComputedStyle(n);
    var c=_rgb(st.backgroundColor);
    if(c && (c.length<4 || c[3]>0.95)) return c;
    var bi=st.backgroundImage;
    if(bi && bi.indexOf("gradient") >= 0){
      var g=bi.match(/rgba?\([^)]+\)/g);
      if(g && g.length){
        var f=_rgb(g[0]);
        if(f && (f.length<4 || f[3]>0.5)) return f;
      }
    }
  }
  return [255,255,255];
}
function _ratio(f,b){
  var L1=_lum(f), L2=_lum(b);
  return (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
}
/* ⛔ كان الماسحُ يُرجع **العيوبَ وحدَها** — فلا أحدَ يعلم كم نصّاً قاسه.
   ومن مسح صفراً يُرجع صفرَ عيوبٍ فيُعلن «لا نصَّ دون الحدّ». فصار يُرجع
   العددَ معها، وله أرضيّة. (أمسكه وكيلُ مراجعة الحرّاس ١ أكتوبر ٢٠٢٦) */
window.__scan = function(){
  var out=[], seen={}, n=0;
  [].slice.call(document.querySelectorAll("body *")).forEach(function(e){
    if(!e.offsetParent && e.tagName!=="BODY") return;
    var t="";
    [].slice.call(e.childNodes).forEach(function(n){
      if(n.nodeType===3) t += n.nodeValue; });
    t=t.trim(); if(t.length<2) return;
    var st=getComputedStyle(e);
    if(st.visibility==="hidden"||st.display==="none"||parseFloat(st.opacity)<0.3) return;
    var f=_rgb(st.color); if(!f) return;
    var b=_bg(e), r=_ratio(f,b);
    n++;
    var sz=parseFloat(st.fontSize), bold=(parseInt(st.fontWeight,10)||400)>=700;
    var need=(sz>=18.66||(sz>=14&&bold))?3.0:4.5;
    if(r < need){
      var k=t.slice(0,40)+"|"+st.color+"|"+r.toFixed(2);
      if(seen[k]) return; seen[k]=1;
      out.push([t.slice(0,46), st.color, "rgb("+b.slice(0,3).join(",")+")",
                Math.round(r*100)/100, need, Math.round(sz)]);
    }
  });
  return {n: n, bad: out};
};
</script>
"""

def run(src, tag, lang):
    boot = (T.BOOT.replace("__VIEWS__", json.dumps(T.VIEWS))
                  .replace('setLang("en")', 'setLang("%s")' % lang)
                  .replace("__T__","أ. نموذج").replace("__P__","أ. زائر").replace("__A__","مستشار"))
    boot = boot.replace('__R.push([role+"/"+ph+"/"+(tab||"-"), (document.body.innerText||"")]);',
                        '__R.push([role+"/"+ph+"/"+(tab||"-"), window.__scan()]);')
    boot = boot.replace('__R.push(["login/-/-", (document.body.innerText||"")]);',
                        '__R.push(["login/-/-", window.__scan()]);')
    p=PRB.probe("ct_%s_%s.html"%(tag,lang))
    open(p,"w",encoding="utf-8").write(open(src,encoding="utf-8").read()+BOOT+boot
      +'<script>setTimeout(function(){var d=document.createElement("pre");d.id="dump";'
       'd.textContent=window.__OUT||"";document.body.appendChild(d);},1500);</script>')
    out=subprocess.run([CHROME,"--headless=new","--disable-gpu","--no-sandbox",
        "--window-size=1500,1000","--virtual-time-budget=14000","--dump-dom","file://"+p],
        capture_output=True,text=True).stdout
    m=re.search(r'<pre id="dump">(.*?)</pre>',out,re.S)
    if not m or not m.group(1).strip():
        t=re.search(r"<title>(.*?)</title>",out,re.S)
        print("  ⛔ %s/%s لم يُقس: %s"%(tag,lang,H.unescape(t.group(1)) if t else "?")); return False
    rows=json.loads(H.unescape(m.group(1)))
    bad=[]; seen_n=0
    for name,items in rows:
        # ⚠️ الماسحُ صار يُرجع {n, bad} — والقديمُ كان مصفوفةَ عيوبٍ وحدَها
        if isinstance(items, dict):
            seen_n += items.get("n") or 0
            for it in (items.get("bad") or []): bad.append([name]+it)
        else:
            for it in items: bad.append([name]+it)
    FLOOR = 400      # أقلُّ ما يُقاس في شاشاتٍ حقيقيةٍ — ودونه لم يُقَس شيء
    if seen_n < FLOOR:
        print("  ⛔ %s/%-3s  %d نصّاً مقيساً فقط — والأرضيّةُ %d. الفحصُ لم يَقِس، فهو فاشل."
              % (tag, lang, seen_n, FLOOR)); return False
    if not bad:
        print("  ✓ %s/%-3s  %d نصّاً مقيساً · لا واحدَ دون الحدّ"%(tag,lang,seen_n)); return True
    print("  ⛔ %s/%-3s  %d نصّاً دون حدّ التباين:"%(tag,lang,len(bad)))
    seen=set()
    for nm,t,fg,bg,r,need,sz in bad:
        k=(t,fg,bg)
        if k in seen: continue
        seen.add(k)
        print("       «%-30s» %s على %s = %.2f (المطلوب %.1f) [%s]"%(t,fg,bg,r,need,nm))
    return False

ok=True
# ⛔ وكان يفحص البنين وحدَهم — ونسخةُ البنات لها معجمُها ومؤنَّثاتُها وألقابُها
#    وقد تختلف أطوالُ نصوصها فتُخرج عنصراً عن حدِّه. (١ أكتوبر ٢٠٢٦)
for tag,fn in (("بنين","منصة الحصة الموحَّدة — ابن خلدون.html"),
               ("بنات","منصة الحصة الموحَّدة — ابن خلدون (بنات).html")):
    for lang in ("ar","en"):
        ok &= run(os.path.join(D8,fn),tag,lang)
sys.exit(0 if ok else 1)
