import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from typing import List, Dict, Any
import json
from app.core.config import settings

class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7,
            google_api_key=settings.GEMINI_API_KEY
        )
    
    def analyze_email_content(self, email_content: str) -> Dict[str, Any]:
        """Analisa o conteúdo de um email usando IA"""
        prompt = PromptTemplate(
            input_variables=["email_content"],
            template="""
            Analise o seguinte email e forneça uma resposta em JSON com a seguinte estrutura:
            {{
                "resumo": "resumo conciso do email",
                "sentimento": "positivo/negativo/neutro",
                "urgencia": "alta/media/baixa",
                "categoria": "trabalho/pessoal/spam/outro",
                "acoes_recomendadas": ["ação1", "ação2"]
            }}

            Email para análise:
            {email_content}

            Responda APENAS com o JSON válido, sem texto adicional.
            """
        )
        
        try:
            response = self.llm.invoke(prompt.format(email_content=email_content))
            # Tenta extrair JSON da resposta
            content = response.content
            if isinstance(content, str):
                # Remove possíveis prefixos/sufixos não-JSON
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = content[start:end]
                    return json.loads(json_str)
            return {
                "resumo": "Análise não disponível",
                "sentimento": "neutro",
                "urgencia": "media",
                "categoria": "outro",
                "acoes_recomendadas": ["Revisar manualmente"]
            }
        except Exception as e:
            print(f"Erro na análise de email: {e}")
            return {
                "resumo": "Erro na análise",
                "sentimento": "neutro",
                "urgencia": "media",
                "categoria": "outro",
                "acoes_recomendadas": ["Revisar manualmente"]
            }
    
    def generate_email_response(self, email_content: str, context: str = "") -> str:
        """Gera uma resposta para um email usando IA"""
        prompt = PromptTemplate(
            input_variables=["email_content", "context"],
            template="""
            Com base no seguinte email, gere uma resposta profissional e apropriada em português.

            Email original:
            {email_content}

            Contexto adicional:
            {context}

            Responda de forma clara, profissional e direta ao ponto. Use linguagem formal mas acessível.
            """
        )
        
        try:
            response = self.llm.invoke(prompt.format(email_content=email_content, context=context))
            return response.content
        except Exception as e:
            print(f"Erro na geração de resposta: {e}")
            return "Desculpe, não foi possível gerar uma resposta no momento."
    
    def get_email_insights(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gera insights sobre uma lista de emails"""
        emails_text = "\n".join([f"De: {email.get('from', 'N/A')} - Assunto: {email.get('subject', 'N/A')} - Data: {email.get('date', 'N/A')}" for email in emails])
        
        prompt = PromptTemplate(
            input_variables=["emails"],
            template="""
            Analise os seguintes emails e forneça insights em JSON:

            {emails}

            Responda com JSON válido contendo:
            {{
                "temas_principais": ["tema1", "tema2"],
                "remetentes_frequentes": ["remetente1", "remetente2"],
                "padroes_comunicacao": "descrição dos padrões",
                "sugestoes_organizacao": ["sugestão1", "sugestão2"]
            }}

            Responda APENAS com o JSON válido.
            """
        )
        
        try:
            response = self.llm.invoke(prompt.format(emails=emails_text))
            content = response.content
            if isinstance(content, str):
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = content[start:end]
                    return json.loads(json_str)
            return {
                "temas_principais": ["Análise não disponível"],
                "remetentes_frequentes": [],
                "padroes_comunicacao": "Não foi possível analisar",
                "sugestoes_organizacao": ["Revisar manualmente"]
            }
        except Exception as e:
            print(f"Erro na geração de insights: {e}")
            return {
                "temas_principais": ["Erro na análise"],
                "remetentes_frequentes": [],
                "padroes_comunicacao": "Erro na análise",
                "sugestoes_organizacao": ["Revisar manualmente"]
            }
    
    def search_emails_semantic(self, query: str, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Busca semântica em emails (versão simplificada)"""
        # Por enquanto, retorna todos os emails que contêm a query no assunto ou conteúdo
        results = []
        query_lower = query.lower()
        
        for email in emails:
            subject = email.get('subject', '').lower()
            content = email.get('content', '').lower()
            
            if query_lower in subject or query_lower in content:
                results.append(email)
        
        return results[:10]  # Limita a 10 resultados 