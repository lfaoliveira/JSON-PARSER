import os
import json
from view import Printer
from model import DataManipulator
from controller import Controller


def pegar_JSON(path_dataset, filename):
    path_json = os.path.join(path_dataset, filename)
    with open(path_json, "r") as file:
        data = json.load(file)
        # dados retornados como dict
        return data


# main
if __name__ == "__main__":
    # pegando JSON
    path_dataset = os.getcwd()
    filename = "exemplo.json"
    data = pegar_JSON(path_dataset, filename)
    print(f"JSON: {data}\n\n")
    printer = Printer(data)
    model = DataManipulator(data)
