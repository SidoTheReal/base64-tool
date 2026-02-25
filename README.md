# b64tool — Multi-format encoder/decoder with recursive layer peeling

A security-focused CLI for encoding/decoding **Base64, Base64URL, Base32, Hex, and URL encoding** — with **confidence-based auto-detection** and a **peel** command that recursively strips stacked encoding layers (the exact trick used in payload obfuscation and WAF bypass chains).

> **Important:** Encoding is not encryption. If you can reverse it without a secret key, it’s not security.

---

## Why this exists

In real security work you constantly meet encoded data:

- JWT parts are **Base64URL**
- certificates and blobs are **Base64**
- packet captures and malware configs show up as **hex**
- web payloads and params use **URL encoding**
- attackers stack formats to hide intent (**base64 → hex → url**, etc.)

`b64tool` is built to **decode like an analyst**: detect the most likely format, decode it, then check if the output is *also encoded*, and keep going (with sane limits).

---

## Key features

### Clean CLI design
- Subcommands: `encode`, `decode`, `detect`, `peel`, `chain`
- Strong typing via `EncodingFormat` enum (Typer auto-validates choices)
- Helpful `--help` output and clear defaults

### Helpful error messages
- Invalid formats / bad parameters raise `typer.BadParameter` (clean CLI errors)
- Decode failures are handled as values (`try_decode() -> None`) inside the pipeline
- Crashes don’t dump locals (`pretty_exceptions_show_locals=False`)

### Input from **string OR file OR stdin**
- `--file path` reads from disk
- bare argument reads from CLI
- if stdin is piped, it reads from stdin (Unix-friendly)

### Output to **stdout** (pipeline-safe)
- When piped: raw output to stdout
- When interactive: Rich panels/tables to **stderr**, so you can safely do:
  ```bash
  echo "SGVsbG8=" | b64tool decode | other_tool

  ### Recursive layer peeling (the "star" feature)

-   `peel` iteratively:

    -   detects best format (confidence scoring)

    -   decodes

    -   repeats until it hits non-text/binary or falls below threshold

-   Hard cap to avoid pathological inputs (`PEEL_MAX_DEPTH`)

### Tests

-   `tests/` contains **78 tests** across modules (encoders, detection, peeling, CLI behavior)

### Proper project structure

-   `src/` layout

-   Pure-function core modules

-   Single-responsibility modules with a clean dependency DAG (no circular imports)

* * * * *

Quick start
-----------

### Requirements

-   **Python 3.14+** (Python 3.14 released Oct 7, 2025).

-   `uv` package manager

-   Basic comfort with CLI + piping

### Install & run (from GitHub)

### Clone
```bash
git clone https://github.com/SidoTheReal/base64-tool.git
cd base64-tool
```

### Install dependencies
```bash
uv sync
```

### Run the CLI
```bash
uv run b64tool --help
```


## Usage
### Encode / decode
```bash
uv run b64tool encode "Hello World"
# SGVsbG8gV29ybGQ=

uv run b64tool decode "SGVsbG8gV29ybGQ="
# Hello World
```
### Detect (confidence scoring)
```bash
uv run b64tool detect "SGVsbG8gV29ybGQ="
# base64  0.95  preview: "Hello World"
```

### Peel multi-layer encoding
```bash
uv run b64tool peel "5957786c636e516f4a33687a63796370"
# hex → base64 → alert('xss')
```
### Chain encodings (build obfuscation)
```bash
uv run b64tool chain "alert('xss')" --steps base64,hex
```
### File input
```bash
uv run b64tool decode --file encoded_payload.txt
uv run b64tool peel --file suspicious_blob.txt
```
### Pipe input
```bash
echo "SGVsbG8=" | uv run b64tool decode
cat encoded_payload.txt | uv run b64tool peel
```
Supported formats
-----------------

-   `base64` (RFC 4648 strict decoding)

-   `base64url` (JWT-style `-` and `_`)

-   `base32`

-   `hex` (with common separators stripped: spaces/`:`/`-`/`.`)

-   `url` (percent encoding; form-mode supported internally)

* * * * *

Architecture (how it stays maintainable)
----------------------------------------

This project is a **directed acyclic graph (DAG)** of modules:

-   `constants.py` + `utils.py` sit at the bottom (no internal deps)

-   Core logic modules depend *downward* only

-   `cli.py` sits at the top wiring input/output to the pipeline

### Module roles (single responsibility)

-   `encoders.py`: pure encode/decode functions + registry dispatch

-   `detector.py`: heuristics + confidence scoring + decode validation

-   `peeler.py`: iterative "onion peeling" orchestration (bounded depth)

-   `formatter.py`: Rich output (stderr) + pipeline-safe stdout behavior

-   `cli.py`: Typer commands and argument validation

-   `utils.py`: resolve input from arg/file/stdin, safe previews, helpers

### Why this design matters

If you add a new encoding:

-   implement encode/decode in `encoders.py`

-   implement scorer in `detector.py`

-   register both\
    ...and **everything else stays unchanged**.

* * * * *

Why Base64 exists (and what it's for)
-------------------------------------

Base64 exists to represent **binary data using printable ASCII** so it can safely travel through systems that expect text:

-   email/MIME bodies and attachments

-   JSON/XML/text-based protocols

-   copy/paste safe transfer

Tradeoff: **~33% size overhead** (3 bytes → 4 chars).

* * * * *

Security misconceptions (this is where people get wrecked)
----------------------------------------------------------

### Base64 is not encryption

-   No secret key

-   Reversible by anyone

-   "Base64-encoded secrets" are **plaintext secrets with extra steps**

If your security depends on Base64, your security is imaginary.

* * * * *

Where attackers use encodings
-----------------------------

-   **Payload obfuscation**: multi-layer stacks to hide signatures from naive scanning

-   **WAF bypass**: double URL encoding (`%253C...`) so filters decode once and miss intent

-   **C2 / exfil**:

    -   Base64 blobs in HTTP bodies/headers

    -   Hex in parameters that look "normal"

    -   Encoded chunks embedded in logs/telemetry-like traffic

`peel` exists because real malware and real web attacks routinely do this layering.

* * * * *

Limitations 
-----------------------

-   Detection is **heuristic**. Some strings match multiple formats (e.g., hex-like text can look Base64-valid).

-   `peel` stops when:

    -   confidence drops below threshold

    -   decoding fails

    -   decoded bytes aren't valid UTF-8 (likely hit binary)

-   This tool does **not** decrypt, crack, or break crypto. It only handles encodings.

* * * * *

Project structure
-----------------
## Project Structure

```text
base64-tool/
├── src/
│   └── base64_tool/
│       ├── cli.py          # Typer commands (encode, decode, detect, peel, chain)
│       ├── constants.py    # Enums, thresholds, character sets
│       ├── encoders.py     # Pure encode/decode functions + registry
│       ├── detector.py     # Confidence-based format detection
│       ├── peeler.py       # Iterative multi-layer decoding engine
│       ├── formatter.py    # Rich output + pipeline-safe stdout handling
│       └── utils.py        # Input resolution, text helpers
├── tests/                  # 78 tests across all modules
├── pyproject.toml          # Python 3.14+, typer, rich, pytest
└── Justfile                # Task runner shortcuts
```

## Running tests 
```bash
uv run pytest
```
(If you wired `just`: `just test`)

* * * * *

Future improvements
-------------------

-   Add more formats (e.g., gzip+base64 "blobs", JWT helpers, quoted-printable)

-   Smarter stopping rules for peel on binary outputs (save to file automatically)

-   Optional `--json` output for SIEM/tooling integration

-   More adversarial test corpora (real-world malware/WAF samples)
