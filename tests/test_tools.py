"""Unit tests for all 10 PDF document utilities tools."""

import io
import os
import sys
import tempfile
from pathlib import Path
import pypdf

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pdf_document_utilities.tools.pdf_merge_splitter import execute_pdf_merge_splitter
from pdf_document_utilities.tools.pdf_metadata_scrubber import execute_pdf_metadata_scrubber
from pdf_document_utilities.tools.pdf_text_extractor import execute_pdf_text_extractor
from pdf_document_utilities.tools.pdf_watermark_stamper import execute_pdf_watermark_stamper
from pdf_document_utilities.tools.pdf_page_reorder_rotator import execute_pdf_page_reorder_rotator
from pdf_document_utilities.tools.pdf_table_extractor import execute_pdf_table_extractor
from pdf_document_utilities.tools.pdf_encryption_manager import execute_pdf_encryption_manager
from pdf_document_utilities.tools.pdf_bookmark_toc_builder import execute_pdf_bookmark_toc_builder
from pdf_document_utilities.tools.pdf_image_rasterizer import execute_pdf_image_rasterizer
from pdf_document_utilities.tools.pdf_form_field_inspector import execute_pdf_form_field_inspector


def _create_dummy_pdf(path: str, pages: int = 2, metadata: dict = None) -> None:
    """Helper to create minimal valid multi-page PDF."""
    writer = pypdf.PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=300, height=400)
    if metadata:
        writer.add_metadata(metadata)
    with open(path, "wb") as f:
        writer.write(f)


def test_tool_01_merge_splitter(tmp_path):
    pdf_a = tmp_path / "a.pdf"
    pdf_b = tmp_path / "b.pdf"
    _create_dummy_pdf(str(pdf_a), pages=2)
    _create_dummy_pdf(str(pdf_b), pages=3)

    out_merged = tmp_path / "merged.pdf"
    res_merge = execute_pdf_merge_splitter(
        mode="merge",
        input_files=[str(pdf_a), str(pdf_b)],
        output_path=str(out_merged),
    )
    assert res_merge["status"] == "success"
    assert res_merge["pages_written"] == 5

    out_split = tmp_path / "split.pdf"
    res_split = execute_pdf_merge_splitter(
        mode="split",
        input_files=[str(out_merged)],
        output_path=str(out_split),
        page_ranges="1-2,4",
    )
    assert res_split["status"] == "success"
    assert res_split["pages_written"] == 3


def test_tool_02_metadata_scrubber(tmp_path):
    pdf = tmp_path / "meta.pdf"
    _create_dummy_pdf(str(pdf), pages=1, metadata={"/Author": "Secret Author", "/Title": "Internal Draft"})

    # Inspect
    res_inspect = execute_pdf_metadata_scrubber(input_path=str(pdf), inspect_only=True)
    assert res_inspect["status"] == "success"
    assert "Author" in res_inspect["metadata_fields"]

    # Scrub
    out_clean = tmp_path / "clean.pdf"
    res_scrub = execute_pdf_metadata_scrubber(input_path=str(pdf), output_path=str(out_clean))
    assert res_scrub["status"] == "success"
    assert res_scrub["purged_count"] >= 1


def test_tool_03_text_extractor(tmp_path):
    pdf = tmp_path / "text.pdf"
    _create_dummy_pdf(str(pdf), pages=2)

    res = execute_pdf_text_extractor(input_path=str(pdf))
    assert res["status"] == "success"
    assert res["pages_extracted"] == 2


def test_tool_04_watermark_stamper(tmp_path):
    pdf = tmp_path / "doc.pdf"
    _create_dummy_pdf(str(pdf), pages=2)
    out_wm = tmp_path / "stamped.pdf"

    res = execute_pdf_watermark_stamper(
        input_path=str(pdf),
        output_path=str(out_wm),
        watermark_text="CONFIDENTIAL",
    )
    assert res["status"] == "success"
    assert res["pages_watermarked"] == 2
    assert os.path.isfile(str(out_wm))


def test_tool_05_page_reorder_rotator(tmp_path):
    pdf = tmp_path / "doc3.pdf"
    _create_dummy_pdf(str(pdf), pages=3)
    out_reordered = tmp_path / "reordered.pdf"

    res = execute_pdf_page_reorder_rotator(
        input_path=str(pdf),
        output_path=str(out_reordered),
        page_order=[3, 1],
        global_rotation=90,
    )
    assert res["status"] == "success"
    assert res["output_page_count"] == 2


def test_tool_06_table_extractor(tmp_path):
    pdf = tmp_path / "table.pdf"
    _create_dummy_pdf(str(pdf), pages=1)

    res = execute_pdf_table_extractor(input_path=str(pdf))
    assert res["status"] == "success"
    assert "tables_detected" in res


def test_tool_07_encryption_manager(tmp_path):
    pdf = tmp_path / "plain.pdf"
    _create_dummy_pdf(str(pdf), pages=2)
    out_enc = tmp_path / "enc.pdf"
    out_dec = tmp_path / "dec.pdf"

    # Encrypt
    res_enc = execute_pdf_encryption_manager(
        mode="encrypt",
        input_path=str(pdf),
        output_path=str(out_enc),
        password="PassWord123!",
    )
    assert res_enc["status"] == "success"

    # Decrypt
    res_dec = execute_pdf_encryption_manager(
        mode="decrypt",
        input_path=str(out_enc),
        output_path=str(out_dec),
        password="PassWord123!",
    )
    assert res_dec["status"] == "success"
    assert res_dec["pages_processed"] == 2


def test_tool_08_toc_builder(tmp_path):
    pdf = tmp_path / "book.pdf"
    _create_dummy_pdf(str(pdf), pages=4)
    out_toc = tmp_path / "book_toc.pdf"

    bookmarks = [
        {"title": "Chapter 1", "page": 1},
        {"title": "Chapter 2", "page": 3, "children": [{"title": "Section 2.1", "page": 4}]},
    ]

    res = execute_pdf_bookmark_toc_builder(
        input_path=str(pdf),
        output_path=str(out_toc),
        bookmarks=bookmarks,
    )
    assert res["status"] == "success"
    assert res["bookmarks_injected"] == 3


def test_tool_09_image_rasterizer(tmp_path):
    pdf = tmp_path / "img_test.pdf"
    _create_dummy_pdf(str(pdf), pages=1)
    out_dir = tmp_path / "extracted_images"

    res = execute_pdf_image_rasterizer(
        input_path=str(pdf),
        output_dir=str(out_dir),
    )
    assert res["status"] == "success"
    assert res["pages_scanned"] == 1


def test_tool_10_form_field_inspector(tmp_path):
    pdf = tmp_path / "form.pdf"
    _create_dummy_pdf(str(pdf), pages=1)

    res = execute_pdf_form_field_inspector(input_path=str(pdf))
    assert res["status"] == "success"
    assert res["total_fields"] == 0
