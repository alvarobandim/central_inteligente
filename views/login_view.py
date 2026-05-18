"""
Module: Login & Register View Component
Description: Interface gráfica de autenticação e registro de múltiplos usuários
             com suporte a disparo por teclado (Enter). 
             Modo Cofre: Sem recuperação de senha (perdeu a chave, perdeu o acesso).
"""
import flet as ft
from database.db_manager import conectar_db
from security.auth import gerar_hash_senha, verificar_senha
from views.dashboard_view import carregar_dashboard

def exibir_tela_login(page: ft.Page):
    page.clean()
    page.title = "Central Inteligente - Autenticação"
    
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    # Texto para exibir mensagens de sucesso ou erro na tela principal
    lbl_mensagem = ft.Text(value="", size=14, weight=ft.FontWeight.W_500)

    # ==========================================
    # 1. LÓGICA DE LOGIN E CADASTRO
    # ==========================================
    def processar_autenticacao(e):
        username = txt_user.value.strip().lower()
        password = txt_pass.value.strip()

        if not username or not password:
            lbl_mensagem.value = "Preencha todos os campos."
            lbl_mensagem.color = "red"
            page.update()
            return

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM usuarios WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row and verificar_senha(password, row[0]):
            carregar_dashboard(page, username)
        else:
            lbl_mensagem.value = "Usuário ou senha inválidos."
            lbl_mensagem.color = "red"
            page.update()

    def processar_cadastro(e):
        username = txt_user.value.strip().lower()
        password = txt_pass.value.strip()

        if not username or not password:
            lbl_mensagem.value = "Preencha os campos para cadastrar."
            lbl_mensagem.color = "red"
            page.update()
            return
        
        if len(password) < 3:
            lbl_mensagem.value = "A senha deve ter pelo menos 3 caracteres."
            lbl_mensagem.color = "red"
            page.update()
            return

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = ?", (username,))
        if cursor.fetchone()[0] > 0:
            lbl_mensagem.value = "Este nome de usuário já existe!"
            lbl_mensagem.color = "red"
            conn.close()
            page.update()
            return

        hash_senha = gerar_hash_senha(password)
        cursor.execute("INSERT INTO usuarios (username, password_hash) VALUES (?, ?)", (username, hash_senha))
        conn.commit()
        conn.close()
        
        lbl_mensagem.value = f"Usuário '{username}' criado com sucesso!"
        lbl_mensagem.color = "green"
        txt_user.value = ""
        txt_pass.value = ""
        page.update()

    # ==========================================
    # 2. MONTAGEM DA TELA DE LOGIN
    # ==========================================
    txt_user = ft.TextField(label="Usuário", width=300, on_submit=processar_autenticacao)
    txt_pass = ft.TextField(label="Chave de Acesso", width=300, password=True, can_reveal_password=True, on_submit=processar_autenticacao)

    btn_autenticar = ft.Container(
        content=ft.Text("ENTRAR NO SISTEMA", color="white", weight=ft.FontWeight.BOLD),
        alignment=ft.Alignment(0, 0),
        width=300, height=45, bgcolor="blue", border_radius=5,
        on_click=processar_autenticacao
    )

    btn_cadastrar = ft.Container(
        content=ft.Text("CRIAR NOVA CONTA", color="lightblue", weight=ft.FontWeight.BOLD),
        alignment=ft.Alignment(0, 0),
        width=300, height=45, bgcolor="#222222", border_radius=5,
        on_click=processar_cadastro
    )

    page.add(
        ft.Column(
            controls=[
                ft.Text("🔒", size=60),
                ft.Text("CENTRAL INTELIGENTE", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Ecossistema Pessoal de Gestão", size=14, color="grey"),
                ft.Container(height=10),
                txt_user,
                txt_pass,
                ft.Container(height=5),
                btn_autenticar,
                btn_cadastrar,
                lbl_mensagem
            ],
            horizontal_alignment="center",
            spacing=12
        )
    )