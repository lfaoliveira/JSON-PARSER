import json
import copy
import sys
from os import system
from os.path import exists
from click import getchar
from model import DataManipulator
from view import View
from transitions import Machine
from transitions import Transition

# inspiracao: https://github.com/acm-0/AdventureGame

estados = ['inicial', 'esperando', 'movendo', 'pegando',
           'largando', 'atacando', 'interagindo',
           'dialogando', 'executando', 'andando', 'defendendo', 'end']

transitions = [
    {'trigger': 'iniciarjogo',  # iniciarJogo 'conditions': 'startLocationId'
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
    {'trigger': 'mover',  # mover , 'conditions': ["direcao", "id_local"]
     'source': 'esperando',
     'dest': 'movendo'},
    {'trigger': 'interagir',  # interagir 'conditions': 'id_item'
     'source': 'esperando',
     'dest': 'interagindo',
     'after': 'pegar'},
    {'trigger': 'atacar',  # atacar 'conditions': 'id_enemy'
     'source': 'esperando',
     'dest': 'atacando'},



    # {'trigger': '',
    #  'source': '',
    #  'dest': ''}
]


class Controller(Machine):
    """
    Classe para controlar mudanças de estado
    """

    def __init__(self, manipulador: DataManipulator, printer: View):
        self.manipulador = manipulador
        self.printer = printer
        # dict de mapeamento de comando pra trigger da maquina de estados
        self.mapeamento_cmd = {'usar': 'interagir', 'pegar': 'interagir', 'andar': 'andar',
                               'mover': 'mover', 'inventario': 'inventario', 'ajuda': 'ajuda'}
        super().__init__(model=self, states=estados,
                         transitions=transitions, initial='inicial', name="EngineJogo")

    def mover(self, direcao, id_local):
        pass

    def executar_comando(self, comando, alvo):
        trigger = self.mapeamento_cmd[comando]
        self.trigger(trigger, kwargs=alvo)

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

    def not_end(self):
        return self.state != "end"
