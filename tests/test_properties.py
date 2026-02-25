"""
©AngelaMos | 2026
test_properties.py
"""

from hypothesis import given, settings, strategies as st

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
)


class TestBase64Properties:
    @given(st.binary())
    def test_roundtrip(self, data: bytes) -> None:
        assert decode_base64(encode_base64(data)) == data

    @given(st.binary(min_size=1))
    def test_encoded_is_ascii(self, data: bytes) -> None:
        encoded = encode_base64(data)
        encoded.encode("ascii")

    @given(st.binary())
    def test_encoded_length_is_multiple_of_4(self, data: bytes) -> None:
        encoded = encode_base64(data)
        if encoded:
            assert len(encoded) % 4 == 0


class TestBase64UrlProperties:
    @given(st.binary())
    def test_roundtrip(self, data: bytes) -> None:
        assert decode_base64url(encode_base64url(data)) == data

    @given(st.binary(min_size=1))
    def test_no_standard_base64_chars(self, data: bytes) -> None:
        encoded = encode_base64url(data)
        assert "+" not in encoded
        assert "/" not in encoded


class TestBase32Properties:
    @given(st.binary())
    def test_roundtrip(self, data: bytes) -> None:
        assert decode_base32(encode_base32(data)) == data

    @given(st.binary(min_size=1))
    def test_encoded_is_uppercase(self, data: bytes) -> None:
        encoded = encode_base32(data)
        assert encoded == encoded.upper()

    @given(st.binary())
    def test_encoded_length_is_multiple_of_8(self, data: bytes) -> None:
        encoded = encode_base32(data)
        if encoded:
            assert len(encoded) % 8 == 0


class TestHexProperties:
    @given(st.binary())
    def test_roundtrip(self, data: bytes) -> None:
        assert decode_hex(encode_hex(data)) == data

    @given(st.binary(min_size=1))
    def test_encoded_length_is_double(self, data: bytes) -> None:
        assert len(encode_hex(data)) == len(data) * 2

    @given(st.binary())
    def test_encoded_is_hex_chars_only(self, data: bytes) -> None:
        encoded = encode_hex(data)
        assert all(c in "0123456789abcdef" for c in encoded)


class TestUrlProperties:
    @given(st.text(alphabet=st.characters(codec="utf-8", categories=("L", "N", "P", "S", "Z"))))
    @settings(max_examples=200)
    def test_roundtrip(self, text: str) -> None:
        data = text.encode("utf-8")
        assert decode_url(encode_url(data)) == data

    @given(st.text(alphabet=st.characters(codec="utf-8", categories=("L", "N", "P", "S", "Z"))))
    @settings(max_examples=200)
    def test_form_roundtrip(self, text: str) -> None:
        data = text.encode("utf-8")
        assert decode_url(encode_url(data, form=True), form=True) == data


class TestCrossFormatProperties:
    @given(st.binary(min_size=1, max_size=256))
    def test_all_formats_roundtrip(self, data: bytes) -> None:
        for fmt in (
            EncodingFormat.BASE64,
            EncodingFormat.BASE64URL,
            EncodingFormat.BASE32,
            EncodingFormat.HEX,
        ):
            assert decode(encode(data, fmt), fmt) == data
