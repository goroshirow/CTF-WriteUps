from pwn import *

flag = 'Alpaca{'

p = remote('34.170.146.252', 28539)

for _ in range(50):
    MinLen = 9999
    for c in 'abcdefghijklmnopqrstuvwxyz_A{}':
        candidate = flag + c
        print(f'Trying: {candidate}')
        candidate *= 5
        p.recvuntil(b'Your input: ')
        p.sendline(candidate.encode())
        p.recvuntil(b'Size of compressed data: ')
        size = int(p.recvline().decode().split()[0])
        print(f'Size: {size}')
        if size < MinLen:
            MinLen = size
            next_char = c
            
    flag += next_char
    print(flag)
    if next_char == '}':
        break