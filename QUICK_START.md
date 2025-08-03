# 🚀 Início Rápido - Gmail AI Agent

## ⚡ Execução Rápida (5 minutos)

### 1. Pré-requisitos

-   Docker e Docker Compose instalados
-   Chave da API OpenAI
-   Conta Google com Gmail

### 2. Configuração Rápida

```bash
# Clone o repositório
git clone <repository-url>
cd sentient-inbox-main

# Execute o script de setup
./setup.sh
```

### 3. Configurar Credenciais

Edite o arquivo `.env` criado:

```env
OPENAI_API_KEY=sua_chave_openai_aqui
SECRET_KEY=chave_secreta_aleatoria_aqui
```

### 4. Executar com Docker

```bash
docker-compose up --build
```

### 5. Acessar

-   Frontend: http://localhost:5173
-   Backend API: http://localhost:8000
-   ChromaDB: http://localhost:8001

## 🔧 Configuração Manual

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend

```bash
npm install
npm run dev
```

### ChromaDB

```bash
docker run -p 8001:8000 chromadb/chroma:latest
```

## 📱 Primeiro Uso

1. Acesse http://localhost:5173
2. Clique em "Conectar ao Gmail"
3. Autorize o acesso à sua conta
4. Explore seus emails com IA!

## 🆘 Problemas Comuns

### Erro de CORS

-   Verifique se o backend está rodando na porta 8000
-   Confirme as configurações no `backend/app/core/config.py`

### Erro de Autenticação

-   Verifique se as credenciais do Google estão corretas
-   Confirme os URIs de redirecionamento no Google Cloud Console

### ChromaDB não conecta

```bash
docker-compose restart chromadb
```

## 📞 Suporte

-   Email: riscocuts@gmail.com
-   Issues: GitHub Issues

---

**Pronto para usar! 🎉**
