import json
import copy
import sys
from os import system
from os.path import exists
from click import getchar
from transitions import Machine

# inspiracao: https://github.com/acm-0/AdventureGame

estados = ['inicial', 'movendo', 'pegando',
           'largando', 'atacando', 'parado', 'interagindo',
           'dialogando', 'perdendoVida']


class Controller:
    def __init__(self, dict_data):
        self.dict_data = dict_data

        self.machine = Machine(model=self, states=estados, initial='inicial')

        # Add some transitions. We could also define these using a static list of
        # dictionaries, as we did with states above, and then pass the list to
        # the Machine initializer as the transitions= argument.

        # transicao de mover
        self.machine.add_transition(
            trigger='mover', source='parado', dest='movendo', kwargs=["direcao", "local"])

        # transicao para interagir
        self.machine.add_transition(
            trigger='interagir', source='parado', dest='interagindo', kwargs=["id_item"])

        #
        self.machine.add_transition('', '', '')

        #
        self.machine.add_transition('', '*', '',
                                    before='')

    def get_data_from_model():
        pass
