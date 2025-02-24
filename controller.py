import json
import copy
import sys
import re
import os
from click import getchar
from model import DataManipulator, InventoryError, Item
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
     'after': 'mover'},
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
     'dest': '=',
     'after': 'atacar'},
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
        if comando != "olhar":
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
            print(f"Você moveu {nome_item}")
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

    def atacar(self, **kwargs):
        """
        Usa alvo. Efetivamente nao faz nada, so serve pra registrar acao\n
        NOTE: alvo deve ser NOME do objeto\n
        ------------\n
        Returns:\n
        """
        def helper_atacar(manipulador: DataManipulator, ataque):
            ataque_real = manipulador.defense - ataque
            return ataque_real, ataque_real >= manipulador.life

        # nome do objeto
        nome_inimigo = kwargs.get("alvo", None)
        try:
            if nome_inimigo == None:
                # deu alguma merda grande
                raise ProgramError("ERRO NO PROGRAMA! Reinicie", critical=True)

            sala = self.manipulador.get_sala()
            inimigos = sala["enemies"]
            if len(inimigos) == 0:
                raise CommandError(
                    "Nao ha inimigos nesta sala! Agressividade demais eh ruim")
            # NOTE: SEMPRE ATACA PRIMEIRO INIMIGO
            aux = inimigos[0]
            id, name = aux.get("id", None), aux.get("name", None)
            if id != None and name != None:
                id_inimigo, indice_inimigo = self.manipulador.busca_dupla(
                    sala["enemies"], "id", "name", nome_inimigo)

                if id_inimigo == None:
                    # nao achou alvo
                    raise CommandError("Inimigo nao existe!")

            ataque_ini = int(aux["attack"])
            def_ini = int(aux["defense"])
            ataque_real_ini, impossivel_vencer = helper_atacar(
                self.manipulador, ataque_ini)
            if impossivel_vencer:
                raise CommandError(
                    "Inimigo com ataque muito alto! pegue itens melhores")
            else:
                # hora de atacar
                self.manipulador.life -= ataque_real_ini
                if def_ini > self.manipulador.attack:
                    raise CommandError(
                        "Inimigo com defensa muita alta! pegue itens melhores")
                else:
                    # nao morreu com ataque e inimigo pode ser morto
                    print(f"Você eliminou {nome_inimigo}")
                    sala = self.manipulador.get_sala()
                    sala["enemies"].remove(aux)
                    return True

        except ProgramError as e:
            print(e.args[0])
            if e.critical == True:
                exit(1)
        except CommandError as e:
            print(e.args[0])

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
                    "Personagem bloqueado! Explore mais")

        except ProgramError as e:
            print(e.args[0])
            if e.critical == True:
                exit(1)
            return
        except CommandError as e:
            print(e.args[0])
            return

        diags = sala["npcs"][indice_npc]["dialogues"]
        self.printer.print_with_formatting("DIALOGO: ")

        opcoes = {}
        i = 0

        for i in range(len(diags)):
            opcoes[i] = diags[i]["text"]
            print(f"{i + 1}) {diags[i]['text']}")
        opcoes[i + 1] = "Sair do dialogo"

        idx = int(self.manipulador.escolha(opcoes)) - 1
        if idx + 1 == i + 1:
            return

        resp = diags[idx]["responses"]
        # NOTE: SEMPRE PEGA PRIMEIRO RESULTADO
        resultado = resp[0]["result"]

        active = resultado["active"]
        if len(active) > 0:
            self.manipulador.activate_npc(active)

        lose_item = resultado["lose_item"]
        if len(lose_item) > 0:
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
            print(f"Você andou na direção {nome_direcao}")
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

            self.manipulador.add_inventario(
                sala, id_alvo, nome_item, indice_item)
            print(f"Você pegou {nome_item}")
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

            instancia_item = None
            achou = False
            idx_item = 0
            for i, item in enumerate(inv):
                nome = item.name
                if nome == nome_item:
                    instancia_item = item
                    idx_item = i
                    achou = True
                    break

            if not achou:
                raise CommandError("Item nao esta no inventario!")
            else:
                if isinstance(instancia_item, Item):
                    self.manipulador.soltar_item(instancia_item, idx_item)
                    print(f"Você soltou {nome_item}")
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

            print(f"Você usou {nome_item}")
            return True

        except ProgramError as e:
            print(e.args[0])
            if e.critical == True:
                exit(1)
        except CommandError as e:
            print(e.args[0])

    def mostrarInventario(self, **kwargs):
        itens = self.manipulador.get_itens()
        itens = [str(item.name) for item in itens]
        if len(itens) == 0:
            print("Invetario vazio")
            return
        self.printer.print_inventario(itens)

    def not_end(self):
        return self.state != "end"
