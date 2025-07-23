import html
import re
import unicodedata
from typing import Optional

# Pre-compile regex for allowed ASCII characters. You can adjust as needed.
_SAFE_ASCII_PATTERN = re.compile(
    r"[^A-Za-z0-9\s\.\,\-\_\/\+\!\@\#\$\%\^\&\*\(\)\[\]\{\}\:\;\'\"\`\~\|\=\?\\]"  # exclude < >
)

# If you want to keep < >, add them to the char class.

# Common zero-width characters to strip
_ZERO_WIDTH_CHARS = [
    "\u200b",  # zero width space
    "\u200c",  # zero width non-joiner
    "\u200d",  # zero width joiner
    "\ufeff",  # BOM
    "\u2060",  # word joiner
]

# Fast translation table to remove C0/C1 control chars
_CONTROL_TRANS = {
    c: None
    for c in range(0x00, 0x20)  # C0
    if c not in (0x09, 0x0A, 0x0D)  # keep tab/newline/cr for now (will convert to space)
}
_CONTROL_TRANS.update({c: None for c in range(0x7F, 0xA0)})  # C1

def sanitize_text_for_ui(
    text: Optional[str],
    *,
    allow_unicode_letters: bool = False,
    collapse_whitespace: bool = True,
    ascii_fallback: bool = False,
    xml_escape: bool = False,
    max_length: Optional[int] = None,
) -> str:
    """
    Clean text from web/API for safe use in UI & XML attributes.

    Parameters
    ----------
    text : str | None
        Source string.
    allow_unicode_letters : bool
        True -> keep Unicode letters (Vietnamese, Japanese, etc.) if not a control character.
        False -> all Unicode characters outside the ASCII allowlist are removed.
    collapse_whitespace : bool
        Collapse multiple spaces/tabs/newlines into a single space.
    ascii_fallback : bool
        If True, after keeping Unicode (if allowed), convert to closest ASCII (NFKD + ASCII filter).
    xml_escape : bool
        Finally escape for use in XML attributes (&lt; &amp; ...).
    max_length : int | None
        Truncate string if too long (protect DB/UI).

    Returns
    -------
    str
        Cleaned string.
    """
    if not text:
        return ""

    # Normalize unicode: remove weird forms, split accents (used if ascii_fallback).
    txt = unicodedata.normalize("NFC", text)

    # Remove zero-width & BOM
    for z in _ZERO_WIDTH_CHARS:
        txt = txt.replace(z, "")

    # Drop control chars (C0/C1)
    txt = txt.translate(_CONTROL_TRANS)

    # Normalize whitespace: convert tab, newline, carriage to space
    txt = txt.replace("\t", " ").replace("\r", " ").replace("\n", " ")

    if allow_unicode_letters:
        # If allowing Unicode: only strip non-printable & private use characters
        # Still want to block category "Cs" (surrogate), "Co" (private use)? Up to you
        cleaned_chars = []
        for ch in txt:
            cat = unicodedata.category(ch)
            if cat.startswith("C"):  # control, surrogate, unassigned
                continue
            cleaned_chars.append(ch)
        txt = "".join(cleaned_chars)
        # Should we filter out some extremely rare characters outside BMP? Up to your needs.
    else:
        # Filter to ASCII allowlist
        txt = _SAFE_ASCII_PATTERN.sub("", txt)

    if collapse_whitespace:
        txt = re.sub(r"\s+", " ", txt)

    txt = txt.strip()

    if ascii_fallback and allow_unicode_letters:
        # Convert remaining Unicode to closest ASCII
        decomposed = unicodedata.normalize("NFKD", txt)
        txt = decomposed.encode("ascii", "ignore").decode("ascii", "ignore")
        # (Can run _SAFE_ASCII_PATTERN again)
        txt = _SAFE_ASCII_PATTERN.sub("", txt).strip()

    if max_length is not None and len(txt) > max_length:
        txt = txt[:max_length].rstrip() + "..."

    if xml_escape:
        # Important: escape special XML characters.
        # Note: html.escape is also used for XML (escapes &, <, >, ") — single quote optional.
        txt = html.escape(txt, quote=True)

    return txt
