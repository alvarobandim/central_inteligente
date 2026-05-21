import flet as ft

from components.financas_tab import criar_aba_financas
from components.brain_tab import criar_aba_brain
from components.tarefas_tab import criar_aba_tarefas

def carregar_dashboard(page: ft.Page, username: str):
    page.clean()
    page.title = f"Central Inteligente - Painel de {username.capitalize()}"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = "start"

    # Construímos as abas separadas
    layout_financas = criar_aba_financas(page, username)
    layout_brain = criar_aba_brain(page, username)
    
    # Pegamos o layout de tarefas e a função de atualizar exposta!
    layout_tarefas, disparar_atualizar_kanban = criar_aba_tarefas(page, username)

    # Gerenciamento de cliques do menu superior
    def ir_para_financas(e):
        layout_financas.visible = True
        layout_brain.visible = False
        layout_tarefas.visible = False
        page.update()

    def ir_para_brain(e):
        layout_financas.visible = False
        layout_brain.visible = True
        layout_tarefas.visible = False
        page.update()

    def ir_para_tarefas(e):
        layout_financas.visible = False
        layout_brain.visible = False
        layout_tarefas.visible = True
        
        # MÁGICA DE ESTADO: Manda o Kanban ler do banco e se reordenar na hora do clique!
        disparar_atualizar_kanban()
        page.update()

    def processar_logout(e):
        from views.login_view import exibir_tela_login
        exibir_tela_login(page)

    # Menu Superior
    menu_superior = ft.Row([
        ft.Container(content=ft.TextButton(content=ft.Text("💰 Finanças", color="white"), on_click=ir_para_financas), bgcolor="blue", border_radius=5),
        ft.Container(content=ft.TextButton(content=ft.Text("💡 Second Brain", color="white"), on_click=ir_para_brain), bgcolor="green", border_radius=5),
        ft.Container(content=ft.TextButton(content=ft.Text("📋 Tarefas", color="white"), on_click=ir_para_tarefas), bgcolor="orange700", border_radius=5),
        ft.VerticalDivider(expand=True), 
        ft.Container(content=ft.TextButton(content=ft.Text("🚪 Sair", color="white"), on_click=processar_logout), bgcolor="red", border_radius=5),
    ], spacing=10)
    
    page.add(
        ft.Column([
            menu_superior,
            ft.Divider(),
            layout_financas,
            layout_brain,
            layout_tarefas 
        ], expand=True)
    )