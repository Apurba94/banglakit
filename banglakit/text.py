"""Bangla text basics: clean Unicode, split into words and sentences, and reduce words to stems."""
import re
import unicodedata

VIRAMA = "্"
ZWJ, ZWNJ = "‍", "‌"
DIGITS = "০১২৩৪৫৬৭৮৯"
PUNCT = "।॥"
# Letters with a nukta have two possible spellings, as do the split vowel signs. NFC settles both:
# the nukta letters are excluded from composition, so each always becomes two code points.
NUKTA = {"ড়": "ড়", "ঢ়": "ঢ়", "য়": "য়"}


def normalise(text):
    """One spelling for one word: NFC, with no stray zero-width marks. After a virama, a joiner
    changes how a letter is drawn, so those are kept."""
    t = unicodedata.normalize("NFC", text.replace("﻿", ""))
    t = re.sub(f"(?<!{VIRAMA})[{ZWJ}{ZWNJ}](?!{VIRAMA})", "", t)
    return re.sub(r"[ 	 ]+", " ", t).strip()


def is_mark(c):
    return unicodedata.category(c)[0] == "M" or c in (ZWJ, ZWNJ)


def is_letter(c):
    return unicodedata.category(c)[0] in "LN"


def tokens(text):
    """Split into words. Vowel signs and viramas stay inside a word, which a regex \\w split gets wrong."""
    out, i, n = [], 0, len(text)
    while i < n:
        if not is_letter(text[i]):
            i += 1
            continue
        j = i
        while j < n and (is_letter(text[j]) or is_mark(text[j])):
            j += 1
        out.append(text[i:j])
        i = j
    return out


def sentences(text):
    """Split at the danda, a double danda, ? or !, and at a full stop after a Latin letter or digit."""
    parts = re.split(r"(?<=[।॥?!])\s+|(?<=[a-zA-Z0-9]\.)\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def graphemes(text):
    """Written units: a consonant with its vowel signs, or a whole conjunct."""
    out, i, n = [], 0, len(text)
    while i < n:
        u = text[i]
        i += 1
        while i < n:
            c = text[i]
            if is_mark(c):
                u += c
                i += 1
                if c == VIRAMA and i < n and unicodedata.category(text[i]) == "Lo":
                    u += text[i]
                    i += 1
            else:
                break
        out.append(u)
    return out


def to_bangla_digits(text):
    return str(text).translate(str.maketrans("0123456789", DIGITS))


def to_latin_digits(text):
    return str(text).translate(str.maketrans(DIGITS, "0123456789"))


SUFFIXES = sorted(unicodedata.normalize("NFC", """গুলোতে গুলোকে গুলোর গুলিতে গুলির গুলো গুলি দেরকে দিগকে দেরও দের রাও এরা ওরা টাকে টিকে টির টার টাই টিই খানা খানি টা টি কেও কেই কে তেই তেও তে রাই রা য়ের য়ে েরও েরই ের রও রই""").split(), key=len, reverse=True)
PROTECT = {unicodedata.normalize("NFC", w) for w in "তারা সে কে যে এটি সেটি ওটি আমরা তোমরা এই সেই বাংলা কথা মাতা পিতা খাতা রাতে কাতার".split()}
MIN_STEM_UNITS = 2


def stem(word):
    """A light rule stemmer: it removes noun endings only, and leaves a word alone when unsure.
    It does not handle verbs, because Bangla verb forms need a real morphological analyser."""
    w = normalise(word)
    if w in PROTECT:
        return w
    for s in SUFFIXES:
        if w.endswith(s):
            base = w[:-len(s)]
            if len(graphemes(base)) >= MIN_STEM_UNITS:
                return base
    return w


VOWELS = {"অ": "o", "আ": "a", "ই": "i", "ঈ": "i", "উ": "u", "ঊ": "u", "ঋ": "ri", "এ": "e", "ঐ": "oi", "ও": "o", "ঔ": "ou"}
SIGNS = {"া": "a", "ি": "i", "ী": "i", "ু": "u", "ূ": "u", "ৃ": "ri", "ে": "e", "ৈ": "oi", "ো": "o", "ৌ": "ou"}
CONSONANTS = {"ক": "k", "খ": "kh", "গ": "g", "ঘ": "gh", "ঙ": "ng", "চ": "ch", "ছ": "chh", "জ": "j", "ঝ": "jh", "ঞ": "n", "ট": "t", "ঠ": "th", "ড": "d", "ঢ": "dh", "ণ": "n", "ত": "t", "থ": "th", "দ": "d", "ধ": "dh", "ন": "n", "প": "p", "ফ": "ph", "ব": "b", "ভ": "bh", "ম": "m", "য": "j", "র": "r", "ল": "l", "শ": "sh", "ষ": "sh", "স": "s", "হ": "h", "ড়": "r", "ঢ়": "rh", "য়": "y", "ৎ": "t"}
SIGNS_OTHER = {"ং": "ng", "ঃ": "h", "ঁ": ""}


def romanise(text):
    """A readable Latin spelling for names and search. It is approximate: it cannot know where the
    inherent vowel is silent in every word, so it drops it at word ends, as Bangla usually does."""
    t = normalise(text)
    for pair, letter in NUKTA.items():
        t = t.replace(pair, letter)
    out = []
    n = len(t)
    for i, c in enumerate(t):
        if c in CONSONANTS:
            out.append(CONSONANTS[c])
            nxt = t[i + 1] if i + 1 < n else ""
            if nxt and nxt not in SIGNS and nxt != VIRAMA and nxt not in SIGNS_OTHER and is_letter(nxt):
                out.append("o")
        elif c in VOWELS:
            out.append(VOWELS[c])
        elif c in SIGNS:
            out.append(SIGNS[c])
        elif c in SIGNS_OTHER:
            out.append(SIGNS_OTHER[c])
        elif c == VIRAMA:
            pass
        elif c in DIGITS:
            out.append(str(DIGITS.index(c)))
        elif c in PUNCT:
            out.append(".")
        else:
            out.append(c)
    return "".join(out)
