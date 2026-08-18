# Shared Operator Instructions

## Project Overview

Keyscan is a Python CLI tool that searches public GitHub Gists for accidentally exposed API keys. It uses an LLM (via any OpenAI-compatible endpoint) to classify whether values in gist files look like real API keys, then optionally verifies them against provider endpoints.

Architecture (linear pipeline):

`keywords.txt` → `main.py` (keyword loop) → `src/gists.py` (Gist search + fetch) → `processing.py` dispatch → `src/classify.py` (LLM classification) → `src/verify.py` (provider verification) → `src/storage.py` (JSON records, dedup DB).

Key design decisions:

- File-type extensible: new file types are modules in `src/file_modules/` registered in `processing.py`. Currently only Dotenv.
- Provider extensible: new providers are entries in `PROVIDERS_TYPE` in `src/verify.py`, with an optional verifier in `PROVIDERS_TO_VERIFIER_MAP`.
- Bring-your-own LLM: works with any OpenAI-compatible endpoint; no model-specific logic.
- File-backed dedup: `ScannedDb` tracks scanned gist IDs in a newline-separated text file.
- Configuration via `config.py` (copy from `config.py.example`).

Dependencies: `requests`, `beautifulsoup4`, `openai`.

CLI:

```
python main.py --keywords-file <path> --model <model_name> \
  [--file-type Dotenv] [--output-path ./output] [--delay 5] [--scanned-db ./output/scanned.txt]
```

Output records go to `output/VALID|INVALID|UNKNOWN/` by verification status.

## Rules

- Never commit `config.py` or `output/`; they hold secrets and scan results.
- `config.py` is required at runtime; copy from `config.py.example`.

## Private / Shared Policy

- Shared: project overview, repo rules, and the Project Index.
- Private (`.operator/`): research material under `dont_read/` and any work in progress. Never publish private material.
