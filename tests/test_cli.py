"""Tests for unified CLI dispatcher."""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pdf_document_utilities.cli import build_parser, main


def test_cli_build_parser():
    parser = build_parser()
    assert parser.prog == "pdf-tools-cli"


def test_cli_help():
    assert main(["--help"]) == 0


def test_cli_empty_args():
    assert main([]) == 0


def test_cli_invalid_command():
    assert main(["non_existent_command"]) == 1
