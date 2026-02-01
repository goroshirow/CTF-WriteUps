from pwn import *
from Crypto.Util.number import bytes_to_long, long_to_bytes, inverse, GCD

target_script = './service.py'
HOST = 'crypto.katagaitai-ctf.net' 
PORT = 9012

def solve():
    r = remote(HOST, PORT)
    # r = process(['python3', target_script])

    e = 0x10001
    
    r.recvuntil(b"> ")
    r.sendline(b"1")
    r.recvuntil(b"(hex)> ")
    r.sendline(b"02")
    c1 = int(r.recvline().strip(), 16)
    
    r.recvuntil(b"> ")
    r.sendline(b"1")
    r.recvuntil(b"(hex)> ")
    r.sendline(b"03")
    c2 = int(r.recvline().strip(), 16)
    
    val1 = pow(2, e) - c1
    val2 = pow(3, e) - c2
    N = GCD(val1, val2)
    

    target_msg = b"katagaitai-CTF"
    m = bytes_to_long(target_msg)

    m_dummy = m * 2
    
    r.recvuntil(b"> ")
    r.sendline(b"1")
    
    r.recvuntil(b"(hex)> ")
    r.sendline(long_to_bytes(m_dummy).hex().encode())
    
    cipher_dummy_hex = r.recvline().strip().decode()
    c_dummy = int(cipher_dummy_hex, 16)
    print(f"[*] Received dummy cipher: {c_dummy}")

    inv_factor = inverse(pow(2, e, N), N)
    
    c_target = (c_dummy * inv_factor) % N
    print(f"[*] Calculated target cipher: {c_target}")
    
    print("[*] Sending target cipher to decryption oracle...")
    r.recvuntil(b"> ")
    r.sendline(b"2") 
    
    r.recvuntil(b"(hex)> ")
    r.sendline(hex(c_target)[2:].encode())

    r.interactive()

if __name__ == "__main__":
    solve()