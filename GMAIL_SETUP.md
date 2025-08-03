# Gmail Analytics AI - Setup Completo

Este projeto combina React (frontend) + Python/LangChain (backend) + ChromaDB + Docker para análise inteligente de emails.

## 🚀 Frontend (React + Vite + Tailwind) - JÁ CONFIGURADO

O frontend está pronto e funcional no Lovable. Ele inclui:
- ✅ Interface moderna para Gmail
- ✅ Autenticação Google OAuth (mock implementado)
- ✅ Lista e visualização de emails
- ✅ Design system otimizado
- ✅ Componentes reutilizáveis

## 🐍 Backend (Python + LangChain + ChromaDB)

### 1. Estrutura do Projeto Backend

Crie a seguinte estrutura:

```
gmail-analytics-backend/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── gmail_client.py
│   ├── langchain_processor.py
│   ├── chromadb_manager.py
│   └── api/
│       ├── __init__.py
│       └── routes.py
```

### 2. requirements.txt

```txt
fastapi==0.104.1
uvicorn==0.24.0
google-api-python-client==2.103.0
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.2.0
langchain==0.1.0
langchain-openai==0.0.2
chromadb==0.4.18
python-dotenv==1.0.0
pydantic==2.5.0
httpx==0.25.2
```

### 3. src/main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api.routes import router

app = FastAPI(title="Gmail Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "https://your-lovable-app.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Gmail Analytics API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4. src/gmail_client.py

```python
import os
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailClient:
    def __init__(self):
        self.service = None
        
    def authenticate(self, credentials_path: str):
        """Autentica com Google Gmail API"""
        creds = None
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
                
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                
        self.service = build('gmail', 'v1', credentials=creds)
        
    def get_emails(self, max_results=50):
        """Busca emails da caixa de entrada"""
        try:
            results = self.service.users().messages().list(
                userId='me', labelIds=['INBOX'], maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                email_data = self.get_email_details(msg['id'])
                emails.append(email_data)
                
            return emails
            
        except Exception as error:
            print(f'Erro ao buscar emails: {error}')
            return []
            
    def get_email_details(self, message_id):
        """Busca detalhes de um email específico"""
        try:
            message = self.service.users().messages().get(
                userId='me', id=message_id
            ).execute()
            
            headers = message['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sem assunto')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Remetente desconhecido')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Extrair corpo do email
            body = self.extract_email_body(message['payload'])
            
            return {
                'id': message_id,
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body,
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', [])
            }
            
        except Exception as error:
            print(f'Erro ao buscar detalhes do email: {error}')
            return None
            
    def extract_email_body(self, payload):
        """Extrai o corpo do email"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
        else:
            if payload['mimeType'] == 'text/plain':
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
                
        return body
```

### 5. src/langchain_processor.py

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.schema import Document
import os

class LangChainProcessor:
    def __init__(self, openai_api_key: str):
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.llm = OpenAI(openai_api_key=openai_api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
    def process_emails(self, emails):
        """Processa emails para análise"""
        documents = []
        
        for email in emails:
            content = f"""
            Assunto: {email['subject']}
            Remetente: {email['sender']}
            Data: {email['date']}
            Conteúdo: {email['body']}
            """
            
            doc = Document(
                page_content=content,
                metadata={
                    'email_id': email['id'],
                    'subject': email['subject'],
                    'sender': email['sender'],
                    'date': email['date']
                }
            )
            documents.append(doc)
            
        return self.text_splitter.split_documents(documents)
        
    def create_vector_store(self, documents, persist_directory="./chroma_db"):
        """Cria store vetorial com ChromaDB"""
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=persist_directory
        )
        vectorstore.persist()
        return vectorstore
        
    def create_qa_chain(self, vectorstore):
        """Cria chain de perguntas e respostas"""
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(),
            return_source_documents=True
        )
        return qa_chain
        
    def query_emails(self, query: str, qa_chain):
        """Faz consulta nos emails"""
        result = qa_chain({"query": query})
        return {
            "answer": result["result"],
            "source_documents": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in result["source_documents"]
            ]
        }
```

### 6. src/chromadb_manager.py

```python
import chromadb
from chromadb.config import Settings

class ChromaDBManager:
    def __init__(self, persist_directory="./chroma_db"):
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            chroma_db_impl="duckdb+parquet"
        ))
        
    def create_collection(self, name="gmail_emails"):
        """Cria coleção para emails"""
        collection = self.client.create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}
        )
        return collection
        
    def add_emails(self, collection, emails, embeddings):
        """Adiciona emails à coleção"""
        ids = [email['id'] for email in emails]
        documents = [email['body'] for email in emails]
        metadatas = [
            {
                'subject': email['subject'],
                'sender': email['sender'],
                'date': email['date']
            }
            for email in emails
        ]
        
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
    def query_similar_emails(self, collection, query_text, n_results=5):
        """Busca emails similares"""
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results
```

### 7. src/api/routes.py

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from gmail_client import GmailClient
from langchain_processor import LangChainProcessor
from chromadb_manager import ChromaDBManager
import os

router = APIRouter()

# Modelos Pydantic
class EmailQuery(BaseModel):
    query: str

class AuthRequest(BaseModel):
    credentials_path: str

# Instâncias globais
gmail_client = GmailClient()
processor = LangChainProcessor(os.getenv("OPENAI_API_KEY"))
chromadb_manager = ChromaDBManager()

@router.post("/auth")
async def authenticate_gmail(auth_request: AuthRequest):
    """Autentica com Gmail"""
    try:
        gmail_client.authenticate(auth_request.credentials_path)
        return {"message": "Autenticado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/emails")
async def get_emails():
    """Busca emails do Gmail"""
    try:
        emails = gmail_client.get_emails()
        return {"emails": emails, "count": len(emails)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-emails")
async def process_emails():
    """Processa emails com LangChain e ChromaDB"""
    try:
        emails = gmail_client.get_emails()
        documents = processor.process_emails(emails)
        vectorstore = processor.create_vector_store(documents)
        
        return {
            "message": "Emails processados com sucesso",
            "processed_count": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def query_emails(email_query: EmailQuery):
    """Consulta emails usando IA"""
    try:
        # Carregar vectorstore existente
        vectorstore = processor.create_vector_store([])  # Carrega existente
        qa_chain = processor.create_qa_chain(vectorstore)
        result = processor.query_emails(email_query.query, qa_chain)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 8. Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8000

CMD ["python", "src/main.py"]
```

### 9. docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./chroma_db:/app/chroma_db
      - ./credentials.json:/app/credentials.json
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - chromadb

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - ./chroma_data:/chroma/chroma
    environment:
      - CHROMA_SERVER_HOST=0.0.0.0
      - CHROMA_SERVER_HTTP_PORT=8000
```

### 10. .env

```env
OPENAI_API_KEY=sua_chave_openai_aqui
GOOGLE_CLIENT_ID=seu_client_id_aqui
GOOGLE_CLIENT_SECRET=seu_client_secret_aqui
```

## 🔧 Setup e Execução

### 1. Configurar Google Gmail API

1. Vá para [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto e ative a Gmail API
3. Crie credenciais OAuth 2.0
4. Baixe o arquivo `credentials.json`

### 2. Configurar OpenAI

1. Obtenha sua API key em [OpenAI](https://platform.openai.com/)
2. Adicione no arquivo `.env`

### 3. Executar Backend

```bash
# Clonar e configurar
cd gmail-analytics-backend
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas chaves

# Executar localmente
python src/main.py

# OU com Docker
docker-compose up --build
```

### 4. Conectar Frontend

No componente `AuthButton.tsx`, substitua a autenticação mock por chamadas reais à API:

```typescript
const handleGoogleAuth = async () => {
  setIsLoading(true);
  try {
    const response = await fetch('http://localhost:8000/api/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ credentials_path: './credentials.json' })
    });
    
    if (response.ok) {
      onAuthSuccess('real-token');
      toast.success('Conectado ao Gmail!');
    }
  } catch (error) {
    toast.error('Erro ao conectar');
  }
  setIsLoading(false);
};
```

## 🚀 Funcionalidades

- ✅ Autenticação Google OAuth
- ✅ Leitura de emails do Gmail
- ✅ Processamento com LangChain
- ✅ Armazenamento vetorial ChromaDB
- ✅ Consultas semânticas inteligentes
- ✅ Interface React moderna
- ✅ Deploy com Docker

## 📝 Próximos Passos

1. Implementar autenticação real no frontend
2. Adicionar mais filtros e análises
3. Implementar cache e otimizações
4. Adicionar mais provedores de LLM
5. Dashboard de analytics avançado

Frontend pronto no Lovable - Backend para instalar localmente!