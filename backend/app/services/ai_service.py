from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from typing import List, Dict, Any
import json
from app.core.config import settings
from app.core.database import get_emails_collection

class AIService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Embeddings para português
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Vector store
        self.vectorstore = None
        
    def setup_vectorstore(self):
        """Configura vector store com ChromaDB"""
        try:
            self.vectorstore = Chroma(
                client=get_emails_collection()._client,
                collection_name="emails",
                embedding_function=self.embeddings
            )
            print("✅ Vector store configurado")
        except Exception as e:
            print(f"❌ Erro ao configurar vector store: {e}")
    
    def add_emails_to_vectorstore(self, emails: List[Dict[str, Any]]):
        """Adiciona emails ao vector store"""
        if not self.vectorstore:
            self.setup_vectorstore()
        
        documents = []
        for email in emails:
            # Criar documento para LangChain
            content = f"""
            Assunto: {email['subject']}
            Remetente: {email['sender']}
            Data: {email['date']}
            Conteúdo: {email['body']}
            Snippet: {email['snippet']}
            Labels: {', '.join(email['labels'])}
            """
            
            doc = Document(
                page_content=content,
                metadata={
                    'email_id': email['id'],
                    'subject': email['subject'],
                    'sender': email['sender'],
                    'date': email['date'],
                    'labels': email['labels']
                }
            )
            documents.append(doc)
        
        # Dividir documentos
        split_docs = self.text_splitter.split_documents(documents)
        
        # Adicionar ao vector store
        if split_docs:
            self.vectorstore.add_documents(split_docs)
            print(f"✅ {len(split_docs)} documentos adicionados ao vector store")
    
    def search_emails(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Busca emails semânticos"""
        if not self.vectorstore:
            self.setup_vectorstore()
        
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            return [
                {
                    'content': doc.page_content,
                    'metadata': doc.metadata
                }
                for doc in results
            ]
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            return []
    
    def analyze_email_content(self, email_content: str) -> Dict[str, Any]:
        """Analisa conteúdo do email com IA"""
        prompt = PromptTemplate(
            input_variables=["email_content"],
            template="""
            Analise o seguinte email e forneça:
            1. Resumo do conteúdo
            2. Sentimento (positivo, negativo, neutro)
            3. Urgência (alta, média, baixa)
            4. Categorização (trabalho, pessoal, spam, etc.)
            5. Ações recomendadas
            
            Email:
            {email_content}
            
            Responda em JSON com a seguinte estrutura:
            {{
                "resumo": "resumo do email",
                "sentimento": "positivo/negativo/neutro",
                "urgencia": "alta/media/baixa",
                "categoria": "trabalho/pessoal/spam/etc",
                "acoes_recomendadas": ["ação1", "ação2"]
            }}
            """
        )
        
        try:
            chain = prompt | self.llm
            result = chain.invoke({"email_content": email_content})
            
            # Tentar parsear JSON da resposta
            try:
                return json.loads(result.content)
            except:
                return {
                    "resumo": result.content,
                    "sentimento": "neutro",
                    "urgencia": "media",
                    "categoria": "outro",
                    "acoes_recomendadas": []
                }
                
        except Exception as e:
            print(f"❌ Erro na análise: {e}")
            return {
                "resumo": "Erro na análise",
                "sentimento": "neutro",
                "urgencia": "media",
                "categoria": "outro",
                "acoes_recomendadas": []
            }
    
    def generate_email_response(self, email_content: str, context: str = "") -> str:
        """Gera resposta para email"""
        prompt = PromptTemplate(
            input_variables=["email_content", "context"],
            template="""
            Com base no seguinte email, gere uma resposta profissional e apropriada.
            
            Email original:
            {email_content}
            
            Contexto adicional:
            {context}
            
            Responda de forma clara, profissional e direta ao ponto.
            """
        )
        
        try:
            chain = prompt | self.llm
            result = chain.invoke({
                "email_content": email_content,
                "context": context
            })
            return result.content
        except Exception as e:
            print(f"❌ Erro ao gerar resposta: {e}")
            return "Erro ao gerar resposta."
    
    def get_email_insights(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gera insights sobre os emails"""
        if not emails:
            return {}
        
        # Preparar dados para análise
        email_texts = []
        for email in emails:
            text = f"Assunto: {email['subject']}\nRemetente: {email['sender']}\nConteúdo: {email['body']}"
            email_texts.append(text)
        
        combined_text = "\n\n".join(email_texts[:10])  # Limitar a 10 emails
        
        prompt = PromptTemplate(
            input_variables=["emails"],
            template="""
            Analise os seguintes emails e forneça insights:
            
            {emails}
            
            Forneça:
            1. Principais temas/tópicos
            2. Remetentes mais frequentes
            3. Padrões de comunicação
            4. Sugestões de organização
            
            Responda em JSON:
            {{
                "temas_principais": ["tema1", "tema2"],
                "remetentes_frequentes": ["remetente1", "remetente2"],
                "padroes_comunicacao": "descrição dos padrões",
                "sugestoes_organizacao": ["sugestão1", "sugestão2"]
            }}
            """
        )
        
        try:
            chain = prompt | self.llm
            result = chain.invoke({"emails": combined_text})
            
            try:
                return json.loads(result.content)
            except:
                return {
                    "temas_principais": [],
                    "remetentes_frequentes": [],
                    "padroes_comunicacao": "Análise não disponível",
                    "sugestoes_organizacao": []
                }
                
        except Exception as e:
            print(f"❌ Erro nos insights: {e}")
            return {} 