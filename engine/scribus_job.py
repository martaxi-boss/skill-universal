"""Scribus Scripter: one short-lived Ferrari publication job.

This file is executed by Scribus itself through -g -ns -py; it is not a
standalone Python integration and it never changes other projects.
"""
from __future__ import annotations

import os
from pathlib import Path
import scribus


def main():
    source = Path(os.environ["FERRARI_SCRIBUS_INPUT"])
    output = Path(os.environ["FERRARI_SCRIBUS_OUTPUT"])
    if not source.is_file() or source.is_symlink():
        raise ValueError("Ferrari Scribus source must be a regular file")
    if not output.is_dir() or output.is_symlink():
        raise ValueError("Ferrari Scribus output must be a directory")
    text = source.read_text(encoding="utf-8-sig")
    if not text.strip() or "\x00" in text:
        raise ValueError("Ferrari Scribus requires nonempty UTF-8 text")
    # Small independent A4 pages. Do not truncate text silently.
    chunks = []
    while text:
        if len(text) <= 1600:
            chunks.append(text)
            break
        boundary = max(text.rfind("\n", 800, 1600), text.rfind(" ", 800, 1600))
        if boundary < 800:
            boundary = 1600
        chunks.append(text[:boundary])
        text = text[boundary:].lstrip("\n ")

    created = scribus.newDoc(
        scribus.PAPER_A4, (16, 16, 16, 16),
        scribus.PORTRAIT, 1, scribus.UNIT_MILLIMETERS,
        scribus.NOFACINGPAGES, scribus.FIRSTPAGERIGHT
    )
    if not created:
        raise RuntimeError("Scribus could not create its A4 document")
    for index, chunk in enumerate(chunks):
        if index:
            scribus.newPage(-1)
        frame = scribus.createText(18, 20, 174, 252, "FerrariText" + str(index + 1))
        scribus.setText(chunk, frame)
        scribus.setFontSize(11, frame)
    scribus.saveDocAs(str(output / "publication.sla"))
    pdf = scribus.PDFfile()
    pdf.file = str(output / "publication.pdf")
    pdf.save()
    scribus.closeDoc()
    print("FERRARI_SCRIBUS_SCRIPT_EXPORT=PASS")


main()
