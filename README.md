# Minha Estante — Backend (API REST)

API REST do **Minha Estante**, um gerenciador de biblioteca pessoal de livros.
O usuário busca livros na API pública do **Google Books**, salva os que quiser
na sua estante, adiciona anotações e remove quando desejar (CRUD completo).

> Este repositório contém **apenas o backend**. O frontend (HTML/CSS/TypeScript)
> fica em um repositório separado.

## Integrantes do grupo

- Alexandre Sanson — 1711450

## Links

- **Site do backend (API):** https://inf1407trabalho2backend-production.up.railway.app
- **Documentação Swagger:** https://inf1407trabalho2backend-production.up.railway.app/api/docs/
- **Repositório do frontend:** https://github.com/ags1999/INF1407_Trabalho2_Frontend
- **Site do frontend:** https://inf1407trabalho2frontend-production.up.railway.app

## Tecnologias

- Python 3.12 + Django 5.1
- Django REST Framework (API REST)
- SimpleJWT (autenticação por tokens JWT)
- drf-spectacular (documentação OpenAPI / Swagger)
- django-cors-headers (liberação de CORS para o frontend)
- WhiteNoise + Gunicorn (produção); PostgreSQL no Railway, SQLite em dev

## Funcionalidades

- **CRUD completo** de livros na estante (`/api/livros/`).
- **Autenticação JWT**: login, refresh e cadastro com **ativação por e-mail**.
- **Endpoint protegido**: todas as rotas de livros exigem token válido.
- **Visões por usuário**: cada usuário só enxerga e manipula a própria estante.
- **Gerência de senha**: troca de senha e recuperação ("esqueci minha senha").
- **Busca de livros** via API do Google Books (`/api/search/`).
- **Swagger** com todos os endpoints documentados e testáveis.

## Principais endpoints

| Método | Rota | Descrição | Autenticado |
|---|---|---|---|
| POST | `/api/auth/register/` | Cadastra usuário (conta inativa) | Não |
| POST | `/api/auth/activate/` | Ativa a conta (uid + token) | Não |
| POST | `/api/auth/login/` | Retorna tokens JWT | Não |
| POST | `/api/auth/refresh/` | Renova o token de acesso | Não |
| POST | `/api/auth/password/change/` | Troca a senha | Sim |
| POST | `/api/auth/password/reset/` | Solicita recuperação de senha | Não |
| POST | `/api/auth/password/reset/confirm/` | Confirma nova senha | Não |
| GET/PATCH | `/api/profile/` | Lê e atualiza o perfil | Sim |
| GET | `/api/search/?q=` | Busca no Google Books | Sim |
| GET/POST | `/api/livros/` | Lista / adiciona livros | Sim |
| GET/PUT/PATCH/DELETE | `/api/livros/{id}/` | Detalhe / edita / remove | Sim |
| GET | `/api/docs/` | Swagger UI | Não |
| GET | `/api/schema/` | Schema OpenAPI | Não |

## Instalação local

Pré-requisitos: **Python 3.12+**.

```bash
git clone https://github.com/ags1999/INF1407_Trabalho2_Backend.git
cd INF1407_Trabalho2_Backend

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # edite os valores (ver seção abaixo)

python manage.py migrate
python manage.py createsuperuser   # opcional, para acessar o /admin/
python manage.py runserver
```

A API fica em `http://localhost:8000` e o Swagger em `http://localhost:8000/api/docs/`.

> **E-mails em desenvolvimento:** sem configuração SMTP, os e-mails de ativação e
> recuperação de senha são **impressos no console** onde o servidor roda. Copie o
> link mostrado para ativar a conta.

### Via Docker

O projeto pode subir junto com o frontend e o Postgres pelo `docker-compose.yml`
(ver repositório do frontend / pasta de deploy). O `Dockerfile` aplica as
migrações e coleta os estáticos **no start** do container.

## Variáveis de ambiente

Veja `.env.example`. **Atenção ao formato** — cada variável tem uma regra
diferente, e o erro mais comum no deploy é confundi-las:

| Variável | Formato | Exemplo |
|---|---|---|
| `SECRET_KEY` | texto | (gere uma chave única em produção) |
| `DEBUG` | `True`/`False` | `False` em produção |
| `ALLOWED_HOSTS` | **só host, sem esquema**, separado por vírgula | `.up.railway.app` |
| `CORS_ALLOWED_ORIGINS` | **URL com `https://`, sem barra final** | `https://meu-front.up.railway.app` |
| `FRONTEND_URL` | **URL com `https://`** (usada nos links de e-mail) | `https://meu-front.up.railway.app` |
| `GBOOKS_API_KEY` | chave da API do Google Books | `AIza...` |
| `DATABASE_URL` | string do Postgres (opcional; sem ela usa SQLite) | `postgres://...` |
| `EMAIL_*` | configuração SMTP (ver seção E-mail) | — |

Resumo: `CORS_ALLOWED_ORIGINS` e `FRONTEND_URL` levam `https://`;
`ALLOWED_HOSTS` vai **sem** esquema.

## Publicação (Railway)

1. Deploy do repositório via GitHub. O Railway usa o `Dockerfile` automaticamente.
2. Adicione um serviço **PostgreSQL** e referencie `DATABASE_URL=${{Postgres.DATABASE_URL}}`.
3. Configure as variáveis acima em *Variables* (respeitando o formato).
4. Gere o domínio público (porta **8000**).
5. Crie o superusuário no ambiente publicado (roda dentro do container, com o
   banco de produção):
   ```bash
   railway ssh python manage.py createsuperuser
   ```

O `Dockerfile` executa `migrate` + `collectstatic` + `gunicorn` no start, então
não há passo manual de deploy. O superusuário criado já nasce **ativo** e serve
tanto para o `/admin/` quanto para login no frontend.

## E-mail (Resend)

O envio de e-mails é configurado **só por variáveis de ambiente** (sem alterar
código). Para usar o Resend, defina no backend:

```
EMAIL_HOST=smtp.resend.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=resend
EMAIL_HOST_PASSWORD=re_suaApiKey
DEFAULT_FROM_EMAIL=onboarding@resend.dev   # ou um endereço de domínio verificado
```

Sem `EMAIL_HOST` definido, o backend usa o modo console (e-mail aparece só no log).

## Testes

```bash
python manage.py test
```

6 testes cobrindo proteção de endpoints, login com token, CRUD de livros e o
isolamento entre usuários.



## O que funcionou / o que não funcionou

**Funcionou (testado):**

- CRUD completo de livros pela API (testado via `curl`, testes automatizados e
  pelo frontend publicado).
- Cadastro com ativação por e-mail e gerência de senha (troca e recuperação).
- Login/refresh JWT e bloqueio de endpoints sem token (401).
- Isolamento entre usuários (cada um vê só os próprios livros).
- Documentação Swagger com todos os endpoints.
- Publicação no Railway (backend + PostgreSQL) com domínio HTTPS.

**Pontos de atenção:**

- A **busca depende da `GBOOKS_API_KEY`**: sem chave, a API do Google responde
  **429 (cota anônima esgotada)** e a busca pode falhar de forma intermitente.
  Com a chave configurada, fica estável.
- A busca também depende de o backend ter **acesso à internet** para alcançar a
  API do Google Books.
- O backend serve apenas a API; o `/admin/` e o Swagger usam o HTML nativo do
  Django/DRF (não há frontend próprio no backend).