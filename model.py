import os
import json
import re

ATRIB_PLAYER = ["startLocationId", "attack", "defense", "life"]
ATRIB_OPCIONAIS = ["max_itens", "max_turns_easy",
                   "max_turns_normal", "max_turns_hard"]


class DataError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InventoryError(DataError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InteractionError(DataError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MoveError(DataError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DataManipulator:
    def __init__(self, path_dataset, filename):
        self.dict_data = self.pegar_JSON(path_dataset, filename)
        # acoes permitidas ao usuario
        self.COMANDOS = ["usar", "olhar", "pegar", "andar",
                         "mover", "itens", "ajuda", "soltar"]
        # localizacao
        self.loc = self.dict_data.get("locations", [])
        self.loc.sort(key=lambda x: int(x.get("id")))
        # id da sala atual
        self.sala_atual = self.dict_data["startLocationId"]
        # itens do usuario
        self.inv = []
        # ATRIBUTOS OPCIONAIS
        self.max_itens = int(self.dict_data.get("max_itens", None))
        self.max_turns_easy = int(self.dict_data.get("max_turns_easy", None))
        self.max_turns_normal = int(
            self.dict_data.get("max_turns_normal", None))
        self.max_turns_hard = int(self.dict_data.get("max_turns_hard", None))

    def pegar_JSON(self, path_dataset: str, filename: str) -> dict:
        """
        Lê JSON e retorna dict
        """
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

    def hash_reverso(self, lista: list[dict], prop_alvo: str, prop_chave: str, value):
        """
        Implementa logica de hash reverso para buscar dentro de objetos
        """
        for i, obj in enumerate(lista):
            if obj[prop_chave] == value:
                return obj[prop_alvo], i
        return None, None

    def get_sala(self) -> dict:
        """
        Retorna objeto sala
        NOTE: considera id da sala como numerico
        """
        return self.loc[int(self.sala_atual)]

    def mudar_sala(self, alvo: str) -> dict:
        """
        Muda de objeto sala
        """
        self.sala_atual = alvo
        return self.loc[int(self.sala_atual)]

    def parse_input(self, in_: str):
        """
        Faz parse do input, analisa se comandos estao corretos.
        retorna inteiro para erro ou lista contendo comando ou comando e alvo
        """

        COMANDOS_1 = ["olhar", "itens", "ajuda"]
        COMANDOS_2 = ["usar", "pegar", "soltar", "andar", "mover"]

        sequencia_str = re.split(r"\s|;|,", in_)
        tam_seq = len(sequencia_str)
        if tam_seq == 1:
            comando = sequencia_str[0]
            if comando in COMANDOS_1:
                return [comando, ""]
            elif comando == "sair":
                exit(0)
            else:
                # comando de 1 palavra errado
                return [-1, -1]
        elif tam_seq == 2:
            comando = sequencia_str[0]
            if comando in COMANDOS_2:
                alvo = str(sequencia_str[1])
                return [comando, alvo]
            else:
                # comando de 2 palavras errado
                return [-2, -2]
        else:
            # comando de 3 palavras, nao existe
            return [-3, -3]

    def get_itens(self) -> list[dict]:
        return self.inv

    def add_inventario(self, sala: dict, id_alvo: str, nome_alvo: str, idx_item):
        """
        Adiciona item ao inventario com base em max_itens.\n
        -----------------
        Parameters:\n
        - alvo: `str` que deve ser o id do item dentro da sala\n
        """
        sala = self.get_sala()
        lista_itens = sala["items"]
        dict_item = lista_itens[idx_item]
        if self.max_itens is None:
            self.inv.append(dict_item)
        else:
            if len(self.inv) < self.max_itens:
                self.inv.append(dict_item)
            else:
                raise InventoryError("Inventario cheio!")

        return sala["items"].pop(idx_item)

    def soltar_item(self, dict_item, idx_item):
        sala = self.get_sala()
        sala["items"].append(dict_item)
        self.inv.pop(idx_item)

    def mover_item(self, sala: dict, id_alvo, id_destino):
        pass

    def usar_item(self, sala: dict, id_item, efeito):
        pass
