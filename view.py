# import

class View:
    def __init__(self, data):
        self.author = data["author"]
        self.title = data["title"]
        self.desc = data["description"]
        self.tab = "   "
        self.leading = "# "
        self.trail = " #"

    def print_inicial(self):
        max_width = 100
        str = "#"*30
        print(str)

        str = f"Titulo: {self.title}"
        self.ligar_str(self.tab, self.leading, str, self.trail, nl="\n\n")
        self.ligar_str(tab=self.tab, conteudo="#")
        self.ligar_str(tab=self.tab, conteudo="#")

        str = f"Descrição: {self.desc}"

        self.ligar_str(self.tab, self.leading, str, self.trail)

        str = f"Criado por: {self.author}"
        self.ligar_str(self.tab, self.leading, str, self.trail)

    def ligar_str(self, tab="", leading="", conteudo="", trail="", nl=""):
        str = f"{tab}{leading}{conteudo}{trail}{nl}"
        print(str)

    def print_dialogo(self):
        pass
