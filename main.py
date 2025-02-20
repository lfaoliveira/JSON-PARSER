import os
from view import View
from model import DataManipulator
from controller import Controller


dict_erro_comandos = {
    -1: "Comando inexistente",
    -2: "Comando inexistente",
    -3: "Palavras nao sao comandos!"}

# main
if __name__ == "__main__":
    # pegando JSON
    path_dataset = os.getcwd()
    filename = "exemplo.json"
    # modelo pega todos os atributos do JSON
    model = DataManipulator(path_dataset, filename)
    printer = View(model)
    ctrl = Controller(model, printer)
    ctrl.trigger("iniciarjogo")
    while ctrl.not_end():
        comando, alvo = model.parse_input(input(">>> "))
        if type(comando) == int:
            printer.print_erro(comando, dict_erro_comandos)
        elif (type(comando) == str):
            ctrl.executar_comando(comando, alvo)
