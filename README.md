<p align="center">
  <img src="https://raw.githubusercontent.com/aerovato/keyscan/main/.github/README/banner.jpg" alt="Keyscan Banner" />
</p>

# Keyscan

Keyscan: LLM-powered API key scanner.

Keyscan searches public GitHub Gists for exposed API keys and helps surface potential exposures for further review. It uses GitHub's web search pages to locate candidate gists, fetches gist contents via the GitHub API, and calls an OpenAI-compatible chat completions endpoint to classify whether a value looks like an API key. When a likely exposure is found, the project saves a structured record and prepares a user-facing message to notify the gist owner.

This repository is intended as a research / defensive tool to help users find and remediate accidentally exposed credentials. Do not use Keyscan to access, exfiltrate, or otherwise misuse credentials that do not belong to you. See the terms of use below.

## Features

- Scan entire lists of keywords.
- Bring your own LLM model and customizable prompts for classification.
- Configurable file types.
- Optional GitHub token support for increased rate limits.
- Verification of discovered values against provider endpoints when possible.
- Structured output saving for manual review.

## Installation

1. Clone the repository:

```sh
git clone https://github.com/aerovato/keyscan.git
cd keyscan

# OR, if project directory already created:
git clone https://github.com/aerovato/keyscan.git .
```

2. (Recommended): Create and activate a virtual environment:

```sh
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```sh
pip install -r requirements.txt
```

4. Configure application settings. Copy `config.py.example` to `config.py` and update values as needed.

```python
GITHUB_TOKEN = "ghp_..." # GitHub Token for increased API rate limits
GITHUB_SESSION_COOKIE = "..." # Optional: GitHub session cookie for HTML requests

LLM_BASE_URL = "http://localhost:1234/v1" # Required: Base URL for OpenAI compatible endpoint
LLM_API_KEY = "API_KEY_HERE" # Change to API key if authentication needed
```

5. Ensure that your OpenAI-compatible endpoint is reachable from this machine and that you have configured `config.py` with `LLM_BASE_URL` (and optionally `LLM_API_KEY`).

## Usage

Prepare a newline separated keywords file with terms to search for. An example file is provided in `keywords.txt`.

Configure an OpenAI-compatible endpoint. Provide the base URL and API key (if required) in `config.py`. This project works with any API that implements the OpenAI chat completions protocol (e.g., LM Studio, Llama.cpp, vLLM, self-hosted gateways, etc.).

Run the scanner from the repository root:

```sh
python main.py --keywords-file keywords.txt --model qwen3:1.7b
```

Optional arguments:

- `--file-type`: File language to filter in Gist search results. Default: `Dotenv` (i.e. the script only searches for `.env` style files).
- `--output-path`: Directory to save outputs. Default: `./output`
- `--delay`: Delay in seconds between HTML gist search page requests. Default: 5 seconds.
- `--scanned-db`: Path to a newline-separated file used to record already scanned gist IDs. Default: `./output/scanned.txt`

### Output

When potential exposures are detected, Keyscan will write JSON records into the `output/` directory. Records are organized by verification result using subfolders:

- `output/VALID/`: Verified live API keys.
- `output/INVALID/`: High confidence but seemingly invalid API keys. Saved for manual verification. It's possible that the LLM misclassified the API key or the API endpoint is not the typical endpoint.
- `output/UNKNOWN/`: High confidence but unable to be verified.

## Processing Pipeline

1. Searching: The tool uses GitHub Gist's web search pages to find gists containing the given keyword and filters results by file type.
2. Fetching: For each discovered gist, the tool fetches gist data using the ID and the GitHub Gist API.
3. Preprocessing: File contents are preprocessed to extract candidate text strings. In the case of `Dotenv` files, the file is split into lines with empty lines and comments removed.
4. Classification: Each candidate line is sent to your configured OpenAI-compatible endpoint for classification. The model outputs two values: `confidence` and `provider`.
5. Verification: When a potential key is found, Keyscan attempts to verify the key by calling a provider-specific endpoint.
6. Recording: Records deemed interesting are saved for manual verification and notification.

## Extending and Customizing

#### Prompt Customization

Tweak classification behavior by editing the system prompt in `prompt.txt`.

#### Adding File Types

Add support for additional file types by extending `processing.py` and adding a new helper module in `file_modules/` that implements preprocessing and value extraction functions for the file type.

#### Adding Additional Providers

Add additional provider identifiers in `verify.py` and an optional verification function in the same file.

## Terms of Usage

Keyscan may discover credentials that grant access to private services and accounts. Because of this, a strict terms of usage must be followed while using the Keyscan software. All users must agree that

- The author provides Keyscan for the sole purpose of education and societal improvement.
- Keyscan may only be used for defensive and educational purposes only.
- Users may not use discovered keys to access or misuse third-party accounts or services.
- Users will notify owners as soon as they find exposed API keys.
- Users will holds themselves solely responsible for all outcomes arising from the usage of the software.
- Users will follow GitHub's terms of service and all applicable local regulations.

## License

Keyscan is provided under GPLv3. By downloading or using this software,

- Users agree that they may not modify the software for malicious use.
- Users agree that they will only use the provided software for defensive and educational purposes only.
- Users agree that the author will not be held responsible for any outcomes arising from usage of the software.
