from http.server import HTTPServer, BaseHTTPRequestHandler
import os

class WhitespaceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        
        ws_code = "（app.ws が見つかりません）"
        if os.path.exists("app.ws"):
            with open("app.ws", "r", encoding="utf-8", errors="ignore") as f:
                ws_code = f.read()
                
        # 空白やタブ、改行をあらかじめ置換しておく
        visual_code = ws_code.replace(" ", "␣").replace("\t", "→\t").replace("\n", "↵\n")
        
        # カウント数を変数に保持（f-string内で関数を呼ばない）
        space_count = ws_code.count(' ')
        tab_count = ws_code.count('\t')
        line_count = ws_code.count('\n')

        html = f"""<html>
            <head><title>Whitespace Web Server</title></head>
            <body style="font-family: monospace; padding: 30px; background: #1e1e1e; color: #d4d4d4;">
                <h2>🌌 Whitespace Web Inspector</h2>
                <h3>📄 app.ws のソースコード</h3>
                <pre style="background: #2d2d2d; padding: 15px; border-radius: 5px; color: #4ec9b0; overflow-x: auto;">{visual_code}</pre>
                <h3>🚀 解析結果</h3>
                <div style="background: #2d2d2d; padding: 15px; border-radius: 5px; color: #ce9178;">
                    スペースの数: {space_count} 個<br>
                    タブの数: {tab_count} 個<br>
                    改行の数: {line_count} 個
                </div>
            </body>
        </html>"""
        self.wfile.write(html.encode('utf-8'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), WhitespaceHandler)
    server.serve_forever()
