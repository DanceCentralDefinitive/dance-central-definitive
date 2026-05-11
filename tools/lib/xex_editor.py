#!/usr/bin/env python3
import struct
from pathlib import Path

class XEXEditor:
    def __init__(self, xex_path):
        self.path = Path(xex_path)
        with open(self.path, 'rb') as f:
            self.data = bytearray(f.read())
        
        # Verify XEX magic
        magic = self.data[0:4]
        if magic != b'XEX2':
            raise ValueError(f"Not a valid XEX2 file (magic: {magic})")
        
        # Parse XEX header
        self.module_flags = struct.unpack('>I', self.data[0x4:0x8])[0]
        self.pe_data_offset = struct.unpack('>I', self.data[0x8:0xC])[0]
        self.reserved = struct.unpack('>I', self.data[0xC:0x10])[0]
        self.security_info_offset = struct.unpack('>I', self.data[0x10:0x14])[0]
        self.optional_header_count = struct.unpack('>I', self.data[0x14:0x18])[0]
    
    def find_optional_header(self, header_id):
        """Find an optional header by ID and return offset"""
        # Optional headers start at offset 0x18
        offset = 0x18
        
        for i in range(self.optional_header_count):
            if offset + 8 > len(self.data):
                break
                
            opt_header_id = struct.unpack('>I', self.data[offset:offset+4])[0]
            opt_header_data = struct.unpack('>I', self.data[offset+4:offset+8])[0]
            
            if opt_header_id == header_id:
                # Bit 0 indicates if data is inline
                is_inline = (opt_header_id & 0x01) == 0x01
                
                if is_inline:
                    # Data is stored inline in the data field
                    return opt_header_data
                else:
                    # Data is at the specified offset
                    return opt_header_data
            
            offset += 8
        
        return None
    
    def get_title_id(self):
        """Read current Title ID from Execution ID optional header"""
        # Title ID is in optional header 0x40006 (Execution ID)
        # Structure: MediaID(4) + Version(4) + BaseVersion(4) + TitleID(4)
        exec_id_offset = self.find_optional_header(0x40006)
        
        if exec_id_offset is None:
            return None
        
        # Title ID is at offset +12 in the structure
        title_id_offset = exec_id_offset + 12
        if title_id_offset + 4 > len(self.data):
            raise ValueError("Title ID offset out of bounds")
            
        title_id = struct.unpack('>I', self.data[title_id_offset:title_id_offset+4])[0]
        return title_id
    
    def get_media_id(self):
        """Read current Media ID from Execution ID optional header"""
        exec_id_offset = self.find_optional_header(0x40006)
        
        if exec_id_offset is None:
            return None
        
        # Media ID is at offset 0 in the structure
        if exec_id_offset + 4 > len(self.data):
            raise ValueError("Media ID offset out of bounds")
            
        media_id = struct.unpack('>I', self.data[exec_id_offset:exec_id_offset+4])[0]
        return media_id
    
    def set_title_id(self, new_title_id):
        """Set new Title ID"""
        exec_id_offset = self.find_optional_header(0x40006)
        
        if exec_id_offset is None:
            raise ValueError("Execution ID header not found")
        
        title_id_offset = exec_id_offset + 12
        if title_id_offset + 4 > len(self.data):
            raise ValueError("Title ID offset out of bounds")
        
        # Write new Title ID (big-endian)
        struct.pack_into('>I', self.data, title_id_offset, new_title_id & 0xFFFFFFFF)
    
    def set_media_id(self, new_media_id):
        """Set new Media ID"""
        exec_id_offset = self.find_optional_header(0x40006)
        
        if exec_id_offset is None:
            raise ValueError("Execution ID header not found")
        
        if exec_id_offset + 4 > len(self.data):
            raise ValueError("Media ID offset out of bounds")
        
        # Write new Media ID (big-endian)
        struct.pack_into('>I', self.data, exec_id_offset, new_media_id & 0xFFFFFFFF)

    def save(self, output_path=None):
        """Save modified XEX"""
        if output_path is None:
            output_path = self.path
        
        with open(output_path, 'wb') as f:
            f.write(self.data)
        