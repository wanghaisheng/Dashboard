from psutil import virtual_memory

def check_memory():
    mem = virtual_memory()
    return mem.percent