import zipfile
import numpy as np

class TsiataRomScraper:
    """
    TSIATA Asset Pipeline: Game Boy / GBC 2BPP Tile & Sprite Extractor.
    Unpacks compressed ROM wrappers and translates hardware planar bytes into visual matrices.
    """
    def __init__(self, archive_path):
        self.archive_path = archive_path
        self.rom_data = self._unpack_rom()

    def _unpack_rom(self):
        """Extracts the raw binary ROM stream from inside the PK zip wrapper."""
        with zipfile.ZipFile(self.archive_path, 'r') as zf:
            # Grab the first file inside the archive
            rom_filename = zf.namelist()[0]
            print(f"[Unpacker] Extracting raw binary stream: {rom_filename}")
            return zf.read(rom_filename)

    def decode_2bpp_tiles(self, byte_offset, num_tiles=256):
        """
        Decodes Game Boy 2BPP planar graphics memory into a 2D NumPy pixel array.
        Every 16 bytes represents a single 8x8 pixel hardware tile.
        """
        tile_data = self.rom_data[byte_offset : byte_offset + (num_tiles * 16)]
        tiles = []

        for t in range(num_tiles):
            tile_bytes = tile_data[t*16 : (t+1)*16]
            if len(tile_bytes) < 16:
                break
                
            tile_matrix = np.zeros((8, 8), dtype=np.uint8)
            
            # Game Boy hardware interlaces two bitplanes per 8-pixel row
            for row in range(8):
                byte1 = tile_bytes[row * 2]
                byte2 = tile_bytes[row * 2 + 1]
                
                for col in range(8):
                    bit_idx = 7 - col
                    # Combine the low bit and high bit to determine shade (0, 1, 2, or 3)
                    low_bit = (byte1 >> bit_idx) & 1
                    high_bit = (byte2 >> bit_idx) & 1
                    color_value = (high_bit << 1) | low_bit
                    tile_matrix[row, col] = color_value
                    
            tiles.append(tile_matrix)
            
        print(f"[Success] Decoded {len(tiles)} hardware 8x8 tiles from offset {hex(byte_offset)}.")
        return np.array(tiles)

# ==========================================
# EXECUTION TEST
# ==========================================
if __name__ == "__main__":
    # Point this to your local ROM file path
    # scraper = TsiataRomScraper("Legend of Zelda, The - Link's Awakening (U) (V1.2) [!].gb")
    # zelda_sprites = scraper.decode_2bpp_tiles(byte_offset=0x40000, num_tiles=128)
    print("TSIATA ROM Scraper module ready for local deployment.")
