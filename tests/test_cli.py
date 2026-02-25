"""
©AngelaMos | 2026
test_cli.py
"""

from typer.testing import CliRunner

from base64_tool.cli import app


runner = CliRunner()


class TestEncodeCommand:
    def test_encode_base64(self) -> None:
        result = runner.invoke(app, ["encode", "Hello World"])
        assert result.exit_code == 0
        assert "SGVsbG8gV29ybGQ=" in result.output

    def test_encode_hex(self) -> None:
        result = runner.invoke(
            app,
            ["encode",
             "Hello",
             "--format",
             "hex"],
        )
        assert result.exit_code == 0
        assert "48656c6c6f" in result.output

    def test_encode_base32(self) -> None:
        result = runner.invoke(
            app,
            ["encode",
             "Hello",
             "--format",
             "base32"],
        )
        assert result.exit_code == 0
        assert "JBSWY3DP" in result.output

    def test_encode_url(self) -> None:
        result = runner.invoke(
            app,
            ["encode",
             "hello world&test",
             "--format",
             "url"],
        )
        assert result.exit_code == 0
        assert "%20" in result.output or "hello" in result.output

    def test_encode_empty_string(self) -> None:
        result = runner.invoke(app, ["encode", ""])
        assert result.exit_code == 0


class TestDecodeCommand:
    def test_decode_base64(self) -> None:
        result = runner.invoke(
            app,
            ["decode",
             "SGVsbG8gV29ybGQ="],
        )
        assert result.exit_code == 0
        assert "Hello World" in result.output

    def test_decode_hex(self) -> None:
        result = runner.invoke(
            app,
            ["decode",
             "48656c6c6f",
             "--format",
             "hex"],
        )
        assert result.exit_code == 0
        assert "Hello" in result.output

    def test_decode_invalid_base64(self) -> None:
        result = runner.invoke(
            app,
            ["decode",
             "!!!invalid!!!"],
        )
        assert result.exit_code != 0


class TestDetectCommand:
    def test_detect_base64(self) -> None:
        result = runner.invoke(
            app,
            ["detect",
             "SGVsbG8gV29ybGQ="],
        )
        assert result.exit_code == 0
        assert "base64" in result.output.lower()

    def test_detect_hex(self) -> None:
        result = runner.invoke(
            app,
            ["detect",
             "48656c6c6f20576f726c64"],
        )
        assert result.exit_code == 0
        assert "hex" in result.output.lower()

    def test_detect_no_match(self) -> None:
        result = runner.invoke(
            app,
            ["detect",
             "just plain text"],
        )
        assert result.exit_code == 0
        assert "no encoding" in result.output.lower()


class TestPeelCommand:
    def test_peel_single_layer(self) -> None:
        result = runner.invoke(
            app,
            ["peel",
             "SGVsbG8gV29ybGQ="],
        )
        assert result.exit_code == 0
        assert "layer" in result.output.lower()

    def test_peel_no_encoding(self) -> None:
        result = runner.invoke(
            app,
            ["peel",
             "hello world"],
        )
        assert result.exit_code == 0


class TestChainCommand:
    def test_chain_single_step(self) -> None:
        result = runner.invoke(
            app,
            ["chain",
             "Hello",
             "--steps",
             "base64"],
        )
        assert result.exit_code == 0
        assert "SGVsbG8=" in result.output

    def test_chain_multiple_steps(self) -> None:
        result = runner.invoke(
            app,
            ["chain",
             "Hi",
             "--steps",
             "base64,hex"],
        )
        assert result.exit_code == 0

    def test_chain_invalid_format(self) -> None:
        result = runner.invoke(
            app,
            ["chain",
             "test",
             "--steps",
             "fake"],
        )
        assert result.exit_code != 0


class TestVersionFlag:
    def test_version_output(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "b64tool" in result.output
