from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import urllib.parse

def parse_and_run_whitespace(code, stdin_text=""):
    """Whitespace実行エンジン（標準入力・数値/文字出力修正版）"""
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
    heap = {}
    output_buf = []
    input_chars = list(stdin_text)
    idx = 0
    length = len(tokens)
    
    try:
        while idx < length:
            if tokens[idx] == 'S':  # Stack Manipulation
                idx += 1
                if idx < length and tokens[idx] == 'S':  # Push
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
                    if idx < length and tokens[idx] == 'S':  # Duplicate
                        idx += 1
                        if stack:
                            stack.append(stack[-1])
                    elif idx < length and tokens[idx] == 'L':  # Discard
                        idx += 1
                        if stack:
                            stack.pop()
                else:
                    idx += 1

            elif tokens[idx] == 'T':  # I/O or Heap
                idx += 1
                if idx < length and tokens[idx] == 'L':  # I/O
                    idx += 1
                    if idx < length and tokens[idx] == 'S':  # Output
                        idx += 1
                        if idx < length and tokens[idx] == 'S':  # Output Char
                            idx += 1
                            if stack:
                                char_code = stack.pop()
                                output_buf.append(chr(char_code & 0xFF))
                        elif idx < length and tokens[idx] == 'T':  # Output Num
                            idx += 1
                            if stack:
                                num_val = stack.pop()
                                output_buf.append(str(num_val))
                    elif idx < length and tokens[idx] == 'T':  # Input
                        idx += 1
                        if idx < length and tokens[idx] == 'S':  # Read Char
                            idx += 1
                            if stack:
                                addr = stack.pop()
                                char_val = ord(input_chars.pop(0)) if input_chars else 0
                                heap[addr] = char_val
                        elif idx < length and tokens[idx] == 'T':  # Read Num (1行から整数読み取り)
                            idx += 1
                            if stack:
                                addr = stack.pop()
                                num_str = ""
                                # 余白や改行をスキップ
                                while input_chars and input_chars[0] not in '0123456789-':
                                    input_chars.pop(0)
                                while input_chars and input_chars[0] in '0123456789-':
                                    num_str += input_chars.pop(0)
                                heap[addr] = int(num_str) if num_str else 0
                else:
                    idx += 1
            else:
                idx += 1

        res = "".join(output_buf)
        return res if res else "（出力結果はありませんでした）"
    except Exception as e:
        return f"実行時エラー: {str(e)}"

class WhitespaceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()

        if path == "/test":
            html = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Whitespace Code Test</title>
    </head>
    <body style="font-family: sans-serif; padding: 30px; background: #1e1e1e; color: #d4d4d4;">
        <h2>🧪 Whitespace コードテスト</h2>
        <form action="/test" method="POST">
            <h3>📄 ソースコード</h3>
            <textarea name="code" style="width: 100%; height: 180px; background: #2d2d2d; color: #4ec9b0; font-family: monospace; padding: 10px; border: 1px solid #444; border-radius: 5px;" placeholder="Whitespaceコードを入力..."></textarea>
            
            <h3>📥 標準入力 (stdin)</h3>
            <textarea name="stdin" style="width: 100%; height: 70px; background: #2d2d2d; color: #ce9178; font-family: monospace; padding: 10px; border: 1px solid #444; border-radius: 5px;" placeholder="プログラムへ渡す入力値（例: 32）"></textarea><br><br>
            
            <button type="submit" style="padding: 10px 20px; background: #0e639c; color: white; border: none; border-radius: 5px; font-size: 1em; cursor: pointer;">🚀 実行する</button>
        </form>
        <hr style="border: 0; border-top: 1px solid #444; margin-top: 30px;">
        <p><a href="/" style="color: #4ec9b0;">🏠 トップページに戻る</a></p>
    </body>
</html>"""
            self.wfile.write(html.encode('utf-8'))
            return

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
        <h2>🌌 wswsws, Whitespace Web server Workspace</h2>
        
        <h3>🚀 実行結果</h3>
        <pre style="background: #2d2d2d; padding: 20px; border-radius: 8px; color: #ce9178; white-space: pre-wrap; font-family: monospace; font-size: 1.4em; border: 1px solid #444;">{execution_result}</pre>
        
        <h3>📄 app.ws のソースコード</h3>
        <pre style="background: #2d2d2d; padding: 15px; border-radius: 5px; color: #4ec9b0; overflow-x: auto; font-family: monospace;">{visual_code}</pre>
        
        <h3>📊 コード解析 (文字数統計)</h3>
        <div style="background: #2d2d2d; padding: 15px; border-radius: 5px; color: #9cdcfe; font-family: monospace;">
            スペースの数: <strong>{space_count}</strong> 個<br>
            タブの数: <strong>{tab_count}</strong> 個<br>
            改行の数: <strong>{line_count}</strong> 個
        </div>

        <hr style="border: 0; border-top: 1px solid #444; margin-top: 30px;">
        <p>🧪 任意コードの動作確認はこちら: <a href="/test" style="color: #4ec9b0; text-decoration: underline;">コードテストページ (/test) へ</a></p>
    </body>
</html>"""
        self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8', errors='ignore')
        
        params = urllib.parse.parse_qs(post_data)
        input_code = params.get('code', [''])[0]
        stdin_text = params.get('stdin', [''])[0]
        
        execution_result = parse_and_run_whitespace(input_code, stdin_text)
        visual_code = input_code.replace(" ", "␣").replace("\t", "→\t").replace("\n", "↵\n")

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()

        html = f"""<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Whitespace Code Test Result</title>
    </head>
    <body style="font-family: sans-serif; padding: 30px; background: #1e1e1e; color: #d4d4d4;">
        <h2>🧪 Whitespace コードテスト結果</h2>
        
        <h3>🚀 実行結果</h3>
        <pre style="background: #2d2d2d; padding: 20px; border-radius: 8px; color: #ce9178; white-space: pre-wrap; font-family: monospace; font-size: 1.4em; border: 1px solid #444;">{execution_result}</pre>

        <h3>📥 与えた標準入力</h3>
        <pre style="background: #2d2d2d; padding: 10px; border-radius: 5px; color: #9cdcfe; font-family: monospace;">{stdin_text if stdin_text else "（入力なし）"}</pre>

        <h3>📄 ソースコード</h3>
        <pre style="background: #2d2d2d; padding: 15px; border-radius: 5px; color: #4ec9b0; overflow-x: auto; font-family: monospace;">{visual_code}</pre>

        <hr style="border: 0; border-top: 1px solid #444; margin-top: 30px;">
        <p><a href="/test" style="color: #4ec9b0;">← 別のコードをテストする</a> | <a href="/" style="color: #4ec9b0;">🏠 トップページに戻る</a></p>
    </body>
</html>"""
        self.wfile.write(html.encode('utf-8'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), WhitespaceHandler)
    server.serve_forever()
