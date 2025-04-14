from openai import OpenAI, RateLimitError
from time import sleep
from .model_response import ModelResponse


class OpenAIClient:

    # As in API
    SUPPORTED_VARIANTS = [
        'gpt-4o',
        'gpt-4o-mini',
        'o3-mini',
    ]

    def __init__(self, variant, apiKey):
        if variant not in self.SUPPORTED_VARIANTS:
            raise Exception(f'Unsupported variant: {variant}')

        self.modelName = variant
        self.client = OpenAI(
            api_key=apiKey
        )

    def ask(self, prompt):
        retry = 0
        while True:
            try:
                retry += 1

                params = {
                    'temperature': 0.1,
                    # 'max_completion_tokens': 10,
                    'n': 1,
                }
                # o3-mini doesn't support temperature
                # drop token limit beacuse of hidden 'reasoning' tokens
                if self.modelName.startswith('o'):
                    del params['temperature']
                    # del params['max_completion_tokens']

                response = self.client.chat.completions.create(
                    model=self.modelName,
                    messages=[
                        {'role': 'user', 'content': prompt}
                    ],
                    **params
                )
                break
            except RateLimitError as e:
                if retry < 3:
                    sleep(retry * 15)
                    print('Retrying...')
                else:
                    raise

        rawResponse = response.to_dict()
        return ModelResponse(
            model=self.model.model_name,
            prompt=prompt,
            rawResponse=rawResponse,
            responseText=self._getResponseText(rawResponse),
            inputTokens=self._countInputTokens(rawResponse),
            outputTokens=self._countOutputTokens(rawResponse),
        )
    
    def _getResponseText(self, rawResponse):
        return rawResponse['choices'][0]['message']['content']
    
    def _countInputTokens(self, rawResponse):
        usage_data = rawResponse['usage']
        return usage_data['prompt_tokens']

    def _countOutputTokens(self, rawResponse):
        usage_data = rawResponse['usage']
        return usage_data['completion_tokens']
