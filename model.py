import os
import json

""" ATRIB_SIST = ["title", "description", "author", "startLocationId", "max_itens",
              "max_turns_easy", "max_turns_normal", "max_turns_hard", "attack", "defense", "life"]
"""
ATRIB_PLAYER = ["startLocationId", "attack", "defense", "life"]
ATRIB_OPCIONAIS = ["max_itens", "max_turns_easy",
                   "max_turns_normal", "max_turns_hard"]
# acoes permitidas ao usuario
COMANDOS = ["usar", "pegar", "andar", "mover", "invetario", "ajuda"]


class DataManipulator:
    def __init__(self, path_dataset, filename):
        self.dict_data = self.pegar_JSON(path_dataset, filename)
        chaves = self.dict_data.keys()

    def pegar_JSON(self, path_dataset, filename):
        path_json = os.path.join(path_dataset, filename)
        with open(path_json, "r") as file:
            data = json.load(file)
            # dados retornados como dict
            print(f"JSON: {data}\n\n")
            return data

    def get_data(self, arg):
        return self.dict_data[str(arg)]
