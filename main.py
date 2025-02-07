import os
import json


def pegar_JSON(path_dataset, filename):
    path_json = os.path.join(path_dataset, filename)
    with open(path_json, "r") as file:
        data = json.load(file)
        return data


if __name__ == "__main__":
    # pegando JSON
    path_dataset = os.getcwd()
    filename = "data.json"
    data = pegar_JSON(path_dataset, filename)
    # 
