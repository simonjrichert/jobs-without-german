"""Keep jobs from jobs.csv whose titles look entry-level (about 0–2 years).

A title is dropped when it names a student role or a senior/lead level.
The advert text is not read, so this is only as good as the title.
"""

import csv
import re
from datetime import date
from pathlib import Path

SOURCE = Path(__file__).with_name("jobs.csv")
OUTPUT = Path(__file__).with_name("entry level jobs.csv")
README = Path(__file__).with_name("README.md")

# Whole words/phrases only, so "intern" does not match "international".
EXCLUDE = [
    "intern",
    "internship",
    "internships",
    "working student",
    "werkstudent",
    "student",
    "fellow",
    "fellowship",
    "premaster",
    "senior",
    "sr",
    "lead",
    "teamlead",
    "head",
    "director",
    "principal",
    "staff",
    "expert",
    "vp",
    "vice president",
    "chief",
    "cfo",
    "ceo",
    "cto",
    "cpo",
    "chro",
    "cmo",
    "leader",
    "developer",
    "engineer",
    "backend",
    "legal counsel",
    "partner",
    "deployment",
]


def exclude_pattern():
    parts = [re.escape(word) for word in EXCLUDE]
    return re.compile(rf"\b(?:{'|'.join(parts)})\b", re.IGNORECASE)


def is_entry_level(title, pattern):
    return pattern.search(title or "") is None


def md_cell(text):
    return (text or "").replace("|", "\\|").replace("\n", " ")


def write_readme(header, rows):
    title_i = header.index("Position title")
    employer_i = header.index("Employer")
    city_i = header.index("City")
    label_i = header.index("Language label")
    url_i = header.index("Listing URL")
    source_i = header.index("Search term")

    lines = [
        "# Entry-level jobs without German",
        "",
        "English-language roles in Germany, Austria, and Switzerland. "
        "Titles that look intern, student, or senior are left out.",
        "",
        f"{len(rows)} jobs · updated {date.today().isoformat()} · "
        "source: [Jobs without German](https://www.jobswithoutgerman.de/)",
        "",
        "The same list is in "
        "[entry level jobs.csv](entry%20level%20jobs.csv).",
        "",
        "| Title | Employer | City | Language | Source |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        title = md_cell(row[title_i])
        url = row[url_i]
        linked = f"[{title}]({url})" if url else title
        lines.append(
            "| "
            + " | ".join(
                [
                    linked,
                    md_cell(row[employer_i]),
                    md_cell(row[city_i]),
                    md_cell(row[label_i]),
                    md_cell(row[source_i]),
                ]
            )
            + " |"
        )
    lines.append("")
    README.write_text("\n".join(lines), encoding="utf-8")


def main():
    if not SOURCE.exists():
        raise SystemExit(f"Missing {SOURCE}. Run scrape_jobs.py first.")

    pattern = exclude_pattern()
    kept = []
    dropped = 0

    with SOURCE.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        title_index = header.index("Position title")
        for row in reader:
            if len(row) <= title_index:
                continue
            if is_entry_level(row[title_index], pattern):
                kept.append(row)
            else:
                dropped += 1

    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        writer.writerows(kept)

    write_readme(header, kept)

    print(f"{dropped} titles dropped (level / student / tech / legal counsel)")
    print(f"{len(kept)} rows written to {OUTPUT}")
    print(f"README table updated ({len(kept)} jobs)")


if __name__ == "__main__":
    main()
