#!/usr/bin/env python3
"""Unit tests for organize-downloads scripts.

Usage:
    conda run -n henri_env python -m pytest tests/
"""
import sys, os, json, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# --- rename_pdfs.py tests ---
from rename_pdfs import (
    extract_lastname, extract_year, sanitize_title, needs_rename,
    extract_authors_from_text, extract_title_from_text, _is_junk_line,
    FALSE_AUTHORS, _COMMON_SURNAMES,
)


class TestExtractLastname:
    def test_english_lastname(self):
        assert extract_lastname("John Smith") == "Smith"
        assert extract_lastname("Smith, John") == "Smith"
        assert extract_lastname("Ziming Liu") == "Liu"

    def test_chinese_lastname(self):
        name = extract_lastname("刘慈欣")
        assert name == "刘慈欣" or name == "刘慈"

    def test_single_name(self):
        assert extract_lastname("Aristotle") == "Aristotle"

    def test_skip_publishers(self):
        assert extract_lastname("arXiv:2401.12345") is None
        assert extract_lastname("Elsevier Inc.") is None

    def test_skip_numbers(self):
        assert extract_lastname("0007855") is None

    def test_empty(self):
        assert extract_lastname("") is None
        assert extract_lastname(None) is None


class TestExtractYear:
    def test_published_online(self):
        assert extract_year("Published online: 15 May 2024") == "2024"

    def test_cn_year(self):
        assert extract_year("2023年出版") == "2023"

    def test_recent_year(self):
        assert extract_year("Some text 2024 more text 2023") == "2024"

    def test_no_year(self):
        assert extract_year("no digits here") is None

    def test_creation_date(self):
        assert extract_year("text", "D:20240301120000") == "2024"


class TestSanitizeTitle:
    def test_shorten_long(self):
        result = sanitize_title("A Very Long Title That Should Definitely Be Truncated By The Function", 20)
        assert len(result) <= 20

    def test_remove_colons(self):
        assert ":" not in sanitize_title("Title: Subtitle")

    def test_trim_whitespace(self):
        assert sanitize_title("   Spaced Out  ") == "Spaced Out"

    def test_none_input(self):
        assert sanitize_title(None) is None

    def test_remove_pdf(self):
        assert not sanitize_title("Title.pdf").endswith('.pdf')


class TestNeedsRename:
    def test_already_renamed(self):
        assert needs_rename("Smith_2024_Some Title.pdf") is False

    def test_arxiv_needs_rename(self):
        assert needs_rename("2403.12345v1.pdf") is True

    def test_ssrn_needs_rename(self):
        assert needs_rename("ssrn-4840317.pdf") is True

    def test_isbn_needs_rename(self):
        assert needs_rename("978-3-031-22170-5.pdf") is True

    def test_skip_chinese(self):
        assert needs_rename("数学分析.pdf") is False

    def test_unknown_needs_rename(self):
        assert needs_rename("Unknown_2024_Untitled.pdf") is True

    def test_skip_proper_format(self):
        assert needs_rename("Smith_XXXX_Some Title.pdf") is True  # XXXX is invalid year


class TestIsJunkLine:
    def test_issn_is_junk(self):
        assert _is_junk_line("ISSN 1234-5678") is True

    def test_abstract_is_junk(self):
        assert _is_junk_line("Abstract") is True

    def test_long_text_not_junk(self):
        assert _is_junk_line("This is a real paper title about something interesting") is False

    def test_short_line_is_junk(self):
        assert _is_junk_line("ab") is True

    def test_url_is_junk(self):
        assert _is_junk_line("https://example.com") is True


class TestExtractTitleFromText:
    def test_chinese_title(self):
        text = "微分几何入门\n陈维桓\nAbstract..."
        assert extract_title_from_text(text) is not None

    def test_english_title(self):
        text = "Functional Analysis\nPeter D. Lax\nAbstract..."
        assert extract_title_from_text(text) is not None

    def test_skip_junk(self):
        text = "ISSN 1234\nVol. 5\nActual Title Here\nmore text"
        assert extract_title_from_text(text) == "Actual Title Here"


class TestConstants:
    def test_false_authors_no_leading_space(self):
        for a in FALSE_AUTHORS:
            assert a == a.strip(), f"'{a}' has leading/trailing whitespace"

    def test_common_surnames(self):
        assert len(_COMMON_SURNAMES) > 100
        assert '李' in _COMMON_SURNAMES
        assert '王' in _COMMON_SURNAMES
        assert '张' in _COMMON_SURNAMES


# --- classify_images.py tests ---
from classify_images import (
    IMAGE_EXTS, _READ_LIMIT, _THUMB_SIZE
)


class TestImageConstants:
    def test_heic_supported(self):
        assert '.heic' in IMAGE_EXTS

    def test_read_limit_set(self):
        assert _READ_LIMIT == 8 * 1024 * 1024

    def test_thumb_size_set(self):
        assert _THUMB_SIZE == (1600, 1600)
