# Hash Lab – Python scripts and report

**Course:** Information Security, *Cryptographic Hash Functions in Practice* lab
**Author:** Diellart Mulolli (230756200035)
**Repository:** <https://github.com/Diellart-Mulolli/hash-lab>

This repository contains the lab report (`report.tex` / `report.pdf`) and six small Python
scripts. The scripts verify the calculations and claims made in the report:

| Script | Report section | What it shows |
|---|---|---|
| `q1_toy_hash.py` | Question 1(b) | Stamp's toy checksum: second preimages and targeted preimages are trivial |
| `q2_birthday.py` | Questions 1(c), 2(b), 2(c) | Birthday collision probability and brute-force timing |
| `q3_length_extension.py` | Question 3(b) | A working length-extension forgery against `SHA-256(K‖M)` |
| `q4_hmac.py` | Question 4(b) | HMAC-SHA-256 structure (key padding, ipad/opad, block counts) |
| `q5_merkle.py` | Question 5(c) | Merkle tree with a toy combiner: root, inclusion proof, tamper detection |
| `q5_passwords.py` | Question 5(a) | Offline password-cracking time estimates |

## Project structure

```
hash-lab/
├── .gitignore              keeps Python caches and LaTeX build files out of git
├── README.md               this file: running guide and explanation of every script
├── report.tex              LaTeX source of the report (IEEE references, pdfLaTeX/Overleaf/Tectonic)
├── report.pdf              compiled report, 13 pages (Appendix A: script values and outputs)
├── q1_toy_hash.py          Q1: toy checksum h(X) = (3*X0 + 2*X1 + X2) mod 256
├── q2_birthday.py          Q1c/Q2b/Q2c: birthday bound and brute-force timing
├── q3_length_extension.py  Q3: length-extension attack, with a from-scratch resumable SHA-256
├── q4_hmac.py              Q4: HMAC-SHA-256 structure, checked against the stdlib
├── q5_merkle.py            Q5c: Merkle tree with T(x,y) = (3x + 5y + 7) mod 101
└── q5_passwords.py         Q5a: SHA-256 vs Argon2id cracking-time estimates
```

---

## Running guide

### 1. Prerequisites

Only **Python 3.8 or newer** is required (check with `python3 --version`). Every script uses
the standard library alone — `hashlib`, `hmac`, `math`, `struct` — so there is **nothing to
install** and no virtual environment to set up.

### 2. Get the project

Download it from GitHub (*Code → Download ZIP*) or clone it:

```bash
git clone https://github.com/Diellart-Mulolli/hash-lab.git
```
```bash
cd hash-lab
```

### 3. Run the scripts

Run each script from inside the project folder (on Windows, write `py` instead of `python3`).
All six finish in well under a second.

| Command | What to look for in the output |
|---|---|
| `python3 q1_toy_hash.py` | `h(BID) = ... = 156`; a second preimage `CIA` and a targeted preimage `OK\x19`, both with `h = 156` |
| `python3 q2_birthday.py` | `P(16 messages) ~= 0.374`; `2^80: ~3.8e4 years`; `2^32 variants` |
| `python3 q3_length_extension.py` | `custom SHA-256 matches hashlib: True` and, at the end, `forgery accepted: True` |
| `python3 q4_hmac.py` | `K XOR ipad: 0x5D 0x53 0x4F ...`; `HMAC total = 19 blocks`; `manual == hmac.new: True` |
| `python3 q5_merkle.py` | root `R = 83`, proof verifies `(matches root 83: True)`, altered root `98` |
| `python3 q5_passwords.py` | unsalted SHA-256 cracks all users in minutes; Argon2id makes one user `~8.9 years` |

### 4. Troubleshooting

| Problem | Fix |
|---|---|
| `python3: command not found` (Windows) | Use `py` or `python` instead. |
| A `SyntaxError` on an f-string | Your Python is older than 3.8; upgrade it. |

### 5. Suggested live demo for the presentation

`python3 q3_length_extension.py` is the strongest demo: it forges a valid `SHA-256(K‖M)` tag
for a tampered request **without the key**, and the forged tag matches the one the server
computes with the key — the whole length-extension attack in under a second.

---

## 1. `q1_toy_hash.py` – a checksum is not a hash (Question 1(b))

Stamp's toy hash is `h(X) = (3*X0 + 2*X1 + X2) mod 256` on a 3-byte message. The script
computes `h(BID)`, then **breaks** two security properties to show the formula is weak:

```
message BID = (66, 73, 68) = b'BID'
(i)   h(BID) = (3*66 + 2*73 + 68) mod 256 = 412 mod 256 = 156
(ii)  second preimage: (67, 73, 65) = b'CIA', h = 156  (equal: True)
      total 3-byte messages with this hash: 65536 (= 256^2, one for every (X0,X1))
(iii) targeted preimage starting 'OK': X2 = (156 - 3*79 - 2*75) mod 256 = 25
      message = (79, 75, 25) = b'OK\x19', h = 156  (equal: True)
```

**What it means.** The formula is *linear*: given a target and any two free bytes, the third
byte is the solution of one equation mod 256. So a second preimage (`CIA`) and even a
preimage with a chosen prefix (`OK`) are instant. A real hash has diffusion and
one-wayness, so neither is feasible. The short 8-bit output is not the weakness here — the
linearity is.

## 2. `q2_birthday.py` – birthday bound and brute-force time (Q1c, Q2b, Q2c)

Uses `P(k) ≈ 1 − exp(−k(k−1)/2^(n+1))`.

**What it means.** For the 8-bit toy hash, just 16 messages already collide with ~37%
probability, and ~19 reach 50% — far fewer than the 256 inputs, which is the birthday effect.
At 10^12 hashes/s, `2^64` takes ~214 days, `2^80` ~38,000 years, and `2^128` longer than the
universe has existed. This is why 128-bit security needs a 256-bit hash (collisions cost
`2^(n/2)`). The script also shows 32 either/or phrasings give `2^32` message variants, which
is exactly enough to birthday-attack any 64-bit hash.

## 3. `q3_length_extension.py` – length-extension forgery (Question 3(b))

The script implements SHA-256 from scratch so it can **resume** from a captured digest, which
is what makes the attack possible. It plays QuickPay's `tag = SHA-256(K‖M)` scheme:

```
sanity: custom SHA-256 matches hashlib: True
intercepted M   = b'amount=10&to=alice' (18 bytes)
...
forged tag (no key)   = 6abffc5fdeeda4397a8d76ba769e43000aa94e933bee39ce881e3d7a7723c1ac
server tag (with key) = 6abffc5fdeeda4397a8d76ba769e43000aa94e933bee39ce881e3d7a7723c1ac
forgery accepted: True
```

**What it means.** Because a Merkle–Damgård digest *is* the full internal state, Mallory sets
that state from the intercepted tag, appends the glue padding plus `&to=trudy`, and keeps
hashing — producing a tag the server accepts, **without ever knowing K**. The server reads the
last `to=` value, so the payment is redirected. This is why you must use HMAC (or SHA-3, or a
truncated hash), not `SHA-256(K‖M)`.

## 4. `q4_hmac.py` – HMAC-SHA-256 by hand (Question 4(b))

Computes the HMAC structure (without computing SHA-256 itself) for `K = "key"`, and checks the
two-pass construction against Python's `hmac` module (`manual == hmac.new: True`).

**What it means.** The 3-byte key is zero-padded to the 64-byte block; `K⊕ipad` and `K⊕opad`
differ from the pad bytes only in the first 3 positions. HMAC adds just ~2 compression
blocks over a plain hash (19 vs 16 for a 1000-byte message), so the authentication is
essentially free.

## 5. `q5_merkle.py` – Merkle tree by hand (Question 5(c))

Uses the toy combiner `T(x,y) = (3x + 5y + 7) mod 101` on four leaves.

**What it means.** The root is `R = 83`. A light client that stores only the root can verify
transaction 3 with a 2-value proof `[L4, N12]`, recomputing `T(N12, T(L3, L4)) = 83`. Changing
one leaf changes the root to `98`, so tampering is detected. A 4096-transaction block needs a
12-hash proof — the logarithmic cost that makes Merkle trees (and blockchains) scalable.

## 6. `q5_passwords.py` – password-cracking economics (Question 5(a))

Estimates offline cracking time for an 8-character alphanumeric space (`36^8 ≈ 2^41`).

**What it means.** Unsalted SHA-256 lets one precomputed table crack **all** users in minutes.
A per-user salt removes the shared table, so all users cost ~8.9 years, but one chosen user is
still minutes. A memory-hard Argon2id (slow by design) raises even one user to ~8.9 years.
Salts stop precomputation; peppers add a secret the attacker lacks; memory-hardness kills
GPU/ASIC parallelism. The lesson: use Argon2id with a salt — and still require long passwords.

---

## Building the PDF

`report.pdf` is already compiled. To rebuild it after editing `report.tex`:

- **Overleaf (no installation):** upload `report.tex` and click *Recompile* (pdfLaTeX works).
- **Tectonic** (single binary, downloads only what it needs):
  ```bash
  tectonic report.tex
  ```
- **TeX Live:** run pdfLaTeX twice so the citation numbers resolve:
  ```bash
  pdflatex report.tex && pdflatex report.tex
  ```
