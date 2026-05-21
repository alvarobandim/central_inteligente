import flet as ft
import csv
import os
from database.db_manager import conectar_db

def criar_aba_financas(page: ft.Page, username: str):
    drop_tipo = ft.Dropdown(label="Tipo", width=110, options=[ft.dropdown.Option("RECEITA"), ft.dropdown.Option("DESPESA")], value="DESPESA")
    txt_valor = ft.TextField(label="Valor (R$)", width=110, hint_text="0.00", keyboard_type="number")
    txt_descricao = ft.TextField(label="Descrição", width=220, hint_text="Opcional")
    txt_filtro = ft.TextField(width=250, hint_text="Filtrar Categoria...", prefix_icon=ft.Icons.SEARCH)
    
    lbl_tot_receitas = ft.Text(value="Receitas: R$ 0.00", color="green", size=16, weight=ft.FontWeight.W_500)
    lbl_tot_despesas = ft.Text(value="Despesas: R$ 0.00", color="red", size=16, weight=ft.FontWeight.W_500)
    lbl_balanco = ft.Text(value="Balanço Geral: R$ 0.00", size=22, weight=ft.FontWeight.BOLD)
    
    painel_graficos = ft.Column(spacing=15, expand=True)
    lista_transacoes = ft.ListView(expand=True, spacing=10, padding=20)
    lbl_aviso_export = ft.Text("", size=12, color="green", weight=ft.FontWeight.BOLD)

    drop_categoria = ft.Dropdown(label="Categoria", width=160, visible=True)
    txt_nova_categoria = ft.TextField(label="Nova Categoria", width=160, visible=False)
    
    def atualizar_dropdown_categorias(selecionar_nova=None):
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
                pass 
            finally:
                conn.close()
            atualizar_dropdown_categorias(selecionar_nova=nova_cat)
        cancelar_nova_categoria(None)

    txt_nova_categoria.on_submit = salvar_nova_categoria

    btn_add_cat = ft.IconButton(icon=ft.Icons.ADD, icon_color="grey500", icon_size=20, tooltip="Adicionar Categoria", on_click=iniciar_nova_categoria, visible=True)
    btn_save_cat = ft.IconButton(icon=ft.Icons.CHECK, icon_color="green", icon_size=20, tooltip="Salvar", on_click=salvar_nova_categoria, visible=False)
    btn_cancel_cat = ft.IconButton(icon=ft.Icons.CLOSE, icon_color="red", icon_size=20, tooltip="Cancelar", on_click=cancelar_nova_categoria, visible=False)

    def deletar_transacao(id_registro):
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
            pass 

    def construir_barra_grafico(dados, total, titulo, paleta_cores):
        if not dados or total <= 0:
            return ft.Text(f"Sem dados de {titulo.lower()}.", size=12, color="grey500", italic=True)
        
        barra_mestra = ft.Row(spacing=0, height=15)
        legenda_grafico = ft.Row(wrap=True, spacing=10)
        
        for i, (cat, val) in enumerate(dados):
            cor_fatia = paleta_cores[i % len(paleta_cores)]
            percentual = (val / total) * 100
            
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
        
        cursor.execute("SELECT tipo, SUM(valor) FROM financas WHERE usuario = ? GROUP BY tipo", (username,))
        totais = dict(cursor.fetchall())
        receitas = totais.get("RECEITA", 0.0)
        despesas = totais.get("DESPESA", 0.0)
        balanco = receitas - despesas
        
        lbl_tot_receitas.value = f"Receitas: R$ {receitas:.2f}"
        lbl_tot_despesas.value = f"Despesas: R$ {despesas:.2f}"
        lbl_balanco.value = f"Balanço Geral: R$ {balanco:.2f}"
        lbl_balanco.color = "green" if balanco >= 0 else "red"
        
        painel_graficos.controls.clear()
        
        cursor.execute("SELECT categoria, SUM(valor) FROM financas WHERE usuario = ? AND tipo = 'RECEITA' GROUP BY categoria", (username,))
        dados_rec = cursor.fetchall()
        
        cursor.execute("SELECT categoria, SUM(valor) FROM financas WHERE usuario = ? AND tipo = 'DESPESA' GROUP BY categoria", (username,))
        dados_desp = cursor.fetchall()

        cores_receitas = ["#10b981", "#059669", "#34d399", "#047857", "#6ee7b7"] 
        cores_despesas = ["#ef4444", "#f97316", "#eab308", "#ec4899", "#a855f7"] 

        painel_graficos.controls.append(construir_barra_grafico(dados_rec, receitas, "Distribuição de Receitas", cores_receitas))
        painel_graficos.controls.append(construir_barra_grafico(dados_desp, despesas, "Distribuição de Despesas", cores_despesas))

        termo_busca = txt_filtro.value.strip().upper()
        if termo_busca:
            cursor.execute("SELECT id, tipo, categoria, valor, descricao FROM financas WHERE usuario = ? AND categoria LIKE ? ORDER BY id DESC", (username, f"%{termo_busca}%"))
        else:
            cursor.execute("SELECT id, tipo, categoria, valor, descricao FROM financas WHERE usuario = ? ORDER BY id DESC LIMIT 15", (username,))
            
        for item_id, tipo, cat, val, desc in cursor.fetchall():
            cor = "green" if tipo == "RECEITA" else "red"
            sinal = "+" if tipo == "RECEITA" else "-"
            emoji = "💰" if tipo == "RECEITA" else "💸"
            
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
                val_formatado = f"{val:.2f}".replace('.', ',')
                writer.writerow([tipo, cat, val_formatado, desc])
        
        lbl_aviso_export.value = f"✅ Exportado com sucesso!"
        lbl_aviso_export.color = "green"
        page.update()

    painel_resumo_financeiro = ft.Row([
        ft.Column([
            ft.Text("Resumo Financeiro", size=18, weight=ft.FontWeight.BOLD, color="grey300"),
            lbl_tot_receitas, 
            lbl_tot_despesas,
            lbl_balanco
        ], expand=1), 
        ft.Container(content=painel_graficos, width=500, alignment=ft.Alignment(1, 0))
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

    # Executa as funções iniciais antes de devolver o layout
    atualizar_dropdown_categorias()
    atualizar_financeiro()

    return layout_financas