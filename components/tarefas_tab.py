import flet as ft
import re
from database.db_manager import conectar_db
from datetime import datetime

def criar_aba_tarefas(page: ft.Page, username: str):
    
    # Armazena o estado do critério de ordenação no escopo da função
    # para evitar a perda de estado durante ciclos de re-renderização do Flet.
    if not hasattr(criar_aba_tarefas, "criterio_atual"):
        criar_aba_tarefas.criterio_atual = "PRAZO"

    # Define o fallback do dia corrente para melhorar a usabilidade do formulário.
    data_hoje_str = datetime.now().strftime("%d/%m/%Y")

    # ----------------------------------------------------
    # 1. DECLARAÇÃO DOS CONTROLES VISUAIS (DESIGN ENXUTO)
    # ----------------------------------------------------
    txt_data = ft.TextField(
        label="Prazo (DD/MM/AAAA)", 
        width=150, 
        dense=True, 
        value=data_hoje_str,  
        hint_text="Ex: 20/05/2026"
    )
    txt_titulo = ft.TextField(label="Tarefa...", width=200, dense=True)
    txt_desc = ft.TextField(label="Detalhes...", width=280, dense=True)
    
    drop_importancia = ft.Dropdown(
        label="Importância", width=120, dense=True,
        options=[ft.dropdown.Option("BAIXA"), ft.dropdown.Option("MÉDIA"), ft.dropdown.Option("ALTA")],
        value="MÉDIA"
    )

    lbl_erro_criacao = ft.Text("", color="red400", size=12, weight=ft.FontWeight.W_500)
    row_tags_criacao = ft.Row(wrap=True, spacing=6)
    tags_selecionadas_criacao = []

    drop_ordenacao = ft.Dropdown(
        label="Ordenar por", width=150, dense=True,
        options=[
            ft.dropdown.Option("PRAZO", "Prazo (Mais próximo)"),
            ft.dropdown.Option("NOME", "Nome (A-Z)"),
            ft.dropdown.Option("IMPORTANCIA", "Importância")
        ],
        value="PRAZO"
    )

    # Elemento container que atua como viewport dinâmico para a substituição do grid Kanban.
    conteiner_quadro_dinamico = ft.Container(expand=True)

    # ----------------------------------------------------
    # 2. FUNÇÕES DE SUPORTE, VALIDAÇÃO E ALERTAS VISUAIS
    # ----------------------------------------------------
    def aplicar_mascara_data(e):
        # Intercepta a entrada por regex e reconstrói as barras de corte do formato brasileiro.
        texto = e.control.value
        numeros = "".join(re.findall(r"\d", texto))
        numeros = numeros[:8]
        
        texto_formatado = ""
        if len(numeros) > 0: texto_formatado += numeros[:2]
        if len(numeros) > 2: texto_formatado += "/" + numeros[2:4]
        if len(numeros) > 4: texto_formatado += "/" + numeros[4:8]
            
        e.control.value = texto_formatado
        page.update()

    txt_data.on_change = aplicar_mascara_data

    def validar_formato_data(data_str):
        padrao = r"^\d{2}/\d{2}/\d{4}$"
        if not re.match(padrao, data_str):
            return False
        try:
            datetime.strptime(data_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    def obtener_dia_semana(data_str):
        if not data_str:
            return ""
        try:
            dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
            dt = datetime.strptime(data_str, "%d/%m/%Y")
            return f"({dias[dt.weekday()]})"
        except:
            return ""

    def criar_linha_prazo_com_alerta(dt_entrega, status):
        # Gerencia as regras de coloração com base na proximidade do prazo de entrega.
        if not dt_entrega:
            return ft.Text("Prazo: Sem prazo", size=11, color="grey500", weight="w500")

        dia_semana = obtener_dia_semana(data_str=dt_entrega)
        texto_exibido = f"Prazo: {dt_entrega} {dia_semana}"
        cor_prazo = "lightblue" 

        # Ignora regras de atraso para tarefas categorizadas como finalizadas.
        if status != "CONCLUIDO":
            try:
                hoje = datetime.now().date()
                prazo_tarefa = datetime.strptime(dt_entrega, "%d/%m/%Y").date()

                if prazo_tarefa < hoje:
                    texto_exibido = f"Atrasada - {dt_entrega} {dia_semana}"
                    cor_prazo = "red400"
                elif prazo_tarefa == hoje:
                    texto_exibido = f"Vence Hoje - {dt_entrega} {dia_semana}"
                    cor_prazo = "orange400"
            except:
                pass 

        return ft.Text(texto_exibido, size=11, color=cor_prazo, weight="bold" if cor_prazo != "lightblue" else "w500")

    def carregar_tags_sistema():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM tags WHERE usuario = 'sistema' OR usuario = ? ORDER BY nome ASC", (username,))
        tags = [r[0] for r in cursor.fetchall()]
        conn.close()
        return tags

    def alterar_status(id_tf, novo_status):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE tarefas SET status = ? WHERE id = ? AND usuario = ?", (novo_status, id_tf, username))
        conn.commit()
        conn.close()
        executar_f5_da_aba()

    def deletar_tarefa(id_tf):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tarefas WHERE id = ? AND usuario = ?", (id_tf, username))
        conn.commit()
        conn.close()
        executar_f5_da_aba()

    def criar_card_tarefa(id_tf, tit, desc, status, imp, dt_entrega, tags_str):
        cor_imp = "red" if imp == "ALTA" else "orange" if imp == "MÉDIA" else "blue"

        row_tags_card = ft.Row(spacing=4, wrap=True)
        lista_tags_card = [t.strip() for t in tags_str.split(",") if t.strip()]
        for tg in lista_tags_card:
            row_tags_card.controls.append(
                ft.Container(content=ft.Text(tg, size=9, color="white"), bgcolor="grey700", padding=4, border_radius=4)
            )

        botoes_fluxo = []
        if status == "A FAZER":
            botoes_fluxo.append(ft.IconButton(icon=ft.Icons.ARROW_FORWARD, icon_size=18, icon_color="orange400", tooltip="Iniciar", on_click=lambda e: alterar_status(id_tf, "EM ANDAMENTO")))
            botoes_fluxo.append(ft.IconButton(icon=ft.Icons.CHECK, icon_size=18, icon_color="green", tooltip="Concluir Direto", on_click=lambda e: alterar_status(id_tf, "CONCLUIDO")))
        elif status == "EM ANDAMENTO":
            botoes_fluxo.append(ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_size=18, icon_color="blue400", tooltip="Pendente", on_click=lambda e: alterar_status(id_tf, "A FAZER")))
            botoes_fluxo.append(ft.IconButton(icon=ft.Icons.CHECK, icon_size=18, icon_color="green", tooltip="Concluir", on_click=lambda e: alterar_status(id_tf, "CONCLUIDO")))
        elif status == "CONCLUIDO":
            botoes_fluxo.append(ft.IconButton(icon=ft.Icons.RESTART_ALT, icon_size=18, icon_color="orange400", tooltip="Reabrir", on_click=lambda e: alterar_status(id_tf, "EM ANDAMENTO")))

        edit_t = ft.TextField(value=tit, label="Título", dense=True)
        edit_d = ft.TextField(value=desc, label="Descrição", dense=True)
        edit_imp = ft.Dropdown(value=imp, dense=True, options=[ft.dropdown.Option("BAIXA"), ft.dropdown.Option("MÉDIA"), ft.dropdown.Option("ALTA")])
        edit_dt = ft.TextField(value=dt_entrega, label="Prazo (DD/MM/AAAA)", dense=True, on_change=aplicar_mascara_data)
        lbl_erro_edit = ft.Text("", color="red", size=11, weight=ft.FontWeight.BOLD)
        
        tags_globais = carregar_tags_sistema()
        tags_edicao_temp = list(lista_tags_card)
        row_tags_edit = ft.Row(wrap=True, spacing=4)

        def renderizar_tags_edicao():
            row_tags_edit.controls.clear()
            for t in tags_globais:
                sel = t in tags_edicao_temp
                def toggle_edit(e, tag=t):
                    if tag in tags_edicao_temp: tags_edicao_temp.remove(tag)
                    else: tags_edicao_temp.append(tag)
                    renderizar_tags_edicao()
                row_tags_edit.controls.append(
                    ft.Container(
                        content=ft.Text(t, size=9, color="white"),
                        bgcolor="blue700" if sel else "grey800",
                        padding=4, border_radius=8, on_click=toggle_edit
                    )
                )
            page.update()

        row_comandos_gerenciais = ft.Row([
            ft.IconButton(icon=ft.Icons.EDIT, icon_size=16, on_click=lambda e: (setattr(layout_leitura, "visible", False), setattr(layout_escrita, "visible", True), renderizar_tags_edicao(), page.update())),
            ft.IconButton(icon=ft.Icons.DELETE, icon_size=16, icon_color="red400", on_click=lambda e: deletar_tarefa(id_tf))
        ], spacing=0, visible=False)

        def alternar_comandos(e):
            if layout_leitura.visible:
                row_comandos_gerenciais.visible = not row_comandos_gerenciais.visible
                card_customizado.border = ft.Border.all(1, "grey700") if row_comandos_gerenciais.visible else ft.Border.all(1, "transparent")
                card_customizado.bgcolor = "#2d2d38" if row_comandos_gerenciais.visible else "#25252d"
                card_customizado.update()

        layout_leitura = ft.Column([
            ft.Row([
                ft.Container(content=ft.Text(imp, size=10, weight="bold", color="white"), bgcolor=cor_imp, padding=5, border_radius=4),
                row_comandos_gerenciais 
            ], alignment="spaceBetween"),
            ft.Text(tit, weight="bold", size=14),
            ft.Text(desc, size=12, color="grey400", visible=bool(desc)),
            criar_linha_prazo_com_alerta(dt_entrega, status), 
            row_tags_card,
            ft.Divider(height=10, color="transparent"),
            ft.Row([ft.Text("Ações:", size=11, color="grey500"), ft.Row(botoes_fluxo, spacing=2)], alignment="spaceBetween")
        ])

        layout_escrita = ft.Column([
            edit_t, edit_d,
            ft.Row([edit_imp, edit_dt], spacing=5),
            lbl_erro_edit,
            ft.Text("Tags:", size=11, color="grey500"),
            row_tags_edit,
            ft.Row([
                ft.IconButton(icon=ft.Icons.CHECK, icon_color="green", on_click=lambda e: salvar_edicao_tarefa(id_tf, edit_t.value, edit_d.value, edit_imp.value, edit_dt.value, tags_edicao_temp, lbl_erro_edit)),
                ft.IconButton(icon=ft.Icons.CLOSE, icon_color="red", on_click=lambda e: (setattr(layout_leitura, "visible", True), setattr(layout_escrita, "visible", False), setattr(row_comandos_gerenciais, "visible", False), page.update()))
            ], alignment="end")
        ], visible=False)

        card_customizado = ft.Container(
            padding=12, bgcolor="#25252d", border_radius=8,
            border=ft.Border.all(1, "transparent"), 
            content=ft.Column([layout_leitura, layout_escrita]),
            on_click=alternar_comandos 
        )
        return card_customizado

    def salvar_edicao_tarefa(id_tf, novo_t, nova_d, nova_imp, nova_dt, lista_tgs, lbl_erro_edit):
        if not novo_t.strip() or not nova_dt.strip() or not validar_formato_data(nova_dt.strip()):
            lbl_erro_edit.value = "Erro: Dados fornecidos sao invalidos."
            page.update()
            return
        str_tags = ",".join(lista_tgs) if lista_tgs else ""
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE tarefas SET titulo = ?, descricao = ?, importancia = ?, data_entrega = ?, tags = ? WHERE id = ? AND usuario = ?", (novo_t, nova_d, nova_imp, nova_dt.strip(), str_tags, id_tf, username))
        conn.commit()
        conn.close()
        executar_f5_da_aba()

    def salvar_tarefa(e):
        lbl_erro_criacao.value = ""
        if not txt_titulo.value or not txt_data.value or not validar_formato_data(txt_data.value.strip()):
            lbl_erro_criacao.value = "Erro: O titulo deve estar preenchido e o prazo deve ser valido."
            page.update()
            return
        str_tags = ",".join(tags_selecionadas_criacao) if tags_selecionadas_criacao else ""
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tarefas (usuario, titulo, descricao, status, importancia, data_entrega, tags) VALUES (?, ?, ?, 'A FAZER', ?, ?, ?)", (username, txt_titulo.value.strip(), txt_desc.value.strip(), drop_importancia.value, txt_data.value.strip(), str_tags))
        conn.commit()
        conn.close()
        
        txt_titulo.value = ""
        txt_desc.value = ""
        txt_data.value = datetime.now().strftime("%d/%m/%Y")
        tags_selecionadas_criacao.clear()
        renderizar_tags_criacao()
        executar_f5_da_aba()

    # ----------------------------------------------------
    # 3. ROTINA DE SINCRO E ORDENAÇÃO SOB DEMANDA (RESET DE CONTROLES)
    # ----------------------------------------------------
    def executar_f5_da_aba(e=None):
        if drop_ordenacao.value:
            criar_aba_tarefas.criterio_atual = drop_ordenacao.value

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, titulo, descricao, status, importancia, data_entrega, tags FROM tarefas WHERE usuario = ?", (username,))
        dados_brutos = cursor.fetchall()
        conn.close()

        tarefas_processadas = []
        for id_tf, tit, desc, status, imp, dt_entrega, tgs in dados_brutos:
            # ISO-formatting ad-hoc para correta ordenacao lexicografica das strings no sort.
            if dt_entrega and len(dt_entrega) == 10:
                parts = dt_entrega.split("/")
                data_invertida = f"{parts[2]}-{parts[1]}-{parts[0]}" if len(parts) == 3 else "9999-12-31"
            else:
                data_invertida = "9999-12-31"
            tarefas_processadas.append({"id": id_tf, "titulo": tit, "descricao": desc, "status": status, "importancia": imp, "data_entrega": dt_entrega, "tags": tgs, "data_ordenacao": data_invertida})

        if criar_aba_tarefas.criterio_atual == "PRAZO":
            tarefas_processadas.sort(key=lambda x: x["data_ordenacao"])
        elif criar_aba_tarefas.criterio_atual == "NOME":
            tarefas_processadas.sort(key=lambda x: x["titulo"].lower())
        elif criar_aba_tarefas.criterio_atual == "IMPORTANCIA":
            peso = {"ALTA": 1, "MÉDIA": 2, "BAIXA": 3}
            tarefas_processadas.sort(key=lambda x: peso.get(x["importancia"], 2))

        col_f = ft.ListView(expand=True, spacing=10)
        col_a = ft.ListView(expand=True, spacing=10)
        col_c = ft.ListView(expand=True, spacing=10)

        for tf in tarefas_processadas:
            card = criar_card_tarefa(tf["id"], tf["titulo"], tf["descricao"], tf["status"], tf["importancia"], tf["data_entrega"], tf["tags"])
            if tf["status"] == "A FAZER": col_f.controls.append(card)
            elif tf["status"] == "EM ANDAMENTO": col_a.controls.append(card)
            elif tf["status"] == "CONCLUIDO": col_c.controls.append(card)

        quadro_reconstruido = ft.Row([
            ft.Container(expand=1, bgcolor="#1e1e24", padding=10, border_radius=8, content=ft.Column([ft.Text("A FAZER", weight="bold", color="blue400"), ft.Divider(color="blue900"), col_f])),
            ft.Container(expand=1, bgcolor="#1e1e24", padding=10, border_radius=8, content=ft.Column([ft.Text("EM PROGRESSO", weight="bold", color="orange400"), ft.Divider(color="orange900"), col_a])),
            ft.Container(expand=1, bgcolor="#1e1e24", padding=10, border_radius=8, content=ft.Column([ft.Text("CONCLUIDO", weight="bold", color="green400"), ft.Divider(color="green900"), col_c])),
        ], expand=True, spacing=15)

        conteiner_quadro_dinamico.content = quadro_reconstruido
        
        try:
            page.update()
        except:
            pass

    btn_mini_ordenar = ft.IconButton(
        icon=ft.Icons.REFRESH,
        icon_size=20,
        icon_color="grey400",
        tooltip="Aplicar Ordenacao",
        on_click=executar_f5_da_aba
    )

    def renderizar_tags_criacao():
        row_tags_criacao.controls.clear()
        tags_globais = carregar_tags_sistema()
        for t in tags_globais:
            is_sel = t in tags_selecionadas_criacao
            def toggle(e, tag=t):
                if tag in tags_selecionadas_criacao: tags_selecionadas_criacao.remove(tag)
                else: tags_selecionadas_criacao.append(tag)
                renderizar_tags_criacao()
            row_tags_criacao.controls.append(
                ft.Container(
                    content=ft.Text(t, size=10, color="white"),
                    bgcolor="blue700" if is_sel else "grey800",
                    padding=6, border_radius=10, on_click=toggle
                )
            )
        page.update()

    # ----------------------------------------------------
    # 4. MONTAGEM E RETORNO ESTRUTURAL DA VIEW
    # ----------------------------------------------------
    layout_tarefas = ft.Column([
        ft.Row([
            ft.Text("Quadro Kanban Corporativo", size=22, weight="bold"),
            ft.Row([drop_ordenacao, btn_mini_ordenar], spacing=0, alignment="center")
        ], alignment="spaceBetween"),
        ft.Divider(),
        
        ft.Row([txt_data, txt_titulo, txt_desc, drop_importancia, ft.Container(content=ft.TextButton(content=ft.Text("Criar", color="white"), on_click=salvar_tarefa), bgcolor="blue", border_radius=5, height=40)], spacing=10, alignment="start", wrap=True),
        lbl_erro_criacao,
        ft.Text("Selecione as Tags para a nova tarefa:", size=11, color="grey500"),
        row_tags_criacao,
        conteiner_quadro_dinamico 
    ], expand=True, visible=False)

    renderizar_tags_criacao()
    executar_f5_da_aba()
    
    return layout_tarefas, executar_f5_da_aba