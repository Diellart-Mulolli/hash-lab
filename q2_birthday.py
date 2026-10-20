"""Questions 1(c) and 2(b),(c): birthday bound and brute-force timing."""
import math


def collision_prob(k, n_bits):
    """Approximate probability of >=1 collision among k random n-bit hashes."""
    return 1 - math.exp(-k * (k - 1) / 2 ** (n_bits + 1))


print("Q1(c): 8-bit toy hash")
p16 = collision_prob(16, 8)
print(f"  P(16 messages) = 1 - exp(-16*15 / 2^9) = 1 - exp(-{16*15}/512) = {p16:.4f}  (~{p16*100:.1f}%)")
k50 = 1.18 * 2 ** (8 / 2)
print(f"  k for P~=50%: 1.18 * 2^(8/2) = 1.18 * {2**4} = {k50:.1f}  (~19 messages)")
# exact search for the smallest k crossing 50%
k = next(k for k in range(1, 100) if collision_prob(k, 8) >= 0.5)
print(f"  smallest k with P>=0.5 (exact from the formula): {k}")

print("\nQ2(b): attacker at 1e12 hashes/second")
rate = 1e12
sec_per_year = 365.25 * 24 * 3600
for e in (64, 80, 128):
    secs = 2 ** e / rate
    years = secs / sec_per_year
    if years < 1:
        print(f"  2^{e}: {secs:.3g} s = {secs/86400:.3g} days")
    else:
        print(f"  2^{e}: {secs:.3g} s = {years:.3g} years")
print(f"  for comparison, 2^80 / 1e12 = {2**80/rate/sec_per_year:.3g} years")
print(f"  SHAttered (2017) used ~2^63.1 compression calls; 2^63.1/1e12 = {2**63.1/rate/86400:.2f} days "
      f"at this imagined rate")

print("\nQ2(c): birthday attack on signatures")
print(f"  32 independent either/or phrasings -> 2^32 = {2**32} variants of each message")
print("  collision between the 'good' and 'evil' sets needs ~2^(n/2) variants;")
print("  2^32 variants defeat any hash with n <= 64 bits (2^(64/2) = 2^32).")
