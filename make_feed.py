"""Holt neue QEC-Paper von arXiv und schreibt sie als RSS-Feed nach feed.xml."""

import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import format_datetime
from datetime import datetime

# Suchbegriffe hier anpassen
QUERY = (
    'cat:quant-ph AND ('
    'abs:"error correction" OR ti:"fault-tolerant" OR abs:"surface code" '
    'OR abs:LDPC OR abs:decoder OR abs:"magic state" OR abs:"stabilizer code")'
)
MAX_RESULTS = 100
FEED_TITLE = "arXiv: Quantum Error Correction"
FEED_LINK = "https://arxiv.org/list/quant-ph/new"

ATOM = "{http://www.w3.org/2005/Atom}"


def fetch():
    params = urllib.parse.urlencode({
        "search_query": QUERY,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": MAX_RESULTS,
    })
    url = "https://export.arxiv.org/api/query?" + params
    req = urllib.request.Request(url, headers={"User-Agent": "qec-feed/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return ET.fromstring(resp.read())


def build_rss(atom_root):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = FEED_TITLE
    ET.SubElement(channel, "link").text = FEED_LINK
    ET.SubElement(channel, "description").text = "Gefilterte neue arXiv-Paper zu QEC"

    for entry in atom_root.findall(ATOM + "entry"):
        title = " ".join(entry.findtext(ATOM + "title", "").split())
        link = entry.findtext(ATOM + "id", "").strip()
        summary = " ".join(entry.findtext(ATOM + "summary", "").split())
        authors = [a.findtext(ATOM + "name", "") for a in entry.findall(ATOM + "author")]
        if len(authors) > 6:
            authors = authors[:6] + [f"und {len(authors) - 6} weitere"]
        published = entry.findtext(ATOM + "published", "")

        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "link").text = link
        ET.SubElement(item, "guid").text = link
        ET.SubElement(item, "description").text = (
            f"<p><b>{', '.join(authors)}</b></p><p>{summary}</p>"
        )
        if published:
            dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
            ET.SubElement(item, "pubDate").text = format_datetime(dt)

    return ET.ElementTree(rss)


if __name__ == "__main__":
    tree = build_rss(fetch())
    ET.indent(tree)
    tree.write("feed.xml", encoding="utf-8", xml_declaration=True)
    print("feed.xml geschrieben")
