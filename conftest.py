"""
Shared fixtures for integration contract tests.
"""
import os
import pytest
from pathlib import Path
from lxml import etree

# Root of the monorepo (can be overridden in CI)
REPO_ROOT = Path(os.getenv("INTEGRATION_REPO_ROOT", Path(__file__).resolve().parent.parent))


def load_xsd(xsd_path: Path) -> etree.XMLSchema:
    """Load and compile an XSD schema from the given path."""
    if not xsd_path.exists():
        pytest.skip(f"XSD not found: {xsd_path.relative_to(REPO_ROOT)}")
    with open(xsd_path, "rb") as f:
        schema_doc = etree.parse(f)
    return etree.XMLSchema(schema_doc)


def validate_xml_against_xsd(xml_string: str, xsd_path: Path) -> tuple[bool, str]:
    """
    Validate an XML string against an XSD file.
    Returns (is_valid, error_message).
    """
    schema = load_xsd(xsd_path)
    try:
        doc = etree.fromstring(xml_string.encode("utf-8"))
    except etree.XMLSyntaxError as e:
        return False, f"XML parse error: {e}"

    is_valid = schema.validate(doc)
    if not is_valid:
        errors = "\n".join(str(e) for e in schema.error_log)
        return False, errors
    return True, ""
