# ML AutoResponder 🤖

Sistema profissional de respostas automáticas para Mercado Livre com IA (OpenAI GPT-4).
Responde mensagens de compradores **somente fora do horário comercial**.

---

## ✨ Funcionalidades

- 🔔 Recebe webhooks do Mercado Livre com validação HMAC-SHA256
- 🤖 Resposta automática via OpenAI com proteção contra prompt injection
- 🕐 Respeita horário comercial configurável (padrão 08h–18h, America/Sao_Paulo)
- 📊 Dashboard em tempo real via WebSocket
- 🔐 Autenticação JWT + refresh token
- ✅ Aprovação manual opcional
- 📋 Logs detalhados de todos os eventos
- 🛡️ Segurança OWASP Top 10

---

## 🗂️ Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2 (async), Alembic |
| Banco | MySQL 8.0 |
| Cache/Rate limit | Redis 7 |
| IA | OpenAI API (gpt-4o-mini) |
| Frontend | React 18, Vite 5, TailwindCSS 3 |

---

## 🚀 Como Executar Localmente

Você tem duas opções para iniciar o projeto: usar o script automático ou iniciar manualmente.

### Opção A: Início Rápido (Automático)
Na raiz do projeto (onde está a pasta), execute o arquivo `start.bat` para iniciar o Backend e o Frontend simultaneamente:
```bash
.\start.bat
```
*(Você também pode dar um duplo clique no arquivo `start.bat` pelo Explorador de Arquivos do Windows)*

### Opção B: Início Manual

#### 1. Backend

Configure o ambiente virtual e instale as dependências:
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
cp .env.example .env
# Edite o .env configurando o banco de dados (SQLite ou MySQL local)
alembic upgrade head
```

Para iniciar o servidor backend em desenvolvimento:
```bash
uvicorn app.main:app --reload --port 8000
```

**Criar o primeiro usuário admin:**
```bash
python -c "
import asyncio
from app.core.database.engine import AsyncSessionLocal
from app.repositories.user_repository import UserRepository
from app.core.security.password import hash_password

async def main():
    async with AsyncSessionLocal() as s:
        repo = UserRepository(s)
        user = await repo.create('admin', 'admin@empresa.com', hash_password('SuaSenhaForte123!'), is_admin=True)
        await s.commit()
        print(f'Admin criado: {user.username}')

asyncio.run(main())
"
```

### 2. Frontend

Instale as dependências e inicie o servidor do frontend:
```bash
cd frontend
npm install
npm run dev
```

### 3. Acesso

- **Frontend**: http://localhost:5173
- **API Docs** (FastAPI): http://localhost:8000/docs

---

## 🔐 Variáveis de Ambiente Obrigatórias

| Variável | Descrição |
|----------|-----------|
| `DATABASE_URL` | URL de conexão MySQL async |
| `SECRET_KEY` | Chave JWT (gere com `openssl rand -hex 32`) |
| `ML_CLIENT_ID` | Client ID do app Mercado Livre |
| `ML_CLIENT_SECRET` | Client Secret do app ML |
| `ML_ACCESS_TOKEN` | Access Token do ML |
| `ML_WEBHOOK_SECRET` | Secret para validar webhooks |
| `ML_SELLER_ID` | ID do vendedor no ML |
| `OPENAI_API_KEY` | Chave da API OpenAI |

---

## 🧪 Testes

```bash
cd backend
pytest app/tests/ -v
```

---

## 📡 Webhook do Mercado Livre

Configure no painel do ML:
- **URL**: `https://seu-dominio.com/api/v1/webhook/mercadolivre`
- **Tópicos**: `messages`

---

## 🏗️ Arquitetura

```
Mercado Livre
      │ webhook
      ▼
  FastAPI (HMAC validation)
      │
      ├─ MessageRepository → MySQL
      │
      ├─ ScheduleChecker → Horário comercial?
      │         │ Fora do horário
      │         ▼
      │   SafetyFilter → Prompt injection? Ameaça?
      │         │ Seguro
      │         ▼
      │   OpenAI API → Resposta
      │         │
      │   SafetyFilter (saída) → Dado sensível?
      │         │ Limpo
      │         ▼
      │   ML API → Envia resposta ao comprador
      │
      └─ WebSocket → Frontend (tempo real)
```

---

## ⚠️ Segurança

- Nunca commite o arquivo `.env`
- Use HTTPS em produção (Nginx + Let's Encrypt)
- Revise o `ALLOWED_ORIGINS` no `.env`

---

## 📄 Licença

Uso interno. Todos os direitos reservados.
