try:
    from Akoma.tokenizer.patterns import recognize_pattern, FoundToken
    from Akoma.tokenizer.TokenType import TokenType
    from Akoma.tokenizer.BasicTokenizer import BasicTokenizer
except ModuleNotFoundError:
    try:
        from tokenizer.patterns import recognize_pattern, FoundToken,eng_tags
        from tokenizer.TokenType import TokenType
        from tokenizer.BasicTokenizer import BasicTokenizer
    except ModuleNotFoundError:
        print("Error")
        exit(-1)


class HTMLTokenizer(BasicTokenizer):

    # def __init__(self, source):
    #     super(source)

    def token_generator(self):
        for child in self.source:
            for child2 in child:
                # print(child2.text)
                current_token = recognize_pattern(child2.text)
                if child2.tag == "table" or child2.tag == "img":
                    yield self.handle_table_img(child2)
                if current_token == False:
                    continue
                # print(self.current_token.type,self.current_token.value)
                yield current_token

            current_token = recognize_pattern(child.text)
            if child.tag == "table" or child.tag == "img":
                yield self.handle_table_img(child)
            if current_token == False:
                continue
            # print(self.current_token.type,self.current_token.value)
            yield current_token

    def handle_table_img(self, el):
        retval = FoundToken(TokenType.STAV, "став", "Special value.", None, special=el) #TODO ANDRIJA OVDE SE DODAJE 'STAV' na srpskom
        # print(el.tag)
        return retval
