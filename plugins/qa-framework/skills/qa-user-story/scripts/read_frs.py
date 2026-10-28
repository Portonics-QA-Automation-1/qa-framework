"""Print an FRS .docx in document order (headings, paragraphs, tables) and save its embedded images.

Usage:
    .venv/bin/python -I scripts/read_frs.py <frs.docx> [image-out-dir]
"""
import os
import sys

import docx
from docx.oxml.ns import qn

BLIP = "{http://schemas.openxmlformats.org/drawingml/2006/main}blip"


def main(path, img_dir=None):
    d = docx.Document(path)
    for el in d.element.body.iterchildren():
        if el.tag == qn("w:p"):
            text = "".join(x.text or "" for x in el.iter(qn("w:t"))).strip()
            style = el.find(qn("w:pPr"))
            sid = style.find(qn("w:pStyle")).get(qn("w:val")) if style is not None and style.find(qn("w:pStyle")) is not None else ""
            has_img = bool(list(el.iter(BLIP)))
            if text:
                print(f"[{sid}] {text}" if sid.lower().startswith("heading") else text)
            if has_img:
                print("[IMAGE]")
        elif el.tag == qn("w:tbl"):
            print("--TABLE--")
            for tr in el.iter(qn("w:tr")):
                print(" | ".join("".join(x.text or "" for x in tc.iter(qn("w:t"))) for tc in tr.iter(qn("w:tc"))))
            print("--END TABLE--")
    if img_dir:
        os.makedirs(img_dir, exist_ok=True)
        n = 0
        for rel in d.part.rels.values():
            if "image" in rel.reltype:
                n += 1
                name = f"frs-image-{n}{os.path.splitext(rel.target_ref)[1]}"
                with open(os.path.join(img_dir, name), "wb") as f:
                    f.write(rel.target_part.blob)
        print(f"\n{n} embedded image(s) saved to {img_dir}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
