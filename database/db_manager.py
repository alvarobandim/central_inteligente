"""
Module: Database Manager
Description: Gerenciamento do banco de dados SQLite com suporte a tabelas
             de usuários, finanças, notas, categorias e tags customizadas.
"""
import sqlite3

def conectar_db():
    return sqlite3.connect("central_inteligente.db")

def inicializar_banco():
    conn = conectar_db()
    cursor = conn.cursor()
    
    # 1. Tabela de Usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    """)
    
    # 2. Tabela de Finanças
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        tipo TEXT NOT NULL,
        categoria TEXT NOT NULL,
        valor REAL NOT NULL,
        descricao TEXT
    )
    """)
    
    # 3. Tabela de Notas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        titulo TEXT NOT NULL,
        conteudo TEXT NOT NULL,
        tags TEXT
    )
    """)
    
    # 4. Tabela de Categorias Customizadas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        nome TEXT NOT NULL,
        UNIQUE(usuario, nome)
    )
    """)
    
    # 5. Nova Tabela: Tags Customizadas para o Second Brain
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        nome TEXT NOT NULL,
        UNIQUE(usuario, nome)
    )
    """)
    
    # Inserir categorias padrão de fábrica
    categorias_padrao = ["ALIMENTAÇÃO", "TRANSPORTE", "LAZER", "SAÚDE", "MORADIA", "OUTROS"]
    for cat in categorias_padrao:
        cursor.execute("INSERT OR IGNORE INTO categorias (usuario, nome) VALUES ('sistema', ?)", (cat,))
        
    # Inserir tags padrão de fábrica para o Second Brain
    tags_padrao = ["ESTUDOS", "IDEIAS", "CÓDIGO", "LEITURAS", "PESSOAL", "PROJETOS"]
    for tag in tags_padrao:
        cursor.execute("INSERT OR IGNORE INTO tags (usuario, nome) VALUES ('sistema', ?)", (tag,))
        
    conn.commit()
    conn.close()