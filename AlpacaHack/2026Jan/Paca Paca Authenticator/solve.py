from Crypto.Util.Padding import pad
import json
from pwn import *
import warnings
warnings.filterwarnings("ignore")

def xor_bytes(a, b):
    # 短い方に合わせる
    return bytes(x ^ y for x, y in zip(a, b))

def blockify(data, block_size=32):
    return ' '.join(data[i:i+block_size] for i in range(0, len(data), block_size))

origin = pad(json.dumps({"name": "alpaca", "message": "paca paca!"}).encode(), 16)
payload  = b'{"name":  "llama", "message": "paca paca!"}\x05\x05\x05\x05\x05'

p = process(['nc', '34.170.146.252', '13161'])
# p = process(['python3', 'server.py'])

p.recvuntil(b'[debug] ')
iv = p.recvline().strip().decode()

# tokenはなくても良いが、確認のために取得しておく
p.recvuntil(b'This is your login token: ')
token = p.recvline().strip().decode()

print("IV:", iv)
print("token:", token)

iv = bytes.fromhex(iv)

print("Original message:", origin)
print("Payload  message:", payload)
diff = xor_bytes(origin, payload)
print("Diff:", blockify(diff.hex()))

modified_iv = xor_bytes(iv, diff)
print("modified IV:", modified_iv.hex())

p.recvuntil(b'help me> ')
p.sendline(modified_iv.hex())
p.interactive()

