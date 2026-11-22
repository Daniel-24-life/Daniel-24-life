import argparse
import collections
import html
import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNER = "Daniel-24-life"
REPO = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PALETTES = {
    "light": ("#f6f5ee", "#1c2924", "#4c655c", "#226b5b", "#c4d4c8"),
    "dark": ("#151a19", "#edf2e9", "#a0beb3", "#83c7b4", "#344a43"),
}

def entries():
    listed = json.loads((ROOT / "featured.json").read_text(encoding="utf-8"))
    slugs = [entry["repo"] for entry in listed]
    if len(slugs) != len(set(slugs)) or not 4 <= len(slugs) <= 6 or not all(REPO.fullmatch(slug) for slug in slugs):
        raise ValueError("Choose four to six distinct public repository slugs")
    return listed

def request(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "daniel-public-work-snapshot"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    url = "https://api.github.com/" + path
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20) as response:
        return json.load(response)

def collect(listed):
    languages = collections.Counter()
    dates = []
    for entry in listed:
        slug = entry["repo"]
        prefix = f"repos/{OWNER}/{slug}"
        repo = request(prefix)
        if repo.get("private") or repo["full_name"].casefold() != f"{OWNER}/{slug}".casefold():
            raise ValueError("Snapshot contains a repository outside the public allowlist")
        dates.append((repo["pushed_at"][:10], entry["title"]))
        for language, size in request(prefix + "/languages").items():
            if not isinstance(size, int) or size < 0:
                raise ValueError("Unexpected GitHub language count")
            languages[language] += size
    return languages, sorted(dates, reverse=True)

def svg(listed, languages, updates, theme):
    canvas, ink, muted, accent, rail = PALETTES[theme]
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 550" role="img" aria-labelledby="title description">',
        '<title id="title">Public work snapshot</title>',
        '<desc id="description">Project counts by focus area, selected public repository language bytes and recently updated projects.</desc>',
        f'<rect width="760" height="550" fill="{canvas}"/>',
        f'<path d="M28 75H732M28 417H732" stroke="{rail}"/>',
    ]

    def text(x, y, label, *, size=25, fill=ink, weight=450):
        out.append(f'<text x="{x}" y="{y}" fill="{fill}" font-family="system-ui, sans-serif" font-size="{size}" font-weight="{weight}">{html.escape(label)}</text>')

    text(30, 52, "Public Work Snapshot", size=34, weight=650)
    text(30, 114, "Focus areas", size=26, weight=650)
    areas = collections.Counter(entry["area"] for entry in listed)
    for index, (area, count) in enumerate(areas.items()):
        y = 151 + index * 34
        text(30, y, area, size=23)
        text(680, y, str(count), size=23, fill=accent, weight=650)
    text(30, 264, "Language share", size=26, weight=650)
    total = sum(languages.values())
    top = languages.most_common(3)
    other = total - sum(value for _, value in top)
    if other:
        top.append(("Other", other))
    if not total:
        text(30, 312, "GitHub reported no language bytes.", size=21, fill=muted)
    for index, (name, value) in enumerate(top):
        y = 299 + index * 30
        ratio = value / total
        text(30, y, name, size=21)
        out.append(f'<rect x="215" y="{y - 15}" width="375" height="12" rx="3" fill="{rail}"/>')
        out.append(f'<rect x="215" y="{y - 15}" width="{ratio * 375:.2f}" height="12" rx="3" fill="{accent}"/>')
        text(650, y, f"{ratio:.0%}", size=21, fill=muted)
    text(30, 455, "Recently updated", size=26, weight=650)
    for index, (date, title) in enumerate(updates[:2]):
        y = 493 + index * 33
        text(30, y, title, size=22)
        text(545, y, date, size=20, fill=muted)
    out.append("</svg>")
    return "\n".join(out) + "\n"

def verify(listed):
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    wanted = [entry["repo"] for entry in listed]
    section = readme.split("## Featured Work\n", 1)[1].split("## Public Work Snapshot", 1)[0]
    actual = re.findall(r"^### \[[^\]]+\]\(https://github\.com/Daniel-24-life/([a-z0-9-]+)\)$", section, flags=re.M)
    if actual != wanted:
        raise ValueError("README and featured.json have different gallery entries or order")
    if re.findall(r'src="assets/work/([a-z0-9-]+)\.(?:png|svg)"', section) != wanted:
        raise ValueError("Gallery artwork does not match the featured list")
    for target in re.findall(r'(?:src|srcset)="([^"]+)"|\]\(([^)]+)\)', readme):
        ref = next(value for value in target if value)
        if ref.startswith("https://"):
            continue
        asset = (ROOT / ref).resolve()
        if not asset.is_relative_to(ROOT) or not asset.is_file():
            raise ValueError(f"Missing local reference: {ref}")
        if asset.suffix == ".svg":
            ET.parse(asset)
    print(f"Profile assets and {len(wanted)} featured repository links: PASS")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    listed = entries()
    if not args.check:
        languages, updates = collect(listed)
        cards = {theme: svg(listed, languages, updates, theme) for theme in PALETTES}
        for image in cards.values():
            ET.fromstring(image)
        for theme, image in cards.items():
            (ROOT / "assets" / f"metrics-{theme}.svg").write_text(image, encoding="utf-8", newline="\n")
    verify(listed)

if __name__ == "__main__":
    main()
