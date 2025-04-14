import google.generativeai as genai
from time import sleep
from .model_response import ModelResponse


class GeminiClient:

    # As in API, but without the `gemini-` prefix
    SUPPORTED_VARIANTS = [
        '2.0-flash',
        '2.0-flash-lite',
        '2.0-flash-thinking-exp-01-21',
    ]

    def __init__(self, variant, apiKey):
        if variant not in self.SUPPORTED_VARIANTS:
            raise Exception(f'Unsupported variant: {variant}')

        genai.configure(api_key=apiKey)
        self.model = genai.GenerativeModel(
            f'gemini-{variant}',
            generation_config=genai.GenerationConfig(
                # max_output_tokens=10 if 'thinking' not in variant else 5000,
                temperature=0.1,
            )
        )

    def ask(self, prompt):
        retry = 0
        while True:
            try:
                retry += 1
                response = self.model.generate_content(prompt)
                break
            except Exception as e:
                if '429' in str(e) and retry < 3:
                    sleep(retry * 15)
                    print('Retrying...')
                else:
                    raise
    
        rawResponse = response.to_dict()
        return ModelResponse(
            model=self.model.model_name,
            prompt=prompt,
            rawResponse=rawResponse,
            response=self._getResponseText(rawResponse),
            inputTokens=self._countInputTokens(rawResponse),
            outputTokens=self._countOutputTokens(rawResponse),
        )
    
    def _getResponseText(self, rawResponse):
        return rawResponse['candidates'][0]['content']['parts'][0]['text']
    
    def _countInputTokens(self, rawResponse):
        usageData = rawResponse['usage_metadata']
        return usageData['prompt_token_count']

    def _countOutputTokens(self, rawResponse):
        usageData = rawResponse['usage_metadata']
        return usageData['candidates_token_count']
