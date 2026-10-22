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
        if tokens[idx] == 'S' and tokens[idx+1] == 'S':
            idx += 2
            sign = 1 if tokens[idx] == 'S' else -1
            idx += 1
            val = 0
            while idx < length and tokens[idx] != 'L':
                val = (val << 1) | (1 if tokens[idx] == 'T' else 0)
                idx += 1
            idx += 1
            stack.append(sign * val)

        # I/O: Output Num
        elif tokens[idx] == 'T' and tokens[idx+1] == 'N' and tokens[idx+2] == 'T':  # トークン構造に合わせた分岐
            idx += 2
            if stack:
                output_bytes.extend(str(stack.pop()).encode('utf-8'))
        
        # その他の命令処理...
        idx += 1

    return output_bytes
