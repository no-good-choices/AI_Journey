# TSIATA Reverse Engineering Probe: Extracts Cartridge Header & Entry Vector
# @category TSIATA_Extraction

def inspect_cartridge_dna():
    program_name = currentProgram.getName()
    memory = currentProgram.getMemory()
    
    print("==========================================")
    print("TSIATA ROM PROBE ACTIVE: " + program_name)
    print("==========================================")
    
    # In Game Boy ROMs, the internal ASCII title is stored at 0x0134 - 0x0143
    title_addr = toAddr(0x0134)
    title_bytes = getBytes(title_addr, 15)
    
    # Filter out null bytes and decode into readable ASCII text
    clean_title = "".join([chr(b & 0xFF) for b in title_bytes if 32 <= (b & 0xFF) <= 126])
    print("[Cartridge Header Title] : " + clean_title)
    
    # Read the Boot Jump instruction at 0x0100 - 0x0103
    boot_addr = toAddr(0x0100)
    boot_bytes = getBytes(boot_addr, 4)
    hex_dump = " ".join(["{:02X}".format(b & 0xFF) for b in boot_bytes])
    print("[Boot Vector (0x0100)]    : " + hex_dump)
    print("==========================================")

inspect_cartridge_dna()
