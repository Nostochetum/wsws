from http.server import HTTPServer, BaseHTTPRequestHandler
import os

def parse_and_run_whitespace(code):
    """Whitespace実行エンジン（日本語UTF-8出力対応）"""
    # 余計なスペースが入らないよう修正
    cleaned = [c for c in code if c in (' ', '\t', '\n')]
    
    tokens = []
    for c in cleaned:
        if c == ' ':
            tokens.append('S')
        elif c == '\t':
            tokens.append('T')
        elif c == '\n':
            tokens.append('L')
            
    stack = []
    output_bytes = bytearray()
    idx = 0
    length = len(tokens)
    
    try:
        while idx < length:
            if tokens[idx] == 'S':
                idx += 1
                if idx < length and tokens[idx] == 'S':
                    idx += 1
                    if idx < length:
                        sign = 1 if tokens[idx] == 'S' else -1
                        idx += 1
                        val = 0
                        while idx < length and tokens[idx] != 'L':
                            val = (val << 1) | (1 if tokens[idx] == 'T' else 0)
                            idx += 1
                        idx += 1
                        stack.append(sign * val)
                elif idx < length and tokens[idx] == 'L':
                    idx += 1
                    if idx < length and tokens[idx] == 'S':
                        idx += 1
                        if stack:
                            stack.append(stack[-1])
                    elif idx < length and tokens[idx] == 'L':
                        idx += 1
                        if stack:
                            stack.pop()
                else:
                    idx += 1

            elif tokens[idx] == 'T' and idx + 1 < length and tokens[idx+1] == 'L':
                idx += 2
                if idx < length and tokens[idx] == 'S':
                    idx += 1
                    if idx < length and tokens[idx] == 'S':
                        idx += 1
                        if stack:
                            char_code = stack.pop()
                            # バイト列として追加（UTF-8文字の正しい結合）
                            output_bytes.append(char_code & 0xFF)
                    elif idx < length and tokens[idx] == 'T':
                        idx += 1
                        if stack:
                            output_bytes.extend(str(stack.pop()).encode('utf-8'))
                else:
                    idx += 1
            else:
                idx += 1

        res = output_bytes.decode('utf-8', errors='replace')
        return res if res else "（出力結果はありませんでした）"
    except Exception as e:
        return f"実行時エラー: {str(e)}"

class WhitespaceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        
        ws_code = ""
        if os.path.exists("app.ws"):
            with open("app.ws", "r", encoding="utf-8", errors="ignore") as f:
                ws_code = f.read()
                
        visual_code = ws_code.replace(" ", "␣").replace("\t", "→\t").replace("\n", "↵\n")
        
        execution_result = parse_and_run_whitespace(ws_code)
        space_count = ws_code.count(' ')
        tab_count = ws_code.count('\t')
        line_count = ws_code.count('\n')

        html = f"""<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Whitespace Web Server</title>
    </head>
    <body style="font-family: sans-serif; padding: 30px; background: #1e1e1e; color: #d4d4d4;">
        <h2>🌌 Whitespace Web Inspector & Runner</h2>
        
        <!-- 実行結果を一番上に表示 -->
        <h3>🚀 実行結果</h3>
        <pre style="background: #2d2d2d; padding: 20px; border-radius: 8px; color: #ce9178; white-space: pre-wrap; font-family: monospace; font-size: 1.4em; border: 1px solid #444;">{execution_result}</pre>
        
        <h3>📄 app.ws のソースコード</h3>
        <pre style="background: #2d2d2d; padding: 15px; border-radius: 5px; color: #4ec9b0; overflow-x: auto; font-family: monospace;">{visual_code}</pre>
        
        <!-- 下部にカウンターを表示 -->
        <h3>📊 コード解析 (文字数統計)</h3>
        <div style="background: #2d2d2d; padding: 15px; border-radius: 5px; color: #9cdcfe; font-family: monospace;">
            スペースの数: <strong>{space_count}</strong> 個<br>
            タブの数: <strong>{tab_count}</strong> 個<br>
            改行の数: <strong>{line_count}</strong> 個
        </div>
    </body>
</html>"""
        self.wfile.write(html.encode('utf-8'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), WhitespaceHandler)
    server.serve_forever()
