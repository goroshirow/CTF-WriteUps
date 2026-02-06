from pwn import *
import time

p = remote("34.170.146.252", 23758)

p.recvuntil(b"[Warmup] current time (seconds)?")
t = int(time.time())
p.sendline(str(t).encode())
p.recvuntil(b"[Impossible] current time (nanoseconds)?")
t2 = int(time.time_ns())
p.sendline(str(t2).encode())
p.interactive()
