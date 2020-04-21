try:
    from Akoma.reasoner.BasicReasoner import BasicReasoner
    from Akoma.tokenizer.TokenType import TokenType
except ModuleNotFoundError:
    try:
        from reasoner.BasicReasoner import BasicReasoner
        from tokenizer.TokenType import TokenType
    except ModuleNotFoundError:
        print("error")
        exit(-1)


class OdlukaReasoner(BasicReasoner):

    def start(self):
        body = False
        preface = []
        while self.current_token is not None:
            self.current_token = self.tokenizer.get_next_token()

            if (self.current_token is None):
                break
            if body is False and self.current_token.type <= TokenType.TACKA:
                body = True
                self.akomabuilder.build_preface(preface)
            else:
                preface.append(self.current_token)
            if body:
                self.reason()
