# import

class Printer:
    def __init__(self, data):
        self.author = data["author"]
        self.title = data["title"]
        self.desc = data["description"]

        tab = "   "
        str = tab + "#"*30
        print(str, "\n")
        str = tab + f"Titulo: {self.title}\n\n"
        print(str)
        str = tab + f"Descrição: {self.desc}"
        print(str)
        str = f"{tab}Autor: {self.author}              Criado por Mateus e Luis"
        print(str)

    def print_dialogo(self):
        pass
