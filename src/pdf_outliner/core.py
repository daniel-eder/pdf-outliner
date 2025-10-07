# SPDX-FileCopyrightText: 2025 Daniel Eder
#
# SPDX-License-Identifier: MIT

"""
Core functionality for PDF Outliner
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import litellm
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pypdf import PdfReader, PdfWriter


class Heading(BaseModel):
    """Represents a heading in the document."""

    title: str = Field(..., description="The text of the heading")
    level: int = Field(..., ge=1, le=6, description="The heading level (1-6, where 1 is top-level)")
    page: int = Field(..., ge=1, description="The page number where the heading appears")


class DocumentOutline(BaseModel):
    """Represents the complete outline of a document."""

    headings: list[Heading] = Field(..., description="List of headings in the document")


class PDFOutliner:
    """Analyzes PDFs and adds bookmarks based on detected headings."""

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize the PDF outliner.

        Args:
            model: The LiteLLM model to use for analysis
        """
        self.model = model
        load_dotenv()

    def extract_text_with_pages(self, pdf_path: Path) -> list[dict[str, Any]]:
        """
        Extract text from PDF with page information.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of dictionaries containing page number and text
        """
        reader = PdfReader(pdf_path)
        pages = []

        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            pages.append({"page": page_num, "text": text})

        return pages

    def analyze_pdf_with_llm(self, pages: list[dict[str, Any]]) -> DocumentOutline:
        """
        Analyze PDF text using LLM to detect headings.

        Args:
            pages: List of page dictionaries with text

        Returns:
            DocumentOutline containing detected headings
        """
        # Prepare the document text with page markers
        document_text = ""
        for page_data in pages:
            document_text += f"\n--- PAGE {page_data['page']} ---\n"
            document_text += page_data["text"]

        # Truncate if too long (keep within context limits)
        max_chars = 50000
        if len(document_text) > max_chars:
            document_text = document_text[:max_chars] + "\n\n[Document truncated...]"

        system_prompt = """You are a document analysis assistant. Your task is to identify all headings in a document and create an outline.

Analyze the provided document text and identify:
1. Main headings and subheadings
2. Their hierarchical level (1 = main heading, 2 = subheading, etc.)
3. The page number where each heading appears (indicated by PAGE markers)

Guidelines:
- Level 1: Main chapter/section titles
- Level 2: Major subsections
- Level 3+: Nested subsections
- Ignore headers/footers, page numbers, and running titles
- Focus on actual content structure
- Be conservative - only include clear headings

Return the outline as a structured list."""

        user_prompt = f"""Analyze this document and extract all headings with their levels and page numbers:

{document_text}

Return a JSON object with a "headings" array where each heading has:
- title: the heading text
- level: hierarchical level (1-6)
- page: page number where it appears"""

        try:
            response = litellm.completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            # Parse the response
            content = response.choices[0].message.content
            data = json.loads(content)

            # Validate with Pydantic
            outline = DocumentOutline(**data)
            return outline

        except Exception as e:
            raise RuntimeError(f"Error analyzing PDF with LLM: {e}") from e

    def add_bookmarks_to_pdf(
        self,
        input_path: Path,
        output_path: Path,
        outline: DocumentOutline,
    ) -> None:
        """
        Add bookmarks to PDF based on the detected outline.

        Args:
            input_path: Path to input PDF
            output_path: Path to save output PDF with bookmarks
            outline: DocumentOutline with headings to add
        """
        reader = PdfReader(input_path)
        writer = PdfWriter()

        # Add all pages
        for page in reader.pages:
            writer.add_page(page)

        # Track parent bookmarks for nested structure
        parent_stack: list[Any] = [None]  # Stack to track parent bookmarks by level

        for heading in outline.headings:
            page_num = heading.page - 1  # Convert to 0-based index

            # Validate page number
            if page_num < 0 or page_num >= len(writer.pages):
                print(
                    f"Warning: Skipping heading '{heading.title}' - "
                    f"page {heading.page} out of range",
                    file=sys.stderr,
                )
                continue

            # Adjust parent stack to current level
            # Ensure we have the right parent for this level
            while len(parent_stack) > heading.level:
                parent_stack.pop()

            # Get parent (None for top-level, or the bookmark at level-1)
            parent = parent_stack[-1] if len(parent_stack) > 0 else None

            # Add bookmark
            bookmark = writer.add_outline_item(
                title=heading.title,
                page_number=page_num,
                parent=parent,
            )

            # Update stack: ensure we have exactly heading.level items
            while len(parent_stack) < heading.level:
                parent_stack.append(parent_stack[-1])

            if len(parent_stack) == heading.level:
                parent_stack.append(bookmark)
            else:
                parent_stack[heading.level] = bookmark

        # Write output PDF
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

    def process_pdf(
        self,
        input_path: Path,
        output_path: Path | None = None,
    ) -> DocumentOutline:
        """
        Complete workflow: extract text, analyze, and add bookmarks.

        Args:
            input_path: Path to input PDF
            output_path: Path to output PDF (defaults to input_path with '_outlined' suffix)

        Returns:
            DocumentOutline with detected headings
        """
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_outlined.pdf"

        print(f"📄 Reading PDF: {input_path}")
        pages = self.extract_text_with_pages(input_path)
        print(f"   Found {len(pages)} pages")

        print(f"\n🤖 Analyzing with {self.model}...")
        outline = self.analyze_pdf_with_llm(pages)
        print(f"   Detected {len(outline.headings)} headings")

        print(f"\n📑 Adding bookmarks to PDF...")
        self.add_bookmarks_to_pdf(input_path, output_path, outline)
        print(f"   ✅ Saved to: {output_path}")

        return outline
