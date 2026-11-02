import unicodedata
import unittest
from datetime import date, timedelta

from banglakit import MONTHS, format_bangla, format_date, from_bengali, graphemes, group_digits, month_lengths, normalise, number_to_words, romanise, season, sentences, stem, taka_in_words, to_bangla_digits, to_bengali, to_latin_digits, tokens
from banglakit.numbers import UNDER_100


class TestNormalise(unittest.TestCase):
    def test_both_spellings_become_one(self):
        self.assertEqual(normalise("ড়"), normalise("ড়"))
        self.assertEqual(normalise("য়"), normalise("য়"))
        self.assertEqual(normalise("বাড়ি"), normalise("বাড়ি"))

    def test_result_is_standard_nfc(self):
        for t in ("য়", "বাড়ি", "কোথায়", "কো"):
            self.assertTrue(unicodedata.is_normalized("NFC", normalise(t)))

    def test_split_vowel_signs_join(self):
        self.assertEqual(normalise("কো"), "কো")
        self.assertEqual(normalise("কৌ"), "কৌ")

    def test_stray_zero_width_goes_and_joiners_after_virama_stay(self):
        self.assertEqual(normalise("ক‍ম"), "কম")
        self.assertIn("‍", normalise("ক্‍ষ"))

    def test_spaces(self):
        self.assertEqual(normalise("  এক   দুই তিন "), "এক দুই তিন")

    def test_same_result_twice(self):
        for t in ("বাড়ি", "কোথায়", "ক্ষুদ্র", "﻿আমি"):
            self.assertEqual(normalise(normalise(t)), normalise(t))


class TestTokens(unittest.TestCase):
    def test_words_stay_whole(self):
        self.assertEqual(tokens("আমি পানি খাই।"), ["আমি", "পানি", "খাই"])

    def test_conjuncts(self):
        self.assertEqual(tokens("ক্ষুদ্র শিক্ষা"), ["ক্ষুদ্র", "শিক্ষা"])

    def test_mixed(self):
        self.assertEqual(tokens("Python ১২৩ ও AI-তে"), ["Python", "১২৩", "ও", "AI", "তে"])

    def test_sentences(self):
        self.assertEqual(sentences("আমি যাব। তুমি কি যাবে? হ্যাঁ!"), ["আমি যাব।", "তুমি কি যাবে?", "হ্যাঁ!"])

    def test_graphemes(self):
        self.assertEqual(graphemes("পানি"), ["পা", "নি"])
        self.assertEqual(graphemes("ক্ষ"), ["ক্ষ"])
        self.assertEqual("".join(graphemes("স্কুলে যাব")), "স্কুলে যাব")

    def test_digits(self):
        self.assertEqual(to_bangla_digits("2026"), "২০২৬")
        self.assertEqual(to_latin_digits("১৯৭১"), "1971")


class TestStem(unittest.TestCase):
    def test_noun_endings(self):
        cases = {"ছেলেরা": "ছেলে", "মানুষের": "মানুষ", "বইগুলো": "বই", "শিক্ষকদের": "শিক্ষক", "ছাত্রটি": "ছাত্র", "স্কুলে": "স্কুলে"}
        for w, s in cases.items():
            self.assertEqual(stem(w), s, w)

    def test_short_and_protected_words_are_left_alone(self):
        for w in ("তারা", "কে", "বাংলা", "রাতে", "মা"):
            self.assertEqual(stem(w), normalise(w))

    def test_unknown_words_stay(self):
        self.assertEqual(stem("সুন্দর"), "সুন্দর")


class TestRomanise(unittest.TestCase):
    def test_examples(self):
        self.assertEqual(romanise("বাংলা"), "bangla")
        self.assertEqual(romanise("আমি"), "ami")
        self.assertEqual(romanise("পানি"), "pani")

    def test_nothing_bangla_is_left_behind(self):
        for t in ("কম্পিউটার", "ক্ষুদ্র ঋণ", "বিশ্ববিদ্যালয়", "১৯৭১"):
            self.assertFalse(any("ঀ" <= c <= "৿" for c in romanise(t)), t)


class TestNumbers(unittest.TestCase):
    def test_table_is_complete_and_unique(self):
        self.assertEqual(len(UNDER_100), 100)
        self.assertEqual(len(set(UNDER_100)), 100)
        self.assertTrue(all(unicodedata.normalize("NFC", w) == w for w in UNDER_100))

    def test_landmarks(self):
        self.assertEqual(number_to_words(0), "শূন্য")
        self.assertEqual(number_to_words(21), "একুশ")
        self.assertEqual(number_to_words(52), "বায়ান্ন")
        self.assertEqual(number_to_words(71), "একাত্তর")
        self.assertEqual(number_to_words(99), "নিরানব্বই")

    def test_large(self):
        self.assertEqual(number_to_words(100), "একশত")
        self.assertEqual(number_to_words(1971), "এক হাজার নয়শত একাত্তর")
        self.assertEqual(number_to_words(250000), "দুই লক্ষ পঞ্চাশ হাজার")
        self.assertEqual(number_to_words(12345678), "এক কোটি তেইশ লক্ষ পঁয়তাল্লিশ হাজার ছয়শত আটাত্তর")

    def test_very_large_nests_crores(self):
        self.assertIn("কোটি", number_to_words(10 ** 12))

    def test_negative_and_bad(self):
        self.assertTrue(number_to_words(-5).endswith("পাঁচ"))
        with self.assertRaises(TypeError):
            number_to_words(1.5)

    def test_taka(self):
        self.assertEqual(taka_in_words(250.5), "দুইশত পঞ্চাশ টাকা পঞ্চাশ পয়সা মাত্র")
        self.assertEqual(taka_in_words(1000), "এক হাজার টাকা মাত্র")
        with self.assertRaises(ValueError):
            taka_in_words(-1)

    def test_grouping(self):
        self.assertEqual(group_digits(1234567), "12,34,567")
        self.assertEqual(group_digits(999), "999")
        self.assertEqual(group_digits(-100000), "-1,00,000")
        self.assertEqual(format_bangla(1000), "১,০০০")


class TestCalendar(unittest.TestCase):
    def check(self, d, month, day, year=None):
        y, m, n = to_bengali(d)
        self.assertEqual((MONTHS[m], n), (month, day), d)
        if year:
            self.assertEqual(y, year)

    def test_national_dates(self):
        self.check(date(2026, 4, 14), "বৈশাখ", 1, 1433)        # Pohela Boishakh
        self.check(date(2026, 2, 21), "ফাল্গুন", 8)             # Language Martyrs' Day
        self.check(date(2024, 2, 21), "ফাল্গুন", 8)             # the same in a leap year
        self.check(date(2026, 3, 26), "চৈত্র", 12)              # Independence Day
        self.check(date(2024, 3, 26), "চৈত্র", 12)
        self.check(date(2026, 12, 16), "পৌষ", 1)                # Victory Day

    def test_year_turns_on_14_april(self):
        self.assertEqual(to_bengali(date(2026, 4, 13))[0], 1432)
        self.assertEqual(to_bengali(date(2026, 4, 14))[0], 1433)

    def test_months_add_up(self):
        for y in range(1400, 1460):
            total = sum(month_lengths(y))
            self.assertEqual(total, (date(y + 594, 4, 14) - date(y + 593, 4, 14)).days, y)

    def test_every_day_round_trips(self):
        d = date(2019, 1, 1)
        while d < date(2032, 1, 1):
            y, m, n = to_bengali(d)
            self.assertEqual(from_bengali(y, m, n), d)
            d += timedelta(days=1)

    def test_days_never_skip(self):
        d = date(2023, 4, 14)
        last = to_bengali(d)
        for _ in range(800):
            d += timedelta(days=1)
            cur = to_bengali(d)
            self.assertTrue(cur[2] == last[2] + 1 or cur[2] == 1)
            last = cur

    def test_bad_date(self):
        with self.assertRaises(ValueError):
            from_bengali(1433, 6, 31)

    def test_format(self):
        self.assertEqual(format_date(date(2026, 4, 14)), "মঙ্গলবার, ১ বৈশাখ ১৪৩৩ বঙ্গাব্দ")

    def test_seasons(self):
        self.assertEqual(season(date(2026, 4, 20)), "গ্রীষ্ম")
        self.assertEqual(season(date(2026, 1, 20)), "শীত")


if __name__ == "__main__":
    unittest.main()
