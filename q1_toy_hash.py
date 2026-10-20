"""Question 1(b): Stamp's toy checksum h(X) = (3*X0 + 2*X1 + X2) mod 256."""


def h(msg):
    assert len(msg) == 3
    return (3 * msg[0] + 2 * msg[1] + msg[2]) % 256


BID = b"BID"
target = h(BID)
print(f"message BID = {tuple(BID)} = {BID!r}")
print(f"(i)   h(BID) = (3*66 + 2*73 + 68) mod 256 = {3*66 + 2*73 + 68} mod 256 = {target}")

# (ii) second preimage: any other 3-byte message with the same hash.
# Changing X2 by +d and X0 by something that cancels 3*? ... easiest: X2 -> X2+256 is impossible (byte),
# so adjust two bytes: increasing X0 by 1 adds 3; compensate by decreasing X2 by 3.
second = bytes([BID[0] + 1, BID[1], BID[2] - 3])
print(f"\n(ii)  second preimage: {tuple(second)} = {second!r}, h = {h(second)}  (equal: {h(second) == target})")
# brute-force confirmation that many exist
count = sum(1 for a in range(256) for b in range(256) for c in range(256)
            if (3*a + 2*b + c) % 256 == target)
print(f"      total 3-byte messages with this hash: {count} (= 256^2, one for every (X0,X1))")

# (iii) targeted preimage with first two bytes = 'OK'
O, K = ord("O"), ord("K")  # 79, 75
x2 = (target - 3*O - 2*K) % 256
targeted = bytes([O, K, x2])
print(f"\n(iii) targeted preimage starting 'OK': X2 = ({target} - 3*{O} - 2*{K}) mod 256 = {x2}")
print(f"      message = {tuple(targeted)} = {targeted!r}, h = {h(targeted)}  (equal: {h(targeted) == target})")
