# PDF Document Utilities

An offline, stream-oriented Python suite for document restructuring, metadata scrubbing, text/table extraction, and cryptographic security operations.

## Architecture

```text
[ Input PDF Files ]
  │   ├── Encrypted / Password Protected Documents
  │   ├── Scanned & Multi-Page Reports
  │   └── Interactive AcroForm Fillable Files
  ▼
[ Document Operations Engine ]
  │   ├── Merge & Page Range Splitter
  │   ├── Metadata Sanitization & Footprint Purging
  │   ├── Text Layout & Word Metric Extractor
  │   ├── Dynamic Watermark Injection (Overlay/Underlay)
  │   ├── Arbitrary Page Reordering & Orthogonal Rotation
  │   ├── Tabular Matrix Detection & CSV Exporter
  │   ├── Cryptographic Encryption / Decryption (AES-256)
  │   ├── Hierarchical Bookmark & Table of Contents Builder
  │   ├── Embedded Image Extractor
  │   └── AcroForm & Signature Field Inspector
  ▼
[ Output Artifacts ]
  ├── Sanitized Production PDFs
  ├── Structured CSV Tables & JSON Text Dumps
  └── Extracted Embedded Raster Assets
```

## Tool Inventory

| Tool | Module | Description |
|---|---|---|
| Merge & Splitter | `pdf_merge_splitter.py` | Combines multiple PDF streams and extracts arbitrary page ranges |
| Metadata Scrubber | `pdf_metadata_scrubber.py` | Audits and eliminates author information and printer footprints |
| Text Extractor | `pdf_text_extractor.py` | Extracts text preserving layout structure with character counts |
| Watermark Stamper | `pdf_watermark_stamper.py` | Imprints customizable diagonal watermark banners across pages |
| Page Reorder & Rotator | `pdf_page_reorder_rotator.py` | Reorders page sequences and applies 90/180/270 degree rotations |
| Table Extractor | `pdf_table_extractor.py` | Detects aligned column structures and exports tables to CSV |
| Encryption Manager | `pdf_encryption_manager.py` | Secures documents with AES-128/256 user and owner passwords |
| TOC & Bookmark Builder | `pdf_bookmark_toc_builder.py` | Injects nested outline bookmarks and navigation hierarchies |
| Image Rasterizer | `pdf_image_rasterizer.py` | Extracts raw embedded raster graphics from document pages |
| Form Field Inspector | `pdf_form_field_inspector.py` | Inspects interactive AcroForm widgets, values, and signatures |

## Quickstart

### Installation

```bash
git clone https://github.com/abdelrahmanabuzed-onepice/pdf-document-utilities.git
cd pdf-document-utilities
pip install -e .
```

### Usage Examples

Run via unified CLI dispatcher:

```bash
# Display CLI help
pdf-tools-cli --help

# Merge multiple documents into a single PDF
pdf-tools-cli merge-split --mode merge --inputs part1.pdf part2.pdf --output combined.pdf

# Scrub identifying metadata from a document
pdf-tools-cli scrub-metadata --input contract.pdf --output contract_sanitized.pdf

# Encrypt a document with AES-256 password protection
pdf-tools-cli encryption --mode encrypt --input report.pdf --output secure.pdf --password SecretKey123
```

Or execute individual tool scripts directly:

```bash
python src/pdf_document_utilities/tools/pdf_watermark_stamper.py --input doc.pdf --output watermarked.pdf --text "INTERNAL ONLY"
```

## Testing

Execute the unit test suite:

```bash
pytest tests/
```

## Author

Abdelrahman Abouzed  
GitHub: [abdelrahmanabuzed-onepice](https://github.com/abdelrahmanabuzed-onepice)
