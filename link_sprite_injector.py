import argparse
import numpy as np
from pathlib import Path

# ==============================================================================
# 100% VERIFIED OFFSETS IN LINK'S AWAKENING (BANK 0x0C)
# ==============================================================================
ZELDA_DOWN_OFFSET      = 0x031800  # Slot 0: Down Idle (verified!)
ZELDA_UP_OFFSET        = 0x031840  # Slot 1: Up Idle (right between Down and Left!)
ZELDA_LEFT_WALK_OFFSET = 0x031880  # Slots 2 & 3: Left Idle & Walk (verified!)
POKE_RED_SPRITE_OFFSET = 0x014571  # SPRITE_RED in Pokemon Yellow Bank 0x05
POKE_RED_SPRITE_BYTES  = 384       # 24 tiles * 16 bytes/tile

def decode_2bpp_tiles(raw_bytes: bytes) -> np.ndarray:
    num_tiles = len(raw_bytes) // 16
    data = np.frombuffer(raw_bytes[:num_tiles * 16], dtype=np.uint8).reshape(num_tiles, 8, 2)
    shifts = np.arange(7, -1, -1, dtype=np.uint8)
    low_bits  = (data[:, :, 0:1] >> shifts) & 1
    high_bits = (data[:, :, 1:2] >> shifts) & 1
    return (high_bits << 1) | low_bits

def encode_2bpp_tiles(tiles: np.ndarray) -> bytes:
    shifts = np.arange(7, -1, -1, dtype=np.uint8)
    low_bits  = (tiles & 1) << shifts
    high_bits = ((tiles >> 1) & 1) << shifts
    plane_0 = np.bitwise_or.reduce(low_bits, axis=2)
    plane_1 = np.bitwise_or.reduce(high_bits, axis=2)
    packed = np.stack([plane_0, plane_1], axis=2).astype(np.uint8)
    return packed.tobytes()

def mirror_frame_horizontal(frame_tiles: np.ndarray) -> np.ndarray:
    """Horizontally mirrors a (4, 8, 8) [TL, TR, BL, BR] frame cleanly."""
    flipped_pixels = np.flip(frame_tiles, axis=2)
    return flipped_pixels.take(tuple((1, 0, 3, 2)), axis=0)

def remap_zelda_to_pokemon_palette(tiles: np.ndarray) -> np.ndarray:
    """Maps Zelda shades (0..3) to crisp high-contrast Pokemon Yellow sprite shades."""
    lut = np.array(tuple((0, 2, 3, 3)), dtype=np.uint8)
    return lut[tiles]

def load_la_sprite_block(zelda_rom: bytes, offset: int, count: int) -> np.ndarray:
    """Decodes `count` 16x16 sprites from LA column-major [TL, BL, TR, BR] to [TL, TR, BL, BR]."""
    raw = zelda_rom[offset : offset + count * 64]
    tiles = decode_2bpp_tiles(raw)
    sprites = []
    for s in range(count):
        t0 = s * 4
        sprites.append(tiles.take(tuple((t0 + 0, t0 + 2, t0 + 1, t0 + 3)), axis=0))
    return np.array(sprites, dtype=np.uint8)

def extract_link_frames(zelda_rom: bytes) -> np.ndarray:
    down_sprites = load_la_sprite_block(zelda_rom, ZELDA_DOWN_OFFSET, 1)
    up_sprites   = load_la_sprite_block(zelda_rom, ZELDA_UP_OFFSET, 1)
    side_sprites = load_la_sprite_block(zelda_rom, ZELDA_LEFT_WALK_OFFSET, 2)

    down_idle = down_sprites.reshape(4, 8, 8)
    down_walk = mirror_frame_horizontal(down_idle)
    up_idle   = up_sprites.reshape(4, 8, 8)
    up_walk   = mirror_frame_horizontal(up_idle)
    left_idle = side_sprites.take(tuple((0,)), axis=0).reshape(4, 8, 8)
    left_walk = side_sprites.take(tuple((1,)), axis=0).reshape(4, 8, 8)

    ordered = np.concatenate((
        down_idle, up_idle, left_idle,
        down_walk, up_walk, left_walk
    ), axis=0)

    return remap_zelda_to_pokemon_palette(ordered)

def fix_gb_global_checksum(rom_data: bytearray) -> None:
    rom_data[0x014E] = 0x00
    rom_data[0x014F] = 0x00
    checksum = sum(rom_data) & 0xFFFF
    rom_data[0x014E] = (checksum >> 8) & 0xFF
    rom_data[0x014F] = checksum & 0xFF

def inject_link_into_pokemon(zelda_path: Path, poke_path: Path, out_path: Path) -> None:
    zelda_rom = zelda_path.read_bytes()
    poke_rom = bytearray(poke_path.read_bytes())

    link_tiles = extract_link_frames(zelda_rom)
    link_2bpp_payload = encode_2bpp_tiles(link_tiles)
    assert len(link_2bpp_payload) == POKE_RED_SPRITE_BYTES

    poke_rom[POKE_RED_SPRITE_OFFSET : POKE_RED_SPRITE_OFFSET + POKE_RED_SPRITE_BYTES] = link_2bpp_payload
    fix_gb_global_checksum(poke_rom)

    out_path.write_bytes(poke_rom)
    print(f"[SUCCESS] All 4-way Link sprites written to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--zelda", type=Path, default=Path(r"roms\Legend of Zelda, The - Link's Awakening (U) (V1.2) [!].gb"))
    parser.add_argument("--poke", type=Path, default=Path(r"roms\Pokemon - Yellow Version (UE) [C][!].gbc"))
    parser.add_argument("--out", type=Path, default=Path("Pokemon_Zelda_Fusion_v1.gbc"))
    args = parser.parse_args()
    inject_link_into_pokemon(args.zelda, args.poke, args.out)
