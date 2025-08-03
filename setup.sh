#!/bin/bash

echo "🚀 Configurando Gmail AI Agent..."

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

echo "✅ Docker e Docker Compose encontrados"

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cat > .env << EOF
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Google OAuth Credentials
GOOGLE_CLIENT_ID=349138754128-rug3moio7qlfq09cukl5hiie9rjr0ru9.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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

# JWT Secret
SECRET_KEY=your_secret_key_here

# Database
CHROMADB_HOST=localhost
CHROMADB_PORT=8001
EOF
    echo "✅ Arquivo .env criado"
    echo "⚠️  IMPORTANTE: Edite o arquivo .env com suas credenciais antes de continuar!"
    echo "   - Adicione sua OPENAI_API_KEY"
    echo "   - Altere SECRET_KEY para uma chave segura"
    read -p "Pressione Enter após editar o arquivo .env..."
fi

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p backend/data
mkdir -p backend/credentials

# Copiar credenciais do Google se existirem
if [ -f "backend/credentials/google_credentials.json" ]; then
    echo "✅ Credenciais do Google encontradas"
else
    echo "⚠️  Credenciais do Google não encontradas em backend/credentials/google_credentials.json"
fi

# Verificar se as variáveis de ambiente estão configuradas
if grep -q "your_openai_api_key_here" .env; then
    echo "❌ OPENAI_API_KEY não foi configurada no arquivo .env"
    echo "   Por favor, adicione sua chave da API OpenAI"
    exit 1
fi

if grep -q "your_secret_key_here" .env; then
    echo "❌ SECRET_KEY não foi configurada no arquivo .env"
    echo "   Por favor, adicione uma chave secreta segura"
    exit 1
fi

echo "✅ Configuração básica concluída"

# Perguntar se quer executar com Docker
echo ""
echo "🎯 Como você gostaria de executar o projeto?"
echo "1) Docker (Recomendado - mais fácil)"
echo "2) Desenvolvimento local"
read -p "Escolha uma opção (1 ou 2): " choice

case $choice in
    1)
        echo "🐳 Iniciando com Docker..."
        docker-compose up --build
        ;;
    2)
        echo "🔧 Iniciando em modo desenvolvimento local..."
        echo ""
        echo "📋 Instruções para desenvolvimento local:"
        echo "1. Terminal 1 - Backend:"
        echo "   cd backend"
        echo "   pip install -r requirements.txt"
        echo "   python main.py"
        echo ""
        echo "2. Terminal 2 - ChromaDB:"
        echo "   docker run -p 8001:8000 chromadb/chroma:latest"
        echo ""
        echo "3. Terminal 3 - Frontend:"
        echo "   npm install"
        echo "   npm run dev"
        echo ""
        echo "🌐 Acesse: http://localhost:5173"
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac 