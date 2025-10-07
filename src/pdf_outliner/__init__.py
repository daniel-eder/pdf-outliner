# SPDX-FileCopyrightText: 2025 Daniel Eder
#
# SPDX-License-Identifier: MIT

"""
PDF Outliner - AI-powered PDF bookmark generator
"""

from pdf_outliner.cli import cli
from pdf_outliner.core import DocumentOutline, Heading, PDFOutliner

__all__ = ["PDFOutliner", "Heading", "DocumentOutline", "__version__", "main"]


def main() -> None:
    """Entry point for the pdf-outliner CLI."""
    cli()
