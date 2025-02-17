import json
import copy
import sys
from os import system
from os.path import exists
from click import getchar
from model import DataManipulator
from transitions import Machine
from transitions import Transition

# inspiracao: https://github.com/acm-0/AdventureGame

estados = ['inicial', 'esperando', 'movendo', 'pegando',
           'largando', 'atacando', 'interagindo',
           'dialogando', 'executando', 'andando', 'defendendo']

transitions = [
    {'trigger': 'iniciarjogo', 'source': 'inicial',
        'dest': 'esperando'},  # iniciarJogo 'conditions': 'startLocationId'
    {'trigger': 'mover', 'source': 'esperando',
        'dest': 'movendo'},  # mover , 'conditions': ["direcao", "id_local"]
    {'trigger': 'interagir', 'source': 'esperando',
        'dest': 'interagindo'},  # interagir 'conditions': 'id_item'
    {'trigger': 'atacar', 'source': 'esperando',
        'dest': 'atacando', },  # atacar 'conditions': 'id_enemy'
    # {'trigger': '', 'source': '', 'dest': ''}
]


class Controller(object):
    """
    Classe para controlar mudanças de estado
    """

    def __init__(self, manipulador: DataManipulator):
        self.model = manipulador
        self.machine = Machine(
            states=estados, transitions=transitions, initial='inicial')

    def mover(self, direcao, id_local):
        pass
