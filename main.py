# Arquivo principal do projeto
# Esse é o arquivo que a gente roda para abrir o aplicativo.

import sys
import os
import flet as ft

# Importando o banco de dados e a tela de login
from database.db_manager import inicializar_banco
from views.login_view import exibir_tela_login

# Dica que peguei para o PyInstaller não dar erro de tela preta (--noconsole).
# O Flet precisa de um terminal para cuspir os logs, então criei um "falso" aqui.
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

def main(page: ft.Page):
    # Chama a tela de login assim que o app abre
    exibir_tela_login(page)

if __name__ == "__main__":
    # Primeiro cria o banco de dados (se não existir) para não dar erro na tela
    inicializar_banco()
    
    # Roda o aplicativo Flet
    ft.app(target=main)