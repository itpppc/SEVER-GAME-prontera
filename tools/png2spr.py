#!/usr/bin/env python3
"""Turn one of our own character PNGs into a Ragnarok sprite pair (.spr + .act).

The art is ours (see characters/CHARACTER-BIBLE.md), so the output can ship with
the installer. No Gravity file is read or copied.

    python3 tools/png2spr.py characters/png/ruesi.png client-data/data/sprite/npc/prt_ruesi --height 110

Writes <out>.spr (v2.1, 256-colour palette, RLE) and <out>.act (v2.5) with
40 actions (idle, walk, attack, hurt, die x 8 directions), so the same files
work for an NPC or a monster. --preview also renders the files back to a PNG
by parsing them, which proves they decode.
"""
import argparse
import struct
from PIL import Image

DIRS = 8
MAGENTA = (255, 0, 255)


def load_frame(path, height):
    im = Image.open(path).convert("RGBA")
    im = im.crop(im.getbbox())
    w = max(1, round(im.width * height / im.height))
    im = im.resize((w, height), Image.LANCZOS)
    # Hard alpha edge: RO palette sprites have no partial transparency.
    alpha = im.getchannel("A").point(lambda a: 255 if a >= 128 else 0)
    rgb = Image.new("RGB", im.size, MAGENTA)
    rgb.paste(im.convert("RGB"), mask=alpha)
    q = im.convert("RGB").quantize(colors=255, method=Image.MEDIANCUT, dither=Image.NONE)
    pal = q.getpalette()[: 255 * 3]
    pal += [0] * (255 * 3 - len(pal))
    idx = bytes(0 if a == 0 else p + 1 for p, a in zip(q.getdata(), alpha.getdata()))
    palette = [MAGENTA] + [tuple(pal[i:i + 3]) for i in range(0, 255 * 3, 3)]
    return im.width, im.height, idx, palette


def rle(data):
    out, i = bytearray(), 0
    while i < len(data):
        if data[i] == 0:
            n = 0
            while i < len(data) and data[i] == 0 and n < 255:
                n += 1
                i += 1
            out += bytes((0, n))
        else:
            out.append(data[i])
            i += 1
    return bytes(out)


def write_spr(path, w, h, idx, palette):
    body = rle(idx)
    if len(body) > 0xFFFF:
        raise SystemExit("image too large for one SPR frame; lower --height")
    with open(path, "wb") as f:
        f.write(b"SP" + struct.pack("<HHH", 0x0201, 1, 0))
        f.write(struct.pack("<HHH", w, h, len(body)) + body)
        for r, g, b in palette:
            f.write(bytes((r, g, b, 0)))


def layer(w, h, x=0, y=0, rgba=(255, 255, 255, 255), scale=1.0, angle=0, mirror=0):
    return (struct.pack("<iiii", x, y, 0, mirror) + bytes(rgba)
            + struct.pack("<ffiiii", scale, scale, angle, 0, w, h))


def frame(lyr):
    return bytes(32) + struct.pack("<I", 1) + lyr + struct.pack("<iI", -1, 0)


def write_act(path, w, h):
    feet = -h // 2  # layer x,y is the image centre; put the feet on the cell
    groups = [  # (frames, delay in 25 ms ticks)
        ([layer(w, h, y=feet), layer(w, h, y=feet - 2)], 12),              # idle: slow breathing bob
        ([layer(w, h, y=feet - d) for d in (0, 3, 5, 3)], 4),             # walk: hop
        ([layer(w, h, y=feet, angle=a) for a in (0, 350, 10, 0)], 3),     # attack: wobble
        ([layer(w, h, y=feet, rgba=(255, 140, 140, 255)), layer(w, h, y=feet)], 3),  # hurt: red flash
        ([layer(w, h, y=feet, angle=a, rgba=(255, 255, 255, t))            # die: tip over and fade
          for a, t in ((0, 255), (30, 200), (60, 140), (90, 90))], 4),
    ]
    actions, delays = [], []
    for frames, delay in groups:
        for _ in range(DIRS):
            actions.append(struct.pack("<I", len(frames)) + b"".join(frame(l) for l in frames))
            delays.append(float(delay))
    with open(path, "wb") as f:
        f.write(b"AC" + struct.pack("<HH", 0x0205, len(actions)) + bytes(10))
        f.write(b"".join(actions))
        f.write(struct.pack("<I", 0))  # no sound events
        f.write(struct.pack(f"<{len(delays)}f", *delays))


def read_back(spr_path, act_path):
    """Decode the files we wrote (independent of the writer's in-memory data)."""
    d = open(spr_path, "rb").read()
    assert d[:2] == b"SP" and struct.unpack_from("<H", d, 2)[0] == 0x0201
    n, _ = struct.unpack_from("<HH", d, 4)
    w, h, size = struct.unpack_from("<HHH", d, 8)
    src, px, i = d[14:14 + size], bytearray(), 0
    while i < len(src):
        if src[i] == 0:
            px += bytes(src[i + 1])
            i += 2
        else:
            px.append(src[i])
            i += 1
    assert len(px) == w * h, (len(px), w * h)
    pal = d[-1024:]
    img = Image.new("RGBA", (w, h))
    img.putdata([(0, 0, 0, 0) if p == 0 else (pal[p * 4], pal[p * 4 + 1], pal[p * 4 + 2], 255) for p in px])
    a = open(act_path, "rb").read()
    assert a[:2] == b"AC"
    ver, nact = struct.unpack_from("<HH", a, 2)
    assert ver == 0x0205 and nact == 40 and n == 1
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("png")
    ap.add_argument("out", help="output path without extension")
    ap.add_argument("--height", type=int, default=110, help="sprite height in pixels (RO players are ~80-100)")
    ap.add_argument("--preview", help="write a PNG decoded back from the .spr")
    a = ap.parse_args()
    w, h, idx, pal = load_frame(a.png, a.height)
    write_spr(a.out + ".spr", w, h, idx, pal)
    write_act(a.out + ".act", w, h)
    img = read_back(a.out + ".spr", a.out + ".act")
    if a.preview:
        img.save(a.preview)
    print(f"ok {a.out}.spr/.act {w}x{h}")


if __name__ == "__main__":
    main()
