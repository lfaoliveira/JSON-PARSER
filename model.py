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

        escolha = self.escolher_dificuldade()
        if escolha != None:
            tur, dif = escolha
            print(dif)
            self.dificuldade = dif
            self.max_turnos = tur
            self.turnos = 0
        else:
            self.turnos = None

    def escolha(self, opcoes: dict[int, str]):
        """
        ### Desc:
        Faz input de escolha
        Estrutura de opcoes: 
        {num1: "nome", num2: "nome2", ...}\n
        ---------------------------\n
        ### Parameters:\n

        Sempre retorna 
        """
        nums = [i + 1 for i in range(len(opcoes.keys()))]
        a = input(">>> ")

        # so aceita ate 9 escolhas
        match = re.match(f'[{nums[0]}-{nums[-1]}]', a)
        while (match == None):
            print("Insira um número válido! ")
            a = input(">>> ")
            match = re.match(f'[{nums[0]}-{nums[-1]}]', a)
        string = re.split(f"([{nums[0]}-{nums[-1]}])", match.string)[1]

        return string

    def escolher_dificuldade(self):

        easy = self.max_turns_easy
        med = self.max_turns_normal
        hard = self.max_turns_hard

        difs = [(easy, "facil"), (med, "normal"), (hard, "dificil")]
        # so fica o que nao eh None
        difs = list(filter(lambda x: x[0] != None, difs))
        if len(difs) == 0:
            return None
        elif (len(difs) == 1):
            return difs[0]

        opcoes = {}

        print("Escolha um número de dificuldade: ")
        for i, dif in enumerate(difs):
            print(f"{i+1}) {dif[1]}: {dif[0]} Turnos")
            opcoes[i] = dif[1]

        string = self.escolha(opcoes)
        idx = int(string) - 1
        return difs[idx]

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

    def contar_turnos(self):
        """
        Conta turnos; se houver, retorna true se passar de max_turns senao retorna falso
        """
        end = False
        if self.turnos != None:
            self.turnos += 1
            if self.turnos == self.max_turnos:
                end = True
                return end

        return end

    def get_data_rec(self, args: list):
        """funcao para pegar propriedades de objetos recursivamente"""
        data = self.dict_data
        for arg in args:
            data = data[arg]
        return data

    def get_data(self, arg):
        """funcao para pegar dados normalmente"""
        return self.dict_data[arg]

    def busca_dupla(self, lista: list[dict[str, str]], prop_alvo: str, prop_chave: str, value):
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

    def mudar_sala(self, id_alvo: str) -> dict:
        """
        Muda de objeto sala
        NOTE: considera id da sala como numerico
        """
        self.sala_atual = id_alvo
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
        comando = sequencia_str[0].lower()
        if tam_seq == 1:

            if comando in COMANDOS_1:
                return [comando, ""]
            elif comando == "sair":
                exit(0)
            else:
                # comando de 1 palavra errado
                return [-1, -1]
        elif tam_seq == 2:

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
