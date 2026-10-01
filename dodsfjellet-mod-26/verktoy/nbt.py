"""Minimal NBT les/skriv (gzip, big-endian) – nok til å redigere level.dat."""
import gzip, struct, sys

class Tag:
    def __init__(self, t, v): self.t, self.v = t, v
    def __repr__(self): return f"Tag({self.t},{self.v!r})"

def _les(t, b, i):
    if t == 1: return struct.unpack_from(">b", b, i)[0], i + 1
    if t == 2: return struct.unpack_from(">h", b, i)[0], i + 2
    if t == 3: return struct.unpack_from(">i", b, i)[0], i + 4
    if t == 4: return struct.unpack_from(">q", b, i)[0], i + 8
    if t == 5: return struct.unpack_from(">f", b, i)[0], i + 4
    if t == 6: return struct.unpack_from(">d", b, i)[0], i + 8
    if t == 7:
        n = struct.unpack_from(">i", b, i)[0]; return b[i+4:i+4+n], i + 4 + n
    if t == 8:
        n = struct.unpack_from(">H", b, i)[0]; return b[i+2:i+2+n].decode("utf-8", "surrogatepass"), i + 2 + n
    if t == 9:
        et, n = struct.unpack_from(">bi", b, i); i += 5; ut = []
        for _ in range(n):
            v, i = _les(et, b, i); ut.append(v)
        return (et, ut), i
    if t == 10:
        d = {}
        while True:
            tt = b[i]; i += 1
            if tt == 0: return d, i
            n = struct.unpack_from(">H", b, i)[0]; navn = b[i+2:i+2+n].decode("utf-8", "surrogatepass"); i += 2 + n
            v, i = _les(tt, b, i); d[navn] = Tag(tt, v)
    if t == 11:
        n = struct.unpack_from(">i", b, i)[0]; return list(struct.unpack_from(f">{n}i", b, i+4)), i + 4 + 4*n
    if t == 12:
        n = struct.unpack_from(">i", b, i)[0]; return list(struct.unpack_from(f">{n}q", b, i+4)), i + 4 + 8*n
    raise ValueError(t)

def _skriv(t, v):
    if t in (1, 2, 3, 4, 5, 6): return struct.pack(">" + " bhiqfd"[t], v)
    if t == 7: return struct.pack(">i", len(v)) + v
    if t == 8:
        e = v.encode("utf-8", "surrogatepass"); return struct.pack(">H", len(e)) + e
    if t == 9:
        et, ut = v; return struct.pack(">bi", et, len(ut)) + b"".join(_skriv(et, x) for x in ut)
    if t == 10:
        o = b""
        for navn, tag in v.items():
            e = navn.encode("utf-8"); o += struct.pack(">bH", tag.t, len(e)) + e + _skriv(tag.t, tag.v)
        return o + b"\x00"
    if t == 11: return struct.pack(">i", len(v)) + struct.pack(f">{len(v)}i", *v)
    if t == 12: return struct.pack(">i", len(v)) + struct.pack(f">{len(v)}q", *v)

def load(sti):
    b = gzip.decompress(open(sti, "rb").read())
    n = struct.unpack_from(">H", b, 1)[0]
    v, _ = _les(10, b, 3 + n)
    return v

def save(sti, rot):
    open(sti, "wb").write(gzip.compress(b"\x0a\x00\x00" + _skriv(10, rot)))

if __name__ == "__main__":
    r = load(sys.argv[1])
    def vis(d, inn=0):
        for k, t in d.items():
            if t.t == 10:
                print(" " * inn + k + ":"); vis(t.v, inn + 2) if inn < 4 else None
            else:
                s = repr(t.v); print(" " * inn + f"{k} = {s[:80]}")
    vis(r)
