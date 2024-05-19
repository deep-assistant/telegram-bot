import tiktoken


class TokenizeService:
    encoding = tiktoken.encoding_for_model("gpt-4")

    def is_available_context(self, max_tokens, message: str):
        tokens_count = len(self.encoding.encode(message))

        return tokens_count < max_tokens


tokenizeService = TokenizeService()
