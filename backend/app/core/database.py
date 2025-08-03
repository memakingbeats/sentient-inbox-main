import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
import asyncio

# Cliente ChromaDB global
chroma_client = None

async def init_chromadb():
    """Inicializa conexão com ChromaDB"""
    global chroma_client
    
    try:
        # Configurar cliente ChromaDB
        chroma_client = chromadb.HttpClient(
            host=settings.CHROMADB_HOST,
            port=settings.CHROMADB_PORT,
            settings=ChromaSettings(
                chroma_api_impl="rest",
                chroma_server_host=settings.CHROMADB_HOST,
                chroma_server_http_port=settings.CHROMADB_PORT
            )
        )
        
        # Verificar conexão
        chroma_client.heartbeat()
        print(f"✅ Conectado ao ChromaDB em {settings.CHROMADB_HOST}:{settings.CHROMADB_PORT}")
        
        # Criar coleção para emails se não existir
        try:
            collection = chroma_client.get_collection("emails")
            print("✅ Coleção 'emails' encontrada")
        except:
            collection = chroma_client.create_collection("emails")
            print("✅ Coleção 'emails' criada")
            
    except Exception as e:
        print(f"❌ Erro ao conectar com ChromaDB: {e}")
        raise e

def get_chroma_client():
    """Retorna cliente ChromaDB"""
    if chroma_client is None:
        raise Exception("ChromaDB não foi inicializado")
    return chroma_client

def get_emails_collection():
    """Retorna coleção de emails"""
    client = get_chroma_client()
    return client.get_collection("emails") 