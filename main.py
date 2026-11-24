#!/usr/bin/env python3
"""news-23 b134 numbers-led: copy entry.png (1024x1024) to $MAKEFUN_OUTPUT_DIR/entry.png.

Stdlib only (no PIL). Never writes next to itself: it writes only to MAKEFUN_OUTPUT_DIR,
which must be an existing directory outside this repository. Validates the PNG
header and chunk structure (IHDR 1024x1024, CRCs, IEND last) before copying,
then re-reads the output and confirms it is byte-identical to the source.
"""
import hashlib
import os
import struct
import sys
import zlib


def fail(msg):
    print("error: " + msg, file=sys.stderr)
    sys.exit(1)


def read_png(path):
    with open(path, "rb") as f:
        data = f.read()
    return data


def validate_png(data):
    # PNG signature: 8 bytes.
    if len(data) < 8 or data[:8] != b"\x89PNG\r\n\x1a\n":
        fail("bad PNG signature")
    # Chunk layout: length (4) + type (4) + data + CRC (4). The first chunk
    # starts at byte 8, so its data runs 16..28, its CRC is 29..32, and the
    # next chunk starts at byte 33.
    # First chunk must be IHDR, 13 bytes of data: width, height, bit depth,
    # colour type, compression, filter, interlace.
    if len(data) < 33:
        fail("file too small to hold an IHDR chunk")
    (length,) = struct.unpack(">I", data[8:12])
    ctype = data[12:16]
    if ctype != b"IHDR" or length != 13:
        fail("first chunk is not a 13-byte IHDR")
    # CRC of the IHDR chunk lives in data[29:33] (length 4 + type 4 + data 13).
    (crc_stored,) = struct.unpack(">I", data[29:33])
    crc_calc = zlib.crc32(b"IHDR" + data[16:29]) & 0xFFFFFFFF
    if crc_stored != crc_calc:
        fail("bad CRC in chunk IHDR")
    width, height = struct.unpack(">II", data[16:24])
    bit_depth = data[24]
    colour_type = data[25]
    compression, filt, interlace = data[26], data[27], data[28]
    if (width, height) != (1024, 1024):
        fail("expected 1024x1024, got %dx%d" % (width, height))
    if bit_depth != 8:
        fail("expected bit depth 8, got %d" % bit_depth)
    if colour_type not in (2, 6):
        fail("expected colour type 2 or 6, got %d" % colour_type)
    if (compression, filt, interlace) != (0, 0, 0):
        fail("compression/filter/interlace must all be 0")
    # Walk the remaining chunks: check CRC of each, require non-empty IDAT
    # payload (>=1000 bytes total) and a 0-byte IEND as the last chunk with
    # no trailing data after it.
    pos = 33
    idat_total = 0
    last_type = None
    while pos + 8 <= len(data):
        (clen,) = struct.unpack(">I", data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        end = pos + 8 + clen + 4
        if end > len(data):
            fail("truncated chunk " + ctype.decode("latin-1", "replace"))
        (crc_stored,) = struct.unpack(">I", data[pos + 8 + clen:pos + 12 + clen])
        crc_calc = zlib.crc32(data[pos + 4:pos + 8 + clen]) & 0xFFFFFFFF
        if crc_stored != crc_calc:
            fail("bad CRC in chunk " + ctype.decode("latin-1", "replace"))
        if ctype == b"IDAT":
            if clen == 0:
                fail("empty IDAT chunk")
            idat_total += clen
        last_type = ctype
        pos = end
        if ctype == b"IEND":
            break
    if last_type != b"IEND":
        fail("no IEND chunk found")
    if pos != len(data):
        fail("trailing data after IEND")
    if idat_total < 1000:
        fail("IDAT payload too small (%d bytes)" % idat_total)
    if len(data) < 10000:
        fail("file too small (%d bytes)" % len(data))
    if len(data) > 1024 * 1024:
        fail("file exceeds 1 MiB (%d bytes)" % len(data))


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        fail("entry.png not found next to main.py")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    if not out_dir:
        fail("MAKEFUN_OUTPUT_DIR is empty")
    out_dir_abs = os.path.abspath(out_dir)
    here_abs = os.path.abspath(here)
    if out_dir_abs == here_abs or out_dir_abs.startswith(here_abs + os.sep):
        fail("MAKEFUN_OUTPUT_DIR must be outside the repository")
    if not os.path.isdir(out_dir_abs):
        fail("MAKEFUN_OUTPUT_DIR is not an existing directory: " + out_dir)
    dst = os.path.join(out_dir_abs, "entry.png")
    if os.path.abspath(dst) == os.path.abspath(src):
        fail("output would overwrite the source")

    data = read_png(src)
    validate_png(data)
    with open(dst, "wb") as f:
        f.write(data)
    # Re-read the output and confirm it is byte-identical to the source.
    check = read_png(dst)
    if check != data:
        fail("output differs from source after copy")
    sha = hashlib.sha256(data).hexdigest()
    print("wrote %s (%d bytes, sha256 %s)" % (dst, len(data), sha))


if __name__ == "__main__":
    main()
