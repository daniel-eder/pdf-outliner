# SPDX-FileCopyrightText: 2025 Daniel Eder
#
# SPDX-License-Identifier: MIT

"""
Command-line interface for PDF Outliner
"""

import argparse
import os
import sys
from pathlib import Path

from pdf_outliner.core import PDFOutliner


def cli() -> None:
    """Command-line interface for PDF Outliner."""
    parser = argparse.ArgumentParser(
        description="Add AI-generated bookmarks to PDFs based on detected headings"
    )
    parser.add_argument("input_pdf", type=Path, help="Input PDF file path")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output PDF file path (default: input_outlined.pdf)",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default=os.getenv("DEFAULT_MODEL", "gemini/gemini-3.1-flash-lite"),
        help="LiteLLM model to use (default: gemini/gemini-3.1-flash-lite)",
    )
    parser.add_argument(
        "-g",
        "--guidance",
        type=str,
        help="Additional guidance for the AI about what kind of outline to produce",
    )
    parser.add_argument(
        "--show-outline",
        action="store_true",
        help="Print the detected outline to console",
    )

    args = parser.parse_args()

    # Validate input file
    if not args.input_pdf.exists():
        print(f"[ERROR] Input file not found: {args.input_pdf}", file=sys.stderr)
        sys.exit(1)

    # Create outliner and process
    try:
        outliner = PDFOutliner(model=args.model)
        outline = outliner.process_pdf(args.input_pdf, args.output, guidance=args.guidance)

        # Optionally print the outline
        if args.show_outline:
            print("\n[*] Detected Outline:")
            print("=" * 60)
            for heading in outline.headings:
                indent = "  " * (heading.level - 1)
                print(f"{indent}{'>' * heading.level} {heading.title} (p.{heading.page})")

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
