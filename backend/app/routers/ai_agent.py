from fastapi import APIRouter, HTTPException, Depends, Query, Header
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import jwt
from app.core.config import settings
from app.core.database import load_emails
from app.services.ai_service import AIService

router = APIRouter()
security = HTTPBearer()

class AIQuery(BaseModel):
    query: str
    context: Optional[str] = ""

class AIResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]] = []
    confidence: float = 0.0

class EmailInsights(BaseModel):
    temas_principais: List[str]
    remetentes_frequentes: List[str]
    padroes_comunicacao: str
    sugestoes_organizacao: List[str]

def get_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autorização inválido")
    return authorization.replace("Bearer ", "")

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

@router.post("/chat", response_model=AIResponse)
async def chat_with_ai(
    ai_query: AIQuery,
    token: str = Depends(get_token)
):
    """Chat com o agente de IA sobre emails"""
    try:
        ai_service = AIService()
        # Buscar emails relevantes usando busca semântica
        relevant_emails = ai_service.search_emails(ai_query.query, k=5)
        
        # Preparar contexto dos emails encontrados
        context = ""
        sources = []
        
        for email in relevant_emails:
            context += f"\n{email['content']}\n"
            sources.append({
                'subject': email['metadata'].get('subject', ''),
                'sender': email['metadata'].get('sender', ''),
                'date': email['metadata'].get('date', ''),
                'content': email['content'][:200] + "..." if len(email['content']) > 200 else email['content']
            })
        
        # Gerar resposta com IA
        full_context = f"{ai_query.context}\n\nEmails relevantes:\n{context}"
        response = ai_service.generate_email_response(ai_query.query, full_context)
        
        return AIResponse(
            response=response,
            sources=sources,
            confidence=0.8  # Placeholder
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no chat com IA: {str(e)}")

@router.get("/insights", response_model=EmailInsights)
async def get_email_insights(
    max_emails: int = Query(50, ge=10, le=200),
    token: str = Depends(get_token)
):
    """Obtém insights gerais sobre os emails"""
    try:
        ai_service = AIService()
        emails = load_emails()
        
        if not emails:
            return EmailInsights(
                temas_principais=[],
                remetentes_frequentes=[],
                padroes_comunicacao="Nenhum email encontrado para análise",
                sugestoes_organizacao=[]
            )
        
        # Gerar insights com IA
        insights = ai_service.get_email_insights(emails)
        
        return EmailInsights(
            temas_principais=insights.get('temas_principais', []),
            remetentes_frequentes=insights.get('remetentes_frequentes', []),
            padroes_comunicacao=insights.get('padroes_comunicacao', ''),
            sugestoes_organizacao=insights.get('sugestoes_organizacao', [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar insights: {str(e)}")

@router.post("/analyze-batch")
async def analyze_emails_batch(
    email_ids: List[str],
    token: str = Depends(get_token)
):
    """Analisa múltiplos emails em lote"""
    try:
        ai_service = AIService()
        emails = load_emails()
        analyses = []
        
        for email_id in email_ids[:10]:  # Limitar a 10 emails por vez
            try:
                email_data = next((e for e in emails if e.get('id') == email_id), None)
                if not email_data:
                    print(f"Email {email_id} não encontrado.")
                    continue
                
                # Preparar conteúdo para análise
                content = f"""
                Assunto: {email_data['subject']}
                Remetente: {email_data['sender']}
                Data: {email_data['date']}
                Conteúdo: {email_data['body']}
                """
                
                # Analisar com IA
                analysis = ai_service.analyze_email_content(content)
                analysis['email_id'] = email_id
                analysis['subject'] = email_data['subject']
                analysis['sender'] = email_data['sender']
                
                analyses.append(analysis)
                
            except Exception as e:
                print(f"Erro ao analisar email {email_id}: {e}")
                continue
        
        return {
            "total_analyzed": len(analyses),
            "analyses": analyses
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise em lote: {str(e)}")

@router.get("/search/advanced")
async def advanced_email_search(
    query: str = Query(..., description="Query de busca"),
    category: Optional[str] = Query(None, description="Categoria (trabalho, pessoal, etc.)"),
    sentiment: Optional[str] = Query(None, description="Sentimento (positivo, negativo, neutro)"),
    urgency: Optional[str] = Query(None, description="Urgência (alta, média, baixa)"),
    k: int = Query(10, ge=1, le=50),
    token: str = Depends(get_token)
):
    """Busca avançada de emails com filtros"""
    try:
        ai_service = AIService()
        # Busca semântica inicial
        results = ai_service.search_emails(query, k=k*2)  # Buscar mais para filtrar depois
        
        # Aplicar filtros se especificados
        filtered_results = []
        
        for result in results:
            # Analisar cada resultado para aplicar filtros
            analysis = ai_service.analyze_email_content(result['content'])
            
            # Aplicar filtros
            if category and analysis.get('categoria') != category:
                continue
            if sentiment and analysis.get('sentimento') != sentiment:
                continue
            if urgency and analysis.get('urgencia') != urgency:
                continue
            
            filtered_results.append({
                **result,
                'analysis': analysis
            })
            
            if len(filtered_results) >= k:
                break
        
        return {
            "query": query,
            "filters": {
                "category": category,
                "sentiment": sentiment,
                "urgency": urgency
            },
            "results": filtered_results,
            "total": len(filtered_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca avançada: {str(e)}")

@router.post("/generate-response")
async def generate_email_response(
    email_id: str,
    context: Optional[str] = "",
    token: str = Depends(get_token)
):
    """Gera resposta para um email específico"""
    try:
        ai_service = AIService()
        emails = load_emails()
        email_data = next((e for e in emails if e.get('id') == email_id), None)
        
        if not email_data:
            raise HTTPException(status_code=404, detail=f"Email com ID {email_id} não encontrado.")
        
        # Preparar conteúdo do email
        email_content = f"""
        Assunto: {email_data['subject']}
        Remetente: {email_data['sender']}
        Data: {email_data['date']}
        Conteúdo: {email_data['body']}
        """
        
        # Gerar resposta
        response = ai_service.generate_email_response(email_content, context)
        
        return {
            "email_id": email_id,
            "original_email": {
                "subject": email_data['subject'],
                "sender": email_data['sender'],
                "content": email_data['body']
            },
            "generated_response": response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resposta: {str(e)}")

@router.get("/recommendations")
async def get_email_recommendations(
    token: str = Depends(get_token)
):
    """Obtém recomendações baseadas nos emails"""
    try:
        ai_service = AIService()
        emails = load_emails()
        
        if not emails:
            return {"recommendations": []}
        
        # Analisar emails para gerar recomendações
        insights = ai_service.get_email_insights(emails)
        
        # Gerar recomendações baseadas nos insights
        recommendations = []
        
        # Recomendação baseada em remetentes frequentes
        if insights.get('remetentes_frequentes'):
            recommendations.append({
                "type": "frequent_sender",
                "title": "Remetentes Frequentes",
                "description": f"Você recebe muitos emails de: {', '.join(insights['remetentes_frequentes'][:3])}",
                "action": "Considerar criar filtros ou labels para organizar melhor"
            })
        
        # Recomendação baseada em temas
        if insights.get('temas_principais'):
            recommendations.append({
                "type": "main_topics",
                "title": "Temas Principais",
                "description": f"Principais temas em seus emails: {', '.join(insights['temas_principais'][:3])}",
                "action": "Criar labels específicos para cada tema"
            })
        
        # Recomendação baseada em sugestões
        if insights.get('sugestoes_organizacao'):
            for suggestion in insights['sugestoes_organizacao'][:2]:
                recommendations.append({
                    "type": "organization",
                    "title": "Sugestão de Organização",
                    "description": suggestion,
                    "action": "Implementar sugestão"
                })
        
        return {"recommendations": recommendations}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar recomendações: {str(e)}") 