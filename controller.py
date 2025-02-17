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
    {'trigger': 'mover',  # mover , 'conditions': ["direcao", "id_local"]
     'source': 'esperando',
     'dest': 'movendo'},
    {'trigger': 'interagir',  # interagir 'conditions': 'id_item'
     'source': 'esperando',
     'dest': 'interagindo'},
    {'trigger': 'atacar',  # atacar 'conditions': 'id_enemy'
     'source': 'esperando',
     'dest': 'atacando'},
    {'trigger': 'andar',  # andar
     'source': 'esperando',
     'dest': 'andando'},
    {'trigger': 'inventario',  # inventario
     'source': 'esperando',
     'dest': '='},
    {'trigger': 'ajuda',  # ajuda
     'source': 'esperando',
     'dest': '=',
     'after': 'mostrar_ajuda'}


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
        self.mapeamento = {'usar': 'interagir', 'pegar': 'interagir', 'andar': 'andar',
                           'mover': 'mover', 'inventario': 'inventario', 'ajuda': 'ajuda'}
        super().__init__(model=self, states=estados,
                         transitions=transitions, initial='inicial', name="EngineJogo")

    def mover(self, direcao, id_local):
        pass

    def executar_comando(self, comando, alvo):
        trigger = self.mapeamento[comando]
        self.trigger(trigger, kwargs=alvo)

    def mostrar_ajuda(self, **kwargs):
        print("COMO JOGAR: \n")
        print("Comandos: usar, pegar, andar, mover, inventario, ajuda")
        print("USO: usar nome do item")
        print("USO: pegar nome do item")
        print("USO: mover nome do item")
        print("USO: andar direcao(norte, sul, leste, oeste e derivados)")
        print("USO: inventario: mostra inventario")
        print("USO: ajuda: pede ajuda pro computador")

    def desc_inicial(self):
        id_inicial = self.manipulador.get_data("startLocationId")
        # considerando que locations eh lista ordenada
        desc = self.manipulador.get_data_rec(
            ["locations", int(id_inicial), "description"])
        nome = self.manipulador.get_data_rec(
            ["locations", int(id_inicial), "name"])
        self.printer.print_inicial([nome, desc])

    def not_end(self):
        return self.state != "end"
