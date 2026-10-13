#!/usr/bin/env python3
"""Signal – RSS-Aggregator (nur Python-Standardbibliothek, keine API-Schlüssel)."""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "news-data.json"
EDITION = {"hl": "de", "gl": "DE", "ceid": "DE:de"}
GOOGLE = "https://news.google.com/rss"
MAX_PER_FEED = 55
MAX_TOTAL = 260
RECENCY = timedelta(days=14)


# Medienmarken von Axel Springer (inkl. 2026 hinzugekommener Telegraph-Gruppe)
# bewusst keine generische "Springer"-Sperre: Springer Nature ist ein anderes Unternehmen.
BLOCKED_PUBLISHERS = {
    "bild", "bild de", "bild zeitung", "bild am sonntag", "bam s",
    "auto bild", "autobild", "computer bild", "computerbild",
    "sport bild", "sportbild", "bz", "bz berlin", "b z", "b z berlin",
    "welt", "welt de", "die welt", "welt am sonntag", "welt tv",
    "business insider", "business insider deutschland", "insider",
    "politico", "politico europe", "politico eu", "politico deutschland",
    "upday", "morning brew", "morning brew inc",
    "the telegraph", "daily telegraph", "the daily telegraph",
    "sunday telegraph", "the sunday telegraph", "telegraph media group",
    "bisnow", "emarketer", "e marketer",
    "fakt", "fakt24", "onet", "newsweek polska", "forbes polska",
}
BLOCKED_DOMAINS = {
    "bild.de", "welt.de", "bz-berlin.de", "businessinsider.de",
    "businessinsider.com", "insider.com", "politico.eu", "politico.com",
    "upday.com", "morningbrew.com", "telegraph.co.uk",
    "bisnow.com", "emarketer.com", "autobild.de", "computerbild.de",
    "sportbild.de", "fakt.pl", "onet.pl", "newsweek.pl", "forbes.pl",
}

def publisher_key(value):
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()

def host_from_url(value):
    try:
        return (urllib.parse.urlparse(value or "").hostname or "").lower().rstrip(".")
    except ValueError:
        return ""

def is_blocked_story(publisher, article_url, source_url=""):
    if publisher_key(publisher) in BLOCKED_PUBLISHERS:
        return True
    for url in (article_url, source_url):
        hostname = host_from_url(url)
        if any(hostname == domain or hostname.endswith("." + domain) for domain in BLOCKED_DOMAINS):
            return True
    return False


def google_url(path="", search=None):
    params = dict(EDITION)
    if search:
        params["q"] = search
    return GOOGLE + path + "?" + urllib.parse.urlencode(params)

FEEDS = [
    {"name": "Google News · Top", "topic": "Top-News", "url": google_url()},
    {"name": "Google News · Technologie", "topic": "Technologie", "url": google_url("/headlines/section/topic/TECHNOLOGY")},
    {"name": "Google News · Wirtschaft", "topic": "Wirtschaft", "url": google_url("/headlines/section/topic/BUSINESS")},
    {"name": "Google News · Wissenschaft", "topic": "Wissenschaft", "url": google_url("/headlines/section/topic/SCIENCE")},
    {"name": "Google News · KI", "topic": "KI", "url": google_url("/search", '("Künstliche Intelligenz" OR "Artificial Intelligence" OR OpenAI) when:7d')},
    {"name": "Google News · Umwelt", "topic": "Umwelt", "url": google_url("/search", '(Umwelt OR Klimawandel OR Nachhaltigkeit) when:7d')},
    {"name": "t3n · News", "topic": "Technologie", "url": "https://t3n.de/rss.xml"},
    {"name": "t3n · KI", "topic": "KI", "url": "https://t3n.de/tag/kuenstliche-intelligenz/rss.xml"},
]

class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.chunks = []
        self.suppress = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.suppress += 1
        if tag in {"br", "p", "li"}:
            self.chunks.append(" ")

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.suppress:
            self.suppress -= 1

    def handle_data(self, value):
        if not self.suppress:
            self.chunks.append(value)

def clean(value, limit=600):
    p = PlainText()
    p.feed(html.unescape(value or ""))
    return re.sub(r"\s+", " ", "".join(p.chunks)).strip()[:limit]

def child_text(node, name):
    child = node.find(name)
    return (child.text or "").strip() if child is not None else ""

def iso_date(raw):
    if not raw:
        return ""
    try:
        date = parsedate_to_datetime(raw)
    except (ValueError, TypeError, IndexError):
        try:
            date = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return ""
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)
    return date.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def safe_link(url):
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme == "https" and parsed.netloc and not parsed.username and not parsed.password:
            return url
    except ValueError:
        pass
    return None

def load_feed(feed):
    request = urllib.request.Request(
        feed["url"],
        headers={"User-Agent": "SignalRSSReader/1.0 (+https://github.com/DaWdLeo/nextcloud-iframe)", "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9"},
    )
    with urllib.request.urlopen(request, timeout=22) as resp:
        if int(resp.status) != 200:
            raise RuntimeError(f"HTTP {resp.status}")
        xml_data = resp.read(3_000_000)
    root = ET.fromstring(xml_data)
    items = root.findall("./channel/item")
    if not items:
        raise ValueError("RSS-Feed enthält keine Einträge")
    output = []
    for entry in items[:MAX_PER_FEED]:
        raw_url = child_text(entry, "link")
        url = safe_link(raw_url)
        if not url:
            continue
        title = clean(child_text(entry, "title"), 300)
        if not title:
            continue
        source = child_text(entry, "source")
        source_element = entry.find("source")
        source_url = source_element.get("url", "") if source_element is not None else ""
        publisher = clean(source, 100) if source else ("t3n" if "t3n.de" in feed["url"] else "Google News")
        if is_blocked_story(publisher, url, source_url):
            continue
        if source and title.endswith(" - " + publisher):
            title = title[: -(3 + len(publisher))]
        published = iso_date(child_text(entry, "pubDate") or child_text(entry, "{http://purl.org/dc/elements/1.1/}date"))
        # Google-News-Descriptions enthalten oft lange eingebettete Empfehlungslisten,
        # daher dort keine vollständigen HTML-Listen in die Vorschau übernehmen.
        description = "" if "news.google.com" in feed["url"] else clean(child_text(entry, "description"), 400)
        if description == title:
            description = ""
        stable_id = hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]
        output.append({
            "id": stable_id,
            "title": title,
            "url": url,
            "description": description,
            "publisher": publisher,
            "source_url": source_url,
            "topic": feed["topic"],
            "topics": [feed["topic"]],
            "published": published,
        })
    if not output:
        raise ValueError("Feed ohne nutzbare Nachrichten")
    return output

def main():
    merged = {}
    failed = []
    successes = 0
    with ThreadPoolExecutor(max_workers=6) as pool:
        jobs = {pool.submit(load_feed, feed): feed for feed in FEEDS}
        for future in as_completed(jobs):
            feed = jobs[future]
            try:
                items = future.result()
                successes += 1
                print(f"OK: {feed['name']} ({len(items)})")
                for item in items:
                    key = item["url"]
                    if key in merged:
                        current = merged[key]
                        for topic in item["topics"]:
                            if topic not in current["topics"]:
                                current["topics"].append(topic)
                        # Bei gleicher URL bevorzugen wir die redaktionelle Kurzbeschreibung.
                        if not current["description"] and item["description"]:
                            current["description"] = item["description"]
                        if not current["published"] and item["published"]:
                            current["published"] = item["published"]
                    else:
                        merged[key] = item
            except Exception as exc:
                print(f"WARN: {feed['name']}: {exc}", file=sys.stderr)
                failed.append(feed["name"])

    if not successes:
        raise RuntimeError("Keine RSS-Quelle erreichbar – bisherige news-data.json bleibt erhalten.")

    now = datetime.now(timezone.utc)
    min_date = now - RECENCY
    def included(item):
        try:
            return not item["published"] or datetime.fromisoformat(item["published"].replace("Z", "+00:00")) >= min_date
        except ValueError:
            return True

    news = [x for x in merged.values() if included(x)]
    news.sort(key=lambda item: item["published"], reverse=True)
    news = news[:MAX_TOTAL]
    payload = {
        "updated_at": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "articles": news,
        "failed_feeds": sorted(failed),
        "successful_feeds": successes,
        "total_feeds": len(FEEDS),
    }
    temp = OUTPUT.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, OUTPUT)
    print(f"Gespeichert: {len(news)} Artikel aus {successes}/{len(FEEDS)} Quellen")

if __name__ == "__main__":
    main()
