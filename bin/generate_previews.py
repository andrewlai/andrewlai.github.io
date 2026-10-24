#!/usr/bin/env python3
"""Generate publication preview images for entries in _bibliography/papers.bib.

For every entry that has a DOI but no `preview` field:
  1. Look the DOI up in Europe PMC. If the paper is open access, take its
     graphical abstract (or, failing that, Figure 1) from the full text.
  2. Otherwise draw a simple title card (journal, year, title).
The image is saved to assets/img/publication_preview/<key>.jpg and a
`preview = {<key>.jpg}` line is added to the entry.

Usage:
  python bin/generate_previews.py            # process all missing previews
  python bin/generate_previews.py --dry-run  # write images, leave papers.bib alone
  python bin/generate_previews.py --only KEY [KEY ...]
  python bin/generate_previews.py --cards-only
"""

import argparse
import io
import json
import re
import sys
import tarfile
import textwrap
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "_bibliography" / "papers.bib"
OUT = ROOT / "assets" / "img" / "publication_preview"
UA = "andrewlai.github.io preview generator (+https://andrewlai.github.io)"
MAX_W = 800
XLINK = "{http://www.w3.org/1999/xlink}href"

ACCENT = (38, 152, 186)  # site cyan, #2698ba
BG = (247, 248, 250)
INK = (33, 37, 41)
MUTED = (108, 117, 125)


# --------------------------------------------------------------------------- bib


def split_entries(text):
    """Return list of (key, start, end) spans for each @entry{...} block."""
    spans = []
    for m in re.finditer(r"@\w+\s*\{\s*([^,\s]+)\s*,", text):
        depth, i = 0, text.index("{", m.start())
        for j in range(i, len(text)):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    spans.append((m.group(1), m.start(), j + 1))
                    break
    return spans


def field(block, name):
    m = re.search(r"\n\s*" + name + r"\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}", block, re.I)
    return m.group(1).strip() if m else None


def clean(s):
    s = re.sub(r"\\[a-zA-Z]+\s*\{([^{}]*)\}", r"\1", s or "")
    s = re.sub(r"\\['\"`^~=.vcuHk]\{?(\w)\}?", r"\1", s)
    s = s.replace("\\&", "&").replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()


def add_preview_field(text, key, filename):
    for k, start, end in split_entries(text):
        if k != key:
            continue
        block = text[start:end]
        body = block[:-1].rstrip()
        if not body.endswith(","):
            body += ","
        block = body + "\n  preview = {" + filename + "}\n}"
        return text[:start] + block + text[end:]
    raise KeyError(key)


# ---------------------------------------------------------------------- network


def get(url, binary=False, tries=3):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                return data if binary else data.decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            if attempt == tries - 1:
                raise
            time.sleep(2 * (attempt + 1))


def europepmc_record(doi):
    q = urllib.parse.quote(f'DOI:"{doi}"')
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&format=json&resultType=core"
    res = json.loads(get(url)).get("resultList", {}).get("result", [])
    return res[0] if res else None


def pick_graphic(xml_text):
    """Return graphic href: graphical abstract first, else first figure."""
    root = ET.fromstring(xml_text.encode("utf-8"))
    for ab in root.iter("abstract"):
        if (ab.get("abstract-type") or "").lower() in ("graphical", "graphical-abstract", "toc"):
            for g in ab.iter("graphic"):
                if g.get(XLINK):
                    return g.get(XLINK), "graphical abstract"
    for fig in root.iter("fig"):
        tag = " ".join(filter(None, [fig.get("fig-type"), fig.get("id"), fig.get("specific-use")])).lower()
        if "graphical" in tag or re.search(r"\b(ga|toc)\d*\b", tag):
            for g in fig.iter("graphic"):
                if g.get(XLINK):
                    return g.get(XLINK), "graphical abstract"
    body = root.find(".//body")
    for fig in (body if body is not None else root).iter("fig"):
        for g in fig.iter("graphic"):
            if g.get(XLINK):
                return g.get(XLINK), "figure 1"
    return None, None


def _image_ok(data):
    try:
        Image.open(io.BytesIO(data)).verify()
        return True
    except Exception:  # noqa: BLE001
        return False


def fetch_figure(pmcid, href, log):
    """Try several sources for a figure file. Returns bytes or None; appends notes to log."""
    stem = Path(re.sub(r"\.(jpe?g|png|gif|tiff?)$", "", href, flags=re.I)).name
    # 1. Europe PMC figure files
    for ext in (".jpg", ".png", ".gif"):
        url = f"https://europepmc.org/articles/{pmcid}/bin/{stem}{ext}"
        try:
            data = get(url, binary=True, tries=1)
            if _image_ok(data):
                return data
            log.append(f"epmc{ext}: not an image")
        except Exception as e:  # noqa: BLE001
            log.append(f"epmc{ext}: {str(e)[:60]}")
    # 2. PMC article page: find the figure's image URL on the CDN
    try:
        html = get(f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/", tries=2)
        urls = re.findall(r'(?:src|href|data-src)="(https://cdn\.ncbi\.nlm\.nih\.gov/pmc/blobs/[^"]+)"', html)
        hits = [u for u in urls if stem.lower() in u.lower()] or [u for u in urls if re.search(r"\.(jpe?g|png|gif)$", u, re.I)]
        for url in hits[:3]:
            data = get(url, binary=True, tries=2)
            if _image_ok(data):
                return data
        log.append(f"pmc page: {len(urls)} cdn images, {len(hits)} matched")
    except Exception as e:  # noqa: BLE001
        log.append(f"pmc page: {str(e)[:60]}")
    # 3. PMC open-access package
    try:
        oa = get(f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmcid}")
        m = re.search(r'format="tgz"[^>]*href="([^"]+)"', oa)
        if not m:
            log.append("oa package: none listed")
        else:
            url = m.group(1).replace("ftp://", "https://")
            with tarfile.open(fileobj=io.BytesIO(get(url, binary=True)), mode="r:gz") as tar:
                for member in tar.getmembers():
                    name = Path(member.name).name
                    if name.startswith(stem) and re.search(r"\.(jpe?g|png|gif)$", name, re.I):
                        return tar.extractfile(member).read()
            log.append("oa package: figure not found")
    except Exception as e:  # noqa: BLE001
        log.append(f"oa package: {str(e)[:60]}")
    return None


# ----------------------------------------------------------------------- images


def font(size, bold=False):
    names = ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf"] if bold else ["DejaVuSans.ttf"]
    for name in names + [
        "/usr/share/fonts/truetype/dejavu/" + names[0],
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def save_jpg(img, path):
    img = img.convert("RGB")
    if img.width > MAX_W:
        img = img.resize((MAX_W, round(img.height * MAX_W / img.width)), Image.LANCZOS)
    img.save(path, "JPEG", quality=85, optimize=True)


def title_card(title, journal, year, path):
    W, H = 800, 450
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 14, H], fill=ACCENT)
    pad = 56
    f_j, f_t, f_y = font(28, bold=True), font(38, bold=True), font(26)
    d.text((pad, 44), journal, font=f_j, fill=ACCENT)
    # wrap title to fit width, shrink font if needed
    for size in (38, 34, 30, 27, 24):
        f_t = font(size, bold=True)
        width_chars = max(18, int((W - 2 * pad) / (size * 0.56)))
        lines = textwrap.wrap(title, width=width_chars)
        if len(lines) * size * 1.3 <= H - 190:
            break
    else:
        lines = lines[: int((H - 190) / (size * 1.3))]
        lines[-1] = lines[-1].rstrip(".,;: ") + "…"
    y = 110
    for line in lines:
        d.text((pad, y), line, font=f_t, fill=INK)
        y += int(size * 1.3)
    d.text((pad, H - 60), year, font=f_y, fill=MUTED)
    save_jpg(img, path)


# ------------------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--cards-only", action="store_true")
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()

    text = BIB.read_text(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    report = []

    keys = [k for k, _, _ in split_entries(text)]
    for key in keys:
        # re-locate the entry each time: earlier edits shift positions
        start, end = next((s, e) for k, s, e in split_entries(text) if k == key)
        block = text[start:end]
        doi = field(block, "doi")
        if args.only and key not in args.only:
            continue
        if field(block, "preview") or not doi:
            continue
        title = clean(field(block, "title") or key)
        journal = clean(field(block, "journal") or field(block, "booktitle") or field(block, "abbr") or "")
        year = clean(field(block, "year") or "")
        path = OUT / f"{key}.jpg"
        source = None
        reason = ""

        if not args.cards_only:
            log = []
            try:
                rec = europepmc_record(doi)
                pmcid = rec.get("pmcid") if rec else None
                if not rec:
                    reason = "not in Europe PMC"
                elif not pmcid:
                    reason = "no full text in PMC"
                elif rec.get("isOpenAccess") != "Y":
                    reason = f"{pmcid} not open access"
                else:
                    xml = get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML")
                    href, kind = pick_graphic(xml)
                    if not href:
                        reason = f"{pmcid}: no figure in full text"
                    else:
                        data = fetch_figure(pmcid, href, log)
                        if data:
                            save_jpg(Image.open(io.BytesIO(data)), path)
                            source = f"{kind} ({pmcid}, {rec.get('license') or 'open access'})"
                        else:
                            reason = f"{pmcid} {href}: download failed [" + "; ".join(log) + "]"
            except Exception as e:  # noqa: BLE001
                reason = f"lookup failed: {str(e)[:80]}"
            time.sleep(0.4)
        else:
            reason = "cards only"

        if not source:
            title_card(title, journal, year, path)
            source = f"title card ({reason})"

        report.append((key, year, source, title[:80]))
        print(f"{key}: {source}")
        if not args.dry_run:
            text = add_preview_field(text, key, path.name)

    if not args.dry_run:
        BIB.write_text(text, encoding="utf-8")

    summary = ROOT / "preview_report.md"
    with summary.open("w", encoding="utf-8") as f:
        f.write("| Entry | Year | Source | Title |\n|---|---|---|---|\n")
        for key, year, source, title in report:
            f.write(f"| `{key}` | {year} | {source} | {title} |\n")
    print(f"\n{len(report)} preview(s) generated.")


if __name__ == "__main__":
    main()
