import sys
from pathlib import Path
_s = str(Path(__file__).resolve().parent.parent)
if _s not in sys.path:
    sys.path.insert(0, _s)

"""Unified Command Line Interface dispatcher for PDF Document Utilities."""

import argparse
import sys
from typing import List, Optional

from pdf_document_utilities.tools.pdf_merge_splitter import build_parser as parse_merge, main as main_merge
from pdf_document_utilities.tools.pdf_metadata_scrubber import build_parser as parse_scrub, main as main_scrub
from pdf_document_utilities.tools.pdf_text_extractor import build_parser as parse_text, main as main_text
from pdf_document_utilities.tools.pdf_watermark_stamper import build_parser as parse_stamp, main as main_stamp
from pdf_document_utilities.tools.pdf_page_reorder_rotator import build_parser as parse_reorder, main as main_reorder
from pdf_document_utilities.tools.pdf_table_extractor import build_parser as parse_table, main as main_table
from pdf_document_utilities.tools.pdf_encryption_manager import build_parser as parse_crypt, main as main_crypt
from pdf_document_utilities.tools.pdf_bookmark_toc_builder import build_parser as parse_toc, main as main_toc
from pdf_document_utilities.tools.pdf_image_rasterizer import build_parser as parse_img, main as main_img
from pdf_document_utilities.tools.pdf_form_field_inspector import build_parser as parse_form, main as main_form


def build_parser() -> argparse.ArgumentParser:
    """Build unified multi-command argument parser."""
    parser = argparse.ArgumentParser(
        prog="pdf-tools-cli",
        description="PDF Document Utilities: Unified document processing suite.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available PDF utility subcommands")

    subparsers.add_parser("merge-split", parents=[parse_merge()], add_help=False, help="Merge PDFs or extract page ranges")
    subparsers.add_parser("scrub-metadata", parents=[parse_scrub()], add_help=False, help="Inspect and purge metadata footprints")
    subparsers.add_parser("extract-text", parents=[parse_text()], add_help=False, help="Extract page text and word metrics")
    subparsers.add_parser("watermark", parents=[parse_stamp()], add_help=False, help="Stamp text watermarks across pages")
    subparsers.add_parser("reorder-rotate", parents=[parse_reorder()], add_help=False, help="Reorder and rotate document pages")
    subparsers.add_parser("extract-table", parents=[parse_table()], add_help=False, help="Extract tabular structures to CSV")
    subparsers.add_parser("encryption", parents=[parse_crypt()], add_help=False, help="Encrypt or decrypt with AES passwords")
    subparsers.add_parser("toc-builder", parents=[parse_toc()], add_help=False, help="Inject hierarchical outline bookmarks")
    subparsers.add_parser("extract-images", parents=[parse_img()], add_help=False, help="Extract embedded raster images")
    subparsers.add_parser("inspect-fields", parents=[parse_form()], add_help=False, help="Inspect AcroForm interactive fields")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Unified CLI dispatch routine."""
    if argv is None:
        argv = sys.argv[1:]

    parser = build_parser()
    if not argv or argv[0] in ("-h", "--help"):
        parser.print_help()
        return 0

    command_map = {
        "merge-split": main_merge,
        "scrub-metadata": main_scrub,
        "extract-text": main_text,
        "watermark": main_stamp,
        "reorder-rotate": main_reorder,
        "extract-table": main_table,
        "encryption": main_crypt,
        "toc-builder": main_toc,
        "extract-images": main_img,
        "inspect-fields": main_form,
    }

    subcommand = argv[0]
    if subcommand in command_map:
        return command_map[subcommand](argv[1:])

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
