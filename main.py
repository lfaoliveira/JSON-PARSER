import os
from view import View
from model import DataManipulator
from controller import Controller


dict_erro_comandos = {
    -1: "Comando errado",
    -2: "Comando errado",
    -3: "Palavras nao sao comandos!"}

# main
if __name__ == "__main__":
    # pegando JSON
    path_dataset = os.getcwd()
    filename = "exemplo.json"
    # modelo pega todos os atributos do JSON
    model = DataManipulator(path_dataset, filename)
    # faz parte de printagem, mas nem sempre
    printer = View(model)
    # implementacao da logica da aplicacao
    ctrl = Controller(model, printer)
    ctrl.trigger("iniciarjogo")
    while ctrl.not_end():
        if model.turnos != None:
            rest = int(model.max_turnos) - model.turnos
            print("Turnos Restantes: ", rest)

        comando, alvo = model.parse_input(input(">>> "))
        if type(comando) == int:
            printer.print_erro(comando, dict_erro_comandos)
        elif (type(comando) == str):
            ctrl.executar_comando(comando, alvo)
