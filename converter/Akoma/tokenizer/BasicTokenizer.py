try:
    from Akoma.tokenizer.patterns import recognize_pattern
except ModuleNotFoundError:
    from tokenizer.patterns import recognize_pattern


class BasicTokenizer():

    def __init__(self, source):
        self.source = source
        self.generator = None

    def token_generator(self):
        for child in self.source.split("\n"):

            current_token = recognize_pattern(child)
            if current_token == False:
                continue
            # print(self.current_token.type,self.current_token.value)
            yield current_token

    def get_next_token(self):
        if self.generator is None:
            self.generator = self.token_generator()
        try:
            return next(self.generator)
        except StopIteration:
            return None
