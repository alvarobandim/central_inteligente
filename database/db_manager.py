import sqlite3
import os

DB_PATH = "central_inteligente.db"

def conectar_db():
    return sqlite3.connect(DB_PATH)

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

    # 3. Tabela de Categorias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            nome TEXT NOT NULL
        )
    """)

    # 4. Tabela de Notas (Second Brain)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            titulo TEXT NOT NULL,
            conteudo TEXT,
            tags TEXT
        )
    """)

    # 5. Tabela de Tags (Para as Notas e Tarefas)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            nome TEXT NOT NULL
        )
    """)

    # 6. Tabela de Tarefas Avançada (Kanban)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            titulo TEXT NOT NULL,
            descricao TEXT,
            status TEXT NOT NULL DEFAULT 'A FAZER',
            importancia TEXT NOT NULL DEFAULT 'MÉDIA', -- BAIXA, MÉDIA, ALTA
            data_entrega TEXT,                         -- Formato YYYY-MM-DD
            tags TEXT                                  -- Tags separadas por vírgula
        )
    """)

    conn.commit()
    conn.close()