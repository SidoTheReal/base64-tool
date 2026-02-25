"""
©AngelaMos | 2026
utils.py
"""

import sys
from pathlib import Path

import typer


def resolve_input_bytes(
    data: str | None,
    file: Path | None,
) -> bytes:
    if file is not None:
        if not file.exists():
            raise typer.BadParameter(f"File not found: {file}")
        return file.read_bytes()
    if data is not None:
        return data.encode("utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.buffer.read()
    raise typer.BadParameter(
        "No input provided. Pass an argument, use --file, or pipe stdin."
    )


def resolve_input_text(
    data: str | None,
    file: Path | None,
) -> str:
    if file is not None:
        if not file.exists():
            raise typer.BadParameter(f"File not found: {file}")
        return file.read_text("utf-8").strip()
    if data is not None:
        return data.strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    raise typer.BadParameter(
        "No input provided. Pass an argument, use --file, or pipe stdin."
    )


def truncate(text: str, length: int = 72) -> str:
    if len(text) <= length:
        return text
    return text[: length] + "..."


def safe_bytes_preview(data: bytes, length: int = 72) -> str:
    try:
        text = data.decode("utf-8")
        return truncate(text, length)
    except (UnicodeDecodeError, ValueError):
        return truncate(data.hex(), length)


def is_printable_text(data: bytes, threshold: float = 0.8) -> bool:
    try:
        text = data.decode("utf-8")
    except (UnicodeDecodeError, ValueError):
        return False
    if not text:
        return False
    printable_count = sum(1 for c in text if c.isprintable() or c in "\n\r\t")
    return (printable_count / len(text)) >= threshold
