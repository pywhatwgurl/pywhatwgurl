# SPDX-License-Identifier: MIT
"""
WHATWG URL Standard compliant IDNA processing.

This module implements domain-to-ASCII and domain-to-Unicode algorithms
per the WHATWG URL Standard section 3.3, using Unicode IDNA Compatibility
Processing (UTS46) with the following parameters for beStrict=false:

- CheckHyphens: false (allows leading/trailing hyphens, xx-- patterns)
- CheckBidi: true
- CheckJoiners: true
- UseSTD3ASCIIRules: false
- Transitional_Processing: false
- VerifyDnsLength: false (allows labels > 63 bytes)
- IgnoreInvalidPunycode: false

Reference: https://url.spec.whatwg.org/#idna
"""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

import idna
from idna.core import IDNABidiError, IDNAError, InvalidCodepoint

from .encoding import FORBIDDEN_DOMAIN_CODE_POINTS

# Unicode dots that should be treated as label separators
_UNICODE_DOTS_RE = re.compile(r"[\u002e\u3002\uff0e\uff61]")


def _is_ascii_string(s: str) -> bool:
    """Check if string contains only ASCII characters."""
    try:
        s.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def _has_xn_prefix_label(domain: str) -> bool:
    """Check if any label starts with 'xn--' (case-insensitive)."""
    labels = domain.split(".")
    return any(label.lower().startswith("xn--") for label in labels)


def _check_bidi_label(label: str) -> bool:
    """Validate Bidi rules for a label per RFC 5893 section 2.

    Returns True if label passes Bidi validation, False otherwise.
    Note: We return True for "Unknown directionality" errors since these
    occur for unassigned code points which the WHATWG spec allows.
    """
    if not label:
        return True

    try:
        idna.check_bidi(label)
        return True
    except IDNABidiError as e:
        # Allow labels with unassigned characters (unknown directionality)
        # These are valid per the WHATWG URL spec even though they fail strict Bidi
        if "Unknown directionality" in str(e):
            return True
        return False


def _check_joiner_context(label: str, pos: int) -> bool:
    """Validate CONTEXTJ rules for ZWNJ (U+200C) and ZWJ (U+200D).

    Returns True if joiner at position is valid, False otherwise.
    """
    return idna.valid_contextj(label, pos)


def _check_label_initial_combiner(label: str) -> bool:
    """Check that label doesn't start with a combining mark.

    Returns True if valid (no initial combining mark), False otherwise.
    """
    if not label:
        return True
    # General_Category Mark includes Mn (Nonspacing_Mark), Mc (Spacing_Combining_Mark), Me (Enclosing_Mark)
    category = unicodedata.category(label[0])
    return not category.startswith("M")


def _validate_label(label: str, be_strict: bool) -> bool:
    """Validate a single label per WHATWG/UTS46 requirements.

    CheckBidi=true, CheckJoiners=true, CheckHyphens=beStrict

    Returns True if label is valid, False otherwise.
    """
    if not label:
        return True  # Empty labels allowed (for trailing dots)

    # CheckHyphens only when beStrict is true
    if be_strict:
        # Check for hyphens in positions 3 and 4
        if len(label) >= 4 and label[2:4] == "--":
            return False
        # Check for leading/trailing hyphens
        if label.startswith("-") or label.endswith("-"):
            return False

    # Label must not start with combining mark
    if not _check_label_initial_combiner(label):
        return False

    # CheckJoiners: validate ZWNJ and ZWJ context
    for i, char in enumerate(label):
        if char in ("\u200c", "\u200d"):  # ZWNJ, ZWJ
            if not _check_joiner_context(label, i):
                return False

    # CheckBidi: validate bidirectional text
    if not _check_bidi_label(label):
        return False

    return True


def _punycode_encode(label: str) -> Optional[str]:
    """Encode a Unicode label to Punycode (xn-- prefixed).

    Returns the encoded label or None if encoding fails.
    """
    try:
        # Encode to punycode and prefix with xn--
        encoded = label.encode("punycode").decode("ascii")
        return "xn--" + encoded
    except (UnicodeError, UnicodeEncodeError):
        return None


def _punycode_decode(label: str) -> Optional[str]:
    """Decode a Punycode label (xn-- prefixed) to Unicode.

    Returns the decoded label or None if decoding fails.
    """
    if not label.lower().startswith("xn--"):
        return label
    try:
        # Remove xn-- prefix and decode
        return label[4:].encode("ascii").decode("punycode")
    except (UnicodeError, UnicodeDecodeError):
        return None


def _process_label_to_ascii(label: str, be_strict: bool) -> Optional[str]:
    """Process a single label through UTS46 ToASCII.

    Returns the ASCII label or None on failure.
    """
    if not label:
        return ""

    # P4 check: If label starts with "xn--" but is NOT ASCII, it's invalid
    # (Punycode labels must be pure ASCII - non-ASCII in xn-- prefix is an error)
    if label.lower().startswith("xn--") and not _is_ascii_string(label):
        return None

    # If already ASCII
    if _is_ascii_string(label):
        # Check if it's a Punycode label that needs validation
        if label.lower().startswith("xn--"):
            # Decode punycode to validate
            decoded = _punycode_decode(label)
            if decoded is None:
                return None  # Invalid punycode

            # Empty decoded punycode (xn-- with no content) is invalid
            if not decoded:
                return None

            # V4 check: Decoded punycode should not start with "xn--" (nested punycode)
            # This catches cases like "xn--xn--a--gua" which decodes to "xn--a-ä"
            if decoded.lower().startswith("xn--"):
                return None

            # Apply UTS46 mapping to the decoded label (this is the key step!)
            # If the decoded label maps to something different, the punycode is invalid
            try:
                mapped = idna.uts46_remap(decoded, std3_rules=False, transitional=False)
            except (IDNAError, InvalidCodepoint, UnicodeError):
                return None

            # NFC normalize
            mapped = unicodedata.normalize("NFC", mapped)

            # If mapped result is empty, the punycode is invalid
            if not mapped:
                return None

            # Validate the mapped label
            if not _validate_label(mapped, be_strict):
                return None

            # Re-encode the MAPPED version to verify round-trip
            # (IgnoreInvalidPunycode=false means we reject if it doesn't round-trip)
            # For ASCII-only mapped results, the expected output is just the lowercased ASCII
            # For non-ASCII mapped results, encode to punycode
            if _is_ascii_string(mapped):
                # If mapped to ASCII-only, original punycode label is invalid
                # (punycode should only be used for non-ASCII content)
                re_encoded: Optional[str] = mapped.lower()
            else:
                re_encoded = _punycode_encode(mapped)
            if re_encoded is None or re_encoded.lower() != label.lower():
                return None

            return label.lower()
        else:
            # Plain ASCII label - validate and lowercase
            if not _validate_label(label, be_strict):
                return None
            return label.lower()

    # Non-ASCII label - validate then encode
    if not _validate_label(label, be_strict):
        return None

    encoded = _punycode_encode(label)
    if encoded is None:
        return None

    return encoded.lower()


def domain_to_ascii(domain: str, be_strict: bool = False) -> Optional[str]:
    """Convert a domain name to ASCII using IDNA processing.

    Implements the WHATWG URL Standard "domain to ASCII" algorithm
    using Unicode IDNA Compatibility Processing (UTS46).

    Args:
        domain: Unicode domain name to convert.
        be_strict: If True, apply stricter validation rules
            (CheckHyphens=true, UseSTD3ASCIIRules=true, VerifyDnsLength=true).

    Returns:
        ASCII domain string, or None if conversion fails.
    """
    # Handle empty domain
    if not domain:
        return "" if not be_strict else None

    # Fast path: ASCII-only domain without xn-- labels
    # Per spec: "If beStrict is false, domain is an ASCII string, and strictly
    # splitting domain on U+002E (.) does not produce any item that starts with
    # an ASCII case-insensitive match for 'xn--', this step is equivalent to
    # ASCII lowercasing domain."
    # BUT we still need to check for forbidden code points!
    if _is_ascii_string(domain) and not _has_xn_prefix_label(domain):
        lowercased = domain.lower()
        # Still need to check for forbidden domain code points
        for char in lowercased:
            if char in FORBIDDEN_DOMAIN_CODE_POINTS:
                return None
        return lowercased

    try:
        # Step 1: Apply UTS46 character mapping
        # UseSTD3ASCIIRules=be_strict, Transitional_Processing=false
        mapped = idna.uts46_remap(domain, std3_rules=be_strict, transitional=False)
    except (IDNAError, InvalidCodepoint, UnicodeError):
        return None

    # Step 2: NFC normalize (uts46_remap already does this, but be explicit)
    normalized = unicodedata.normalize("NFC", mapped)

    # Step 3: Split into labels using Unicode dots
    labels = _UNICODE_DOTS_RE.split(normalized)

    # Track if we had a trailing dot
    trailing_dot = labels and labels[-1] == ""
    if trailing_dot:
        labels = labels[:-1]

    # If no labels left (domain was empty or only contained ignored chars), fail
    if not labels:
        return None

    # Step 4: Process each label
    result_labels = []
    for label in labels:
        processed = _process_label_to_ascii(label, be_strict)
        if processed is None:
            return None
        result_labels.append(processed)

    # Rejoin with dots
    result = ".".join(result_labels)
    if trailing_dot:
        result += "."

    # Step 5: WHATWG post-processing for non-strict mode
    if not be_strict:
        # Empty result is failure
        if result == "" or (result == "." and not trailing_dot):
            return None

        # Check for forbidden domain code points
        for char in result:
            if char in FORBIDDEN_DOMAIN_CODE_POINTS:
                return None

    # VerifyDnsLength only when be_strict=true
    if be_strict:
        # Check total domain length (max 253 without trailing dot, 254 with)
        check_length = len(result.rstrip("."))
        if check_length > 253:
            return None

        # Check each label length (max 63)
        for label in result.rstrip(".").split("."):
            if len(label) > 63:
                return None

    return result


def domain_to_unicode(domain: str, be_strict: bool = False) -> str:
    """Convert a domain name to Unicode using IDNA processing.

    Implements the WHATWG URL Standard "domain to Unicode" algorithm.

    Args:
        domain: ASCII domain name (possibly with Punycode labels).
        be_strict: If True, apply stricter validation rules.

    Returns:
        Unicode domain string. Returns the original domain if decoding fails
        (per spec, errors are signified but result is still returned).
    """
    if not domain:
        return domain

    try:
        # Apply UTS46 mapping and decode
        mapped = idna.uts46_remap(domain, std3_rules=be_strict, transitional=False)
    except (IDNAError, InvalidCodepoint, UnicodeError):
        return domain

    # Split and decode each label
    labels = _UNICODE_DOTS_RE.split(mapped)
    result_labels = []

    for label in labels:
        if label.lower().startswith("xn--"):
            decoded = _punycode_decode(label)
            if decoded is not None:
                result_labels.append(decoded)
            else:
                result_labels.append(label)  # Keep original on error
        else:
            result_labels.append(label)

    return ".".join(result_labels)
