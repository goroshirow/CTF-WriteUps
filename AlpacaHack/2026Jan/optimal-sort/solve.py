from pwn import *

def solve():
    io = remote('34.170.146.252', 43373)

    for stage in range(4):
        io.recvuntil(b'size = ')
        size = int(io.recvline().strip())

        print(f"stage {stage+1}, size={size}")

        max_try = size + 5

        for step in range(max_try):
            io.recvuntil(b'i> ')
            i = step
            io.sendline(str(i).encode())

            io.recvuntil(b'j> ')
            j = i - size
            io.sendline(str(j).encode())

            io.recvuntil(b'is_sorted = ')
            result = io.recvline().strip().decode()

            if result == 'True':
                print(f"stage {stage+1} cleare!")
                break
        else:
            print(f"stage {stage+1} failed")

    io.recvuntil(b'flag:')
    print(io.recvline().decode())

    io.close()

if __name__ == "__main__":
    solve()
