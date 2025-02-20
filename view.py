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

        self.print_with_formatting(f"\tTitulo: {self.title}", "\n\n")
        self.print_with_formatting("")
        self.print_with_formatting(
            f"Escreva 'ajuda' para ver os comandos ou 'sair' para sair do jogo", newline="\n\n")
        self.print_with_formatting(f"Descrição do Jogo: {self.desc}")
        self.print_with_formatting(f"Criado por: {self.author}")
        self.print_with_formatting(f"Local: {local_inicial[0]}", "\n")
        self.print_with_formatting(f"{local_inicial[1]}")

    def print_with_formatting(self, content: str, newline: str = "\n"):
        formatted_str = f"{self.tab}{self.leading}{content}{self.trail}"
        print(formatted_str, end=newline)

    def print_elems(self, elems):
        """
        Funcao de helper pra printar itens de uma lista
        """
        cont = 0
        end = ", "
        for elem in elems:
            cont += 1
            if cont == len(elems):
                end = "\n"
            self.print_with_formatting(elem, newline=end)

    def print_inventario(self, itens: list[str]):
        print("Inventario: ", end=" ")
        self.print_elems(itens)

    def print_olhar(self, **kwargs):
        desc = kwargs.get("desc")
        name = kwargs.get("name")
        itens = kwargs.get("itens", [])
        itens = [item["name"] for item in itens]
        npcs = kwargs.get("npcs", [])

        npcs = [
            f"{npc['name']}: {npc['description']}" for npc in npcs]
        enemies = kwargs.get("enemies", [])
        exits = kwargs.get("exits", [])
        exits = [
            f"{saida['description']}: {saida['direction']} - Inativo: {saida['inactive']}" for saida in exits
        ]

        self.print_with_formatting(f"{name}: {desc}")
        self.print_with_formatting(f"Itens:")
        self.print_elems(itens)
        print()
        self.print_with_formatting(f"Personagens:")
        self.print_elems(npcs)
        print()
        self.print_with_formatting("Saídas: ")
        self.print_elems(exits)
        print()
        self.print_with_formatting(f"Inimigos: {enemies}")

    def print_erro(self, num_erro: int, dict_erro: dict):
        print(dict_erro[num_erro])

    def print_dialogo(self):
        pass
