"""
Configuração do banco de dados
"""
from typing import Optional
import os

# Por enquanto, vamos usar um sistema simples de armazenamento
# em arquivo JSON para os emails

EMAILS_FILE = "data/emails.json"

def ensure_data_directory():
    """Garante que o diretório de dados existe"""
    os.makedirs("data", exist_ok=True)

def get_emails_collection():
    """Retorna uma referência para a coleção de emails (simulada)"""
    ensure_data_directory()
    return {"file": EMAILS_FILE}

def save_emails(emails: list):
    """Salva emails em arquivo JSON"""
    import json
    ensure_data_directory()
    with open(EMAILS_FILE, 'w', encoding='utf-8') as f:
        json.dump(emails, f, ensure_ascii=False, indent=2)

def load_emails() -> list:
    """Carrega emails do arquivo JSON"""
    import json
    ensure_data_directory()
    try:
        with open(EMAILS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return [] 