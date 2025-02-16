# import

class View:
    def __init__(self, data):
        # dados
        self.author = data["author"]
        self.title = data["title"]
        self.desc = data["description"]
        self.startLocationId = data["startLocationId"]
        self.attack = data["attack"]
        self.defense = data["defense"]
        self.life = data["life"]
        # variaveis de texto
        self.tab = " "*3
        self.leading = "# "
        self.trail = " #"

        self.print_inicial()

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
