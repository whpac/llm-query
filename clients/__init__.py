from .gemini import GeminiClient
from .openai import OpenAIClient
from .llm_client import LLMClient


_MODEL_PREFIXES = {
    'gemini': GeminiClient,
    'openai': OpenAIClient,
}

AVAILABLE_MODELS = []
for prefix, client in _MODEL_PREFIXES.items():
    for variant in client.SUPPORTED_VARIANTS:
        AVAILABLE_MODELS.append(f'{prefix}:{variant}')


def createClient(modelCode: str, apiKey: str) -> LLMClient:
    modelFamily, modelVariant = modelCode.split(':')
    if modelFamily in _MODEL_PREFIXES:
        return _MODEL_PREFIXES[modelFamily](modelVariant, apiKey)
    else:
        raise Exception(f'Unsupported model family: {modelFamily}')
