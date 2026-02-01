from pwn import *
from math import gcd
from Crypto.Util.number import long_to_bytes

enc_pass = 3567252736412634555920569398403787395170577668834666742330267390011828943495692402033350307843527370186546259265692029368644049938630024394169760506488003

p = remote('titan.picoctf.net', 60428)

p.recvuntil(b'E --> encrypt D --> decrypt.')
p.sendline(b'e')

p.recvuntil(b'enter text to encrypt (encoded length must be less than keysize):')
p.sendline(b'\x02')

p.recvuntil(b'ciphertext (m ^ e mod n) ')
cipher2 = int(p.recvline().strip())
print(f"Cipher for 2: {cipher2}")

enc_2pass = cipher2 * enc_pass
print(f"Enc of 2 * pass: {enc_2pass}")

p.recvuntil(b'E --> encrypt D --> decrypt.')
p.sendline(b'd')

p.recvuntil(b'Enter text to decrypt: ')
p.sendline(str(enc_2pass).encode())

p.recvuntil(b'decrypted ciphertext as hex (c ^ d mod n): ')
dec_2pass = int(p.recvline().strip(), 16)
print(f"Decrypted 2 * pass: {dec_2pass}")

print(f"Password: {long_to_bytes(dec_2pass // 2)}")
