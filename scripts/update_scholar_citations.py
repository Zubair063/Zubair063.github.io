#!/usr/bin/env python3
"""Refresh the citation cache used by the static portfolio."""

from __future__ import annotations

import json
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
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "scholar-citations.json"


def parse_count(value: str) -> int:
    text = value.strip().replace(",", "")
    return int(text) if text.isdigit() else 0


def main() -> None:
    response = requests.get(
        PROFILE_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; portfolio citation updater)"},
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    stats = soup.select("#gsc_rsb_st td.gsc_rsb_std")
    rows = soup.select(".gsc_a_tr")
    if not stats or not rows:
        raise RuntimeError("Google Scholar returned no profile data")

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

    payload = {
        "profile_id": PROFILE_ID,
        "profile_url": PROFILE_URL,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_citations": parse_count(stats[0].get_text(" ", strip=True)),
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
