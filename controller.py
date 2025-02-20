import json
import copy
import sys
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
     'dest': 'andando'},
    {'trigger': 'inventario',  # inventario
     'source': 'esperando',
     'dest': '='},
    {'trigger': 'ajuda',  # ajuda
     'source': 'esperando',
     'dest': '=',
     'after': 'mostrar_ajuda'},
    {'trigger': 'mover',  # mover , 'dados': "id_item, direcao"
     'source': 'esperando',
     'dest': 'movendo',
     'after': 'moverObj'},
    {'trigger': 'pegar',  # pegar 'dados': 'id_item'
     'source': 'esperando',
     'dest': 'interagindo',
     'after': 'pegar'},
    {'trigger': 'usar',  # interagir 'dados': 'id_item'
     'source': 'esperando',
     'dest': 'interagindo',
     'after': 'usar'},
    {'trigger': 'atacar',  # atacar 'dados': 'id_enemy'
     'source': 'esperando',
     'dest': 'atacando'},



    # {'trigger': '',
    #  'source': '',
    #  'dest': ''}
]


class ProgramError(Exception):
    def __init__(self, *args: object, critical) -> None:
        super().__init__(*args)
        self.critical = critical


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
        self.trigger(comando, kwargs=alvo)

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
        print("USO: olhar mostra a sala atual")
        print("USO: mover <nome do item>")
        print("USO: andar direcao(norte, sul, leste, oeste e derivados)")
        print("USO: inventario: mostra inventario")
        print("USO: ajuda: pede ajuda pro computador")

    def desc_inicial(self):
        # considerando que locations eh lista ordenada
        sala = self.manipulador.get_sala()
        desc = sala["description"]
        nome = sala["name"]
        self.printer.print_inicial([nome, desc])

    def interacao(self, comando: str, id_alvo):
        """
        Helper pras funcoes de USAR PEGAR e MOVER
        """
        # mapeamento de comando para funcao de dados do manipulador
        dict_cmd = {"pegar": self.manipulador.add_inventario,
                    "mover": self.manipulador.mover_item,
                    "usar": self.manipulador.usar_item
                    }
        if comando == "pegar":
            pass
        elif comando == "usar":
            pass
        elif comando == "mover":
            pass

    def pegar(self, **kwargs):
        """
        Recebe alvo e tenta adicionar alvo ao inventario\n
        NOTE: alvo deve ser NOME do objeto\n
        ------------\n
        Returns:\n
        """
        # nome do objeto
        alvo = kwargs.get("alvo", None)
        falha = False
        dict_falhas = {1: "ERRO NO PROGRAMA! Reinicie",
                       2: "Item nao existe!",
                       3: "Inventario cheio!"}

        if alvo != None:
            sala = self.manipulador.get_sala()
            id_alvo = self.manipulador.hash_reverso(sala["items"], "id", alvo)
            if id_alvo != None:
                resp = self.manipulador.add_inventario(sala, id_alvo)
                if resp == False:
                    # nao deu pra botar
                    falha = 3
            else:
                # nao achou alvo
                falha = 2
        else:
            # deu alguma merda muito grande pra isso
            falha = 1

        # logica final de retorno
        if falha:
            return dict_falhas[falha]
        else:
            return True

    def pegar(self, **kwargs):
        """
        Recebe alvo e tenta adicionar alvo ao inventario\n
        NOTE: alvo deve ser NOME do objeto\n
        ------------\n
        Returns:\n
        """
        # nome do objeto
        alvo = kwargs.get("alvo", None)
        falha = False
        dict_falhas = {2: "Item nao existe!", 3: "Inventario cheio!"}
        try:
            if alvo == None:
                raise ProgramError("ERRO NO PROGRAMA! Reinicie", critical=True)
            else:
                sala = self.manipulador.get_sala()
                id_alvo = self.manipulador.hash_reverso(
                    sala["items"], "id", alvo)
                if id_alvo != None:
                    resp = self.manipulador.add_inventario(sala, id_alvo)
                else:
                    # nao achou alvo
                    falha = 2

            # logica final de retorno
            if falha:
                return dict_falhas[falha]
            else:
                return True

        except ProgramError as e:
            if e.critical == True:
                exit(1)

        except InventoryError:
            print(1)

        except MoveError:
            print(2)

        except InteractionError:
            print(3)

    def usar(self, **kwargs):
        nome_item = kwargs.get("alvo", None)

        falha = False
        dict_falhas = {1: "ERRO NO PROGRAMA! Reinicie",
                       2: "Item nao existe!",
                       3: "Inventario cheio!"}
        if nome_item != None:
            sala = self.manipulador.get_sala()
            id_alvo = self.manipulador.hash_reverso(
                sala["items"], "id", nome_item)

    def error_handler(self, error):
        pass

    def not_end(self):
        return self.state != "end"
