# MentorPDI

Mentor de carreira em TI movido a Inteligência Artificial. O usuário informa seu perfil
profissional e a aplicação gera, via IA, um **Plano de Desenvolvimento Individual (PDI)**
completo: diagnóstico, trilha de estudos, certificações recomendadas e cronograma.

Projeto acadêmico — disciplina de desenvolvimento com integração de IA.

## Funcionalidades

- Cadastro e login de usuário (senha com hash bcrypt).
- Geração de PDI personalizado por IA (funcionalidade inteligente principal).
- Persistência em banco de dados (SQLite por padrão).
- Histórico de PDIs gerados, com visualização detalhada de cada um.
- Integração de IA desacoplada (Google Gemini por padrão; troca fácil de provider).

## Stack

Python · FastAPI · SQLModel · Jinja2 · Tailwind CSS · Google Gemini API

## Rodar com Docker (VM / servidor)

Recomendado pra deixar a aplicação rodando num servidor (ex.: VM no Proxmox).
O banco fica num volume persistente, então sobrevive a restart e rebuild.

### 1. Pré-requisitos na VM
- Docker e Docker Compose instalados.

### 2. Configurar o `.env`

```bash
cp .env.example .env
nano .env
```

Importante: no Docker, aponte o banco para o volume (note as **4 barras**):

```
DATABASE_URL=sqlite:////data/mentorpdi.db
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sua-chave-aqui
```

### 3. Subir

```bash
docker compose up -d --build
```

A aplicação fica acessível em `http://IP_DA_VM:8000` (a partir de qualquer máquina
na mesma rede/VPN da VM).

### 4. Comandos úteis

```bash
docker compose logs -f        # ver logs
docker compose restart        # reiniciar
docker compose down           # parar (o volume com o banco é preservado)
docker compose down -v        # parar E apagar o banco (cuidado!)
```

> Se a VM tiver firewall (ufw), libere a porta: `sudo ufw allow 8000/tcp`.

## Como rodar (local, sem Docker)

### 1. Pré-requisitos
- Python 3.11 ou superior
- Uma chave de API de IA (ex.: Anthropic)

### 2. Instalar dependências

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar o ambiente

```bash
cp .env.example .env
```

Edite o `.env` e preencha:

```
SECRET_KEY=uma-chave-aleatoria-longa
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sua-chave-aqui
AI_MODEL=claude-sonnet-4-20250514
```

> Para testar a aplicação **sem consumir API**, use `AI_PROVIDER=mock` (gera um PDI de
> exemplo). Não use o modo mock na apresentação final — a banca quer ver a IA real.

### 4. Subir o servidor

```bash
uvicorn app.main:app --reload
```

Acesse: http://127.0.0.1:8000

### 5. Usar

1. Crie uma conta.
2. Clique em **Novo PDI** e preencha seu perfil.
3. A IA gera o plano; ele fica salvo no seu painel.

## Trocar de banco para PostgreSQL

No `.env`:

```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/mentorpdi
```

(instale também `psycopg2-binary`).

## Estrutura

```
app/
  main.py          # aplicação FastAPI
  config.py        # configuração (.env)
  database.py      # banco de dados
  models.py        # tabelas User e PDI
  auth.py          # autenticação
  ai_service.py    # integração com IA
  routers/         # rotas (auth e pdi)
  templates/       # HTML (Jinja2)
  static/          # CSS
docs/DOCUMENTACAO.md
```

A documentação completa (problema, arquitetura, funcionamento da IA, desafios e conclusão)
está em [`docs/DOCUMENTACAO.md`](docs/DOCUMENTACAO.md).
