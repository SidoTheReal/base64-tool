"""
©AngelaMos | 2026
test_encoders.py
"""

import binascii

import pytest

from base64_tool.constants import EncodingFormat
from base64_tool.encoders import (
    decode,
    decode_base32,
    decode_base64,
    decode_base64url,
    decode_hex,
    decode_url,
    encode,
    encode_base32,
    encode_base64,
    encode_base64url,
    encode_hex,
    encode_url,
    try_decode,
)


class TestBase64:
    def test_encode_simple_text(self) -> None:
        assert encode_base64(b"Hello World") == "SGVsbG8gV29ybGQ="

    def test_decode_simple_text(self) -> None:
        assert decode_base64("SGVsbG8gV29ybGQ=") == b"Hello World"

    def test_roundtrip(self) -> None:
        original = b"The quick brown fox jumps over the lazy dog"
        assert decode_base64(encode_base64(original)) == original

    def test_encode_empty(self) -> None:
        assert encode_base64(b"") == ""

    def test_decode_empty(self) -> None:
        assert decode_base64("") == b""

    def test_encode_binary_data(self) -> None:
        data = bytes(range(256))
        assert decode_base64(encode_base64(data)) == data

    def test_decode_with_whitespace(self) -> None:
        encoded = "SGVs\nbG8g\nV29y\nbGQ="
        assert decode_base64(encoded) == b"Hello World"

    def test_decode_invalid_raises(self) -> None:
        with pytest.raises((ValueError, binascii.Error)):
            decode_base64("!!!invalid!!!")

    def test_encode_unicode(self) -> None:
        data = "Hello 世界".encode()
        decoded = decode_base64(encode_base64(data))
        assert decoded == data


class TestBase64Url:
    def test_encode_with_url_chars(self) -> None:
        data = b"\xfb\xff\xfe"
        encoded = encode_base64url(data)
        assert "+" not in encoded
        assert "/" not in encoded

    def test_decode_url_safe(self) -> None:
        result = decode_base64url(encode_base64url(b"test/path+query"))
        assert result == b"test/path+query"

    def test_roundtrip(self) -> None:
        original = b"https://example.com?token=abc+def/ghi"
        assert decode_base64url(encode_base64url(original)) == original


class TestBase32:
    def test_encode_simple(self) -> None:
        assert encode_base32(b"Hello") == "JBSWY3DP"

    def test_decode_simple(self) -> None:
        assert decode_base32("JBSWY3DP") == b"Hello"

    def test_roundtrip(self) -> None:
        original = b"Base32 encoding test"
        assert decode_base32(encode_base32(original)) == original

    def test_decode_lowercase_accepted(self) -> None:
        assert decode_base32("jbswy3dp") == b"Hello"

    def test_decode_with_padding(self) -> None:
        assert decode_base32("JBSWY3DPEBLW64TMMQ======") == b"Hello World"


class TestHex:
    def test_encode_simple(self) -> None:
        assert encode_hex(b"\xca\xfe") == "cafe"

    def test_decode_simple(self) -> None:
        assert decode_hex("cafe") == b"\xca\xfe"

    def test_decode_with_colons(self) -> None:
        assert decode_hex("ca:fe:ba:be") == b"\xca\xfe\xba\xbe"

    def test_decode_with_spaces(self) -> None:
        assert decode_hex("ca fe ba be") == b"\xca\xfe\xba\xbe"

    def test_decode_with_dashes(self) -> None:
        assert decode_hex("ca-fe-ba-be") == b"\xca\xfe\xba\xbe"

    def test_decode_uppercase(self) -> None:
        assert decode_hex("CAFE") == b"\xca\xfe"

    def test_roundtrip(self) -> None:
        original = b"Hello World"
        assert decode_hex(encode_hex(original)) == original


class TestUrl:
    def test_encode_special_chars(self) -> None:
        result = encode_url(b"hello world&foo=bar")
        assert " " not in result
        assert "&" not in result

    def test_decode_percent_encoded(self) -> None:
        assert decode_url("hello%20world") == b"hello world"

    def test_roundtrip(self) -> None:
        original = b"path/to/file?key=value&other=test"
        assert decode_url(encode_url(original)) == original

    def test_form_encode_space_as_plus(self) -> None:
        result = encode_url(b"hello world", form = True)
        assert "+" in result
        assert "%20" not in result

    def test_form_decode_plus_as_space(self) -> None:
        assert decode_url("hello+world", form = True) == b"hello world"


class TestRegistryDispatch:
    @pytest.mark.parametrize("fmt", list(EncodingFormat))
    def test_encode_decode_roundtrip(
        self,
        fmt: EncodingFormat,
    ) -> None:
        original = b"roundtrip test data"
        encoded = encode(original, fmt)
        decoded = decode(encoded, fmt)
        assert decoded == original

    def test_try_decode_valid(self) -> None:
        result = try_decode("SGVsbG8=", EncodingFormat.BASE64)
        assert result == b"Hello"

    def test_try_decode_invalid_returns_none(self) -> None:
        result = try_decode("!!!bad!!!", EncodingFormat.BASE64)
        assert result is None
