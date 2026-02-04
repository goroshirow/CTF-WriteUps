from pwn import *

context.log_level = 'error'

progress = 8
flag = ""

fin_flag = False

while not fin_flag:
    for c in [chr(x) for x in range(32, 127)]:
        test_frag = flag + c
        with process(["python3", "sever.py"]) as p:
            p.sendline(test_frag)
            step = int(p.recvuntil(b'<!>').decode().split()[-2])
            if step > progress:
                progress = step
                flag += c
                print(f"Found so far: {flag} (steps: {step})")
                if c == "}":
                    fin_flag = True
                break
    