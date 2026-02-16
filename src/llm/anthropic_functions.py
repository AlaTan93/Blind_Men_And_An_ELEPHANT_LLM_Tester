from typing import List

from anthropic import Anthropic
from src.llm import ClaudeModel


def get_chat_models(api_key: str) -> List[ClaudeModel]:
    client = Anthropic(
        api_key=api_key,
    )

    page = client.models.list()
    result_list = []

    for i in range(len(page.data)):
        claude_model = ClaudeModel(
            display_name = page.data[i].display_name,
            id = page.data[i].id
        )
        result_list.append(claude_model)

    return result_list


def send_prompt(api_key: str, model_id: str, prompt: str, temperature: float) -> str:
    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model_id,
        max_tokens=4096,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text # type: ignore