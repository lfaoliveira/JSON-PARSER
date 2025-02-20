import json
import copy
import sys
import re
from os import system
from os.path import exists
from click import getchar
from model import DataManipulator, InventoryError, InteractionError, MoveError
from view import View
from transitions import Machine
from transitions import Transition

# inspiracao: https://github.com/acm-0/AdventureGame

estados = ['inicial', 'esperando', 'movendo', 'pegando',
           'largando', 'atacando', 'interagindo',
           'dialogando', 'executando', 'andando', 'defendendo', 'end']

transitions = [
    {'trigger': 'iniciarjogo',  # iniciarJogo
     'source': 'inicial',
     'dest': 'esperando',
     'after': 'desc_inicial'},
    {'trigger': 'andar',  # andar
     'source': 'esperando',
     'dest': '=',
     'after': 'andar'},
    {'trigger': 'itens',  # inventario
     'source': 'esperando',
     'dest': '=',
     'after': 'mostrarInventario'},
    {'trigger': 'olhar',  # olhar
     'source': 'esperando',
     'dest': '=',
     'after': 'olhar'},
    {'trigger': 'ajuda',  # ajuda
     'source': 'esperando',
     'dest': '=',
     'after': 'mostrar_ajuda'},
    {'trigger': 'mover',  # mover , 'dados': "id_item, direcao"
     'source': 'esperando',
     'dest': '=',
     'after': 'moverObj'},
    {'trigger': 'pegar',  # pegar 'dados': 'id_item'
     'source': 'esperando',
     'dest': '=',
     'after': 'pegar'},
    {'trigger': 'soltar',  # soltar 'dados': 'id_item'
     'source': 'esperando',
     'dest': '=',
     'after': 'soltar'},
    {'trigger': 'usar',  # usar 'dados': 'id_item'
     'source': 'esperando',
     'dest': '=',
     'after': 'usar'},
    {'trigger': 'atacar',  # atacar 'dados': 'id_enemy'
     'source': 'esperando',
     'dest': 'atacando'},
    {'trigger': 'endgame',  # fim de jogo 'dados': 'id_enemy'
     'source': 'esperando',
     'dest': 'end'},
]


class ProgramError(Exception):
    def __init__(self, *args: object, critical) -> None:
        super().__init__(*args)
        self.critical = critical


class CommandError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ErroEngine(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Controller(Machine):
    """
    Classe para controlar mudanças de estado
    """

    def __init__(self, manipulador: DataManipulator, printer: View):
        self.manipulador = manipulador
        self.printer = printer

        super().__init__(model=self, states=estados,
                         transitions=transitions, initial='inicial', name="EngineDoJogo")

    def executar_comando(self, comando: str, alvo):
        end = self.manipulador.contar_turnos()
        if end:
            self.trigger('endgame')
        self.trigger(comando, alvo=alvo)

    def mover(self, **kwargs):
        """
        Recebe alvo e tenta adicionar alvo ao inventario\n
        NOTE: alvo deve ser NOME do objeto\n
        ------------\n
        Returns:\n
        """
        pass

    def mostrar_ajuda(self, **kwargs):
        print("COMO JOGAR: \n")
        print("Comandos: usar, olhar, pegar, andar, mover, inventario, ajuda")
        print("USO: usar <nome do item>")
        print("USO: pegar <nome do item>")
        print("USO: soltar <nome do item>")
        print("USO: olhar mostra a sala atual")
        print("USO: mover <nome do item>")
        print("USO: andar direcao(norte, sul, leste, oeste e derivados)")
        print("USO: itens: mostra inventario")
        print("USO: ajuda: pede ajuda pro computador")

    def desc_inicial(self):
        # considerando que locations eh lista ordenada
        sala = self.manipulador.get_sala()
        desc = sala["description"]
        nome = sala["name"]
        self.printer.print_inicial([nome, desc])

    def olhar(self, **kwargs):
        sala = self.manipulador.get_sala()
        desc = sala.get("description")
        name = sala.get("name")
        itens = sala.get("items")
        npcs = sala.get("npcs")
        enemies = sala.get("enemies")
        exits = sala.get("exits")

        self.printer.print_olhar(desc=desc, name=name,
                                 itens=itens, npcs=npcs, enemies=enemies, exits=exits)

    def andar(self, **kwargs):
        """
        Anda na direcao especificada pelo alvo\n
        NOTE: alvo deve ser NOME da direcao\n
        ------------\n
        Returns:\n
        """
        nome_direcao = kwargs.get("alvo", None)
        try:
            if nome_direcao == None:
                # deu alguma merda grande
                raise ProgramError("ERRO NO PROGRAMA! Reinicie", critical=True)

            sala = self.manipulador.get_sala()
            id_exit, indice_item = self.manipulador.busca_dupla(
                sala["exits"], "targetLocationId", "direction", nome_direcao)

            if id_exit == None:
                # nao achou alvo
                raise CommandError("Saída nao existe!")
            inactive = bool(sala["exits"][indice_item]["inactive"])
            if inactive:
                raise CommandError(
                    "Saída indisponivel! Explore mais para conseguir sair")
            self.manipulador.mudar_sala(str(id_exit))

        except ProgramError as e:
            print(e.args[0])
            if e.critical == True:
                exit(1)
        except CommandError as e:
            print(e.args[0])

    def pegar(self, **kwargs):
        """
        Recebe alvo e tenta adicionar alvo ao inventario\n
        NOTE: alvo deve ser NOME do objeto\n
        ------------\n
        Returns:\n
        """
        # nome do objeto
        nome_item = kwargs.get("alvo", None)
        try:
            if nome_item == None:
                # deu alguma merda grande
                raise ProgramError("ERRO NO PROGRAMA! Reinicie", critical=True)

            sala = self.manipulador.get_sala()
            id_alvo, indice_item = self.manipulador.busca_dupla(
                sala["items"], "id", "name", nome_item)

            if id_alvo == None:
                # nao achou alvo
                raise CommandError("Item nao existe!")
            can_take = bool(sala["items"][indice_item]["can_take"])
            if can_take is False:
                raise InventoryError("Item nao pode ser pegado")

            resp = self.manipulador.add_inventario(
                sala, id_alvo, nome_item, indice_item)
            return True

        except ProgramError as e:
            print(e.args[0])
            if e.critical == True:
                exit(1)
        except CommandError as e:
            print(e.args[0])
        except InventoryError as e:
            print(e.args[0])

    def soltar(self, **kwargs):
        """
        Solta item na sala atual\n
        NOTE: alvo deve ser NOME do objeto\n
        ------------\n
        Returns:\n
        """
        # nome do objeto
        nome_item = kwargs.get("alvo", None)
        try:
            if nome_item == None:
                # deu alguma merda grande
                raise ProgramError("ERRO NO PROGRAMA! Reinicie", critical=True)

            inv = self.manipulador.get_itens()

            instancia_item = {}
            achou = False
            idx_item = 0
            for i, item in enumerate(inv):
                nome = item["name"]
                if nome == nome_item:
                    instancia_item = item
                    idx_item = i
                    achou = True
                    break

            if not achou:
                raise CommandError("Item nao esta no inventario!")

            self.manipulador.soltar_item(instancia_item, idx_item)
            return True

        except ProgramError as e:
            print(e.args[0])
            if e.critical == True:
                exit(1)
        except CommandError as e:
            print(e.args[0])
        except InventoryError as e:
            print(e.args[0])

    # TODO: CONSTRUIR LOGICA DE USAR
    def usar(self, **kwargs):
        nome_item = kwargs.get("alvo", None)

        falha = False
        dict_falhas = {1: "ERRO NO PROGRAMA! Reinicie",
                       2: "Item nao existe!",
                       3: "Inventario cheio!"}
        if nome_item != None:
            sala = self.manipulador.get_sala()
            id_alvo, indice_item = self.manipulador.busca_dupla(
                sala["items"], "id", "name", nome_item)

    def mostrarInventario(self, **kwargs):
        itens = self.manipulador.get_itens()
        itens = [item["name"] for item in itens]
        if len(itens) == 0:
            print("Invetario vazio")
            return
        self.printer.print_inventario(itens)

    def not_end(self):
        return self.state != "end"
