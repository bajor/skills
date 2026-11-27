#!/usr/bin/env python3
"""Locate and rasterize Apple Pencil marks in a PDF.

Subcommands:
  info <pdf>                      page count and annotation objects, as JSON
  render <pdf> <outdir> [--dpi N] [--pages 2,5-7]   write page-NN.png files
  diff <clean-pdf> <annotated-pdf>                  pages whose pixels changed

Runs inside the ipad-review venv: python3 -m venv ~/.cache/ipad-review/venv
and pip install pymupdf there first.
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import pymupdf
except ImportError:  # releases before 1.24 export the module as fitz
    try:
        import fitz as pymupdf
    except ImportError:
        sys.exit("pymupdf is not installed in this interpreter; "
                 "run: ~/.cache/ipad-review/venv/bin/pip install pymupdf")

DIFF_DPI = 72  # coarse but deterministic; same engine renders both sides


def cmd_info(args):
    doc = pymupdf.open(args.pdf)
    annotations = []
    for page in doc:
        for annot in page.annots():
            annotations.append({
                "page": page.number + 1,
                "type": annot.type[1],
                "rect": [round(v, 1) for v in annot.rect],
            })
    print(json.dumps({
        "pages": doc.page_count,
        "annotated_pages": sorted({a["page"] for a in annotations}),
        "annotations": annotations,
    }, indent=1))


def parse_pages(spec, page_count):
    if not spec:
        return range(1, page_count + 1)
    pages = set()
    for part in spec.split(","):
        lo, dash, hi = part.partition("-")
        start = int(lo) if lo else 1
        end = int(hi) if hi else (page_count if dash else start)
        pages.update(range(start, end + 1))
    selected = sorted(p for p in pages if 1 <= p <= page_count)
    if not selected:
        sys.exit(f"--pages {spec!r} selects nothing in 1..{page_count}")
    return selected


def cmd_render(args):
    doc = pymupdf.open(args.pdf)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for number in parse_pages(args.pages, doc.page_count):
        pix = doc[number - 1].get_pixmap(dpi=args.dpi)
        path = outdir / f"page-{number:02d}.png"
        pix.save(path)
        print(path)


def cmd_diff(args):
    clean, annotated = pymupdf.open(args.clean), pymupdf.open(args.annotated)
    shared = min(clean.page_count, annotated.page_count)
    changed = []
    for number in range(1, shared + 1):
        pixes = [d[number - 1].get_pixmap(dpi=DIFF_DPI)
                 for d in (clean, annotated)]
        if pixes[0].samples != pixes[1].samples:
            changed.append(number)
    # pages present on only one side (added or deleted) count as changed
    changed += list(range(shared + 1,
                          max(clean.page_count, annotated.page_count) + 1))
    print(json.dumps({"changed_pages": changed,
                      "clean_pages": clean.page_count,
                      "annotated_pages": annotated.page_count}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("info")
    p.add_argument("pdf")
    p.set_defaults(func=cmd_info)
    p = sub.add_parser("render")
    p.add_argument("pdf")
    p.add_argument("outdir")
    p.add_argument("--dpi", type=int, default=150)
    p.add_argument("--pages", default="")
    p.set_defaults(func=cmd_render)
    p = sub.add_parser("diff")
    p.add_argument("clean")
    p.add_argument("annotated")
    p.set_defaults(func=cmd_diff)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
