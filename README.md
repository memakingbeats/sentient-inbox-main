# Gmail AI Agent

Sistema completo de análise inteligente de emails usando Gmail API, LangChain, ChromaDB e Google Gemini 2.0 Flash.

## 🚀 Funcionalidades

-   **Autenticação Gmail**: Integração completa com Google OAuth
-   **Análise de IA**: Processamento inteligente de emails com LangChain
-   **Busca Semântica**: RAG (Retrieval-Augmented Generation) com ChromaDB
-   **Interface Moderna**: Frontend React com Tailwind CSS e shadcn/ui
-   **Containerização**: Docker para fácil deploy
-   **Análise Avançada**: Sentimento, urgência, categorização automática

## 🛠️ Tecnologias

### Frontend

-   React 18 + TypeScript
-   Vite
-   Tailwind CSS
-   shadcn/ui
-   React Router
-   TanStack Query

### Backend

-   FastAPI (Python)
-   LangChain
-   ChromaDB (Vector Database)
-   Google Gmail API
-   Google Gemini 2.0 Flash
-   Docker

## 📋 Pré-requisitos

-   Node.js 18+
-   Python 3.11+
-   Docker e Docker Compose
-   Conta Google com Gmail API habilitada
-   Chave da API Google Gemini

## 🔧 Configuração

### 1. Clone o repositório

```bash
git clone <repository-url>
cd sentient-inbox-main
```

### 2. Configurar Frontend

```bash
# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env
```

### 3. Configurar Backend

```bash
cd backend

# Copiar arquivo de exemplo
cp env.example .env

# Editar .env com suas credenciais
GEMINI_API_KEY=AIzaSyA9kPO-NCce1wpTTVQPTeZB3rF_zxDg_Wk
GOOGLE_CLIENT_ID=349138754128-rug3moio7qlfq09cukl5hiie9rjr0ru9.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
SECRET_KEY=sua_chave_secreta_aqui
```

### 4. Configurar Gmail API

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto ou use o existente
3. Habilite a Gmail API
4. Configure as credenciais OAuth 2.0:
    - **ID do Cliente**: `349138754128-rug3moio7qlfq09cukl5hiie9rjr0ru9.apps.googleusercontent.com`
    - **Origem JavaScript**: `http://localhost:5173`
    - **URI de Redirecionamento**: `http://localhost:5173/auth/callback`
    - **Escopos**:
        - `https://www.googleapis.com/auth/gmail.readonly`
        - `https://www.googleapis.com/auth/gmail.modify`

## 🚀 Executando o Projeto

### Opção 1: Docker (Recomendado)

```bash
# Na raiz do projeto
docker-compose up --build
```

### Opção 2: Desenvolvimento Local

#### Backend

```bash
cd backend

# Instalar dependências Python
pip install -r requirements.txt

# Executar ChromaDB
docker run -p 8001:8000 chromadb/chroma:latest

# Executar backend
python main.py
```

#### Frontend

```bash
# Em outro terminal
npm run dev
```

## 📱 Uso

1. Acesse `http://localhost:5173`
2. Clique em "Conectar ao Gmail"
3. Autorize o acesso à sua conta Gmail
4. Explore seus emails com análise de IA

## 🔍 Funcionalidades Principais

### Análise de Emails

-   **Resumo Automático**: IA gera resumos dos emails
-   **Análise de Sentimento**: Identifica tom positivo/negativo/neutro
-   **Detecção de Urgência**: Classifica prioridade alta/média/baixa
-   **Categorização**: Organiza por trabalho/pessoal/spam/etc

### Busca Inteligente

-   **Busca Semântica**: Encontra emails por significado, não apenas palavras-chave
-   **Filtros Avançados**: Por categoria, sentimento, urgência
-   **RAG**: Retrieval-Augmented Generation para respostas contextuais

### Insights e Recomendações

-   **Padrões de Comunicação**: Identifica remetentes frequentes
-   **Temas Principais**: Extrai tópicos recorrentes
-   **Sugestões de Organização**: Recomendações para melhor gestão

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   ChromaDB      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Vector DB)   │
│   Porta 5173    │    │   Porta 8000    │    │   Porta 8001    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Gmail API     │
                       │   (Google)      │
                       └─────────────────┘
```

## 🔧 Configurações Avançadas

### Variáveis de Ambiente

#### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=349138754128-rug3moio7qlfq09cukl5hiie9rjr0ru9.apps.googleusercontent.com
```

#### Backend (.env)

```env
GEMINI_API_KEY=AIzaSyA9kPO-NCce1wpTTVQPTeZB3rF_zxDg_Wk
GOOGLE_CLIENT_ID=349138754128-rug3moio7qlfq09cukl5hiie9rjr0ru9.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
SECRET_KEY=sua_chave_secreta
CHROMADB_HOST=localhost
CHROMADB_PORT=8001
```

### Personalização

#### Modelos de IA

Edite `backend/app/services/ai_service.py` para alterar:

-   Modelo Gemini (gemini-2.0-flash-exp, gemini-1.5-pro)
-   Embeddings (sentence-transformers)
-   Prompts personalizados

#### Interface

Modifique `src/components/` para:

-   Adicionar novos componentes
-   Personalizar temas
-   Implementar novas funcionalidades

## 🐛 Troubleshooting

### Problemas Comuns

1. **Erro de CORS**

    - Verifique se o backend está rodando na porta 8000
    - Confirme as configurações CORS no backend

2. **Erro de Autenticação Gmail**

    - Verifique as credenciais no Google Cloud Console
    - Confirme os URIs de redirecionamento

3. **ChromaDB não conecta**

    - Verifique se o container está rodando: `docker ps`
    - Reinicie: `docker-compose restart chromadb`

4. **Erro Gemini**

    - Verifique se a API key está correta
    - Confirme se tem créditos disponíveis na Google AI Studio

### Logs

```bash
# Backend logs
docker-compose logs backend

# ChromaDB logs
docker-compose logs chromadb

# Frontend logs (desenvolvimento)
npm run dev
```

## 📊 Monitoramento

### Endpoints de Saúde

-   `GET /health` - Status do backend
-   `GET /` - Informações da API

### Métricas

-   Número de emails processados
-   Tempo de resposta da IA
-   Uso do ChromaDB

## 🔒 Segurança

-   Tokens JWT para autenticação
-   Credenciais OAuth seguras
-   CORS configurado adequadamente
-   Validação de entrada em todas as APIs

## 📝 Licença

MIT License - veja o arquivo LICENSE para detalhes.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:

-   Email: riscocuts@gmail.com
-   Issues: Use a seção Issues do GitHub

---

**Desenvolvido com ❤️ usando React, FastAPI, LangChain, ChromaDB e Google Gemini 2.0 Flash**
