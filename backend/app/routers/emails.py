from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer
from typing import List, Optional
import jwt
from datetime import datetime, timedelta
import json

from app.services.gmail_service import GmailService
from app.services.ai_service import AIService
from app.core.config import settings
from app.core.database import save_emails, load_emails

router = APIRouter()
security = HTTPBearer()

# Função para obter token do header
def get_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autorização inválido")
    return authorization.replace("Bearer ", "")

# Função para decodificar token
def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

@router.get("/")
async def get_emails(token: str = Depends(get_token)):
    """Busca emails do Gmail"""
    try:
        # Decodificar token
        payload = decode_token(token)
        access_token = payload.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=401, detail="Token de acesso não encontrado")
        
        # Inicializar serviço Gmail
        gmail_service = GmailService()
        emails = await gmail_service.get_emails(access_token)
        
        # Salvar emails localmente
        save_emails(emails)
        
        return emails
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar emails: {str(e)}")

@router.post("/{email_id}/read")
async def mark_as_read(email_id: str, token: str = Depends(get_token)):
    """Marca email como lido"""
    try:
        payload = decode_token(token)
        access_token = payload.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=401, detail="Token de acesso não encontrado")
        
        gmail_service = GmailService()
        await gmail_service.mark_as_read(access_token, email_id)
        
        return {"message": "Email marcado como lido"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao marcar email como lido: {str(e)}")

@router.get("/{email_id}/analysis")
async def analyze_email(email_id: str, token: str = Depends(get_token)):
    """Analisa email com IA"""
    try:
        payload = decode_token(token)
        access_token = payload.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=401, detail="Token de acesso não encontrado")
        
        # Buscar email específico
        gmail_service = GmailService()
        email = await gmail_service.get_email(access_token, email_id)
        
        if not email:
            raise HTTPException(status_code=404, detail="Email não encontrado")
        
        # Inicializar serviço de IA
        ai_service = AIService()
        
        # Analisar conteúdo do email
        content = f"Assunto: {email.get('subject', '')}\n\n{email.get('body', '')}"
        analysis = ai_service.analyze_email_content(content)
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}") 