import pathlib
from typing import List

from openai.types.chat import ChatCompletionMessageParam

from src.providers import ALL_PROVIDERS

PROMPT_PATH = pathlib.Path(__file__).resolve().parent.parent / "prompt.txt"


def get_prompt(line: str) -> List[ChatCompletionMessageParam]:
    providers_string = ", ".join(ALL_PROVIDERS)
    system_template = PROMPT_PATH.read_text(encoding="utf-8")
    system = system_template.replace("{providers_string}", providers_string)
    user = f"Analyze the following variable:\n{line}\n"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
