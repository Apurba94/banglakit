"""Numbers in Bangla words, with lakh and crore, and the revised Bengali calendar."""
from datetime import date, timedelta

from .text import to_bangla_digits

UNDER_100 = """শূন্য এক দুই তিন চার পাঁচ ছয় সাত আট নয় দশ এগারো বারো তেরো চৌদ্দ পনেরো ষোলো সতেরো আঠারো উনিশ বিশ
একুশ বাইশ তেইশ চব্বিশ পঁচিশ ছাব্বিশ সাতাশ আটাশ ঊনত্রিশ ত্রিশ একত্রিশ বত্রিশ তেত্রিশ চৌত্রিশ পঁয়ত্রিশ ছত্রিশ সাঁইত্রিশ আটত্রিশ ঊনচল্লিশ চল্লিশ
একচল্লিশ বিয়াল্লিশ তেতাল্লিশ চুয়াল্লিশ পঁয়তাল্লিশ ছেচল্লিশ সাতচল্লিশ আটচল্লিশ ঊনপঞ্চাশ পঞ্চাশ একান্ন বায়ান্ন তিপ্পান্ন চুয়ান্ন পঞ্চান্ন ছাপ্পান্ন সাতান্ন আটান্ন ঊনষাট ষাট
একষট্টি বাষট্টি তেষট্টি চৌষট্টি পঁয়ষট্টি ছেষট্টি সাতষট্টি আটষট্টি ঊনসত্তর সত্তর একাত্তর বাহাত্তর তিয়াত্তর চুয়াত্তর পঁচাত্তর ছিয়াত্তর সাতাত্তর আটাত্তর ঊনআশি আশি
একাশি বিরাশি তিরাশি চুরাশি পঁচাশি ছিয়াশি সাতাশি আটাশি ঊননব্বই নব্বই একানব্বই বিরানব্বই তিরানব্বই চুরানব্বই পঁচানব্বই ছিয়ানব্বই সাতানব্বই আটানব্বই নিরানব্বই""".split()


def number_to_words(n):
    """In the South Asian system: হাজার, লক্ষ and কোটি. Works for any whole number."""
    if not isinstance(n, int):
        raise TypeError("a whole number is needed")
    if n < 0:
        return "ঋণাত্মক " + number_to_words(-n)
    if n < 100:
        return UNDER_100[n]
    parts = []
    crore, n = divmod(n, 10 ** 7)
    if crore:
        parts.append(number_to_words(crore) + " কোটি")
    lakh, n = divmod(n, 10 ** 5)
    if lakh:
        parts.append(UNDER_100[lakh] + " লক্ষ")
    thousand, n = divmod(n, 1000)
    if thousand:
        parts.append(UNDER_100[thousand] + " হাজার")
    hundred, n = divmod(n, 100)
    if hundred:
        parts.append(UNDER_100[hundred] + "শত")
    if n:
        parts.append(UNDER_100[n])
    return " ".join(parts)


def taka_in_words(amount):
    """For cheques and receipts, such as ২৫০.৫০ -> দুইশত পঞ্চাশ টাকা পঞ্চাশ পয়সা মাত্র."""
    if amount < 0:
        raise ValueError("an amount cannot be below zero")
    paisa = int(round(amount * 100))
    taka, p = divmod(paisa, 100)
    text = number_to_words(taka) + " টাকা"
    if p:
        text += " " + number_to_words(p) + " পয়সা"
    return text + " মাত্র"


def group_digits(n):
    """South Asian grouping: 12,34,567."""
    s = str(abs(int(n)))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        groups = []
        while head:
            groups.insert(0, head[-2:])
            head = head[:-2]
        s = ",".join(groups + [tail])
    return ("-" if n < 0 else "") + s


def format_bangla(n):
    return to_bangla_digits(group_digits(n))


MONTHS = ["বৈশাখ", "জ্যৈষ্ঠ", "আষাঢ়", "শ্রাবণ", "ভাদ্র", "আশ্বিন", "কার্তিক", "অগ্রহায়ণ", "পৌষ", "মাঘ", "ফাল্গুন", "চৈত্র"]
SEASONS = ["গ্রীষ্ম", "বর্ষা", "শরৎ", "হেমন্ত", "শীত", "বসন্ত"]
WEEKDAYS = ["সোমবার", "মঙ্গলবার", "বুধবার", "বৃহস্পতিবার", "শুক্রবার", "শনিবার", "রবিবার"]


def month_lengths(bangla_year):
    """Bangladesh's revised calendar (2019): six months of 31 days, then 30 days, with Falgun 29,
    or 30 in a year whose February has a leap day."""
    gregorian_feb = bangla_year + 594
    leap = gregorian_feb % 4 == 0 and (gregorian_feb % 100 != 0 or gregorian_feb % 400 == 0)
    return [31] * 6 + [30, 30, 30, 30, 30 if leap else 29, 30]


def to_bengali(d):
    """Convert a Gregorian date to (year, month index, day). The year begins on 14 April."""
    start_year = d.year if (d.month, d.day) >= (4, 14) else d.year - 1
    days = (d - date(start_year, 4, 14)).days
    year = start_year - 593
    for i, length in enumerate(month_lengths(year)):
        if days < length:
            return year, i, days + 1
        days -= length
    raise ValueError("date out of range")


def from_bengali(year, month, day):
    lengths = month_lengths(year)
    if not 0 <= month < 12 or not 1 <= day <= lengths[month]:
        raise ValueError("no such date in the Bengali calendar")
    return date(year + 593, 4, 14) + timedelta(days=sum(lengths[:month]) + day - 1)


def format_date(d):
    y, m, day = to_bengali(d)
    return f"{WEEKDAYS[d.weekday()]}, {to_bangla_digits(day)} {MONTHS[m]} {to_bangla_digits(y)} বঙ্গাব্দ"


def season(d):
    return SEASONS[to_bengali(d)[1] // 2]
