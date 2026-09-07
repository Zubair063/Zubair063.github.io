#!/usr/bin/env python3
"""Refresh the citation cache used by the static portfolio."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


PROFILE_ID = "CbTdO6kAAAAJ"
PROFILE_URL = (
    "https://scholar.google.com/citations"
    f"?user={PROFILE_ID}&hl=en&pagesize=100"
)
JINA_URL = "https://r.jina.ai/" + PROFILE_URL
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "scholar-citations.json"
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
TITLE_RE = re.compile(
    r"\[([^\]]+)\]\(https://scholar\.google\.com/citations\?view_op=view_citation[^\)]*\)"
)
CITE_RE = re.compile(
    r"\[(\d+)\]\((https://scholar\.google\.com/scholar\?oi=bibs[^\)]*)\)"
)


def parse_count(value: str) -> int:
    text = value.strip().replace(",", "")
    return int(text) if text.isdigit() else 0


def looks_like_profile(html: str) -> bool:
    return "gsc_rsb_st" in html and "gsc_a_tr" in html and "gsc_a_at" in html


def parse_html_profile(html: str) -> tuple[int, list[dict[str, object]]]:
    soup = BeautifulSoup(html, "html.parser")
    stats = soup.select("#gsc_rsb_st td.gsc_rsb_std")
    rows = soup.select(".gsc_a_tr")
    if not stats or not rows:
        raise RuntimeError("Google Scholar HTML did not contain profile data")

    publications = []
    for row in rows:
        title_link = row.select_one(".gsc_a_at")
        citation_link = row.select_one(".gsc_a_c a")
        if title_link is None:
            continue
        publications.append(
            {
                "title": title_link.get_text(" ", strip=True),
                "citations": parse_count(
                    citation_link.get_text(" ", strip=True) if citation_link else ""
                ),
                "url": (
                    urljoin("https://scholar.google.com", citation_link.get("href", ""))
                    if citation_link
                    else PROFILE_URL
                ),
            }
        )
    if not publications:
        raise RuntimeError("Google Scholar HTML contained no publications")
    return parse_count(stats[0].get_text(" ", strip=True)), publications


def parse_markdown_profile(markdown: str) -> tuple[int, list[dict[str, object]]]:
    titles = list(TITLE_RE.finditer(markdown))
    if not titles:
        raise RuntimeError("Google Scholar markdown did not contain publications")

    publications = []
    for index, match in enumerate(titles):
        end = titles[index + 1].start() if index + 1 < len(titles) else len(markdown)
        block = markdown[match.start() : end]
        cite = CITE_RE.search(block)
        publications.append(
            {
                "title": match.group(1).strip(),
                "citations": int(cite.group(1)) if cite else 0,
                "url": cite.group(2) if cite else PROFILE_URL,
            }
        )
    return sum(int(item["citations"]) for item in publications), publications


def parse_profile(text: str) -> tuple[int, list[dict[str, object]]]:
    if looks_like_profile(text):
        return parse_html_profile(text)
    return parse_markdown_profile(text)


def fetch_with_curl_cffi() -> str | None:
    try:
        from curl_cffi import requests as cffi_requests
    except ImportError:
        return None

    response = cffi_requests.get(
        PROFILE_URL,
        impersonate="chrome",
        timeout=30,
        headers={"Accept-Language": "en-US,en;q=0.9"},
    )
    response.raise_for_status()
    return response.text


def fetch_profile_text() -> str:
    errors: list[str] = []

    try:
        html = fetch_with_curl_cffi()
        if html and looks_like_profile(html):
            print("Fetched Google Scholar profile with Chrome TLS impersonation.")
            return html
        if html is not None:
            errors.append("curl_cffi: blocked or empty profile page")
    except Exception as exc:  # noqa: BLE001 - keep the fallback chain going
        errors.append(f"curl_cffi: {exc}")

    for attempt in range(1, 4):
        try:
            response = requests.get(PROFILE_URL, headers=BROWSER_HEADERS, timeout=30)
            response.raise_for_status()
            if looks_like_profile(response.text):
                print("Fetched Google Scholar profile directly.")
                return response.text
            errors.append(f"direct attempt {attempt}: blocked or empty profile page")
        except requests.RequestException as exc:
            errors.append(f"direct attempt {attempt}: {exc}")
        if attempt < 3:
            time.sleep(attempt * 2)

    jina_attempts = (
        ({"Accept": "text/html", "X-Return-Format": "html"}, "jina html"),
        ({"Accept": "text/plain"}, "jina markdown"),
    )
    for headers, label in jina_attempts:
        try:
            response = requests.get(JINA_URL, headers=headers, timeout=60)
            response.raise_for_status()
            parse_profile(response.text)
            print(f"Fetched Google Scholar profile via {label} fallback.")
            return response.text
        except Exception as exc:  # noqa: BLE001 - try the next source
            snippet = ""
            if isinstance(exc, requests.RequestException) and exc.response is not None:
                snippet = " " + " ".join(exc.response.text.split())[:160]
            errors.append(f"{label}: {exc}{snippet}")

    raise RuntimeError("Google Scholar returned no profile data. " + "; ".join(errors))


def main() -> None:
    total_citations, publications = parse_profile(fetch_profile_text())
    payload = {
        "profile_id": PROFILE_ID,
        "profile_url": PROFILE_URL,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_citations": total_citations,
        "publications": publications,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Updated {OUTPUT_PATH} with {len(publications)} publications "
        f"and {payload['total_citations']} citations."
    )


if __name__ == "__main__":
    main()
