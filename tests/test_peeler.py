"""
©AngelaMos | 2026
test_peeler.py
"""

from base64_tool.constants import EncodingFormat
from base64_tool.encoders import encode
from base64_tool.peeler import peel


class TestSingleLayer:
    def test_peel_base64(self) -> None:
        encoded = encode(b"Hello World", EncodingFormat.BASE64)
        result = peel(encoded)
        assert result.success is True
        assert len(result.layers) == 1
        assert result.layers[0].format == EncodingFormat.BASE64
        assert result.final_output == b"Hello World"

    def test_peel_hex(self) -> None:
        encoded = encode(b"Hello World", EncodingFormat.HEX)
        result = peel(encoded)
        assert result.success is True
        assert len(result.layers) >= 1
        assert result.final_output == b"Hello World"

    def test_peel_base32(self) -> None:
        encoded = encode(b"Hello World", EncodingFormat.BASE32)
        result = peel(encoded)
        assert result.success is True
        assert len(result.layers) >= 1


class TestMultiLayer:
    def test_base64_then_hex(self) -> None:
        step1 = encode(b"secret payload", EncodingFormat.BASE64)
        step2 = encode(step1.encode("utf-8"), EncodingFormat.HEX)
        result = peel(step2)
        assert result.success is True
        assert len(result.layers) >= 2
        assert b"secret payload" in result.final_output

    def test_base64_double_encoded(self) -> None:
        step1 = encode(b"double layer", EncodingFormat.BASE64)
        step2 = encode(step1.encode("utf-8"), EncodingFormat.BASE64)
        result = peel(step2)
        assert result.success is True
        assert len(result.layers) >= 2


class TestPeelEdgeCases:
    def test_plaintext_no_layers(self) -> None:
        result = peel("just plain text")
        assert result.success is False
        assert len(result.layers) == 0

    def test_max_depth_respected(self) -> None:
        encoded = encode(b"data", EncodingFormat.BASE64)
        result = peel(encoded, max_depth = 0)
        assert len(result.layers) == 0

    def test_empty_string(self) -> None:
        result = peel("")
        assert result.success is False

    def test_layer_metadata_populated(self) -> None:
        encoded = encode(b"test data", EncodingFormat.BASE64)
        result = peel(encoded)
        if result.success and result.layers:
            layer = result.layers[0]
            assert layer.depth == 1
            assert layer.confidence > 0
            assert len(layer.encoded_preview) > 0
            assert len(layer.decoded_preview) > 0
