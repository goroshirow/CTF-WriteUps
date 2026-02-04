from pwn import *

def main(input: str) -> str:
    payload = input + "#" + input[::-1]
    
    p = remote('34.170.146.252', 34185)
    p.recvuntil(b'> ')
    p.sendline(payload.encode())
    
    p = p.recvall(timeout=2).decode()
    return p

if __name__ == "__main__":
    # print(open('flag.txt', 'r').read())
    input = input("Enter input: ")
    result = main(input)
    print(result)