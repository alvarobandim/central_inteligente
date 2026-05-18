# Tela de Dashboard - Finanças e Second Brain
# Aqui tem muita lógica junta, então separei em blocos para ficar mais fácil de ler.
import flet as ft
import csv
import os
from database.db_manager import conectar_db

def carregar_dashboard(page: ft.Page, username: str):
    page.clean() # Limpa a tela de login antes de carregar o painel
    page.title = f"Central Inteligente - Painel de {username.capitalize()}"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = "start"

    # ==========================================
    # 1. TELA DE FINANÇAS
    # ==========================================
    
    # Campos para adicionar uma nova despesa ou receita
    drop_tipo = ft.Dropdown(label="Tipo", width=110, options=[ft.dropdown.Option("RECEITA"), ft.dropdown.Option("DESPESA")], value="DESPESA")
    txt_valor = ft.TextField(label="Valor (R$)", width=110, hint_text="0.00", keyboard_type="number")
    txt_descricao = ft.TextField(label="Descrição", width=220, hint_text="Opcional")
    txt_filtro = ft.TextField(width=250, hint_text="Filtrar Categoria...", prefix_icon=ft.Icons.SEARCH)
    
    # Textos que vão mostrar os totais calculados
    lbl_tot_receitas = ft.Text(value="Receitas: R$ 0.00", color="green", size=16, weight=ft.FontWeight.W_500)
    lbl_tot_despesas = ft.Text(value="Despesas: R$ 0.00", color="red", size=16, weight=ft.FontWeight.W_500)
    lbl_balanco = ft.Text(value="Balanço Geral: R$ 0.00", size=22, weight=ft.FontWeight.BOLD)
    
    # Coluna onde vou desenhar os gráficos na mão
    painel_graficos = ft.Column(spacing=15, expand=True)
    
    lista_transacoes = ft.ListView(expand=True, spacing=10, padding=20)
    lbl_aviso_export = ft.Text("", size=12, color="green", weight=ft.FontWeight.BOLD)

    # Lógica para mostrar/esconder o campo de criar nova categoria (Deu trabalho isso aqui!)
    drop_categoria = ft.Dropdown(label="Categoria", width=160, visible=True)
    txt_nova_categoria = ft.TextField(label="Nova Categoria", width=160, visible=False)
    
    def atualizar_dropdown_categorias(selecionar_nova=None):
        # Puxa as categorias do banco e joga no dropdown
        drop_categoria.options.clear()
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM categorias WHERE usuario = 'sistema' OR usuario = ? ORDER BY nome ASC", (username,))
        for (nome_cat,) in cursor.fetchall():
            drop_categoria.options.append(ft.dropdown.Option(nome_cat))
        conn.close()
        
        if selecionar_nova:
            drop_categoria.value = selecionar_nova
        elif drop_categoria.options and not drop_categoria.value:
            drop_categoria.value = drop_categoria.options[0].key
        page.update()

    def iniciar_nova_categoria(e):
        # Esconde o dropdown e mostra o input de texto
        drop_categoria.visible = False
        btn_add_cat.visible = False
        txt_nova_categoria.visible = True
        btn_save_cat.visible = True
        btn_cancel_cat.visible = True
        txt_nova_categoria.focus()
        page.update()

    def cancelar_nova_categoria(e):
        txt_nova_categoria.value = ""
        txt_nova_categoria.visible = False
        btn_save_cat.visible = False
        btn_cancel_cat.visible = False
        drop_categoria.visible = True
        btn_add_cat.visible = True
        page.update()

    def salvar_nova_categoria(e):
        nova_cat = txt_nova_categoria.value.strip().upper()
        if nova_cat:
            conn = conectar_db()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO categorias (usuario, nome) VALUES (?, ?)", (username, nova_cat))
                conn.commit()
            except:
                pass # Ignora se já existir uma categoria com o mesmo nome
            finally:
                conn.close()
            atualizar_dropdown_categorias(selecionar_nova=nova_cat)
        cancelar_nova_categoria(None)

    # Para salvar direto dando ENTER no teclado
    txt_nova_categoria.on_submit = salvar_nova_categoria

    btn_add_cat = ft.IconButton(icon=ft.Icons.ADD, icon_color="grey500", icon_size=20, tooltip="Adicionar Categoria", on_click=iniciar_nova_categoria, visible=True)
    btn_save_cat = ft.IconButton(icon=ft.Icons.CHECK, icon_color="green", icon_size=20, tooltip="Salvar", on_click=salvar_nova_categoria, visible=False)
    btn_cancel_cat = ft.IconButton(icon=ft.Icons.CLOSE, icon_color="red", icon_size=20, tooltip="Cancelar", on_click=cancelar_nova_categoria, visible=False)

    def deletar_transacao(id_registro):
        # Remove a finança do banco usando o ID e atualiza a tela
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM financas WHERE id = ? AND usuario = ?", (id_registro, username))
        conn.commit()
        conn.close()
        atualizar_financeiro()

    def salvar_transacao(e):
        if not txt_valor.value or not drop_categoria.value:
            return
        try:
            # Troca vírgula por ponto para o banco de dados não dar erro no float
            valor = float(txt_valor.value.replace(",", "."))
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO financas (usuario, tipo, categoria, valor, descricao) VALUES (?, ?, ?, ?, ?)", (username, drop_tipo.value, drop_categoria.value, valor, txt_descricao.value.strip()))
            conn.commit()
            conn.close()
            txt_valor.value = ""
            txt_descricao.value = ""
            atualizar_financeiro()
        except ValueError:
            pass # Se o cara digitar letras no valor, só ignora

    def construir_barra_grafico(dados, total, titulo, paleta_cores):
        # Função para desenhar o gráfico empilhado calculando a % de cada categoria
        if not dados or total <= 0:
            return ft.Text(f"Sem dados de {titulo.lower()}.", size=12, color="grey500", italic=True)
        
        barra_mestra = ft.Row(spacing=0, height=15)
        legenda_grafico = ft.Row(wrap=True, spacing=10)
        
        for i, (cat, val) in enumerate(dados):
            cor_fatia = paleta_cores[i % len(paleta_cores)]
            percentual = (val / total) * 100
            
            # O "expand" faz a matemática visual baseada no valor para desenhar a barra certa
            barra_mestra.controls.append(
                ft.Container(
                    bgcolor=cor_fatia,
                    expand=int(val * 100), 
                    tooltip=f"{cat}: R$ {val:.2f} ({percentual:.1f}%)"
                )
            )
            
            legenda_grafico.controls.append(
                ft.Row([
                    ft.Container(width=10, height=10, bgcolor=cor_fatia, border_radius=5),
                    ft.Text(f"{cat} ({percentual:.1f}%)", size=11, color="grey300")
                ], spacing=4)
            )
            
        return ft.Column([
            ft.Text(titulo, size=12, color="grey500"),
            ft.Container(content=barra_mestra, border_radius=8, clip_behavior=ft.ClipBehavior.HARD_EDGE),
            legenda_grafico
        ], spacing=5)

    def atualizar_financeiro(e=None):
        lista_transacoes.controls.clear()
        conn = conectar_db()
        cursor = conn.cursor()
        
        # 1. Atualiza as somas totais lá em cima
        cursor.execute("SELECT tipo, SUM(valor) FROM financas WHERE usuario = ? GROUP BY tipo", (username,))
        totais = dict(cursor.fetchall())
        receitas = totais.get("RECEITA", 0.0)
        despesas = totais.get("DESPESA", 0.0)
        balanco = receitas - despesas
        
        lbl_tot_receitas.value = f"Receitas: R$ {receitas:.2f}"
        lbl_tot_despesas.value = f"Despesas: R$ {despesas:.2f}"
        lbl_balanco.value = f"Balanço Geral: R$ {balanco:.2f}"
        lbl_balanco.color = "green" if balanco >= 0 else "red"
        
        # 2. Desenha os gráficos na tela
        painel_graficos.controls.clear()
        
        cursor.execute("SELECT categoria, SUM(valor) FROM financas WHERE usuario = ? AND tipo = 'RECEITA' GROUP BY categoria", (username,))
        dados_rec = cursor.fetchall()
        
        cursor.execute("SELECT categoria, SUM(valor) FROM financas WHERE usuario = ? AND tipo = 'DESPESA' GROUP BY categoria", (username,))
        dados_desp = cursor.fetchall()

        cores_receitas = ["#10b981", "#059669", "#34d399", "#047857", "#6ee7b7"] 
        cores_despesas = ["#ef4444", "#f97316", "#eab308", "#ec4899", "#a855f7"] 

        painel_graficos.controls.append(construir_barra_grafico(dados_rec, receitas, "Distribuição de Receitas", cores_receitas))
        painel_graficos.controls.append(construir_barra_grafico(dados_desp, despesas, "Distribuição de Despesas", cores_despesas))

        # 3. Lista o extrato debaixo dos inputs
        termo_busca = txt_filtro.value.strip().upper()
        if termo_busca:
            cursor.execute("SELECT id, tipo, categoria, valor, descricao FROM financas WHERE usuario = ? AND categoria LIKE ? ORDER BY id DESC", (username, f"%{termo_busca}%"))
        else:
            cursor.execute("SELECT id, tipo, categoria, valor, descricao FROM financas WHERE usuario = ? ORDER BY id DESC LIMIT 15", (username,))
            
        for item_id, tipo, cat, val, desc in cursor.fetchall():
            cor = "green" if tipo == "RECEITA" else "red"
            sinal = "+" if tipo == "RECEITA" else "-"
            emoji = "💰" if tipo == "RECEITA" else "💸"
            
            # Precisou criar essa função separada (closure) para o botão deletar o ID certo no laço for
            def criar_evento_excluir(id_alvo):
                return lambda x: deletar_transacao(id_alvo)

            lista_transacoes.controls.append(
                ft.ListTile(
                    leading=ft.Text(emoji, size=20),
                    title=ft.Text(f"{cat} - {desc if desc else ''}"),
                    subtitle=ft.Text(f"{sinal} R$ {val:.2f}", color=cor, weight=ft.FontWeight.BOLD),
                    trailing=ft.IconButton(icon=ft.Icons.DELETE, icon_color="red700", tooltip="Excluir Registro", on_click=criar_evento_excluir(item_id))
                )
            )
        conn.close()
        page.update()

    txt_filtro.on_submit = atualizar_financeiro

    def exportar_para_csv(e):
        # Pega as finanças e gera um arquivo .csv pra abrir no Excel
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT tipo, categoria, valor, descricao FROM financas WHERE usuario = ? ORDER BY id DESC", (username,))
        transacoes = cursor.fetchall()
        conn.close()

        if not transacoes:
            lbl_aviso_export.value = "⚠️ Nenhuma transação para exportar!"
            lbl_aviso_export.color = "orange"
            page.update()
            return

        nome_arquivo = f"extrato_financas_{username}.csv"
        
        with open(nome_arquivo, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['TIPO', 'CATEGORIA', 'VALOR (R$)', 'DESCRICAO'])
            for tipo, cat, val, desc in transacoes:
                # Arrumando a vírgula pro Excel brasileiro não bugar os números
                val_formatado = f"{val:.2f}".replace('.', ',')
                writer.writerow([tipo, cat, val_formatado, desc])
        
        caminho_completo = os.path.abspath(nome_arquivo)
        lbl_aviso_export.value = f"✅ Exportado com sucesso!"
        lbl_aviso_export.color = "green"
        page.update()


    # ==========================================
    # 2. TELA DO SECOND BRAIN (NOTAS E INSIGHTS)
    # ==========================================
    txt_nota_titulo = ft.TextField(label="Título do Insight", width=300, hint_text="Ex: Dica de Python")
    txt_nota_conteudo = ft.TextField(label="Conteúdo da Nota (Opcional)", width=600, multiline=True, min_lines=3, max_lines=6)
    
    # Em vez de dropdown chato, criei um sistema de botões clicáveis para as tags
    row_tags_criacao = ft.Row(wrap=True, spacing=10)
    tags_acumuladas_criacao = [] 

    txt_nova_tag = ft.TextField(label="Nova Tag", width=160, dense=True)
    row_input_nova_tag = ft.Row([
        txt_nova_tag,
        ft.IconButton(icon=ft.Icons.CHECK, icon_color="green", on_click=lambda e: salvar_nova_tag(e)),
        ft.IconButton(icon=ft.Icons.CLOSE, icon_color="red", on_click=lambda e: cancelar_nova_tag(e))
    ], visible=False)

    txt_filtro_notas = ft.TextField(label="Buscar em Título, Conteúdo ou Tags...", width=350, prefix_icon=ft.Icons.SEARCH)
    lista_notas = ft.ListView(expand=True, spacing=15, padding=20)

    def carregar_tags_disponiveis():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM tags WHERE usuario = 'sistema' OR usuario = ? ORDER BY nome ASC", (username,))
        tags_db = [r[0] for r in cursor.fetchall()]
        conn.close()
        return tags_db

    def renderizar_tags_criacao():
        row_tags_criacao.controls.clear()
        tags_db = carregar_tags_disponiveis()
        
        for t in tags_db:
            is_selected = t in tags_acumuladas_criacao
            
            def toggle_evento(e, tag_alvo=t):
                # Se clica acende, clica de novo apaga
                if tag_alvo in tags_acumuladas_criacao:
                    tags_acumuladas_criacao.remove(tag_alvo)
                else:
                    tags_acumuladas_criacao.append(tag_alvo)
                renderizar_tags_criacao()

            row_tags_criacao.controls.append(
                ft.Container(
                    content=ft.Text(t, size=11, color="white", weight=ft.FontWeight.BOLD),
                    bgcolor="blue700" if is_selected else "grey800",
                    padding=10,
                    border_radius=15,
                    on_click=toggle_evento
                )
            )
        
        row_tags_criacao.controls.append(
            ft.Container(
                content=ft.Text("+ NOVA TAG", size=11, color="grey300", weight=ft.FontWeight.BOLD),
                bgcolor="#111111",
                padding=10,
                border_radius=15,
                on_click=iniciar_nova_tag
            )
        )
        page.update()

    def iniciar_nova_tag(e):
        row_tags_criacao.visible = False
        row_input_nova_tag.visible = True
        txt_nova_tag.focus()
        page.update()

    def cancelar_nova_tag(e):
        txt_nova_tag.value = ""
        row_input_nova_tag.visible = False
        row_tags_criacao.visible = True
        page.update()

    def salvar_nova_tag(e):
        nova_tg = txt_nova_tag.value.strip().upper()
        if nova_tg:
            conn = conectar_db()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO tags (usuario, nome) VALUES (?, ?)", (username, nova_tg))
                conn.commit()
            except:
                pass
            finally:
                conn.close()
            
            if nova_tg not in tags_acumuladas_criacao:
                tags_acumuladas_criacao.append(nova_tg)
            
            renderizar_tags_criacao()
        cancelar_nova_tag(None)

    txt_nova_tag.on_submit = salvar_nova_tag

    def deletar_nota(id_registro):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notas WHERE id = ? AND usuario = ?", (id_registro, username))
        conn.commit()
        conn.close()
        atualizar_notas()

    def atualizar_notes_e_limpar_memoria():
        tags_acumuladas_criacao.clear()
        renderizar_tags_criacao()
        atualizar_notas()

    def salvar_nota(e):
        if not txt_nota_titulo.value:
            return
        # Junta todas as tags selecionadas num texto só separado por vírgula pro banco
        str_tags_salvar = ",".join(tags_acumuladas_criacao) if tags_acumuladas_criacao else "SEM TAG"
        
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notas (usuario, titulo, conteudo, tags) VALUES (?, ?, ?, ?)",
            (username, txt_nota_titulo.value.strip(), txt_nota_conteudo.value.strip(), str_tags_salvar)
        )
        conn.commit()
        conn.close()
        txt_nota_titulo.value = ""
        txt_nota_conteudo.value = ""
        atualizar_notes_e_limpar_memoria()

    def atualizar_notas(e=None):
        lista_notas.controls.clear()
        conn = conectar_db()
        cursor = conn.cursor()
        
        tags_globais = carregar_tags_disponiveis()
        termo_busca = txt_filtro_notas.value.strip().lower()
        
        # Filtro legal que busca em qualquer lugar da nota
        if termo_busca:
            query = """
                SELECT id, titulo, conteudo, tags FROM notas 
                WHERE usuario = ? 
                AND (LOWER(titulo) LIKE ? OR LOWER(conteudo) LIKE ? OR LOWER(tags) LIKE ?) 
                ORDER BY id DESC
            """
            param_busca = f"%{termo_busca}%"
            cursor.execute(query, (username, param_busca, param_busca, param_busca))
        else:
            cursor.execute("SELECT id, titulo, conteudo, tags FROM notas WHERE usuario = ? ORDER BY id DESC", (username,))
            
        for nota_id, tit, cont, tags_string in cursor.fetchall():
            lista_tags_da_nota = [t.strip() for t in tags_string.split(",") if t.strip() and t.strip() != "SEM TAG"]

            def criar_evento_excluir_nota(id_alvo):
                return lambda x: deletar_nota(id_alvo)

            lbl_tit = ft.Text(f"💡 {tit}", size=18, weight=ft.FontWeight.BOLD, color="lightblue", expand=True)
            lbl_cont = ft.Text(cont, size=15, visible=bool(cont))
            
            row_tags_card_leitura = ft.Row(spacing=5, wrap=True)
            if lista_tags_da_nota:
                for tg in lista_tags_da_nota:
                    row_tags_card_leitura.controls.append(
                        ft.Container(
                            content=ft.Text(tg, size=10, color="white", weight=ft.FontWeight.W_600),
                            bgcolor="grey800",
                            padding=5,
                            border_radius=4
                        )
                    )

            # --- PARTE DE EDITAR A NOTA CLICANDO NELA ---
            edit_tit = ft.TextField(value=tit, label="Editar Título", width=250, dense=True)
            edit_cont = ft.TextField(value=cont, label="Editar Conteúdo", multiline=True, min_lines=2, max_lines=4, expand=True)
            
            tags_temporarias_edicao = list(lista_tags_da_nota)
            row_chips_edicao = ft.Row(wrap=True, spacing=5)

            def renderizar_chips_edicao():
                row_chips_edicao.controls.clear()
                for t in tags_globais:
                    is_sel = t in tags_temporarias_edicao
                    
                    def toggle_edit_ev(e, tag_alvo=t, l_temp=tags_temporarias_edicao):
                        if tag_alvo in l_temp:
                            l_temp.remove(tag_alvo)
                        else:
                            l_temp.append(tag_alvo)
                        renderizar_chips_edicao()
                        
                    row_chips_edicao.controls.append(
                        ft.Container(
                            content=ft.Text(t, size=10, color="white"),
                            bgcolor="blue700" if is_sel else "grey800",
                            padding=8,
                            border_radius=12,
                            on_click=toggle_edit_ev
                        )
                    )
                page.update()

            def ligar_modo_edicao(e, layout_view, layout_edit):
                layout_view.visible = False
                layout_edit.visible = True
                renderizar_chips_edicao()
                page.update()

            def desligar_modo_edicao(e, layout_view, layout_edit):
                layout_view.visible = True
                layout_edit.visible = False
                page.update()

            def processar_salvamento_edicao(e, id_alvo, campo_tit, campo_cont, lista_tg_final):
                t_novo = campo_tit.value.strip()
                c_novo = campo_cont.value.strip()
                str_tags_final = ",".join(lista_tg_final) if lista_tg_final else "SEM TAG"
                if not t_novo:
                    return
                
                conn_edit = conectar_db()
                cursor_edit = conn_edit.cursor()
                cursor_edit.execute(
                    "UPDATE notas SET titulo = ?, conteudo = ?, tags = ? WHERE id = ? AND usuario = ?",
                    (t_novo, c_novo, str_tags_final, id_alvo, username)
                )
                conn_edit.commit()
                conn_edit.close()
                atualizar_notas()

            # Desenho de como a nota aparece quando só estou lendo
            layout_modo_leitura = ft.Column([
                ft.Row([
                    lbl_tit,
                    ft.Row([
                        ft.IconButton(icon=ft.Icons.EDIT, icon_color="blue400", tooltip="Editar Insight", on_click=lambda e, lv=None, le=None: ligar_modo_edicao(e, layout_view=layout_modo_leitura, layout_edit=layout_modo_escrita)),
                        ft.IconButton(icon=ft.Icons.DELETE, icon_color="red400", tooltip="Apagar Insight", on_click=criar_evento_excluir_nota(nota_id))
                    ], spacing=0)
                ], alignment="spaceBetween"),
                lbl_cont,
                ft.Container(height=5),
                row_tags_card_leitura
            ], visible=True)

            # Desenho de como a nota fica quando clico em editar
            layout_modo_escrita = ft.Column([
                ft.Row([
                    edit_tit,
                    ft.Row([
                        ft.IconButton(icon=ft.Icons.CHECK, icon_color="green", tooltip="Salvar Alterações", on_click=lambda e, idx=nota_id, ct=edit_tit, cc=edit_cont, lt=tags_temporarias_edicao: processar_salvamento_edicao(e, idx, ct, cc, lt)),
                        ft.IconButton(icon=ft.Icons.CLOSE, icon_color="red", tooltip="Cancelar", on_click=lambda e: desligar_modo_edicao(e, layout_view=layout_modo_leitura, layout_edit=layout_modo_escrita))
                    ], spacing=0)
                ], alignment="spaceBetween"),
                ft.Text("Clique para adicionar/remover tags:", size=12, color="grey500"),
                row_chips_edicao,
                ft.Container(height=5),
                edit_cont
            ], visible=False)

            # Monta o card principal da nota
            card_nota = ft.Card(
                elevation=4,
                content=ft.Container(
                    padding=0,
                    content=ft.Row([
                        ft.Container(width=6, bgcolor="#2e7d32"), 
                        ft.Container(
                            padding=20,
                            expand=True,
                            content=ft.Column([layout_modo_leitura, layout_modo_escrita])
                        )
                    ], spacing=0) 
                )
            )
            lista_notas.controls.append(card_nota)
            
        conn.close()
        page.update()

    txt_filtro_notas.on_submit = atualizar_notas


    # ==========================================
    # 3. MONTAGEM FINAL DA TELA E DOS MENUS
    # ==========================================
    
    painel_resumo_financeiro = ft.Row([
        ft.Column([
            ft.Text("Resumo Financeiro", size=18, weight=ft.FontWeight.BOLD, color="grey300"),
            lbl_tot_receitas, 
            lbl_tot_despesas,
            lbl_balanco
        ], expand=1), 
        
        ft.Container(
            content=painel_graficos,
            width=500,
            alignment=ft.Alignment(1, 0)
        )
    ], alignment="spaceBetween")

    layout_financas = ft.Column([
        ft.Text("Controle de Inteligência Financeira", size=22, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        painel_resumo_financeiro,
        ft.Divider(),
        
        ft.Row([
            drop_tipo, 
            txt_valor, 
            ft.Row([drop_categoria, txt_nova_categoria, btn_add_cat, btn_save_cat, btn_cancel_cat], spacing=0), 
            txt_descricao, 
            ft.Container(content=ft.TextButton(content=ft.Text("Lançar", color="white"), on_click=salvar_transacao), bgcolor="blue", border_radius=5, height=45, alignment=ft.Alignment(0, 0))
        ], alignment="start", spacing=15),
        
        ft.Divider(),
        
        ft.Row([
            txt_filtro,
            ft.Container(content=ft.TextButton(content=ft.Text("Limpar", color="white"), on_click=lambda e: (setattr(txt_filtro, "value", ""), atualizar_financeiro())), bgcolor="grey700", border_radius=5),
            ft.Container(content=ft.TextButton(content=ft.Text("📥 Exportar CSV", color="white"), on_click=exportar_para_csv), bgcolor="green700", border_radius=5),
            lbl_aviso_export
        ], spacing=10, alignment="start"),
        
        ft.Text("Histórico Recente de Lançamentos", size=16, weight=ft.FontWeight.W_500),
        lista_transacoes
    ], expand=True, visible=True)

    layout_brain = ft.Column([
        ft.Text("Second Brain - Central de Conhecimento & Insights", size=22, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        
        ft.Row([
            txt_nota_titulo,
            ft.Container(content=ft.TextButton(content=ft.Text("Fixar Insight", color="white"), on_click=salvar_nota), bgcolor="green", border_radius=5, height=45)
        ], alignment="spaceBetween"),
        
        ft.Text("Selecione as Tags:", size=12, color="grey500"),
        row_tags_criacao,
        row_input_nova_tag,
        
        txt_nota_conteudo,
        
        ft.Divider(),
        
        ft.Row([
            txt_filtro_notas,
            ft.Container(content=ft.TextButton(content=ft.Text("Limpar Busca", color="white"), on_click=lambda e: (setattr(txt_filtro_notas, "value", ""), atualizar_notas())), bgcolor="grey700", border_radius=5),
        ]),
        
        ft.Text("Seus Insights e Notas Salvas", size=16, weight=ft.FontWeight.W_500),
        lista_notas
    ], expand=True, visible=False)

    def ir_para_financas(e):
        layout_financas.visible = True
        layout_brain.visible = False
        atualizar_financeiro()
        page.update()

    def ir_para_brain(e):
        layout_financas.visible = False
        layout_brain.visible = True
        atualizar_notas()
        page.update()

    def processar_logout(e):
        # Desloga e manda de volta pra tela de login
        from views.login_view import exibir_tela_login
        exibir_tela_login(page)

    menu_superior = ft.Row([
        ft.Container(content=ft.TextButton(content=ft.Text("💰 Finanças", color="white"), on_click=ir_para_financas), bgcolor="blue", border_radius=5),
        ft.Container(content=ft.TextButton(content=ft.Text("💡 Second Brain", color="white"), on_click=ir_para_brain), bgcolor="green", border_radius=5),
        ft.VerticalDivider(expand=True), 
        ft.Container(content=ft.TextButton(content=ft.Text("🚪 Sair", color="white"), on_click=processar_logout), bgcolor="red", border_radius=5),
    ], spacing=10)

    # Inicia a tela carregando tudo pra não ficar em branco
    atualizar_dropdown_categorias()
    renderizar_tags_criacao() 
    atualizar_financeiro()
    atualizar_notas()
    
    page.add(
        ft.Column([
            menu_superior,
            ft.Divider(),
            layout_financas,
            layout_brain
        ], expand=True)
    )