import json
import copy
import sys
import re
import os
from click import getchar
from model import DataManipulator, InventoryError
from view import View
from transitions import Machine

# inspiracao: https://github.com/acm-0/AdventureGame

estados = ['inicial', 'esperando',
           'atacando', 'dialogando', 'end']

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
    {'trigger': 'mover',  # mover , 'dados': "nome_item, direcao"
     'source': 'esperando',
     'dest': '=',
     'after': 'moverObj'},
    {'trigger': 'pegar',  # pegar 'dados': 'nome_item'
     'source': 'esperando',
     'dest': '=',
     'after': 'pegar'},
    {'trigger': 'soltar',  # soltar 'dados': 'nome_item'
     'source': 'esperando',
     'dest': '=',
     'after': 'soltar'},
    {'trigger': 'usar',  # usar 'dados': 'nome_item'
     'source': 'esperando',
     'dest': '=',
     'after': 'usar'},
    {'trigger': 'atacar',  # atacar 'dados': 'nome_enemy'
     'source': 'esperando',
     'dest': 'atacando'},
    {'trigger': 'falar',  # falar 'dados': 'nome_npc'
     'source': 'esperando',
     'dest': '=',
     'after': 'falar'},
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
        Movimenta item. Nao precisa especificar direcao\n
        NOTE: alvo deve ser NOME do objeto\n
        ------------\n
        Returns:\n
        """
        # TODO: MELHORAR LOGICA DE MOVER
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

            return True

        except ProgramError as e:
            print(e.args[0])
            if e.critical == True:
                exit(1)
        except CommandError as e:
            print(e.args[0])

    def mostrar_ajuda(self, **kwargs):
        self.printer.mostrar_ajuda()

    def desc_inicial(self):
        # considerando que locations eh lista ordenada
        sala = self.manipulador.get_sala()
        desc = sala["description"]
        nome = sala["name"]
        self.printer.print_inicial([nome, desc])

    def falar(self, **kwargs):
        """
        Fala com NPC especificado por alvo\n
        NOTE: alvo deve ser NOME do NPC\n
        ---
        ### Returns:
        """
        nome_npc = kwargs.get("alvo", None)
        # id_npc = None
        try:
            if nome_npc == None:
                # deu alguma merda grande
                raise ProgramError(
                    "ERRO NO PROGRAMA! Reinicie", critical=True)
            sala = self.manipulador.get_sala()
            id_npc, indice_npc = self.manipulador.busca_dupla(
                sala["npcs"], "id", "name", nome_npc)

            if id_npc == None:
                # nao achou alvo
                raise CommandError("NPC nao existe!")
            inactive = bool(sala["npcs"][indice_npc]["inactive"])
            if inactive:
                raise CommandError(
                    "Personagem bloqueado! Explore mais para conseguir falar")

        except ProgramError as e:
            print(e.args[0])
            if e.critical == True:
                exit(1)
            return
        except CommandError as e:
            print(e.args[0])
            return

        diags = sala["npcs"][indice_npc]["dialogues"]
        opcoes = {}
        cont = 0

        for i in range(1, len(diags) + 1):
            opcoes[i] = diags[i]["text"]
            cont += 1
        opcoes[cont + 1] = "Sair do dialogo"

        loop = True
        while loop:
            idx = int(self.manipulador.escolha(opcoes)) - 1
            if idx + 1 == cont + 1:
                loop = False

            resp = diags[idx]["responses"]
            # NOTE: sempre pega primeiro resultado
            resultado = resp[0]["result"]

            active = resultado["active"]
            if len(active) > 0:
                self.manipulador.activate_npc(active)

            lose_item = resultado["lose_item"]
            if len(lose_item) > 0:
                # TODO: CRIAR LOGICA DE EXCECOES
                self.manipulador.perder_item(lose_item)

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
        ---
        ### Returns:\n
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

    def usar(self, **kwargs):
        """
        Usa alvo. Efetivamente nao faz nada, so serve pra registrar acao\n
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

            return True

        except ProgramError as e:
            print(e.args[0])
            if e.critical == True:
                exit(1)
        except CommandError as e:
            print(e.args[0])

    def mostrarInventario(self, **kwargs):
        itens = self.manipulador.get_itens()
        itens = [item["name"] for item in itens]
        if len(itens) == 0:
            print("Invetario vazio")
            return
        self.printer.print_inventario(itens)

    def not_end(self):
        return self.state != "end"
