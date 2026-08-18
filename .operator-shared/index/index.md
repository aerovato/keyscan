---
description: Main codebase map for Keyscan, a Python CLI that finds exposed API keys in GitHub Gists via LLM classification and provider verification.
read_if: Working anywhere in the codebase, navigating modules, or adding file-type or provider support.
---

# Shared Project Index

## Architecture

- Linear pipeline: `keywords.txt` → `main.py` → `src/gists.py` (search + fetch) → `processing.py` dispatch → `src/classify.py` (LLM) → `src/verify.py` → `src/storage.py`.
- File types are extensible via `src/file_modules/` modules registered in `processing.py`.
- Providers are extensible via `PROVIDERS_TYPE` in `src/verify.py`.
- Config lives in `config.py` (copy from `config.py.example`).

## Project Index

- `main.py` — Entry point. Reads keywords, iterates the search pipeline per keyword, handles top-level errors and interrupts.
- `config.py` — GitHub token, session cookie, LLM base URL and API key. (Copy from `config.py.example`.)
- `config.py.example` — Template for `config.py`.
- `processing.py` — File-type-agnostic preprocessing dispatcher. Maps `GIST_FILE_TYPE` literals to preprocessing and value extraction functions (currently only Dotenv).
- `keywords.txt` — Example keywords file listing common API key environment variable names to search for.
- `prompt.txt` — Classification prompt template read by `src/classify.py`.
- `requirements.txt` — Ditto.
- `opencode.json` — Ditto.

### `src/` — Core pipeline modules

- `__init__.py` — Empty package init.
- `args.py` — CLI argument parsing; `Arguments` dataclass (keywords file, model, file type, output path, delay, scanned DB path).
- `gists.py` — GitHub Gist client. Scrapes gist search pages, fetches gist data with bounded rate-limit retries, filters files by language, returns gist owner and file contents.
- `classify.py` — LLM classification of lines via an OpenAI-compatible endpoint; parses JSON responses into confidence and provider fields. Contains prompt building and `print_err`. Exposes `ClassificationResponse` and `classify_lines`.
- `pipeline.py` — Core orchestration: gist fetching, preprocessing, classification, verification, record saving. Exposes `process_gist` and `search_one_keyword`.
- `storage.py` — File I/O and persistence: directory/file helpers, `save_processing_state` checkpointing, `ScannedDb` dedup, `save_record`, `generate_message`.
- `verify.py` — Provider type definitions (`PROVIDERS_TYPE`), `parse_provider`, per-provider HTTP verifiers, and `verify()` dispatch returning VALID/INVALID/UNKNOWN.

#### `src/file_modules` — File-type preprocessors

- `dotenv.py` — `preprocess_dotenv` (non-comment, non-empty lines) and `get_dotenv_value` (value after `=`).
