import os
import json
from view import View
from model import DataManipulator
from controller import Controller


# lista em que se bota atributos do sistema
LISTA_ATR_SIST = ["author", "title", "description", "max_turns"]

# main
if __name__ == "__main__":
    # pegando JSON
    path_dataset = os.getcwd()
    filename = "exemplo.json"
    # modelo pega todos os atributos do JSON
    model = DataManipulator(path_dataset, filename)
    printer = View(model.get_data)
