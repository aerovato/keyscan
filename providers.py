from typing import Literal, Set, get_args


PROVIDERS_TYPE = Literal[
    "openai",
    "anthropic",
    "google",
    "gemini",
    "grok",
    "xai",
    "groq",
    "deepseek",
    "mistral",
    "cohere",
    "black_forest_labs",
    "together",
    "perplexity",
    "openrouter",
    "replicate",
    "fireworks",
    "deepinfra",
    "azure",
    "azure_openai",
    "aws",
    "bedrock",
    "aws_bedrock",
    "huggingface",
    "stability_ai",
    "nvidia",
    "github",
    "copilot",
    "other",
]
ALL_PROVIDERS: Set[PROVIDERS_TYPE] = set(get_args(PROVIDERS_TYPE))


def parse_provider(providers: str | None) -> PROVIDERS_TYPE | None:
    if providers in ALL_PROVIDERS:
        return providers
    return None
