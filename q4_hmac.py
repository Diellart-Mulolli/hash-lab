"""Question 4(b): HMAC-SHA-256 structure for the 3-byte key K = 'key', verified against the stdlib."""
import hashlib
import hmac
import math

B = 64  # SHA-256 block length in bytes
K = b"key"  # 0x6B 0x65 0x79
print(f"key K = {K!r} = {' '.join(f'0x{b:02X}' for b in K)}")

# (i) padding the key to B bytes
K_padded = K + b"\x00" * (B - len(K))
print(f"\n(i)   K is shorter than {B} bytes, so it is right-padded with zero bytes to {len(K_padded)} bytes.")

# (ii) first three bytes of K xor ipad and K xor opad
ipad, opad = 0x36, 0x5C
k_ipad = bytes(b ^ ipad for b in K_padded)
k_opad = bytes(b ^ opad for b in K_padded)
print("\n(ii)  first three bytes (the rest are the pad byte itself, since 0x00 XOR pad = pad):")
print(f"  K XOR ipad: {' '.join(f'0x{b:02X}' for b in k_ipad[:3])} ... then 0x36 x{B-3}")
print(f"  K XOR opad: {' '.join(f'0x{b:02X}' for b in k_opad[:3])} ... then 0x5C x{B-3}")
for name, pad, got in (("ipad", ipad, k_ipad), ("opad", opad, k_opad)):
    bits = " ; ".join(f"{c:c}=0x{c:02X}^0x{pad:02X}=0x{c ^ pad:02X}" for c in K)
    print(f"    {name}: {bits}")

# (iii) full expression
print("\n(iii) HMAC(M,K) = SHA256( (K XOR opad) || SHA256( (K XOR ipad) || M ) )")

# (iv) block counts for a 1000-byte message
def sha256_blocks(nbytes):
    return math.ceil((nbytes + 9) / B)  # +1 byte 0x80, +8 byte length, then round up

m = 1000
inner = sha256_blocks(B + m)        # (K^ipad) is one full block, then M
outer = sha256_blocks(B + 32)       # (K^opad) one block, then 32-byte inner digest
plain = sha256_blocks(m)
print(f"\n(iv)  SHA-256 of a {m}-byte message: ceil(({m}+9)/{B}) = {plain} blocks")
print(f"      HMAC inner SHA-256 over (K^ipad)||M: ceil(({B+m}+9)/{B}) = {inner} blocks")
print(f"      HMAC outer SHA-256 over (K^opad)||digest: ceil(({B+32}+9)/{B}) = {outer} blocks")
print(f"      HMAC total = {inner} + {outer} = {inner+outer} blocks vs {plain} for a plain hash "
      f"(+{inner+outer-plain} blocks, ~2 extra compressions, negligible).")

# cross-check the structure against Python's hmac
M = b"transfer 100 EUR to Bob"
mine = hashlib.sha256(k_opad + hashlib.sha256(k_ipad + M).digest()).hexdigest()
ref = hmac.new(K, M, hashlib.sha256).hexdigest()
print(f"\ncross-check on M={M!r}: manual == hmac.new: {mine == ref}")
print(f"  HMAC = {ref}")
