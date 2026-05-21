import flet as ft
from database.db_manager import conectar_db

def criar_aba_brain(page: ft.Page, username: str):
    txt_nota_titulo = ft.TextField(label="Título do Insight", width=300, hint_text="Ex: Dica de Python")
    txt_nota_conteudo = ft.TextField(label="Conteúdo da Nota (Opcional)", width=600, multiline=True, min_lines=3, max_lines=6)
    
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

    # Executa a renderização inicial das tags e notas
    renderizar_tags_criacao() 
    atualizar_notas()

    return layout_brain