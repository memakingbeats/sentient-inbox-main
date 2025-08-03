from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv
import os

from app.routers import auth, emails, ai_agent
from app.core.config import settings
from app.core.database import init_chromadb

# Carregar variáveis de ambiente
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Iniciando Gmail AI Agent...")
    await init_chromadb()
    print("✅ ChromaDB inicializado")
    yield
    # Shutdown
    print("🛑 Encerrando aplicação...")

app = FastAPI(
    title="Gmail AI Agent",
    description="Backend para análise inteligente de emails com LangChain e ChromaDB",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(emails.router, prefix="/emails", tags=["emails"])
app.include_router(ai_agent.router, prefix="/ai", tags=["ai-agent"])

@app.get("/")
async def root():
    return {
        "message": "Gmail AI Agent API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 