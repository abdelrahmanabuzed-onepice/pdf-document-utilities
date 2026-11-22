"""PDF Document Utilities Suite.

High-throughput, offline PDF manipulation tools for merging, splitting, metadata scrubbing,
watermarking, encryption, and structural table extraction.
"""

__version__ = "1.0.0"
__author__ = "Abdelrahman Abouzed"

from pdf_document_utilities.tools import (
    execute_pdf_merge_splitter,
    execute_pdf_metadata_scrubber,
    execute_pdf_text_extractor,
    execute_pdf_watermark_stamper,
    execute_pdf_page_reorder_rotator,
    execute_pdf_table_extractor,
    execute_pdf_encryption_manager,
    execute_pdf_bookmark_toc_builder,
    execute_pdf_image_rasterizer,
    execute_pdf_form_field_inspector,
)

__all__ = [
    "__version__",
    "__author__",
    "execute_pdf_merge_splitter",
    "execute_pdf_metadata_scrubber",
    "execute_pdf_text_extractor",
    "execute_pdf_watermark_stamper",
    "execute_pdf_page_reorder_rotator",
    "execute_pdf_table_extractor",
    "execute_pdf_encryption_manager",
    "execute_pdf_bookmark_toc_builder",
    "execute_pdf_image_rasterizer",
    "execute_pdf_form_field_inspector",
]
