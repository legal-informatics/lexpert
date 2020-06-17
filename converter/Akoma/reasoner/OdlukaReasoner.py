try:
    from Akoma.reasoner.BasicReasoner import BasicReasoner
    from Akoma.tokenizer.TokenType import TokenType
except ModuleNotFoundError:
    try:
        from reasoner.BasicReasoner import BasicReasoner
        from tokenizer.TokenType import TokenType
        from utilities import utilities
    except ModuleNotFoundError as e:
        print(e)
        print("error")
        exit(-1)


class OdlukaReasoner(BasicReasoner):

    def start(self, meta=None):
        body = False
        preface = []
        while self.current_token is not None:
            self.current_token = self.tokenizer.get_next_token()

            if (self.current_token is None):
                break
            if body is False and self.current_token.type <= TokenType.TACKA:
                DOC_TYPE = utilities.get_doc_type("".join([s.value for s in self.preface]))
                if meta is not None:
                    meta.change_subtype_url(DOC_TYPE)
                body = True
                self.akomabuilder.build_preface(preface)
            else:
                preface.append(self.current_token)
            if body:
                self.reason()
