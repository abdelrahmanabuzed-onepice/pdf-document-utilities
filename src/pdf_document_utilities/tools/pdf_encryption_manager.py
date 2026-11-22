"""PDF encryption and decryption security management tool with AES support."""

import argparse
import os
import sys
from typing import Any, Dict, List, Optional
import pypdf

try:
    import cryptography  # noqa: F401
    _SUPPORTS_AES = True
except ImportError:
    _SUPPORTS_AES = False


def execute_pdf_encryption_manager(
    mode: str,
    input_path: str,
    output_path: str,
    password: str,
    owner_password: Optional[str] = None,
    algorithm: str = "AES-256",
) -> Dict[str, Any]:
    """Encrypt or decrypt a PDF file using standard AES/RC4 cipher suites.

    Args:
        mode: Operation mode ('encrypt' or 'decrypt').
        input_path: Path to target PDF.
        output_path: Path to save result PDF.
        password: User password for encryption or decryption.
        owner_password: Optional distinct owner/admin password for encryption.
        algorithm: Encryption algorithm ('AES-128', 'AES-256', 'RC4-128').

    Returns:
        Structured dictionary reporting encryption status.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"PDF document not found: {input_path}")

    reader = pypdf.PdfReader(input_path)

    if mode == "decrypt":
        if reader.is_encrypted:
            decrypt_res = reader.decrypt(password)
            if decrypt_res == 0:
                raise ValueError("Decryption failed: Incorrect password provided.")

        writer = pypdf.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

    elif mode == "encrypt":
        if reader.is_encrypted:
            reader.decrypt(password)

        writer = pypdf.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        # Apply encryption with automatic fallback if cryptography library is absent
        algo_flag = algorithm.upper()
        if _SUPPORTS_AES and "AES" in algo_flag:
            selected_algo = "AES-256" if "256" in algo_flag else "AES-128"
        else:
            selected_algo = "RC4-128"

        writer.encrypt(
            user_password=password,
            owner_password=owner_password or password,
            algorithm=selected_algo,
        )
    else:
        raise ValueError(f"Unknown mode: {mode}. Choose 'encrypt' or 'decrypt'.")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    with open(output_path, "wb") as out_f:
        writer.write(out_f)

    return {
        "status": "success",
        "mode": mode,
        "input_path": input_path,
        "output_path": output_path,
        "pages_processed": len(writer.pages),
        "algorithm": selected_algo if mode == "encrypt" else "none",
    }


def build_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        description="PDF encryption and decryption security management tool."
    )
    parser.add_argument(
        "--mode",
        "-m",
        choices=["encrypt", "decrypt"],
        required=True,
        help="Security operation: 'encrypt' or 'decrypt'",
    )
    parser.add_argument("--input", "-i", required=True, help="Input PDF file path")
    parser.add_argument("--output", "-o", required=True, help="Output destination PDF path")
    parser.add_argument("--password", "-p", required=True, help="Password key")
    parser.add_argument("--owner-password", help="Optional owner/admin password")
    parser.add_argument(
        "--algo",
        choices=["AES-128", "AES-256", "RC4-128"],
        default="AES-256",
        help="Cipher algorithm for encryption",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        res = execute_pdf_encryption_manager(
            mode=args.mode,
            input_path=args.input,
            output_path=args.output,
            password=args.password,
            owner_password=args.owner_password,
            algorithm=args.algo,
        )
        print(f"Success: {res['mode'].capitalize()} written to {res['output_path']} ({res['pages_processed']} pages)")
        return 0
    except Exception as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
