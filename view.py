from model import DataManipulator


class View:
    def __init__(self, model: DataManipulator):
        # dados
        self.author = model.get_data("author")
        self.title = model.get_data("title")
        self.desc = model.get_data("description")
        self.startLocationId = model.get_data("startLocationId")
        self.attack = model.get_data("attack")
        self.defense = model.get_data("defense")
        self.life = model.get_data("life")
        # variaveis de texto
        self.tab = " "*3
        self.leading = "# "
        self.trail = " #"

    def print_inicial(self, local_inicial: list[str]):
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
        self.ligar_str(self.tab, self.leading, str)

        str = f"Local: {local_inicial[0]}"
        self.ligar_str("\n" + self.tab, self.leading, str, nl="\n")

        str = f"{local_inicial[1]}"
        self.ligar_str(self.tab, self.leading, str)

    def ligar_str(self, tab="", leading="", conteudo="", trail="", nl=""):
        str = f"{tab}{leading}{conteudo}{trail}{nl}"
        print(str)

    def print_erro(self, num_erro):
        if num_erro == -1 or num_erro == -2:
            print("Comando inexistente")
        else:
            print("Palavras sem sentido!")

    def print_dialogo(self):
        pass
