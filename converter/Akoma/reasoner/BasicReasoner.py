

try:
    from Akoma.tokenizer.TokenType import TokenType
    # from Akoma.tokenizer import patterns
    from Akoma.named_enitity_recognition.ner import do_ner_on_sentences
    from Akoma.convertToLatin.Convert import convert
except ModuleNotFoundError:
    try:
        # from tokenizer import patterns
        from tokenizer.TokenType import TokenType
        from named_enitity_recognition.ner import do_ner_on_sentences
        from convertToLatin.Convert import convert

    except ModuleNotFoundError:
        print("Error")
        exit(-1)


class BasicReasoner():
    def __init__(self, tokenizer, akomabuilder):
        self.tokenizer = tokenizer
        self.akomabuilder = akomabuilder
        self.current_token = False
        self.current_hierarchy = {
            TokenType.DEO: 0,
            TokenType.GLAVA: 0,
            TokenType.ODELJAK: 0,
            TokenType.PODODELJAK: 0,
            TokenType.CLAN: 0,
            TokenType.STAV: 0,
            TokenType.TACKA: 0,
            TokenType.PODTACKA: 0,
            TokenType.ALINEJA: 0}
        self.processed = []
        self.preface = []
        self.stop = False

    def sanity(self, identification):
        if identification == 'gla10-clan72-stav6':
            print("GOT HERE")

        if identification in self.processed:
            return "!STOP!"
        else:
            self.processed.append(identification)
            return identification

    def start(self):
        body = False
        self.preface = []

        while self.current_token is not None:

            self.current_token = self.tokenizer.get_next_token()

            if self.current_token is None:
                self.processed = []
                break
            # if False and body and self.current_token is not None and self.current_token.value is not None and len(
            #         self.current_token.value) > 10:
            #     val = "".join([convert(s) for s in self.current_token.value])
            #     ner = do_ner_on_sentence(val)
            #     print(val)
            #     print()
            #     print(ner)
            if body is False and self.current_token.type <= TokenType.CLAN:
                body = True
                self.akomabuilder.build_preface(self.preface)
            else:
                self.preface.append(self.current_token)
            if body:
                try:
                    self.reason()
                except NameError as e:
                    break

    def add_odeljak(self):
        wid = self.sanity(self.get_identification(self.current_token))
        next_token = self.tokenizer.get_next_token()
        if next_token.type == TokenType.TACKA:
            self.current_token.type = TokenType.TACKA
            self.current_token.name = "point"
            self.akomabuilder.add_token(self.current_token, wid)
        self.current_token = next_token
        self.reason()

    def reason(self):
        if self.current_token is None:
            return
        if self.current_token in self.preface[1::-1]:
            self.stop = True
        if self.current_token.value is not None:
            if len(self.preface)>0:
                if self.current_token.value == self.preface[0].value:
                    raise NameError("Preface repeating itself")
        if self.current_token.type == TokenType.DEO and self.current_token.value is None:
            self.deo_glava_find_title()
        elif self.current_token.type == TokenType.ODELJAK:
            self.add_odeljak()
        elif self.current_token.type == TokenType.PODODELJAK:
            self.add_odeljak()
        elif self.current_token.type == TokenType.GLAVA and self.current_token.value is None:
            self.deo_glava_find_title()
        elif self.current_token.type == TokenType.STAV and self.current_token.value[-1:] != "." and self.current_token.value[-1:] != ":" and self.current_token.value[-1:] != ",":
            self.title_find_clan()
        else:
            self.akomabuilder.add_token(self.current_token, self.sanity(self.get_identification(self.current_token)))
            if self.current_token.type == TokenType.STAV and self.current_token.value[-1:] == ":":
                self.expect_tacke()

    def deo_glava_find_title(self):
        glava = self.current_token
        self.current_token = self.tokenizer.get_next_token()
        wid = self.sanity(self.get_identification(glava))
        if self.current_token.type != TokenType.STAV:
            # print("WARNING - GLAVA NEMA NASLOV")
            self.akomabuilder.add_token(glava, wid)
            self.reason()
        elif self.current_token.value[-1:] == ".":
            # print("WARNING - NASLOV GLAVE NE SME DA IMA TACKU NA KRAJU")
            self.akomabuilder.add_token(glava, wid)
            self.reason()
        else:
            glava.value = self.current_token.value
            self.akomabuilder.add_token(glava, wid)
        # self.reason()

    def title_find_clan(self):
        naslov = self.current_token
        self.current_token = self.tokenizer.get_next_token()
        if self.current_token is None:
            return
        if self.current_token.type != TokenType.CLAN:
            # print("WARNING - NEMA CLANA ISPOD NASLOVA")
            wid = self.sanity(self.get_identification(naslov))
            self.akomabuilder.add_token(naslov, wid)
            self.reason()  # deal with this unknown element
            # print(self.current_hierarchy)
            # print(naslov.value)
        else:
            self.current_token.value = naslov.value
            self.akomabuilder.add_token(self.current_token, self.sanity(self.get_identification(self.current_token)))

    def expect_tacke(self):
        # print("TACKA?")
        while self.current_token is not None:
            self.current_token = self.tokenizer.get_next_token()
            if self.current_token is None or self.stop:
                break
            elif self.current_token.type == TokenType.ODELJAK:
                #if self.current_token.type == TokenType.ODELJAK:
                    #self.current_token.type = TokenType.TACKA
                    #self.current_token.name = "тачка"
                self.reason()
            # elif self.current_token.type <= TokenType.STAV:
            #     self.reason()
            else:
                self.reason()

    def get_identification(self, token):
        if token.number is None:
            self.current_hierarchy[token.type] += 1
        elif token.number2 is not None:
            self.current_hierarchy[token.type] = token.number2
        else:
            self.current_hierarchy[token.type] = token.number

        for i in range(TokenType.ALINEJA, token.type, -1):
            if i == TokenType.CLAN:
                continue
            self.current_hierarchy[i] = 0

        # if token.type+1 != TokenType.CLAN and token.type != TokenType.ALINEJA:
        #   self.current_hierarchy[token.type+1] = 0

        values = ["deo", "gla", "od", "podod", "clan", "stav", "tac", "podtac", "ali"]
        retval = ""
        for i in range(TokenType.DEO, TokenType.ALINEJA + 1):
            if token.type < i:
                break
            if self.current_hierarchy[i] == 0:
                continue

            retval += values[i] + str(self.current_hierarchy[i]) + "-"

        return retval[:-1]
