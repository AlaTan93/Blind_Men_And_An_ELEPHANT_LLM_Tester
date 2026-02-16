from typing import List

from openai import OpenAI
from src.llm import OpenAIModel

ALLOWED_MODELS = ["gpt-5.2", "gpt-5.1", "gpt-5", "gpt-5-mini", "gpt-5-nano"]


def get_chat_models(api_key: str) -> List[OpenAIModel]:
    client = OpenAI(api_key=api_key)
    models = client.models.list()

    result_list = []

    for model in models.data:
        if ("gpt" in model.id or "o1" in model.id or "o3" in model.id or "o4" in model.id) \
        and ("audio" not in model.id and "transcribe" not in model.id and "realtime" not in model.id \
        and "tts" not in model.id and "preview" not in model.id and "image" not in model.id and "search" not in model.id \
        and "codex" not in model.id and "instruct" not in model.id):
            openai_model = OpenAIModel(
                display_name="",
                id = model.id
            )
            result_list.append(openai_model)

    return result_list


def send_prompt(api_key: str, model_id: str, prompt: str, temperature: float) -> str:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model_id,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or ""