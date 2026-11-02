"""Quick tools.

python -m banglakit words 1250000
python -m banglakit taka 2500.50
python -m banglakit date 2026-04-14
python -m banglakit clean file.txt
"""
import sys
from datetime import date

from . import format_date, normalise, number_to_words, season, taka_in_words


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(argv) == 3 and argv[1] == "words":
        print(number_to_words(int(argv[2])))
    elif len(argv) == 3 and argv[1] == "taka":
        print(taka_in_words(float(argv[2])))
    elif len(argv) == 3 and argv[1] == "date":
        d = date.fromisoformat(argv[2])
        print(format_date(d), "·", season(d))
    elif len(argv) == 3 and argv[1] == "clean":
        with open(argv[2], encoding="utf-8") as f:
            print(normalise(f.read()))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
