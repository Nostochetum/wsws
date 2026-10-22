from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import urllib.parse

def parse_and_run_whitespace(code, stdin_text=""):
    """Whitespace実行エンジン"""
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
                        elif idx < length and tokens[idx] == 'T':  # Read Num
                            idx += 1
                            if stack:
                                addr = stack.pop()
                                num_str = ""
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
    <body style="font-family: sans-serif; padding: 30px; background: #1e1e1e; color
