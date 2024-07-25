import itertools
import string
import sys
import textwrap
import matplotlib.pyplot as plt

def vigenere(plaintext, key, a_is_zero=True):
    key = key.lower()
    if not all(k in string.ascii_lowercase for k in key):
        raise ValueError("Invalid key {!r}; the key can only consist of English letters".format(key))
    key_iter = itertools.cycle(map(ord, key))
    return "".join(
        chr(ord('a') + (
            (next(key_iter) - ord('a') + ord(letter) - ord('a'))
            + (0 if a_is_zero else 2)
            ) % 26) if letter in string.ascii_lowercase
        else letter
        for letter in plaintext.lower()
    )

def vigenere_decrypt(ciphertext, key, a_is_zero=True):
    key_ind = [ord(k) - ord('a') for k in key.lower()]
    inverse = "".join(chr(ord('a') +
            ((26 if a_is_zero else 22) -
                (ord(k) - ord('a'))
            ) % 26) for k in key)
    return vigenere(ciphertext, inverse, a_is_zero)

def test_vigenere(text, key, a_is_zero=True):
    ciphertext = vigenere(text, key, a_is_zero)
    plaintext  = vigenere_decrypt(ciphertext, key, a_is_zero)
    assert plaintext == text, "{!r} -> {!r} -> {!r} (a {}= 0)".format(
        text, ciphertext, plaintext, "" if a_is_zero else "!")
for text in ["rewind", "text with spaces", "pun.ctuation", "numb3rs"]:
    for key in ["iepw", "aceaq", "safe", "pwa"]:
        test_vigenere(text, key, True)
        test_vigenere(text, key, False)

ENGLISH_FREQ = (0.0749, 0.0129, 0.0354, 0.0362, 0.1400, 0.0218, 0.0174, 0.0422, 0.0665, 0.0027, 0.0047,
                0.0357, 0.0339, 0.0674, 0.0737, 0.0243, 0.0026, 0.0614, 0.0695, 0.0985, 0.0300, 0.0116,
                0.0169, 0.0028, 0.0164, 0.0004)

def compare_freq(text):
    if not text:
        return None
    text = [t for t in text.lower() if t in string.ascii_lowercase]
    freq = [0] * 26
    total = float(len(text))
    for l in text:
        freq[ord(l) - ord('a')] += 1
    return sum(abs(f / total - E) for f, E in zip(freq, ENGLISH_FREQ))

def solve_vigenere(text, key_min_size=None, key_max_size=None, a_is_zero=True):
    best_keys = []
    key_min_size = key_min_size or 1
    key_max_size = key_max_size or 20
    text_letters = [c for c in text.lower() if c in string.ascii_lowercase]
    for key_length in range(key_min_size, key_max_size):
        key = [None] * key_length
        for key_index in range(key_length):
            letters = "".join(itertools.islice(text_letters, key_index, None, key_length))
            shifts = []
            for key_char in string.ascii_lowercase:
                shifts.append(
                    (compare_freq(vigenere_decrypt(letters, key_char, a_is_zero)), key_char)
                )
            key[key_index] = min(shifts, key=lambda x: x[0])[1]
        best_keys.append("".join(key))
    best_keys.sort(key=lambda key: compare_freq(vigenere_decrypt(text, key, a_is_zero)))
    return best_keys[:2]

CIPHERTEXT = sys.stdin.read().strip()
char_counts = {char: CIPHERTEXT.count(char) for char in string.ascii_uppercase}
total_chars = sum(char_counts.values())
char_freqs = {char: count / total_chars for char, count in char_counts.items()}

plt.figure(figsize=(12, 6))
plt.bar(list(char_freqs.keys()), list(char_freqs.values()))
plt.xlabel('Letters')
plt.ylabel('Frequency')
plt.title('Frequency Distribution of Ciphertext')
plt.savefig('frequency_distribution.jpg')

print("Frequency distribution plot saved as 'frequency_distribution.jpg'")
for key in reversed(solve_vigenere(CIPHERTEXT)):
    print("")
    print("Found key: {!r}".format(key))
    print("Solution:")
    print("=" * 80)
    print(textwrap.fill(vigenere_decrypt(CIPHERTEXT, key)))
    print("=" * 80)