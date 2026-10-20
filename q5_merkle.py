"""Question 5(c): Merkle tree with the toy combiner T(x, y) = (3x + 5y + 7) mod 101."""


def T(x, y):
    return (3 * x + 5 * y + 7) % 101


L1, L2, L3, L4 = 23, 8, 61, 40

N12 = T(L1, L2)
N34 = T(L3, L4)
R = T(N12, N34)
print("(i) building the tree")
print(f"  N12 = T(23, 8)  = (3*23 + 5*8  + 7) mod 101 = {3*23+5*8+7} mod 101 = {N12}")
print(f"  N34 = T(61, 40) = (3*61 + 5*40 + 7) mod 101 = {3*61+5*40+7} mod 101 = {N34}")
print(f"  R   = T(N12,N34)= (3*{N12} + 5*{N34} + 7) mod 101 = {3*N12+5*N34+7} mod 101 = {R}")

print("\n(ii) inclusion proof for transaction 3 (leaf L3, which is the LEFT child of N34)")
print(f"  proof = [ L4 = {L4} (sibling, right), N12 = {N12} (uncle, left) ]")
# L3 is left at the leaf level, N12 is left at the next level, so combine keeping order.
recomputed = T(N12, T(L3, L4))
print(f"  light client: T(N12, T(L3, L4)) = T({N12}, T(61,{L4})) = T({N12},{T(L3, L4)}) = {recomputed}"
      f"  (matches root {R}: {recomputed == R})")

print("\n(iii) transaction 3 altered: L3 = 61 -> 62")
N34b = T(62, L4)
Rb = T(N12, N34b)
print(f"  N34' = T(62, 40) = {N34b},  R' = T({N12}, {N34b}) = {Rb}")
print(f"  root changed {R} -> {Rb}: detected because the stored/signed root no longer matches ({R != Rb})")

print("\n(iv) proof size for a block of 4096 transactions")
import math
print(f"  depth = log2(4096) = {int(math.log2(4096))}, so an inclusion proof has {int(math.log2(4096))} hashes")
