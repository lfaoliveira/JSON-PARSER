import os
import json


class DataManipulator:
    def __init__(self, path_dataset, filename):
        self.dict_data = self.pegar_JSON(path_dataset, filename)

    def get_data(self):
        return self.dict_data

    def pegar_JSON(self, path_dataset, filename):
        path_json = os.path.join(path_dataset, filename)
        with open(path_json, "r") as file:
            data = json.load(file)
            # dados retornados como dict
            print(f"JSON: {data}\n\n")
            return data
