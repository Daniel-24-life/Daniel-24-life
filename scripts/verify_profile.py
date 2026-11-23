"""Verify that the bilingual profile links and displays the same four projects."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import struct
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
FEATURED = [p["repo"] for p in json.loads((ROOT/"featured.json").read_text(encoding="utf-8"))]

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []
        self.images = []
        self.grid = []
        self.active = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "source":
            self.sources.append(a["srcset"])
        if tag == "img":
            self.images.append((a["src"],a["width"]))
        if tag == "table":
            self.active = True
        if self.active and tag == "tr":
            self.grid.append(0)
        if self.active and tag == "td":
            self.grid[-1] += 1

    def handle_endtag(self,tag):
        if tag == "table":
            self.active = False

for file in ("README.md","README.zh.md"):
    text = (ROOT/file).read_text(encoding="utf-8")
    page = Page()
    page.feed(text)
    assert page.grid == [2,2], (file,page.grid)
    assert page.sources == ["assets/header-dark.svg","assets/header-light.svg"], file
    assert page.images == [("assets/header-light.svg","1200"),
                          *((f"assets/work/{s}.png","380") for s in FEATURED)], file
    assert "https://github.com/Daniel-24-life/portfolio" in text
    language_path = "zh/" if file == "README.zh.md" else ""
    gallery = f"https://daniel-24-life.github.io/portfolio/{language_path}"
    gallery_position = text.index(gallery)
    assert gallery_position < text.index("<table>"), file
    assert not re.search(r"mailto:|\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b", text, re.I), file
    assert not re.search(r"/AIfile|Public Work Snapshot|## Focus|\[N\]|you@example\.com",text,re.I)
    for slug in FEATURED:
        assert f"https://github.com/Daniel-24-life/{slug}" in text
for item in ("assets/header-dark.svg","assets/header-light.svg"):
    svg=ElementTree.parse(ROOT/item).getroot()
    assert (svg.attrib["width"],svg.attrib["height"]) == ("1200","240")
for slug in FEATURED:
    data=(ROOT/f"assets/work/{slug}.png").read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n") and struct.unpack(">II",data[16:24])==(600,338)
print("Bilingual profile links, 2×2 gallery, two header assets and four thumbnail dimensions verified.")
