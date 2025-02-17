import os
import json

""" ATRIB_SIST = ["title", "description", "author", "startLocationId", "max_itens",
              "max_turns_easy", "max_turns_normal", "max_turns_hard", "attack", "defense", "life"]
"""
ATRIB_PLAYER = ["startLocationId", "attack", "defense", "life"]
ATRIB_OPCIONAIS = ["max_itens", "max_turns_easy",
                   "max_turns_normal", "max_turns_hard"]


class DataManipulator:
    def __init__(self, path_dataset, filename):
        self.dict_data = self.pegar_JSON(path_dataset, filename)
        # acoes permitidas ao usuario
        self.COMANDOS = ["usar", "pegar", "andar",
                         "mover", "inventario", "ajuda"]

    def pegar_JSON(self, path_dataset, filename):
        path_json = os.path.join(path_dataset, filename)
        with open(path_json, "r") as file:
            data = json.load(file)
            # dados retornados como dict
            # print(f"JSON: {data}\n\n")
            return data

    def get_data_rec(self, args: list):
        """funcao para pegar propriedades de objetos recursivamente"""
        data = self.dict_data
        for arg in args:
            data = data[arg]
        return data

    def get_data(self, arg):
        """funcao para pegar dados normalmente"""
        return self.dict_data[arg]

    def parse_input(self, in_: str):
        """
        Faz parse do input, analisa se comandos estao corretos.
        retorna inteiro para erro ou lista contendo comando ou comando e alvo
        """

        sequencia_str = in_.split(" |,|;")
        tam_seq = len(sequencia_str)
        if tam_seq == 1:
            comando = sequencia_str[0]
            if comando in ["inventario", "ajuda"]:
                return [comando, ""]
            elif comando == "sair":
                exit(0)
            else:
                # comando de 1 palavra errado
                return [-1, -1]
        elif (tam_seq == 2):
            comando = sequencia_str[0]
            if comando in ["usar", "pegar", "andar", "mover"]:
                alvo = sequencia_str[1]
                return [comando, alvo]
            else:
                # comando de 2 palavras errado
                return [-2, -2]
        else:
            # comando de 3 palavras, nao existe
            return [-3, -3]
