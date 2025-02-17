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
        self.tab = " " * 3
        self.leading = ""
        self.trail = ""

    def print_inicial(self, local_inicial: list[str]):
        max_width = 100
        separator = "#" * 30
        print(self.tab + separator)

        self.print_with_formatting(f"Titulo: {self.title}", "\n\n")
        self.print_with_formatting("#")
        self.print_with_formatting("#")
        self.print_with_formatting(f"Escreva 'ajuda' para ver os comandos ")
        self.print_with_formatting(f"Descrição do Jogo: {self.desc}")
        self.print_with_formatting(f"Criado por: {self.author}")
        self.print_with_formatting(f"Local: {local_inicial[0]}", "\n")
        self.print_with_formatting(f"{local_inicial[1]}")

    def print_with_formatting(self, content: str, newline: str = ""):
        formatted_str = f"{self.tab}{self.leading}{content}{self.trail}{newline}"
        print(formatted_str)

    def print_erro(self, num_erro: int, dict_erro: dict):
        print(dict_erro[num_erro])

    def print_dialogo(self):
        pass
