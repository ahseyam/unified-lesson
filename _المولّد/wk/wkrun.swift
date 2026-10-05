import Cocoa
import WebKit

// مُشغّلٌ صغيرٌ يفتح صفحةً في WebKit (محرّكُ سفاري وآيفون) ثم ينفّذ جافاسكربت
// ويطبع النتيجة. لا يحتاج أتمتةَ سفاري ولا إذناً — فالإطارُ في النظام.
let args = CommandLine.arguments
guard args.count >= 3 else { print("usage: wkrun <url> <js-file> [width] [height] [waitMs]"); exit(2) }
let url = URL(string: args[1])!
let js = (try? String(contentsOfFile: args[2], encoding: .utf8)) ?? ""
let w = args.count > 3 ? Double(args[3])! : 390
let h = args.count > 4 ? Double(args[4])! : 844
let waitMs = args.count > 5 ? Int(args[5])! : 6000

let app = NSApplication.shared
app.setActivationPolicy(.prohibited)

final class Runner: NSObject, WKNavigationDelegate {
    let web: WKWebView
    let js: String
    let waitMs: Int
    init(frame: CGRect, js: String, waitMs: Int) {
        let cfg = WKWebViewConfiguration()
        cfg.preferences.javaScriptEnabled = true
        self.web = WKWebView(frame: frame, configuration: cfg)
        self.js = js; self.waitMs = waitMs
        super.init()
        web.navigationDelegate = self
    }
    func webView(_ wv: WKWebView, didFinish nav: WKNavigation!) {
        DispatchQueue.main.asyncAfter(deadline: .now() + .milliseconds(waitMs)) {
            wv.evaluateJavaScript(self.js) { res, err in
                if let e = err { FileHandle.standardError.write("JSERR \(e)\n".data(using: .utf8)!); print("{}") }
                else if let s = res as? String { print(s) }
                else { print(String(describing: res ?? "null")) }
                exit(0)
            }
        }
    }
    func webView(_ wv: WKWebView, didFail nav: WKNavigation!, withError e: Error) {
        FileHandle.standardError.write("NAVFAIL \(e)\n".data(using: .utf8)!); exit(3)
    }
    func webView(_ wv: WKWebView, didFailProvisionalNavigation nav: WKNavigation!, withError e: Error) {
        FileHandle.standardError.write("NAVFAIL2 \(e)\n".data(using: .utf8)!); exit(3)
    }
}
let r = Runner(frame: CGRect(x: 0, y: 0, width: w, height: h), js: js, waitMs: waitMs)
r.web.load(URLRequest(url: url))
DispatchQueue.main.asyncAfter(deadline: .now() + .milliseconds(waitMs + 25000)) {
    FileHandle.standardError.write("TIMEOUT\n".data(using: .utf8)!); exit(4)
}
app.run()
