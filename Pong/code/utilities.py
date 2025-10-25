from settings import *

def hex_to_color(hex_str):
    """Convert a hex string like '#ee322c' or 'ee322c' to a raylib Color."""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 6:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        a = 255
    elif len(hex_str) == 8:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        a = int(hex_str[6:8], 16)
    else:
        raise ValueError(f"Invalid hex color: {hex_str}")

    return Color(r, g, b, a)