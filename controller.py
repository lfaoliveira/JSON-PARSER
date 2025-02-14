import json
import copy
import sys
from os import system
from os.path import exists
from click import getchar
from transitions import Machine
from transitions import Transition

# inspiracao: https://github.com/acm-0/AdventureGame

estados = ['inicial', 'movendo', 'pegando',
           'largando', 'atacando', 'esperando', 'interagindo',
           'dialogando', 'perdendoVida', 'executando', 'andando', 'defendendo']

transitions = [
    {'trigger': 'iniciarJogo', 'source': 'inicial',
        'dest': 'esperando'},  # iniciarJogo
    {'trigger': 'mover', 'source': 'esperando',
        'dest': 'movendo', 'kwargs': ["direcao", "id_local"]},  # mover
    {'trigger': 'interagir', 'source': 'esperando',
        'dest': 'interagindo', 'kwargs': ["id_item"]},  # interagir
    {'trigger': 'atacar', 'source': 'esperando',
        'dest': 'atacando', 'kwargs': ["id_enemy"]},  # atacar
    {'trigger': '', 'source': '', 'dest': ''}

]


class Controller:
    def __init__(self, dict_data):
        self.dict_data = dict_data

        self.machine = Machine(model=self, states=estados, initial='inicial')

        # Add some transitions. We could also define these using a static list of
        # dictionaries, as we did with states above, and then pass the list to
        # the Machine initializer as the transitions= argument.

        # transicao de mover
        self.machine.add_transition(
            trigger='', source='', dest='', )

        # transicao para interagir
        self.machine.add_transition(
            trigger='', source='', dest='', )

        #
        self.machine.add_transition(
            trigger='', source='', dest='', kwargs=["id_item"])

        #
        self.machine.add_transition('', '*', '',
                                    before='')

    def mover(direcao, id_local):
        pass
