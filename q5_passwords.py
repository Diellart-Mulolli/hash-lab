"""Question 5(a): offline password-cracking time estimates."""

CHARSET = 36          # a-z plus 0-9
LENGTH = 8
SPACE = CHARSET ** LENGTH
USERS = 10 ** 6
FAST = 1e10           # SHA-256 guesses per second
SLOW = 1e4            # Argon2id guesses per second (memory-hard, recommended params)

YEAR = 365.25 * 24 * 3600


def human(seconds):
    if seconds < 1:
        return f"{seconds:.3g} s"
    if seconds < 86400:
        return f"{seconds/3600:.3g} hours"
    if seconds < YEAR:
        return f"{seconds/86400:.3g} days"
    return f"{seconds/YEAR:.3g} years"


print(f"password space = 36^8 = {SPACE:,} ~= 2^{SPACE.bit_length()-1}")
print(f"users = {USERS:,}\n")

# (i) unsalted SHA-256: one table covers every user at once.
t_all_unsalted = SPACE / FAST
print("(i) unsalted SHA-256:")
print(f"    search the whole space once = {SPACE:,}/{FAST:.0g} = {human(t_all_unsalted)}")
print("    the same work breaks ALL users (identical passwords hash identically; precomputable).")

# (ii) salted SHA-256: salt removes precomputation and forces per-user work.
t_one_salted = SPACE / FAST
t_all_salted = USERS * SPACE / FAST
print("\n(ii) per-user random salt, still SHA-256:")
print(f"    one chosen user  = {human(t_one_salted)} (same as (i): the hash is still fast)")
print(f"    all {USERS:,} users = {USERS:,} x that = {human(t_all_salted)} (no shared table any more)")

# (iii) salted Argon2id: slow hash multiplies per-user cost.
t_one_argon = SPACE / SLOW
print("\n(iii) salted Argon2id (~1e4 guesses/s):")
print(f"    one chosen user = {SPACE:,}/{SLOW:.0g} = {human(t_one_argon)}")
print(f"    slowdown vs fast hash = {FAST/SLOW:.0g}x")
