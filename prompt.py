from typing import List

from openai.types.chat import ChatCompletionMessageParam

from providers import ALL_PROVIDERS


def get_prompt(line: str) -> List[ChatCompletionMessageParam]:
    providers_string = ", ".join(ALL_PROVIDERS)
    system = (
        "You are a highly specialized AI assistant tasked with analyzing a single variable from a .env file. "
        "Your primary task is to determine if the value of the variable contains a potentially valid API key. "
        "Your output must be in a strict JSON format with two keys: `confidence` and `provider`."
        "\n\n"
        "The `confidence` key indicates how confident you are that the value is a potentially valid API key. "
        "The confidence value must be a string value from the following list: "
        '"NONE", "LOW", "MEDIUM", "HIGH".'
        "\n"
        "The `provider` key indicates the provider of the API key. "
        f"The value must be a value from the following list: {providers_string}"
        "\n"
        "A potentially valid API key does not include example values or placeholder values. "
        "A potentially valid API key should be directly usable for authentiating an API request. "
        "Do not overthink."
    )
    user = f"Analyze the following variable:\n{line}\n"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
