import sys

def parse_and_run_whitespace(code):
    tokens = []
    i = 0
    while i < len(code):
        if code[i:i+2] == '  ':
            tokens.append('S')
            i += 2
        elif code[i:i+2] == ' \t':
            tokens.append('T')
            i += 2
        elif code[i:i+2] == ' \n':
            tokens.append('L')
            i += 2
        else:
            i += 1

    stack = []
    output_bytes = bytearray()
    idx = 0
    length = len(tokens)

    while idx < length:
        # Stack Manipulation: Push
        if idx + 1 < length and tokens[idx] == 'S' and tokens[idx+1] == 'S':
            idx += 2
            if idx < length:
                sign = 1 if tokens[idx] == 'S' else -1
                idx += 1
                val = 0
                while idx < length and tokens[idx] != 'L':
                    val = (val << 1) | (1 if tokens[idx] == 'T' else 0)
                    idx += 1
                if idx < length and tokens[idx] == 'L':
                    idx += 1
                stack.append(sign * val)
                continue

        # I/O: Output Character
        elif idx + 2 < length and tokens[idx] == 'T' and tokens[idx+1] == 'S' and tokens[idx+2] == 'S':
            idx += 3
            if stack:
                val = stack.pop()
                output_bytes.append(val & 0xFF)
            continue

        # I/O: Output Number
        elif idx + 2 < length and tokens[idx] == 'T' and tokens[idx+1] == 'S' and tokens[idx+2] == 'T':
            idx += 3
            if stack:
                val = stack.pop()
                output_bytes.extend(str(val).encode('utf-8'))
            continue

        # その他の命令（必要に応じて追加）
        idx += 1

    return bytes(output_bytes)
