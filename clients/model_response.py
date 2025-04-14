class ModelResponse:

    def __init__(
            self, model, prompt, rawResponse,
            responseText=None, inputTokens=None, outputTokens=None
        ):
        self.model = model
        self.prompt = prompt
        self.rawResponse = rawResponse
        self.responseText = responseText
        self.inputTokens = inputTokens
        self.outputTokens = outputTokens
