"""
©AngelaMos | 2026
test_detector.py
"""

from base64_tool.constants import EncodingFormat
from base64_tool.detector import detect_best, detect_encoding


class TestDetectBase64:
    def test_standard_base64(self) -> None:
        result = detect_best("SGVsbG8gV29ybGQ=")
        assert result is not None
        assert result.format == EncodingFormat.BASE64
        assert result.confidence >= 0.7

    def test_base64_no_padding(self) -> None:
        result = detect_best("SGVsbG8gV29ybGQh")
        assert result is not None
        assert result.format == EncodingFormat.BASE64

    def test_base64_with_plus_slash(self) -> None:
        result = detect_best("dGVzdC9wYXRoK3F1ZXJ5")
        assert result is not None
        assert result.format == EncodingFormat.BASE64


class TestDetectBase64Url:
    def test_url_safe_chars(self) -> None:
        result = detect_best("dGVzdC1kYXRhX3ZhbHVl")
        assert result is not None
        assert result.format in (
            EncodingFormat.BASE64URL,
            EncodingFormat.BASE64,
        )


class TestDetectBase32:
    def test_standard_base32(self) -> None:
        result = detect_best("JBSWY3DPEBLW64TMMQ======")
        assert result is not None
        assert result.format == EncodingFormat.BASE32
        assert result.confidence >= 0.6

    def test_base32_uppercase(self) -> None:
        result = detect_best("JBSWY3DP")
        assert result is not None
        assert result.format == EncodingFormat.BASE32


class TestDetectHex:
    def test_hex_with_letters(self) -> None:
        result = detect_best("48656c6c6f20576f726c64")
        assert result is not None
        assert result.format == EncodingFormat.HEX
        assert result.confidence >= 0.6

    def test_hex_with_colons(self) -> None:
        result = detect_best("48:65:6c:6c:6f:20:57:6f:72:6c:64")
        assert result is not None
        assert result.format == EncodingFormat.HEX

    def test_pure_digits_not_detected(self) -> None:
        result = detect_best("1234567890")
        if result is not None and result.format == EncodingFormat.HEX:
            assert result.confidence < 0.7


class TestDetectUrl:
    def test_url_encoded(self) -> None:
        result = detect_best("hello%20world%21%40%23")
        assert result is not None
        assert result.format == EncodingFormat.URL

    def test_heavily_encoded(self) -> None:
        result = detect_best("%48%65%6C%6C%6F%20%57%6F%72%6C%64")
        assert result is not None
        assert result.format == EncodingFormat.URL
        assert result.confidence >= 0.6


class TestDetectMultiple:
    def test_returns_sorted_by_confidence(self) -> None:
        results = detect_encoding("SGVsbG8gV29ybGQ=")
        if len(results) > 1:
            confidences = [r.confidence for r in results]
            assert confidences == sorted(confidences, reverse = True)

    def test_no_match_returns_empty(self) -> None:
        results = detect_encoding("hello world")
        assert results == []

    def test_short_string_returns_empty(self) -> None:
        results = detect_encoding("ab")
        assert results == []


class TestDetectBest:
    def test_returns_highest_confidence(self) -> None:
        result = detect_best("SGVsbG8gV29ybGQ=")
        assert result is not None
        all_results = detect_encoding("SGVsbG8gV29ybGQ=")
        if all_results:
            assert result.confidence == all_results[0].confidence

    def test_no_match_returns_none(self) -> None:
        assert detect_best("not encoded at all!") is None
