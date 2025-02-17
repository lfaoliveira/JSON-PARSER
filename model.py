import os
import json
import re

ATRIB_PLAYER = ["startLocationId", "attack", "defense", "life"]
ATRIB_OPCIONAIS = ["max_itens", "max_turns_easy",
                   "max_turns_normal", "max_turns_hard"]


class DataManipulator:
    def __init__(self, path_dataset, filename):
        self.dict_data = self.pegar_JSON(path_dataset, filename)
        # acoes permitidas ao usuario
        self.COMANDOS = ["usar", "olhar", "pegar", "andar",
                         "mover", "inventario", "ajuda"]

        self.itens = []

        for atrib in ATRIB_OPCIONAIS:
            if atrib in self.dict_data.keys():
                self.__setattr__(atrib, self.dict_data[atrib])

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

        sequencia_str = re.split(r"\s|;|,", in_)
        tam_seq = len(sequencia_str)
        if tam_seq == 1:
            comando = sequencia_str[0]
            if comando in ["olhar", "inventario", "ajuda"]:
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

    def add_inventario(self, alvo):
        """
        Adiciona item ao inventario com base em max_itens
        """
        if self.__getattribute__("max_itens") is None:
            self.itens.append(alvo)
        else:
            if len(self.itens) < self.max_itens:
                self.itens.append(alvo)
            else:
                return False
        return True
