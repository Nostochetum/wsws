from http.server import HTTPServer, BaseHTTPRequestHandler
import os

def parse_and_run_whitespace(code):
    """簡易Whitespace実行エンジン"""
    # 空白文字(Space, Tab, LF)以外を取り除く
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
    output = []
    idx = 0
    length = len(tokens)
    
    try:
        while idx < length:
            # IMP (Instruction Modification Parameter) 解析
            if tokens[idx] == 'S': # Stack Manipulation
                idx += 1
                if idx < length and tokens[idx] == 'S': # Push
                    idx += 1
                    # 数値取得 (S=0, T=1)
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
                    if idx < length and tokens[idx] == 'S': # Duplicate top
                        idx += 1
                        if stack:
                            stack.append(stack[-1])
                    elif idx < length and tokens[idx] == 'L': # Discard top
                        idx += 1
                        if stack:
                            stack.pop()
                else:
                    idx += 1

            elif tokens[idx] == 'T' and idx + 1 < length and tokens[idx+1] == 'L': # I/O
                idx += 2
                if idx < length and tokens[idx] == 'S': # Output Character
                    idx += 1
                    if idx < length and tokens[idx] == 'S':
                        idx += 1
                        if stack:
                            char_code = stack.pop()
                            output.append(chr(char_code))
                    elif idx < length and tokens[idx] == 'T': # Output Number
                        idx += 1
                        if stack:
                            output.append(str(stack.pop()))
                else:
                    idx += 1
            else:
                idx += 1

        res = "".join(output)
        return res if res else "（出力結果はありませんでした。文字出力命令がないか処理未対応のプログラミング構造が含まれています）"
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
        
        # 実際にWhitespaceを実行して結果を取得
        execution_result = parse_and_run_whitespace(ws_code)

        html = f"""<html>
            <head><title>Whitespace Web Server</title></head>
            <body style="font-family: monospace; padding: 30px; background: #1e1e1e; color: #d4d4d4;">
                <h2>🌌 Whitespace Web Inspector & Runner</h2>
                
                <h3>📄 app.ws のソースコード</h3>
                <pre style="background: #2d2d2d; padding: 15px; border-radius: 5px; color: #4ec9b0; overflow-x: auto;">{visual_code}</pre>
                
                <h3>🚀 実行結果</h3>
                <pre style="background: #2d2d2d; padding: 15px; border-radius: 5px; color: #ce9178; white-space: pre-wrap;">{execution_result}</pre>
            </body>
        </html>"""
        self.wfile.write(html.encode('utf-8'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), WhitespaceHandler)
    server.serve_forever()
