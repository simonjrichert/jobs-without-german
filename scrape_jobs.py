"""Collect jobs from jobswithoutgerman.de.

Keyword matches come from the public search index, using a whole-phrase match
in the title. Category pages (Finance & Legal, People & HR, Project manager)
are read page by page so roles in those groups are included even when the
title never says accounting, HR, or risk.
"""

import csv
import re
import sys
import time
from html import unescape
from pathlib import Path

import requests

SEARCH_TERMS = [
    "accounting",
    "controlling",
    "audit",
    "project management",
    "HR",
    "Risk",
]

CATEGORIES = [
    ("Finance & Legal", "/work/finance-legal/"),
    ("People & HR", "/work/people-hr/"),
    ("Project manager", "/roles/project-manager/"),
]

SITE = "https://www.jobswithoutgerman.de"
INDEX_URL = f"{SITE}/search-index.json"
OUTPUT = Path(__file__).with_name("jobs.csv")
REQUEST_HEADERS = {"User-Agent": "job-title-spreadsheet/1.0"}
SESSION = requests.Session()
SESSION.headers.update(REQUEST_HEADERS)

HEADERS = [
    "Search term",
    "Position title",
    "Employer",
    "City",
    "Language label",
    "Listing URL",
]

CARD_RE = re.compile(r'<li class="card\b.*?</li>', re.DOTALL)


def get(url, allow_404=False):
    last_error = None
    for attempt in range(3):
        try:
            response = SESSION.get(url, timeout=60)
            if allow_404 and response.status_code == 404:
                return response
            response.raise_for_status()
            response.encoding = "utf-8"
            time.sleep(0.6)
            return response
        except requests.RequestException as error:
            last_error = error
            time.sleep(1.5 * (attempt + 1))
    raise last_error


def fetch_index():
    data = get(INDEX_URL).json()
    return data.get("jobs", []), data.get("labels", {})


def phrase_pattern(term):
    """The term as a whole phrase: 'HR' but not 'hrs', 'audit' but not 'auditor'."""
    return re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)


def clean(text):
    text = unescape(re.sub(r"<[^>]+>", " ", text or ""))
    return " ".join(text.split())


def matching_jobs(jobs, term):
    pattern = phrase_pattern(term)
    found = {}
    for job in jobs:
        title = clean(job.get("t", ""))
        if pattern.search(title):
            found.setdefault(job.get("u", ""), (title, job))
    return [
        (title, job)
        for title, job in sorted(found.values(), key=lambda pair: pair[0].lower())
    ]


def listing_url(row):
    return row[-1].rstrip("/") if row else ""


def load_existing():
    if not OUTPUT.exists():
        return [], set()

    rows = []
    seen = set()
    with OUTPUT.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        if header != HEADERS:
            print(f"warning: {OUTPUT.name} header looks different; keeping its rows as-is")
        for row in reader:
            if len(row) < len(HEADERS):
                continue
            url = listing_url(row)
            if not url or url in seen:
                continue
            seen.add(url)
            rows.append(row)
    return rows, seen


def keyword_rows(jobs, labels, seen):
    rows = []
    for term in SEARCH_TERMS:
        for title, job in matching_jobs(jobs, term):
            url = SITE + job.get("u", "")
            key = url.rstrip("/")
            if not key or key in seen:
                continue
            seen.add(key)
            rows.append(
                [
                    term,
                    title,
                    job.get("e", ""),
                    job.get("c", ""),
                    labels.get(job.get("k", ""), ""),
                    url,
                ]
            )
    return rows


def parse_cards(html):
    jobs = []
    for card in CARD_RE.findall(html):
        title_match = re.search(
            r'class="card-title" href="([^"]+)">([^<]+)', card
        )
        if not title_match:
            continue
        employer_match = re.search(r'class="card-emp"[^>]*>([^<]+)', card)
        city_match = re.search(r'class="loc card-city"[^>]*>([\s\S]*?)</a>', card)
        if not city_match:
            city_match = re.search(r'class="where"[^>]*>([\s\S]*?)</span>', card)
        label_match = re.search(r'class="chip[^"]*">([^<]+)', card)
        jobs.append(
            {
                "title": clean(title_match.group(2)),
                "url": SITE + title_match.group(1),
                "employer": clean(employer_match.group(1) if employer_match else ""),
                "city": clean(city_match.group(1) if city_match else ""),
                "label": clean(label_match.group(1) if label_match else ""),
            }
        )
    return jobs


def fetch_category(path):
    found = []
    seen_urls = set()
    page = 1
    while page <= 50:
        url = f"{SITE}{path}" if page == 1 else f"{SITE}{path}page/{page}/"
        response = get(url, allow_404=True)
        if response.status_code == 404:
            break
        page_jobs = parse_cards(response.text)
        new_jobs = [job for job in page_jobs if job["url"] not in seen_urls]
        if not new_jobs:
            break
        for job in new_jobs:
            seen_urls.add(job["url"])
            found.append(job)
        page += 1
    return found


def add_category_rows(seen):
    rows = []
    for name, path in CATEGORIES:
        for job in fetch_category(path):
            key = job["url"].rstrip("/")
            if not key or key in seen:
                continue
            seen.add(key)
            rows.append(
                [
                    name,
                    job["title"],
                    job["employer"],
                    job["city"],
                    job["label"],
                    job["url"],
                ]
            )
    return rows


def write_csv(rows):
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, quoting=csv.QUOTE_ALL)
        writer.writerow(HEADERS)
        writer.writerows(rows)


def main():
    existing, seen = load_existing()
    jobs, labels = fetch_index()
    fresh = keyword_rows(jobs, labels, seen)
    fresh.extend(add_category_rows(seen))
    write_csv(existing + fresh)

    print(f"{len(jobs):,} jobs in the index")
    print(f"{len(existing)} already in {OUTPUT.name}")
    print(f"{len(fresh)} new rows appended")
    for term in SEARCH_TERMS:
        print(f"  {term}: {sum(1 for row in fresh if row[0] == term)}")
    print("category pages (new jobs only)")
    for name, _path in CATEGORIES:
        print(f"  {name}: {sum(1 for row in fresh if row[0] == name)}")
    print(f"{len(existing) + len(fresh)} rows in {OUTPUT}")


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as error:
        sys.exit(f"Could not read the site: {error}")
