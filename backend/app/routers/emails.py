from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.routers.auth import verify_token
from app.services.gmail_service import GmailService
from app.services.ai_service import AIService

router = APIRouter()
security = HTTPBearer()

class EmailResponse(BaseModel):
    id: str
    threadId: str
    subject: str
    sender: str
    date: str
    body: str
    labels: List[str]
    snippet: str
    isRead: bool
    isImportant: bool
    hasAttachments: bool

class EmailAnalysis(BaseModel):
    resumo: str
    sentimento: str
    urgencia: str
    categoria: str
    acoes_recomendadas: List[str]

gmail_service = GmailService()
ai_service = AIService()

@router.get("/", response_model=List[EmailResponse])
async def get_emails(
    max_results: int = Query(50, ge=1, le=100),
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """Busca emails da caixa de entrada"""
    try:
        credentials = gmail_service.get_credentials_from_token({
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'client_id': token_data.get('client_id'),
            'client_secret': token_data.get('client_secret')
        })
        
        emails = gmail_service.get_emails(credentials, max_results=max_results)
        
        # Adicionar emails ao vector store para RAG
        if emails:
            ai_service.add_emails_to_vectorstore(emails)
        
        return emails
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar emails: {str(e)}")

@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(
    email_id: str,
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """Busca email específico"""
    try:
        credentials = gmail_service.get_credentials_from_token({
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'client_id': token_data.get('client_id'),
            'client_secret': token_data.get('client_secret')
        })
        
        # Buscar email específico
        service = gmail_service.build_service(credentials)
        message = service.users().messages().get(
            userId='me',
            id=email_id,
            format='full'
        ).execute()
        
        email_data = gmail_service._parse_email_message(message)
        return email_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar email: {str(e)}")

@router.post("/{email_id}/read")
async def mark_email_as_read(
    email_id: str,
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """Marca email como lido"""
    try:
        credentials = gmail_service.get_credentials_from_token({
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'client_id': token_data.get('client_id'),
            'client_secret': token_data.get('client_secret')
        })
        
        success = gmail_service.mark_as_read(credentials, email_id)
        
        if success:
            return {"message": "Email marcado como lido"}
        else:
            raise HTTPException(status_code=500, detail="Erro ao marcar email como lido")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao marcar email como lido: {str(e)}")

@router.get("/{email_id}/analysis", response_model=EmailAnalysis)
async def analyze_email(
    email_id: str,
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """Analisa email com IA"""
    try:
        credentials = gmail_service.get_credentials_from_token({
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'client_id': token_data.get('client_id'),
            'client_secret': token_data.get('client_secret')
        })
        
        # Buscar email
        service = gmail_service.build_service(credentials)
        message = service.users().messages().get(
            userId='me',
            id=email_id,
            format='full'
        ).execute()
        
        email_data = gmail_service._parse_email_message(message)
        
        # Preparar conteúdo para análise
        content = f"""
        Assunto: {email_data['subject']}
        Remetente: {email_data['sender']}
        Data: {email_data['date']}
        Conteúdo: {email_data['body']}
        """
        
        # Analisar com IA
        analysis = ai_service.analyze_email_content(content)
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

@router.get("/thread/{thread_id}", response_model=List[EmailResponse])
async def get_email_thread(
    thread_id: str,
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """Busca thread completa de emails"""
    try:
        credentials = gmail_service.get_credentials_from_token({
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'client_id': token_data.get('client_id'),
            'client_secret': token_data.get('client_secret')
        })
        
        emails = gmail_service.get_email_thread(credentials, thread_id)
        return emails
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar thread: {str(e)}")

@router.get("/search/semantic")
async def search_emails_semantic(
    query: str = Query(..., description="Query para busca semântica"),
    k: int = Query(5, ge=1, le=20, description="Número de resultados"),
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """Busca emails usando busca semântica"""
    try:
        results = ai_service.search_emails(query, k=k)
        return {
            "query": query,
            "results": results,
            "total": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca semântica: {str(e)}")

@router.get("/stats/overview")
async def get_email_stats(
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """Obtém estatísticas dos emails"""
    try:
        credentials = gmail_service.get_credentials_from_token({
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'client_id': token_data.get('client_id'),
            'client_secret': token_data.get('client_secret')
        })
        
        # Buscar emails para análise
        emails = gmail_service.get_emails(credentials, max_results=100)
        
        # Calcular estatísticas
        total_emails = len(emails)
        unread_emails = len([e for e in emails if not e['isRead']])
        important_emails = len([e for e in emails if e['isImportant']])
        emails_with_attachments = len([e for e in emails if e['hasAttachments']])
        
        # Análise de remetentes
        senders = {}
        for email in emails:
            sender = email['sender']
            senders[sender] = senders.get(sender, 0) + 1
        
        top_senders = sorted(senders.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_emails": total_emails,
            "unread_emails": unread_emails,
            "important_emails": important_emails,
            "emails_with_attachments": emails_with_attachments,
            "top_senders": [{"sender": sender, "count": count} for sender, count in top_senders]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}") 