"""
Module: Security Authentication Engine
Description: Manipulação de hashing criptográfico seguro utilizando a biblioteca bcrypt
             para proteção de credenciais no banco de dados.
"""
import bcrypt

def gerar_hash_senha(senha_pura: str) -> str:
    """Transforma a senha digitada em um hash criptográfico seguro."""
    # Gera um salt (combinação aleatória) e aplica o hash
    salt = bcrypt.gensalt(rounds=12)
    senha_bytes = senha_pura.encode('utf-8')
    hash_resultado = bcrypt.hashpw(senha_bytes, salt)
    return hash_resultado.decode('utf-8')

def verificar_senha(senha_digitada: str, hash_banco: str) -> bool:
    """Compara a senha digitada com o hash guardado para validar o acesso."""
    try:
        return bcrypt.checkpw(
            senha_digitada.encode('utf-8'), 
            hash_banco.encode('utf-8')
        )
    except Exception:
        return False