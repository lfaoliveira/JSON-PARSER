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


class Item:
    def __init__(self, id, name, description, can_take, inactive) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.can_take = can_take
        self.inactive = inactive

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "description": self.description,
                "can_take": self.can_take,
                "inactive": self.inactive}


class DataManipulator:
    def __init__(self, path_dataset, filename):
        self.dict_data = self.pegar_JSON(path_dataset, filename)

        # stats do usuario
        self.attack = self.dict_data["attack"]
        self.defense = self.dict_data["defense"]
        self.life = self.dict_data["life"]

        self.puzzles_resolv = []

        # localizacao
        self.loc = {}
        aux = self.dict_data.get("locations", [])
        for obj in aux:
            self.loc[obj["id"]] = obj

        # hashmaps reverso pra PUZZLES e NPC
        self.npcs = {}  # key = id do npc; value= id da sala
        self.puzzles = {}  # key = id do puzzle; value= id da sala
        self.saidas = {}  # key = id da saida; value= id da sala
        for id_sala, sala in self.loc.items():
            puzzles = sala.get("puzzles", [])
            for puzzle in puzzles:
                id_p = puzzle["id"]
                self.puzzles[id_p] = id_sala

            npcs = sala.get("npcs", [])
            for npc in npcs:
                id_n = npc["id"]
                self.npcs[id_n] = id_sala

            saidas = sala.get("exits", [])
            for saida in saidas:
                id_s = saida["targetLocationId"]
                self.saidas[id_s] = id_sala

        # id da sala atual
        self.sala_atual = self.dict_data["startLocationId"]
        # itens do usuario
        self.inv = []
        # ATRIBUTOS OPCIONAIS
        self.max_itens = self.dict_data.get("max_itens", None)
        self.max_turns_easy = self.dict_data.get("max_turns_easy", None)
        self.max_turns_normal = self.dict_data.get("max_turns_normal", None)
        self.max_turns_hard = self.dict_data.get("max_turns_hard", None)

        # array contendo acoes executadas na sala atual
        self.acoes_atuais = []

        escolha = self.escolher_dificuldade()
        if escolha != None:
            tur, dif = escolha
            print(dif)
            self.dificuldade = dif
            self.max_turnos = int(tur)
            self.turnos = 0
        else:
            self.turnos = None

    def activate_npc(self, lista_npc):
        for id_npc in lista_npc:
            id_sala = self.npcs[id_npc]
            sala = self.loc[id_sala]
            npcs_outra_sala = sala["npcs"]
            for npc in npcs_outra_sala:
                if npc["id"] == id_npc:
                    print(f"{npc['name']} ativado!")
                    npc["inactive"] = False
                    break

    def activate_puzzle(self, lista_puzzle):
        for id_puzzle in lista_puzzle:
            id_sala = self.puzzles[id_puzzle]
            sala = self.loc[id_sala]
            puzzles_outra_sala = sala["puzzles"]
            for puzzle in puzzles_outra_sala:
                if puzzle["id"] == id_puzzle:
                    puzzle["inactive"] = False
                    break

    def activate_saida(self, lista_saida):
        for id_saida in lista_saida:
            id_sala = self.npcs[id_saida]
            sala = self.loc[id_sala]
            saidas_outra_sala = sala["exits"]
            for saida in saidas_outra_sala:
                if saida["targetLocationId"] == id_saida:
                    saida["inactive"] = False
                    break

    def escolha(self, opcoes: dict[int, str]):
        """
        ### Desc:
        Faz input de escolha
        Estrutura de opcoes: 
        {num1: "nome", num2: "nome2", ...}\n
        ---\n
        ### Parameters:\n

        Sempre retorna numero de escolha
        """
        nums = [i + 1 for i in range(len(opcoes.keys()))]
        a = input(" :")

        # so aceita ate 9 escolhas
        match = re.match(f'[{nums[0]}-{nums[-1]}]', a)
        while (match == None):
            print("Insira um número válido! ")
            a = input(" :")
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
        with open(path_json, "r", encoding="utf-8") as file:
            data = json.load(file)
            # dados retornados como dict
            # print(f"JSON: {data}\n\n")
            return data

    def perder_item(self, lista_itens: list[str]):
        for id_item in lista_itens:
            for elem in self.inv:
                if elem.id == id_item:
                    print(f"Item perdido: {elem.name}")
                    self.inv.remove(elem)
                    break

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

    def get_data(self, arg):
        """funcao para pegar dados normalmente"""
        return self.dict_data[arg]

    def reg_acao(self, acao):
        self.acoes_atuais.append(acao)

    def proc_result(self, result: dict):
        active = result["active"]
        if len(active) > 0:
            for elem in active:
                self.puzzles_resolv.append(elem)

        lose_life = int(result["lose_life"])
        self.life -= lose_life

        lose_item = result["lose_item"]
        if len(lose_item) > 0:
            for elem in lose_item:
                self.inv.remove(elem)

    def busca_dupla(self, lista: list[dict[str, str]], prop_alvo: str, prop_chave: str, valor_procurado):
        """
        Implementa logica de hash reverso para buscar dentro de objetos
        """
        "falar velho sábio"
        for i, obj in enumerate(lista):
            value = obj[prop_chave]
            if type(value) == str and " " in value:
                # troca espacos por _ e transforma em lowercase
                value = value.replace(" ", "_").lower()
                # valor_procurado = re.sub(r'\s+', '_', valor_procurado)
                valor_procurado = valor_procurado.lower()
            if value == valor_procurado:
                return obj[prop_alvo], i
        return None, None

    def get_sala(self) -> dict:
        """
        Retorna objeto sala
        NOTE: considera id da sala como numerico
        """
        return self.loc[self.sala_atual]

    def mudar_sala(self, id_alvo: str) -> dict:
        """
        Muda de objeto sala
        NOTE: considera id da sala como numerico
        """
        self.acoes_atuais = []
        self.sala_atual = id_alvo
        return self.get_sala()

    def parse_input(self, in_: str):
        """
        Faz parsing do input, analisa se comandos estao corretos.
        retorna inteiro para erro ou lista contendo comando ou comando e alvo
        """
        # acoes permitidas ao usuario
        COMANDOS_1 = ["olhar", "itens", "ajuda"]
        COMANDOS_2 = ["usar", "pegar", "falar",
                      "soltar", "andar", "mover", "atacar"]

        # transforma espacos, ; e , em _
        in_ = re.sub(r'\s+|;+|,+', '_',  in_)
        # faz split em cada underline
        sequencia_str = re.split(r"_", in_)
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
        elif tam_seq >= 2:

            if comando in COMANDOS_2:
                # alvo = str(sequencia_str[1])
                # registra acao
                self.reg_acao(comando)
                alvo = "_".join(sequencia_str[1:])
                return [comando, alvo]
            else:
                # comando de 2 palavras errado
                return [-2, -2]
        else:
            # comando de 0 palavras, inexistente
            return [-3, -3]

    def get_itens(self) -> list[Item]:
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
        item_class = Item(dict_item["id"], dict_item["name"],
                          dict_item["description"], dict_item["can_take"], dict_item["inactive"])
        if self.max_itens is None:
            self.inv.append(item_class)
        else:
            if len(self.inv) < self.max_itens:
                self.inv.append(item_class)
            else:
                raise InventoryError("Inventario cheio!")

        return

    def soltar_item(self, item: Item, idx_item):
        sala = self.get_sala()
        sala["items"].append(item.to_dict())
        self.inv.pop(idx_item)
        return

    def mover_item(self, sala: dict, id_alvo, id_destino):
        pass

    def usar_item(self, sala: dict, id_item, efeito):
        pass
