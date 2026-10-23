"""Tests for heading cleanup in parse.py.

The numbering rule is small but it ran on 35 corpus papers, so it gets a test:
"1. Introduction" used to come out as ". Introduction" on any paper that numbers
sections with a dot (AISSA in the corpus).
"""
import pytest

from parse import clean_heading


@pytest.mark.parametrize("raw,expected", [
    ("1. Introduction", "Introduction"),
    ("1 Introduction", "Introduction"),
    ("2. Background", "Background"),
    ("3.2.1 Problem Formulation", "Problem Formulation"),
    ("4.1. Method", "Method"),
    ("12 Conclusion", "Conclusion"),
    ("Introduction", "Introduction"),
    ("  Abstract  ", "Abstract"),
])
def test_section_numbers_are_stripped(raw, expected):
    assert clean_heading(raw) == expected


@pytest.mark.parametrize("raw", [
    "5G Networks for Rural Access",   # a year or model number is not a section number
    "2023 Results and Beyond",
    "A1 Baselines",
])
def test_numbers_that_belong_to_the_title_survive(raw):
    assert clean_heading(raw) == raw


def test_stripping_never_returns_an_empty_string():
    assert clean_heading("1.") == "1."
