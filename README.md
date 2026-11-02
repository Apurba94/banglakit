# BanglaKit

Bangla text tools in pure Python, with no dependencies: clean Unicode, proper word splitting, numbers in words, and the revised Bengali calendar.

```python
from datetime import date
from banglakit import format_date, normalise, number_to_words, stem, taka_in_words, tokens

tokens("আমি পানি খাই।")                # ['আমি', 'পানি', 'খাই']
stem("বইগুলো")                          # 'বই'
number_to_words(250000)                 # 'দুই লক্ষ পঞ্চাশ হাজার'
taka_in_words(250.5)                    # 'দুইশত পঞ্চাশ টাকা পঞ্চাশ পয়সা মাত্র'
format_date(date(2026, 4, 14))          # 'মঙ্গলবার, ১ বৈশাখ ১৪৩৩ বঙ্গাব্দ'
```

```
python -m banglakit words 1250000
python -m banglakit taka 2500.50
python -m banglakit date 2026-04-14
```

## Why this exists

Two common bugs break Bangla software without warning.

**Word splitting.** Python's regex `\w` does not match vowel signs, so a regex tokeniser cuts "পানি" into pieces. `tokens` keeps words whole. This same bug was found and fixed during the build of a search engine in this suite.

**Hidden spelling differences.** "ড়" can be stored as one character or as two, and the two look the same on screen, so a plain search can miss a word. `normalise` applies Unicode NFC, which gives each word one spelling, and removes stray zero-width marks.

## What is included

| Tool | Use |
|---|---|
| `normalise` | One spelling for one word, without removing joiners that change how a letter is drawn |
| `tokens`, `sentences`, `graphemes` | Words, sentences and written units |
| `stem` | A light rule stemmer for noun endings |
| `romanise` | An approximate Latin spelling for names and search |
| `number_to_words`, `taka_in_words` | Numbers with হাজার, লক্ষ and কোটি, for cheques and receipts |
| `group_digits`, `format_bangla` | 12,34,567 and Bangla digits |
| `to_bengali`, `from_bengali`, `format_date`, `season` | The revised Bengali calendar |

## The calendar

This follows Bangladesh's revised calendar, used since 2019: six months of 31 days, then 30 days, with Falgun at 29 days, or 30 in a leap year. So 21 February always falls on 8 Falgun, 26 March on 12 Chaitra, and 16 December on 1 Poush. West Bengal uses a different calendar, whose dates can differ by a day or so.

## How it is tested

The calendar is checked against national dates in leap and ordinary years, and every day across 13 years must convert and back. Text tests use real conjuncts and vowel signs.

## Limits

The stemmer handles noun endings only, and verbs need real morphological analysis. It has no dictionary, so it can get unusual words wrong. Romanisation cannot always know when the inherent vowel is silent. Number words use the common forms, and spellings vary between style guides, so check them for official documents.

MIT licence.
