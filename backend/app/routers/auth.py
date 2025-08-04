from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Dict, Any
import jwt
from datetime import datetime, timedelta
from app.core.config import settings
from app.services.gmail_service import GmailService
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request, HTTPException
import os
import httpx




router = APIRouter()
security = HTTPBearer()

# Adicione estas constantes no topo do arquivo (ou crie um config.py)
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
GOOGLE_CLIENT_ID = os.getenv("349138754128-rug3moio7qlfq09cukl5hiie9rjr0ru9.apps.googleusercontent.com")
GOOGLE_CLIENT_SECRET = os.getenv("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")


class TokenRequest(BaseModel):
    access_token: str
    refresh_token: str
    client_id: str
    client_secret: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

gmail_service = GmailService()

def create_access_token(data: Dict[str, Any]) -> str:
    """Cria JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str = Depends(security)) -> Dict[str, Any]:
    """Verifica JWT token"""
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

@router.post("/google", response_model=TokenResponse)
async def google_auth(token_request: TokenRequest):
    """Autenticação com Google OAuth"""
    try:
        # Criar credenciais do Google
        credentials = gmail_service.get_credentials_from_token({
            'access_token': token_request.access_token,
            'refresh_token': token_request.refresh_token,
            'client_id': token_request.client_id,
            'client_secret': token_request.client_secret
        })
        
        # Testar credenciais buscando emails
        emails = gmail_service.get_emails(credentials, max_results=1)
        
        if not emails:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
        # Criar JWT token
        token_data = {
            "sub": "user",
            "access_token": token_request.access_token,
            "refresh_token": token_request.refresh_token,
            "client_id": token_request.client_id,
            "client_secret": token_request.client_secret
        }
        
        access_token = create_access_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Erro na autenticação: {str(e)}")

@router.get("/me")
async def get_current_user(token_data: Dict[str, Any] = Depends(verify_token)):
    """Obtém informações do usuário atual"""
    try:
        credentials = gmail_service.get_credentials_from_token({
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'client_id': token_data.get('client_id'),
            'client_secret': token_data.get('client_secret')
        })
        
        # Buscar informações do perfil Gmail
        service = gmail_service.build_service(credentials)
        profile = service.users().getProfile(userId='me').execute()
        
        return {
            "email": profile.get('emailAddress'),
            "name": profile.get('name', ''),
            "messagesTotal": profile.get('messagesTotal', 0),
            "threadsTotal": profile.get('threadsTotal', 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter perfil: {str(e)}")

        # Adicione esta nova rota ao seu router existente
@router.get("/auth/callback", response_class=HTMLResponse)  # Corrigido para bater com o frontend
async def google_auth_callback(request: Request, code: str):
    try:
        redirect_uri = f"{os.getenv('FRONTEND_ORIGIN')}/auth/callback"  # Corrigido
        
        # Use seu gmail_service para trocar o código por tokens
        tokens = await gmail_service.exchange_code_for_tokens(code, redirect_uri)
        
        html_content = f"""
        <script>
            window.opener.postMessage({{
                type: 'auth_success',
                token: '{tokens["access_token"]}'
            }}, '{os.getenv("FRONTEND_ORIGIN")}');
            window.close();
        </script>
        """
        return HTMLResponse(content=html_content)
    
    except Exception as e:
        error_html = f"""
        <script>
            window.opener.postMessage({{
                type: 'auth_error',
                error: 'Falha na autenticação'
            }}, '{os.getenv("FRONTEND_ORIGIN")}');
            window.close();
        </script>
        """
        return HTMLResponse(content=error_html, status_code=400)
    
@router.post("/refresh")
async def refresh_token(token_data: Dict[str, Any] = Depends(verify_token)):
    """Renova token de acesso"""
    try:
        # Criar novo token com dados atualizados
        new_token_data = {
            "sub": "user",
            "access_token": token_data.get('access_token'),
            "refresh_token": token_data.get('refresh_token'),
            "client_id": token_data.get('client_id'),
            "client_secret": token_data.get('client_secret')
        }
        
        new_access_token = create_access_token(new_token_data)
        
        return TokenResponse(
            access_token=new_access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao renovar token: {str(e)}") 